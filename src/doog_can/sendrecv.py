import can
import queue
import time
import threading

from .constants import (
    FEEDBACK_FRAME_ID_BASE,
    FEEDBACK_OPENTOANGLE_ID_BASE,
    FEEDBACK_FAULT_ID_BASE,
)

NODE_ID_200_MIN = FEEDBACK_FRAME_ID_BASE + 1
NODE_ID_200_MAX = FEEDBACK_FRAME_ID_BASE + 12

NODE_ID_300_MIN = FEEDBACK_OPENTOANGLE_ID_BASE + 1
NODE_ID_300_MAX = FEEDBACK_OPENTOANGLE_ID_BASE + 12

NODE_ID_400_MIN = FEEDBACK_FAULT_ID_BASE + 1
NODE_ID_400_MAX = FEEDBACK_FAULT_ID_BASE + 12

MAXSIZE = 100

class IDError(Exception):
    """Raised when a received CAN frame has an unepxected ID"""
    pass


class Transmit_Threading(threading.Thread):
    def __init__(self, bus:can.BusABC) -> None:
        super().__init__(name = "Transmit_Threading", daemon=True)
        self._bus: can.BusABC = bus
        self._messages: queue.Queue[can.Message | None] = queue.Queue(maxsize=MAXSIZE)


    def transmit_slot(self, msg:can.Message) -> None:
        self._messages.put(msg)
        
    def run(self) -> None:
        while True:
            msg: can.Message | None = self._messages.get()
            if msg is None:
                break
            self._bus.send(msg)

    def my_start(self) -> None:
        self.start()


    def my_stop(self) -> None:
        self._messages.put(None)
        self.join()


class Receive_Threading(threading.Thread):
    def __init__(self, bus:can.BusABC):
        """初始化"""
        super().__init__(name = "Receive_Threading", daemon=True)
        self._bus = bus
        self.running_event = threading.Event()
        self._msg_dict: dict[int, queue.Queue[can.Message]] = {
            node_id: queue.Queue(maxsize=MAXSIZE)
            for node_id in range(1,13)
        }
        self.fault_tag: dict[int, bool] = {
            node_id: False
            for node_id in range(1,13)
        }


    def _filter(self, msg: can.Message) -> None:
        """判断前缀 对id分类"""
        frame_id = msg.arbitration_id
        if NODE_ID_200_MIN <= frame_id <= NODE_ID_200_MAX:
            node_id = frame_id - FEEDBACK_FRAME_ID_BASE
        elif NODE_ID_300_MIN <= frame_id <= NODE_ID_300_MAX:
            node_id = frame_id - FEEDBACK_OPENTOANGLE_ID_BASE
        elif NODE_ID_400_MIN <= frame_id <= NODE_ID_400_MAX:
            node_id = frame_id - FEEDBACK_FAULT_ID_BASE
            if node_id in self.fault_tag:
                self.fault_tag[node_id] = True
        else:
            return
        if node_id in self._msg_dict:
            self._msg_dict[node_id].put(msg)

    def receive_slot(self, node_id) -> can.Message | None:
        """从特定id导出对应的msg"""
        if node_id in self._msg_dict:
            recv_msg = self._msg_dict[node_id].get()
        else:
            raise IDError(f"unknow motor node_id")
        return recv_msg
        
    def run(self) -> None:
        """运行"""
        while self.running_event.is_set():
            msg: can.Message | None = self._bus.recv(timeout=0.05)
            if msg is not None:
                try:
                    self._filter(msg)
                except queue.Full:
                    continue

    def my_start(self) -> None:
        self.running_event.set()
        self.start()

    def my_stop(self) -> None:
        self.running_event.clear()
        self.join()
        