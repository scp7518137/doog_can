from .constants import (
    COMM_TIMEOUT_MS,
    NODE_ID_MIN,
    NODE_ID_MAX,
)
import threading
import time
import logging
import can
"""Periodically send keep-alive frames to a range of motor nodes."""
from .protocol import (
    build_frame,
    CmdList,
)

from .sendrecv import Transmit_Threading

_logger = logging.getLogger(__name__)

class KeepAlive():
    """Send keep-alive heartbeats to a contiguous range of motor nodes.

    A background thread sends a KEEPALIVE command to each node in turn so the
    motors stay powered within the communication timeout window.

    Args:
        start_number: First node ID included in the keep-alive range.
        stop_number: Last node ID included in the keep-alive range.
        bus: CAN bus used to transmit the keep-alive frames.
        all_period: Total time budget (seconds) for one full sweep over all
            nodes; the per-node interval is derived from it. Defaults to half
            of COMM_TIMEOUT_MS.
    """
    def __init__(self, start_number: int, stop_number: int, send_threading: Transmit_Threading, all_period:float = COMM_TIMEOUT_MS/ 2 / 1000) -> None:
        if stop_number - start_number < 0:
            raise ValueError("number not alive")
        if not (NODE_ID_MIN <= start_number <= stop_number <= NODE_ID_MAX):
            raise ValueError("number not alive")
        self._start_number: int = start_number
        self._stop_number: int = stop_number
        self._period: float = all_period / (stop_number  - start_number + 1)
        self._thread: threading.Thread | None = None
        self._running: bool = False
        self._error: Exception | None = None
        self.send_threading = send_threading

    def _send_msg(self) -> None:
        """Continuously send keep-alive frames until stopped.

        Runs in the background thread. Any unexpected exception is captured and
        stored in the ``error`` property while stopping the loop.
        """
        try:
            next_time = time.perf_counter()
            while self._running:
                for i in range(self._start_number, self._stop_number + 1):
                    if not self._running:
                        break
                    frame_id, data = build_frame(i, CmdList.KEEPALIVE, 0)
                    msg = can.Message(arbitration_id=frame_id, is_extended_id=False, data=data)
                    try:
                        self.send_threading.transmit_slot(msg)
                    except can.CanError:
                        _logger.warning("keepalive send failed", exc_info=True)
                    next_time += self._period
                    delay = next_time - time.perf_counter()
                    if delay > 0:
                        time.sleep(delay)
                    else:
                        next_time = time.perf_counter()

        except Exception as exc:
            self._error = exc
            self._running = False
            _logger.exception("keepalive loop crashed, thread exiting")

    def _go(self) -> None:
        """Spawn and start the background keep-alive thread."""
        self._thread = threading.Thread(
            target=self._send_msg, daemon=True, name="doog_can-keepalive"
        )
        self._thread.start()

    def start(self) -> None:
        """Start the keep-alive loop if it is not already running."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._error = None
        self._running = True
        self._go()

    def stop(self) -> None:
        """Stop the keep-alive loop and join the background thread."""
        self._running = False
        if self._thread is not None:
            self._thread.join()
            self._thread = None

    def is_running(self) -> bool:
        """Return whether the keep-alive loop is currently active.

        Returns:
            True if the background thread is alive and running.
        """
        return self._thread is not None and self._thread.is_alive() and self._running

    @property
    def error(self) -> Exception | None:
        """Exception captured from the last keep-alive run, if any."""
        return self._error

