"""ResolutionSwitcher - Command line tool to change Windows display settings."""

from __future__ import annotations

__version__ = "3.0.3"
__all__ = [
    "DisplayAdapter",
    "DisplayAdapterException",
    "DisplayMode",
    "DisplayMonitor",
    "DisplayMonitorException",
    "HdrException",
    "PrimaryMonitorException",
    "get_all_display_monitors",
    "get_primary_monitor",
    "set_display_mode_for_device",
    "set_hdr_state_for_monitor",
]

from .custom_types import (
    DisplayAdapter,
    DisplayAdapterException,
    DisplayMode,
    DisplayMonitor,
    DisplayMonitorException,
    HdrException,
    PrimaryMonitorException,
)
from .display_adapters import set_display_mode_for_device
from .display_monitors import (
    get_all_display_monitors,
    get_primary_monitor,
    set_hdr_state_for_monitor,
)
