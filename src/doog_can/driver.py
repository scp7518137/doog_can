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

    def _msg_send(self, cmd: int, value: float = 0):
        """Build and send a CAN message for the given command."""
        frame_id, data = build_frame(self._node_id, cmd, value)
        msg: can.Message = can.Message(arbitration_id=frame_id, is_extended_id=False, data=data)
        self._bus.send(msg)

#######################################################################
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

########################################################################
    def _msg_receive(self) -> tuple[int, StatusReport]:
        """Receive and decode a motor status response.

        Raises:
            TimeoutError: Noresponse is received before the timeout.
            IDError: The received frame ID does not match the expected ID.
        """
        msg = self._bus.recv(timeout = 0.05)
        if msg is None:
            raise TimeoutError("Timeout")
        msg_id = msg.arbitration_id
        if msg_id != self._feedback_frame_id:
            raise IDError
        msg_data = bytes(msg.data)
        report: StatusReport = decode_frame(msg_data)
        return msg_id - 0x200, report

    def _msg_opentoangle_receive(self) -> tuple[int, OpenToAngle]:
        """Receive and decode an open-to-angle response.

        Raises:
            TimeoutError: No response is received before the timeout.
            IDError: The received frame ID does not match the expected ID.
        """
        msg = self._bus.recv(timeout = 1.0)
        if msg is None:
            raise TimeoutError("Timeout")
        msg_id = msg.arbitration_id
        if msg_id != self._feedback_opentoangle_id:
            raise IDError
        msg_data = bytes(msg.data)
        report: OpenToAngle = decode_opentoangle(msg_data)
        return msg_id, report
    
    # def set_speed(self, value: float) -> None:
    #     """Send a speed command.

    #     Args:
    #         value: Value sent with the command rad/s.
    #     """
    #     self._msg_send(CmdList.SPEED, value)

    # def set_voltage(self, value: float) -> None:
    #     """Send a voltage command.

    #     Args:
    #         value: Value sent with the command V.
    #     """
    #     self._msg_send(CmdList.VOLTAGE, value)

    # def set_mode(self, value: float) -> None:
    #     """Send a mode command.

    #     Args:
    #         0	IDLE	                No output.
    #         1	open-loop	            Open-loop voltage/speed drive.
    #         2	align	                Two-step rotor alignment.
    #         3	closed-loop torque      With Iq directly commanded.
    #         4   closed-loop speed	    Speed loop -> current loop.
    #         5	closed-loop position	Position loop -> speed loop -> current loop.

    #     """
    #     self._msg_send(CmdList.MODE, value)

    # def set_direction(self, value: float) -> None:
    #     """Send a direction command.

    #     Args:
    #         0  Forward rotation
    #         1  Reverse rotation
    #     """
    #     self._msg_send(CmdList.DIRECTION, value)

    # def set_torque(self, value: float) -> None:
    #     """Send a torque command.

    #     Args:
    #         value: Value sent with the command N * M.
    #     """
    #     self._msg_send(CmdList.TORQUE, value)

    # def set_position(self, value: float) -> None:
    #     """Send a position command.

    #     Args:
    #         value: Value sent with the command.
    #     """
    #     self._msg_send(CmdList.POSITION, value)

    # def open_to_angle(self, value: float) -> None:
    #     """Send an open-to-angle command.

    #     Args:
    #         value: Value sent with the command deg.
    #     """
    #     self._msg_send(CmdList.OPENTOANGLE, value)
    
    # def ask_status(self) -> tuple[int, StatusReport]:
    #     """Request and return the motor status.

    #     Returns:
    #         A tuple containing the response frame ID and status report.

    #     Raises:
    #         TimeoutError: No response is received before the timeout.
    #         IDError: The received frame ID does not match the expected ID.
    #     """
    #     self._msg_send(CmdList.ASKSTATUS)
    #     return self._msg_receive()

    # def ask_open_to_angle(self) -> tuple[int, OpenToAngle]:
    #     """Request and return the open-to-angle response.

    #     Returns:
    #         A tuple containing the response frame ID and response data.

    #     Raises:
    #         TimeoutError: No response is received before the timeout.
    #         IDError: The received frame ID does not match the expected ID.
    #     """
    #     self._msg_send(CmdList.ASKOPENTOANGLE)
    #     return self._msg_opentoangle_receive()

    ######################################################

    def speed_build(self, value: float) -> None:
        """Build a speed command.

        Args:
            value: Value sent with the command rad/s.
        """
        self._msg_build(CmdList.SPEED, value)
    
    def voltage_build(self, value: float) -> None:
        """Build a voltage command.

        Args:
            value: Value sent with the command V.
        """
        self._msg_build(CmdList.VOLTAGE, value)

    def mode_build(self, value: float) -> can.Message:
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
    
    def direction_build(self, value: float) -> can.Message:
        """Build a direction command.

        Args:
            0  Forward rotation
            1  Reverse rotation
        """
        return self._msg_build(CmdList.DIRECTION, value)

    def torque_build(self, value: float) -> can.Message:
        """Build a torque command.

        Args:
            value: Value sent with the command N * M.
        """
        return self._msg_build(CmdList.TORQUE, value)

    def position_build(self, value: float) -> can.Message:
        """Build a position command.

        Args:
            value: Value sent with the command.
        """
        return self._msg_build(CmdList.POSITION, value)

    def open_to_angle_build(self, value: float) -> can.Message:
        """Build an open-to-angle command.

        Args:
            value: Value sent with the command deg.
        """
        return self._msg_build(CmdList.OPENTOANGLE, value)

    def ask_status_build(self) -> can.Message:

        return self._msg_build(CmdList.ASKSTATUS)

    def ask_open_to_angle_build(self) -> can.Message:

        return self._msg_build(CmdList.ASKOPENTOANGLE)
