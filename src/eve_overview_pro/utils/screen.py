"""Screen geometry utilities - shared across UI components"""

import logging
import re
import subprocess
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class ScreenGeometry:
    """Screen/monitor geometry"""

    x: int
    y: int
    width: int
    height: int
    is_primary: bool = False


def get_screen_geometry(monitor: int = 0) -> ScreenGeometry:
    """Get screen geometry using xrandr.

    Args:
        monitor: Monitor index (0-based)

    Returns:
        ScreenGeometry for requested monitor, or default 1920x1080 on failure
    """
    try:
        result = subprocess.run(["xrandr", "--query"], capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            logger.error("xrandr failed")
            return ScreenGeometry(0, 0, 1920, 1080, True)

        monitors: List[ScreenGeometry] = []
        for line in result.stdout.split("\n"):
            if " connected" in line:
                match = re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
                if match:
                    w, h, x, y = map(int, match.groups())
                    is_primary = "primary" in line
                    monitors.append(ScreenGeometry(x, y, w, h, is_primary))

        if monitor < len(monitors):
            return monitors[monitor]
        elif monitors:
            return monitors[0]

        logger.warning("Could not parse xrandr output, using default geometry")
        return ScreenGeometry(0, 0, 1920, 1080, True)

    except Exception as e:
        logger.error(f"Failed to get screen geometry: {e}")
        return ScreenGeometry(0, 0, 1920, 1080, True)


def get_all_monitors() -> List[ScreenGeometry]:
    """Get geometry for all connected monitors.

    Returns:
        List of ScreenGeometry for all monitors, or single default on failure
    """
    try:
        result = subprocess.run(["xrandr", "--query"], capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            return [ScreenGeometry(0, 0, 1920, 1080, True)]

        monitors: List[ScreenGeometry] = []
        for line in result.stdout.split("\n"):
            if " connected" in line:
                match = re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
                if match:
                    w, h, x, y = map(int, match.groups())
                    is_primary = "primary" in line
                    monitors.append(ScreenGeometry(x, y, w, h, is_primary))

        return monitors if monitors else [ScreenGeometry(0, 0, 1920, 1080, True)]

    except Exception as e:
        logger.error(f"Failed to get monitors: {e}")
        return [ScreenGeometry(0, 0, 1920, 1080, True)]
