"""Provide an interface to control the motor over the CAN bus"""
from .protocol import (
    build_frame, 
    decode_frame,
    decode_opentoangle,
    decode_faultcode,
    feedback_frame_id,
    feedback_opentoangle_id,
    StatusReport,
    OpenToAngle,
    FaultrCode,
    IDError,
    )

from .constants import (
    CmdList,
)

from .sendrecv import (
    NODE_ID_200_MIN,
    NODE_ID_200_MAX,
    NODE_ID_300_MIN,
    NODE_ID_300_MAX,
)

import can
import queue


class Motor:
    """Control an motor over the CAN bus.

    Args:
        bus: CAN bus used to send and receive mseeages.
        node_id: ID of the motor node.
    """
    def __init__(
            self, send_message: queue.Queue[can.Message | None],
            recv_dir: dict[int, queue.Queue[can.Message]],
            fault_msg_dict: dict[int, queue.Queue[can.Message]],
            node_id: int) -> None:
        """Initialize the move controller."""
        self.node_id = node_id
        self._feedback_frame_id = feedback_frame_id(node_id)
        self._feedback_opentoangle_id = feedback_opentoangle_id(node_id)
        self.message = send_message
        self.recv_dir = recv_dir
        self.fault_msg_dict = fault_msg_dict


    def _msg_build(self, cmd: int, value:float = 0) -> can.Message:
        """Build a CAN message for the given command"""
        frame_id, data = build_frame(self.node_id, cmd, value)
        msg: can.Message = can.Message(arbitration_id=frame_id, is_extended_id=False, data=data)
        return msg

    def send_message(self, msg: can.Message) -> None:
        self.message.put(msg)

    def recv_message(self) -> can.Message | None:
        try:
            return(self.recv_dir[self.node_id].get())
        except queue.Empty:
            return None


    def build_speed_cmd(self, value: float) -> can.Message:
        """Build a speed command.

        Args:
            value: Value sent with the command rad/s.
        """
        return self._msg_build(CmdList.SPEED, value)

    def send_speed_cmd(self, value: float) -> None:
        self.send_message(self.build_speed_cmd(value))


    
    def build_voltage_cmd(self, value: float) -> can.Message:
        """Build a voltage command.

        Args:
            value: Value sent with the command V.
        """
        return self._msg_build(CmdList.VOLTAGE, value)

    def send_voltage_cmd(self, value: float) -> None:
        self.send_message(self.build_voltage_cmd(value))
   

    def build_mode_cmd(self, value: int) -> can.Message:
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

    def send_mode_cmd(self, value: int) -> None:
        self.send_message(self.build_mode_cmd(value))
    
    def build_direction_cmd(self, value: int) -> can.Message:
        """Build a direction command.

        Args:
            0  Forward rotation
            1  Reverse rotation
        """
        return self._msg_build(CmdList.DIRECTION, value)

    def send_direction_cmd(self, value: int) -> None:
        self.send_message(self.build_direction_cmd(value))


    def build_torque_cmd(self, value: float) -> can.Message:
        """Build a torque command.

        Args:
            value: Value sent with the command N * M.
        """
        return self._msg_build(CmdList.TORQUE, value)

    def send_torque_cmd(self, value: float) -> None:
        self.send_message(self.build_torque_cmd(value))

    def build_position_cmd(self, value: float) -> can.Message:
        """Build a position command.

        Args:
            value: Value sent with the command.
        """
        return self._msg_build(CmdList.POSITION, value)

    def send_position_cmd(self, value: float) -> None:
        self.send_message(self.build_position_cmd(value))

    def build_open_to_angle_cmd(self, value: float) -> can.Message:
        """Build an open-to-angle command.

        Args:
            value: Value sent with the command deg.
        """
        return self._msg_build(CmdList.OPENTOANGLE, value)

    def send_open_to_angle_cmd(self, value: float) -> None:
        self.send_message(self.build_open_to_angle_cmd(value))


    def build_ask_status_cmd(self) -> can.Message:
        """Build an ask status command."""

        return self._msg_build(CmdList.ASKSTATUS)

    def send_ask_status_cmd(self) -> None:
        self.send_message(self.build_ask_status_cmd())

    def build_ask_open_to_angle_cmd(self) -> can.Message:
        """Build an ask open_to_angle command."""
        return self._msg_build(CmdList.ASKOPENTOANGLE)

    def send_ask_open_to_angle_cmd(self) -> None:
        self.send_message(self.build_ask_open_to_angle_cmd())


    def decode_ask_status(self, msgdata: bytearray) -> StatusReport:
        """Decode a status frame."""
        return decode_frame(bytes(msgdata))

    def decode_ask_open_to_angle(self, msgdata: bytearray) -> OpenToAngle:
        """Decode an open_to_angle frame."""
        return decode_opentoangle(bytes(msgdata))

    def decode_fault_code(self, msgdata: bytearray) -> FaultrCode:
        """Decode a fault frame"""
        return decode_faultcode(bytes(msgdata))

    def decode_normal_code(self) -> StatusReport | OpenToAngle | None:
        msg = self.recv_message()

        if msg is None:
            return None
        frame_id = msg.arbitration_id
        if NODE_ID_200_MIN <= frame_id <= NODE_ID_200_MAX:
            return self.decode_ask_status(msg.data)
        elif NODE_ID_300_MIN <= frame_id <= NODE_ID_300_MAX:
            return self.decode_ask_open_to_angle(msg.data)

    def check_motors(self) -> FaultrCode | None:
        while not all(q.empty() for q in self.fault_msg_dict.values()):
            for _, q in self.fault_msg_dict.items():
                try:
                    return self.decode_fault_code(q.get_nowait().data)
                except queue.Empty:
                    continue
        return None
