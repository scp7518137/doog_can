"""Define constants and enumerations for the CAN motor protocol."""
from enum import IntEnum
from enum import IntFlag

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

SCALE_MOVEANGLE: int = 10
SCALE_SETTINGVOLTAGE: int = 100
SCALE_RELHOVDEV = 100

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
    SPEED           = 0x01
    VOLTAGE         = 0x02
    MODE            = 0x03
    DIRECTION       = 0x04
    TORQUE          = 0x05
    POSITION        = 0x06
    OPENTOANGLE     = 0x07
    KEEPALIVE       = 0x08
    ASKOPENTOANGLE  = 0x09
    ASKSTATUS       = 0x10


class CommandMode(IntEnum):
    """
    0	IDLE	                No output.
    1	open-loop	            Open-loop voltage/speed drive.
    2	align	                Two-step rotor alignment.
    3	closed-loop torque      With Iq directly commanded.
    4   closed-loop speed	    Speed loop -> current loop.
    5	closed-loop position	Position loop -> speed loop -> current loop.

    """
    IDLE            = 0
    OPENLOOP        = 1
    ALIGN           = 2
    CLOSED_TORQUE   = 3
    CLOSED_SPEED    = 4
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
    IDLE            = 0
    OPENLOOP        = 1
    ALIGN           = 2
    CLOSED_TORQUE   = 3
    CLOSED_SPEED    = 4
    CLOSED_POSITION = 5
    FAULT           = 6


class SystemStatus(IntEnum):
    """
    0  idle/ready(IDLE)
    1  running(alignment/open-loop/closed-loop)
    2  FAULT
    """
    IDLE    = 0
    RUNNING = 1
    FAULT   = 2


class OpenToAngleMode(IntEnum):
    """
    0  inactive
    1  moving
    2  finished
    3  repull
    """
    INITSTATE   = 0
    RUNNING     = 1
    STOPPED     = 2
    REPULL      = 3

class AutoTage(IntEnum):
    """
    0   ask answer
    1   auto answer
    """
    ASKANSWER   = 0
    AUTOANSWER  = 1

class MotorFaultCode_z(IntEnum):
    """
    1   HARDWARE
    2   STALL
    3   ENCODER_STALL
    4   OVERTEMP
    5   OVERVOLT
    6   UNDERVOLT
    7   OVERSPEED
    8   PHASE_OC
    9   I2T
    10  POS_ERROR
    11  SOFT_LIMIT
    12  COMM_TIMEOUT
    """
    HARDWARE        = 1
    STALL           = 2
    ENCODER_STALL   = 3
    OVERTEMP        = 4
    OVERVOLT        = 5
    UNDERVOLT       = 6
    OVERSPEED       = 7
    PHASE_OC        = 8
    I2T             = 9
    POS_ERROR       = 10
    SOFT_LIMIT      = 11
    COMM_TIMEOUT    = 12

class MotorFaultCode_f(IntEnum):
    """
    0x80     Fault status and Model 1 and model 2 is unavailable
    0xC0     Fault status and Model 1 and model 2 is available
    """
    MODELAVA    = 0x80
    MODELUAVA   = 0xc0

class MotorFaultCode_ff(IntEnum):
    """
    0 	0x0001 	VDS_LC 	C-phase low-side VDS overcurrent
    1 	0x0002 	VDS_HC 	C-phase high-side VDS overcurrent
    2 	0x0004 	VDS_LB 	B-phase low-side VDS overcurrent
    3 	0x0008 	VDS_HB 	B-phase high-side VDS overcurrent
    4 	0x0010 	VDS_LA 	A-phase low-side VDS overcurrent
    5 	0x0020 	VDS_HA 	A-phase high-side VDS overcurrent
    6 	0x0040 	OTSD 	Overtemperature shutdown (junction temp exceeded; check heatsink / sustained high current)
    7 	0x0080 	UVLO 	Undervoltage lockout (VM supply too low; check bus / supply dip)
    8 	0x0100 	GDF 	Gate-driver fault (driver-stage general fault)
    9 	0x0200 	VDS_OCP 	VDS monitor overcurrent (phase current exceeds VDS_LVL threshold; usually stall / short circuit)
    10 	0x0400 	FAULT 	Fault status bit (nFAULT logic OR): latches high on any hardware fault; use as a master switch, not as an individual fault cause
    """
    VDS_LC   = 0x0001
    VDS_HC   = 0x0002
    VDS_LB   = 0x0004
    VDS_HB   = 0x0008
    VDS_LA   = 0x0010
    VDS_HA   = 0x0020
    OTSD     = 0x0040
    UVLO     = 0x0080
    GDF      = 0x0100
    VDS_OCP  = 0x0200
    FAULT    = 0x0400

class MotorFaultCode_ss(IntEnum):
    """
    0 	0x0001 	VGS_LC 	C-phase low-side MOSFET VGS gate drive fault
    1 	0x0002 	VGS_HC 	C-phase high-side MOSFET VGS gate drive fault
    2 	0x0004 	VGS_LB 	B-phase low-side MOSFET VGS gate drive fault
    3 	0x0008 	VGS_HB 	B-phase high-side MOSFET VGS gate drive fault
    4 	0x0010 	VGS_LA 	A-phase low-side MOSFET VGS gate drive fault
    5 	0x0020 	VGS_HA 	A-phase high-side MOSFET VGS gate drive fault
    6 	0x0040 	GDUV 	Gate-driver undervoltage (VCP / VGLS, charge pump abnormal)
    7 	0x0080 	OTW 	Overtemperature warning (no shutdown; precedes OTSD, can be used as early warning)
    8 	0x0100 	SC_OC 	C-phase current sense amplifier (CSA) overcurrent
    9 	0x0200 	SB_OC 	B-phase CSA overcurrent
    10 	0x0400 	SA_OC 	A-phase CSA overcurrent
    """
    VGS_LC   = 0x0001
    VGS_HC   = 0x0002
    VGS_LB   = 0x0004
    VGS_HB   = 0x0008
    VGS_LA   = 0x0010
    VGS_HA   = 0x0020
    GDUV     = 0x0040
    OTW      = 0x0080
    SC_OC    = 0x0100
    SB_OC    = 0x0200
    SA_OC    = 0x0400
