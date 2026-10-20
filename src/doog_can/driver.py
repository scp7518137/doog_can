"""Provide an interface to control the motor over the CAN bus"""
from .protocol import (
    build_frame, 
    decode_frame,
    decode_opentoangle,
    feedback_frame_id,
    feedback_opentoangle_id,
    StatusReport,
    OpenToAngle,
    )

from .constants import (
    CmdList
)

import can

class IDError(Exception):
    """Raised when a received CAN frame has an unepxected ID"""
    pass

class Motor:
    """Control an motor over the CAN bus.

    Args:
        bus: CAN bus used to send and receive mseeages.
        node_id: ID of the motor node.
    """
    def __init__(self, bus: can.BusABC, node_id: int) -> None:
        """Initialize the move controller."""
        self._bus = bus
        self._node_id = node_id
        self._feedback_frame_id = feedback_frame_id(node_id)
        self._feedback_opentoangle_id = feedback_opentoangle_id(node_id)


    def _msg_build(self, cmd: int, value:float = 0) -> can.Message:
        """Build a CAN message for the given command"""
        frame_id, data = build_frame(self._node_id, cmd, value)
        msg: can.Message = can.Message(arbitration_id=frame_id, is_extended_id=False, data=data)
        return msg

        
    def msg_recv(self, msg: can.Message) -> tuple[int, StatusReport| OpenToAngle]:
        """decode a motor status response.
        
        Raises:
            IDError: The received frame ID does not match the expected ID.
        """
        msg_id = msg.arbitration_id
        msg_data = bytes(msg.data)
        
        if msg_id == self._feedback_frame_id:
            return self._node_id, decode_frame(msg_data)

        if msg_id == self._feedback_opentoangle_id:
            return self._node_id, decode_opentoangle(msg_data)

        raise IDError(
        f"node {self._node_id} recv error ID:0x{msg_id:X}"
        )


    def build_speed_cmd(self, value: float) -> None:
        """Build a speed command.

        Args:
            value: Value sent with the command rad/s.
        """
        self._msg_build(CmdList.SPEED, value)

    
    def build_voltage_cmd(self, value: float) -> None:
        """Build a voltage command.

        Args:
            value: Value sent with the command V.
        """
        self._msg_build(CmdList.VOLTAGE, value)


    def build_mode_cmd(self, value: float) -> can.Message:
        """Build a mode command.

        Args:
            0	IDLE	                No output.
            1	open-loop	            Open-loop voltage/speed drive.
            2	align	                Two-step rotor alignment.
            3	closed-loop torque      With Iq directly commanded.
            4   closed-loop speed	    Speed loop -> current loop.
            5	closed-loop position	Position loop -> speed loop -> current loop.

        """
        return self._msg_build(CmdList.MODE, value)

    
    def build_direction_cmd(self, value: float) -> can.Message:
        """Build a direction command.

        Args:
            0  Forward rotation
            1  Reverse rotation
        """
        return self._msg_build(CmdList.DIRECTION, value)


    def build_torque_cmd(self, value: float) -> can.Message:
        """Build a torque command.

        Args:
            value: Value sent with the command N * M.
        """
        return self._msg_build(CmdList.TORQUE, value)


    def build_position_cmd(self, value: float) -> can.Message:
        """Build a position command.

        Args:
            value: Value sent with the command.
        """
        return self._msg_build(CmdList.POSITION, value)


    def build_open_to_angle_cmd(self, value: float) -> can.Message:
        """Build an open-to-angle command.

        Args:
            value: Value sent with the command deg.
        """
        return self._msg_build(CmdList.OPENTOANGLE, value)


    def build_ask_status_cmd(self) -> can.Message:
        """Build an ask status command."""

        return self._msg_build(CmdList.ASKSTATUS)


    def build_ask_open_to_angle_cmd(self) -> can.Message:
        """Build an ask open_to_angle command."""
        return self._msg_build(CmdList.ASKOPENTOANGLE)
