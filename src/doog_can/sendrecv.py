import can
import queue
import time
import threading

MAXSIZE = 100


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
        super().__init__(name = "Receive_Threading", daemon=True)
        self._bus = bus
        self._messages: queue.Queue[can.Message | None] = queue.Queue(maxsize=MAXSIZE)
        self.running_event = threading.Event()

    def receive_slot(self) -> can.Message | None:
        recv_msg = self._messages.get()
        return recv_msg
        
    def run(self) -> None:
        while self.running_event.is_set():
            msg: can.Message | None = self._bus.recv(timeout=0.05)
            if self._messages is not None:
                self._messages.put(msg)

    def my_start(self) -> None:
        self.running_event.set()
        self.start()

    def my_stop(self) -> None:
        self.running_event.clear()
        self.join()