import can
import queue
import time
import threading

from .constants import (
    FEEDBACK_FRAME_ID_BASE,
    FEEDBACK_OPENTOANGLE_ID_BASE,
    FEEDBACK_FAULT_ID_BASE,
)

from .protocol import(
    IDError,
)

NODE_ID_200_MIN = FEEDBACK_FRAME_ID_BASE + 1
NODE_ID_200_MAX = FEEDBACK_FRAME_ID_BASE + 12

NODE_ID_300_MIN = FEEDBACK_OPENTOANGLE_ID_BASE + 1
NODE_ID_300_MAX = FEEDBACK_OPENTOANGLE_ID_BASE + 12

NODE_ID_400_MIN = FEEDBACK_FAULT_ID_BASE + 1
NODE_ID_400_MAX = FEEDBACK_FAULT_ID_BASE + 12

MAXSIZE = 100




class Transmit_Threading(threading.Thread):
    """Transmit messages over a CAN bus from a background queue.

    Messages are pushed into ``messages`` and sent by the ``run`` loop, keeping
    all bus writes on a single thread.
    """
    def __init__(self, bus:can.BusABC) -> None:
        """Initialize the transmit thread and its message queue."""
        super().__init__(name = "Transmit_Threading", daemon=True)
        self._bus: can.BusABC = bus
        self.messages: queue.Queue[can.Message | None] = queue.Queue(maxsize=MAXSIZE)


    def transmit_slot(self, msg:can.Message) -> None:
        """Queue a message for transmission."""
        self.messages.put(msg)
        
    def run(self) -> None:
        """Send queued messages until a stop sentinel is received."""
        while True:
            msg: can.Message | None = self.messages.get()
            if msg is None:
                break
            self._bus.send(msg)

    def my_start(self) -> None:
        """Start the transmit thread."""
        self.start()

    def my_stop(self) -> None:
        """Stop the transmit thread and wait for it to finish."""
        self.messages.put(None)
        self.join()


class Receive_Threading(threading.Thread):
    """Receive frames from a CAN bus and distribute them to per-node queues.

    Incoming frames are classified by their ID prefix and pushed into either
    the normal ``msg_dict`` or the ``fault_msg_dict`` queue for that node.
    """
    def __init__(self, bus:can.BusABC):
        """Initialize the receive thread and per-node message queues."""
        super().__init__(name = "Receive_Threading", daemon=True)
        self._bus = bus
        self.running_event = threading.Event()
        self.msg_dict: dict[int, queue.Queue[can.Message]] = {
            node_id: queue.Queue(maxsize=MAXSIZE)
            for node_id in range(1,13)
        }
        self.fault_msg_dict: dict[int, queue.Queue[can.Message]] = {
            node_id: queue.Queue(maxsize=MAXSIZE)
            for node_id in range(1,13)
        }


    def _filter(self, msg: can.Message) -> None:
        """Classify a frame by its ID prefix and route it to the matching queue."""
        frame_id = msg.arbitration_id
        if NODE_ID_200_MIN <= frame_id <= NODE_ID_200_MAX:
            node_id = frame_id - FEEDBACK_FRAME_ID_BASE
        elif NODE_ID_300_MIN <= frame_id <= NODE_ID_300_MAX:
            node_id = frame_id - FEEDBACK_OPENTOANGLE_ID_BASE
        elif NODE_ID_400_MIN <= frame_id <= NODE_ID_400_MAX:
            node_id = frame_id - FEEDBACK_FAULT_ID_BASE
            if node_id in self.fault_msg_dict:
                self.fault_msg_dict[node_id].put(msg)
            return
        else:
            return
        if node_id in self.msg_dict:
            self.msg_dict[node_id].put(msg)

    # def receive_nomal_slot(self, node_id) -> can.Message | None:
    #     """Pop the message for a specific node ID."""
    #     if node_id in self.msg_dict:
    #         recv_msg = self.msg_dict[node_id].get()
    #     else:
    #         raise IDError(f"unknow motor node_id")
    #     return recv_msg

    # def reveive_fault_slot(self) -> can.Message | None:
    #     """Pop a message from the fault queues."""
    #     while not all(q.empty() for q in self.fault_msg_dict.values()):
    #         for _, q in self.fault_msg_dict.items():
    #             try:
    #                 return q.get_nowait()
    #             except queue.Empty:
    #                 continue

    #     return None
        
    def run(self) -> None:
        """Receive loop: read frames and route them into the queues."""
        while self.running_event.is_set():
            msg: can.Message | None = self._bus.recv(timeout=0.05)
            if msg is not None:
                try:
                    self._filter(msg)
                except queue.Full:
                    continue

    def my_start(self) -> None:
        """Start the receive loop and the background thread."""
        self.running_event.set()
        self.start()

    def my_stop(self) -> None:
        """Stop the receive loop and wait for the thread to finish."""
        self.running_event.clear()
        self.join()
        