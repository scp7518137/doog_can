"""Define constants and enumerations for the CAN motor protocol."""
from enum import IntEnum

# Base arbitration ID for outgoing command frames.
CMD_FRAME_ID_BASE: int = 0x100
# Base arbitration ID for incoming status feedback frames.
FEEDBACK_FRAME_ID_BASE: int = 0x200
# Base arbitration ID for incoming open-to-angle feedback frames.
FEEDBACK_OPENTOANGLE_ID_BASE: int = 0x300
# Minimum valid motor node ID.
NODE_ID_MIN: int = 1
# Maximum valid motor node ID.
NODE_ID_MAX: int = 12
# Length in bytes of every CAN data field.
CAN_DATA_LEN: int = 8

# CAN bus bitrate in bits per second.
CAN_BITRATE_BPS: int = 1_000_000

# Communication timeout in milliseconds.
COMM_TIMEOUT_MS: float = 20.0

# Scale factors used to convert between physical values and raw integers.
SCALE_SPEED: int = 10
SCALE_VOLTAGE: int = 100
SCALE_TORQUE: int = 100
SCALE_POSITION: int = 10_000
SCALE_CURRENT: int = 100
SCALE_BUS_VOLTAGE: int = 10
SCALE_OPENTOANGLE: int = 10

SCALE_REMAINANGLE: int = 10
SCALE_SETTINGVOLTAGE: int = 100

class CmdList(IntEnum):
    """Command identifiers sent from the host to a motor node.

    0x01  SPEED          Set target speed.
    0x02  VOLTAGE        Set target voltage.
    0x03  MODE           Set control mode.
    0x04  DIRECTION      Set rotation direction.
    0x05  TORQUE         Set target torque.
    0x06  POSITION       Set target position.
    0x07  OPENTOANGLE    Start an open-to-angle movement.
    0x08  KEEPALIVE      Keep-alive heartbeat with no payload.
    0x10  ASKSTATUS      Request a status feedback frame.
    0x11  ASKOPENTOANGLE Request an open-to-angle feedback frame.
    """
    SPEED = 0x01
    VOLTAGE = 0x02
    MODE = 0x03
    DIRECTION = 0x04
    TORQUE = 0x05
    POSITION = 0x06
    OPENTOANGLE = 0x07
    KEEPALIVE = 0x08
    ASKOPENTOANGLE = 0x09
    ASKSTATUS = 0x10


class CommandMode(IntEnum):
    """
    0	IDLE	                No output.
    1	open-loop	            Open-loop voltage/speed drive.
    2	align	                Two-step rotor alignment.
    3	closed-loop torque      With Iq directly commanded.
    4   closed-loop speed	    Speed loop -> current loop.
    5	closed-loop position	Position loop -> speed loop -> current loop.

    """
    IDLE = 0
    OPENLOOP = 1
    ALIGN = 2
    CLOSED_TORQUE = 3
    CLOSED_SPEED = 4
    CLOSED_POSITION = 5


class Direction(IntEnum):
    """
    0  Forward rotation
    1  Reverse rotation
    """
    FORWARD = 0
    REVERSE = 1


class FeedbackMode(IntEnum):
    """
    0	IDLE	                No output.
    1	open-loop	            Open-loop voltage/speed drive.
    2	align	                Two-step rotor alignment.
    3	closed-loop torque      With Iq directly commanded.
    4   closed-loop speed	    Speed loop -> current loop.
    5	closed-loop position	Position loop -> speed loop -> current loop.
    6   FAULT                   Fault state.
    """
    IDLE = 0
    OPENLOOP = 1
    ALIGN = 2
    CLOSED_TORQUE = 3
    CLOSED_SPEED = 4
    CLOSED_POSITION = 5
    FAULT = 6


class SystemStatus(IntEnum):
    """
    0  idle/ready(IDLE)
    1  running(alignment/open-loop/closed-loop)
    2  FAULT
    """
    IDLE = 0
    RUNNING = 1
    FAULT = 2


class OpenToAngleMode(IntEnum):
    """
    0  inactive
    1  moving
    2  finished
    """
    INITSTATE = 0
    RUNNING = 1
    STOPPED = 2