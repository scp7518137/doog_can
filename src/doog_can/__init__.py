"""Public API for the doog_can motor control package.

This package provides a high-level interface to control motors over a CAN bus,
including frame encoding/decoding, a keep-alive service, and transport setup.
"""
from .constants import (
    CommandMode,
    Direction,
    FeedbackMode,
    OpenToAngleMode,
    SystemStatus,
)
from .driver import IDError, Motor
from .protocol import OpenToAngle, StatusReport, feedback_frame_id, cmd_frame_id
from .keep_alive import KeepAlive
from .transport import can_init, vbus_init, vbus_close

__all__ = [
    "Motor",
    "StatusReport",
    "OpenToAngle",
    "feedback_frame_id",
    "cmd_frame_id",
    "IDError",
    "CommandMode",
    "Direction",
    "FeedbackMode",
    "SystemStatus",
    "OpenToAngleMode",
    "KeepAlive",
    "can_init",
    "vbus_init",
    "vbus_close",
]