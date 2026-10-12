"""Encode and decode CAN frames for the motor protocol.

This module converts high-level commands and physical values into raw CAN
frames, and parses received feedback frames back into typed reports.
"""
from .constants import (
    CMD_FRAME_ID_BASE,
    FEEDBACK_FRAME_ID_BASE,
    FEEDBACK_OPENTOANGLE_ID_BASE,
    NODE_ID_MIN,
    NODE_ID_MAX,
    CAN_DATA_LEN,
    SCALE_SPEED,
    SCALE_VOLTAGE,
    SCALE_TORQUE,
    SCALE_POSITION,
    SCALE_CURRENT,
    SCALE_BUS_VOLTAGE,
    SCALE_OPENTOANGLE,
    SCALE_REMAINANGLE,
    SCALE_SETTINGVOLTAGE,
    CommandMode,
    Direction,
    FeedbackMode,
    SystemStatus,
    CmdList,
    OpenToAngleMode,
)
from dataclasses import dataclass

@dataclass(frozen=True)
class StatusReport:
    """Decoded motor status feedback.

    Attributes:
        status: Current system status of the motor.
        speed: Measured speed in scaled physical units.
        current: Measured phase current in scaled physical units.
        mode: Active feedback (control) mode.
        bus_voltage: Measured bus voltage in scaled physical units.
    """
    status: SystemStatus
    speed: float
    current: float
    mode: FeedbackMode
    bus_voltage: float

@dataclass(frozen=True)
class OpenToAngle:
    """Decoded open-to-angle feedback.

    Attributes:
        status: Current state of the open-to-angle operation.
        remainangle: Remaining angle to travel in scaled physical units.
        settingvoltage: Configured voltage for the movement in scaled units.
        busvoltage: Measured bus voltage in scaled physical units.
        remain: Remaining step count as a raw integer.
    """
    status: OpenToAngleMode
    remainangle: float
    settingvoltage: float
    busvoltage: float
    remain: int


def _check_node_id(node_id: int) -> None:
    """Validate that a node ID is within the supported range.

    Raises:
        ValueError: The node ID is outside [NODE_ID_MIN, NODE_ID_MAX].
    """
    if node_id < NODE_ID_MIN or node_id > NODE_ID_MAX:
        raise ValueError(f"node out of range: {NODE_ID_MIN}-{NODE_ID_MAX}, got {node_id}")

def cmd_frame_id(node_id: int) -> int:
    """Compute the arbitration ID of a command frame for a node.

    Args:
        node_id: ID of the target motor node.

    Returns:
        The arbitration ID used to send commands to the node.

    Raises:
        ValueError: The node ID is outside the supported range.
    """
    _check_node_id(node_id)
    return CMD_FRAME_ID_BASE + node_id


def feedback_frame_id(node_id: int) -> int:
    """Compute the arbitration ID of a status feedback frame for a node.

    Args:
        node_id: ID of the target motor node.

    Returns:
        The arbitration ID on which status feedback is received.

    Raises:
        ValueError: The node ID is outside the supported range.
    """
    _check_node_id(node_id)
    return FEEDBACK_FRAME_ID_BASE + node_id

def feedback_opentoangle_id(node_id: int) -> int:
    """Compute the arbitration ID of an open-to-angle feedback frame.

    Args:
        node_id: ID of the target motor node.

    Returns:
        The arbitration ID on which open-to-angle feedback is received.

    Raises:
        ValueError: The node ID is outside the supported range.
    """
    _check_node_id(node_id)
    return FEEDBACK_OPENTOANGLE_ID_BASE + node_id

def _pack_int16(value: float, scale: int) -> bytes:
    """Scale a float and pack it into a signed 16-bit little-endian value.

    Args:
        value: Physical value to encode.
        scale: Multiplier applied before rounding to an integer.

    Returns:
        Two bytes representing the signed 16-bit integer.

    Raises:
        ValueError: The scaled value does not fit in a signed 16-bit integer.
    """
    rounded: int = round( value * scale)
    if not (-32768 <= rounded <= 32767):
        raise ValueError(f"value out of range: {-32768/scale:.2f}-{32767/scale:.2f}, got {value}")
    return rounded.to_bytes(2, "little", signed=True)


def _pack_int32(value: float, scale: int) -> bytes:
    """Scale a float and pack it into a signed 32-bit little-endian value.

    Args:
        value: Physical value to encode.
        scale: Multiplier applied before rounding to an integer.

    Returns:
        Four bytes representing the signed 32-bit integer.

    Raises:
        ValueError: The scaled value does not fit in a signed 32-bit integer.
    """
    rounded: int = round( value * scale)
    if not (-2147483648 <= rounded <= 2147483647):
        raise ValueError(f"value out of range: {-2147483648/scale:.2f}-{2147483647/scale:.2f}, got {value}")
    return rounded.to_bytes(4, "little", signed=True)

def build_frame(node_id: int, cmd: int, value: float ) -> tuple[int, bytes]:
    """Build a CAN frame for the given command and value.

    Args:
        node_id: ID of the target motor node.
        cmd: Command identifier from CmdList.
        value: Physical value associated with the command.

    Returns:
        A tuple of the arbitration ID and the padded CAN data bytes.

    Raises:
        ValueError: The command is unknown or the payload is too large.
    """
    frame_id = cmd_frame_id(node_id)
    match cmd:
            case CmdList.SPEED:
                payload = _pack_int16(value, SCALE_SPEED)
            case CmdList.VOLTAGE:
                payload = _pack_int16(value, SCALE_VOLTAGE)
            case CmdList.MODE:
                payload = bytes([CommandMode(value)])
            case CmdList.DIRECTION:
                payload = bytes([Direction(value)])
            case CmdList.TORQUE:
                payload = _pack_int16(value, SCALE_TORQUE)
            case CmdList.POSITION:
                payload = _pack_int32(value, SCALE_POSITION)
            case CmdList.OPENTOANGLE:
                payload = _pack_int16(value, SCALE_OPENTOANGLE)
            case CmdList.KEEPALIVE:
                payload = b""
            case CmdList.ASKSTATUS:
                payload = b""
            case CmdList.ASKOPENTOANGLE:
                payload = b""
            case _:
                raise ValueError(f"This command not alive: {cmd:#x}")

    if len(payload) > CAN_DATA_LEN - 1:
        raise ValueError(f"payload max {CAN_DATA_LEN - 1} bytes, but {len(payload)} bytes")
    
    data = bytes([cmd]) + payload
    return frame_id, data.ljust(CAN_DATA_LEN, b"\x00")

def decode_frame(msgdata: bytes) -> StatusReport:
    """Decode a status feedback frame into a StatusReport.

    Args:
        msgdata: Raw CAN data bytes of length CAN_DATA_LEN.

    Returns:
        The decoded status report.

    Raises:
        ValueError: The data length is not CAN_DATA_LEN.
    """
    if len(msgdata) != CAN_DATA_LEN:
        raise ValueError(f"msgdata should {CAN_DATA_LEN} bytes, but {len(msgdata)} bytes")
    return StatusReport(
        status=SystemStatus(msgdata[0]),
        speed=int.from_bytes(msgdata[1:3], "little", signed=True) / SCALE_SPEED,
        current=int.from_bytes(msgdata[3:5], "little", signed=True) / SCALE_CURRENT,
        mode=FeedbackMode(msgdata[5]),
        bus_voltage=int.from_bytes(msgdata[6:8], "little", signed=True) / SCALE_BUS_VOLTAGE,
    )

def decode_opentoangle(msgdata: bytes) -> OpenToAngle:
    """Decode an open-to-angle feedback frame into an OpenToAngle report.

    Args:
        msgdata: Raw CAN data bytes of length CAN_DATA_LEN.

    Returns:
        The decoded open-to-angle report.

    Raises:
        ValueError: The data length is not CAN_DATA_LEN.
    """
    if len(msgdata) != CAN_DATA_LEN:
        raise ValueError(f"msgdata should {CAN_DATA_LEN} bytes, but {len(msgdata)} bytes")
    return OpenToAngle(
        status=OpenToAngleMode(msgdata[0]),
        remainangle=int.from_bytes(msgdata[1:3], "little", signed=True) / SCALE_REMAINANGLE,
        settingvoltage=int.from_bytes(msgdata[3:5], "little", signed=True) / SCALE_SETTINGVOLTAGE,
        busvoltage=int.from_bytes(msgdata[5:7], "little", signed=True) / SCALE_BUS_VOLTAGE,
        remain=msgdata[7]
    )


