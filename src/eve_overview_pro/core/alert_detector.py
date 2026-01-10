"""
Visual Activity Alert Detector
Monitors windows for visual changes and triggers alerts
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

import numpy as np
from PIL import Image


class AlertLevel(Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class AlertConfig:
    """Configuration for alert detection"""

    enabled: bool = True
    red_flash_threshold: float = 0.7  # Threshold for red flash detection
    change_threshold: float = 0.3  # Threshold for general screen change
    alert_cooldown: int = 5  # Seconds between same alerts
    sound_enabled: bool = False
    visual_border: bool = True
    border_color: str = "#ff0000"
    border_flash_duration: int = 3  # Seconds


class AlertDetector:
    """Detects visual activity in window captures"""

    # Size for storing comparison frames (small to save memory)
    COMPARISON_SIZE = (100, 100)

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = AlertConfig()
        self.previous_frames = {}  # window_id -> small grayscale image for comparison
        self.last_alert_times = {}  # window_id -> timestamp
        self.alert_callbacks = {}  # window_id -> callback function

    def set_config(self, config: AlertConfig):
        """Update alert configuration"""
        self.config = config

    def register_callback(self, window_id: str, callback: Callable):
        """Register callback for window alerts

        Args:
            window_id: Window to monitor
            callback: Function to call on alert (receives AlertLevel)
        """
        self.alert_callbacks[window_id] = callback

    def unregister_callback(self, window_id: str):
        """Unregister alert callback and clean up all window data"""
        self.alert_callbacks.pop(window_id, None)
        self.previous_frames.pop(window_id, None)
        self.last_alert_times.pop(window_id, None)

    def analyze_frame(self, window_id: str, image: Image.Image) -> Optional[AlertLevel]:
        """Analyze a frame for alert conditions

        Args:
            window_id: Window being analyzed
            image: Current frame

        Returns:
            AlertLevel if alert detected, None otherwise
        """
        if not self.config.enabled or image is None:
            return None

        alert_level = None

        # Check for red flash (damage indicator)
        if self._detect_red_flash(image):
            alert_level = AlertLevel.HIGH
            self.logger.info(f"RED FLASH detected in window {window_id}")

        # Check for significant screen change
        # Create small grayscale version for comparison (saves memory)
        small_frame = image.resize(self.COMPARISON_SIZE).convert("L")

        if window_id in self.previous_frames:
            if self._detect_screen_change_fast(small_frame, self.previous_frames[window_id]):
                alert_level = AlertLevel.MEDIUM
                self.logger.debug(f"Screen change detected in window {window_id}")

        # Store small frame for next comparison (~10KB vs ~6MB)
        self.previous_frames[window_id] = small_frame

        # Trigger callback if alert detected
        if alert_level and window_id in self.alert_callbacks:
            try:
                self.alert_callbacks[window_id](alert_level)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")

        return alert_level

    def _detect_red_flash(self, image: Image.Image) -> bool:
        """Detect red flash in image (damage indicator)

        Args:
            image: Image to analyze

        Returns:
            True if red flash detected
        """
        try:
            # Convert to RGB array
            img_array = np.array(image.convert("RGB"))

            # Extract color channels
            r = img_array[:, :, 0].astype(float)
            g = img_array[:, :, 1].astype(float)
            b = img_array[:, :, 2].astype(float)

            # Calculate red dominance
            # Red flash: R > G+B and R > threshold
            red_dominant = (r > (g + b)) & (r > 200)

            # Calculate percentage of red pixels
            total_pixels = r.size
            red_pixels = np.sum(red_dominant)
            red_percentage = red_pixels / total_pixels

            # Alert if significant portion is red
            return red_percentage > self.config.red_flash_threshold

        except Exception as e:
            self.logger.error(f"Red flash detection error: {e}")
            return False

    def _detect_screen_change_fast(
        self, current_small: Image.Image, previous_small: Image.Image
    ) -> bool:
        """Detect significant change between pre-resized frames

        Args:
            current_small: Current frame (already resized to COMPARISON_SIZE, grayscale)
            previous_small: Previous frame (already resized to COMPARISON_SIZE, grayscale)

        Returns:
            True if significant change detected
        """
        try:
            # Convert to arrays (already correct size and grayscale)
            current_array = np.array(current_small).astype(np.int16)
            previous_array = np.array(previous_small).astype(np.int16)

            # Calculate difference
            diff = np.abs(current_array - previous_array)

            # Calculate percentage of changed pixels
            total_pixels = diff.size
            changed_pixels = np.sum(diff > 30)  # Threshold for pixel change
            change_percentage = changed_pixels / total_pixels

            # Alert if significant change
            return change_percentage > self.config.change_threshold

        except Exception as e:
            self.logger.error(f"Screen change detection error: {e}")
            return False

    def _detect_screen_change(self, current: Image.Image, previous: Image.Image) -> bool:
        """Detect significant change between frames (legacy method)

        Args:
            current: Current frame
            previous: Previous frame

        Returns:
            True if significant change detected
        """
        try:
            # Resize and convert for comparison
            current_small = current.resize(self.COMPARISON_SIZE).convert("L")
            previous_small = previous.resize(self.COMPARISON_SIZE).convert("L")
            return self._detect_screen_change_fast(current_small, previous_small)
        except Exception as e:
            self.logger.error(f"Screen change detection error: {e}")
            return False

    def clear_history(self, window_id: Optional[str] = None):
        """Clear frame history and alert times

        Args:
            window_id: Specific window to clear, or None for all
        """
        if window_id:
            self.previous_frames.pop(window_id, None)
            self.last_alert_times.pop(window_id, None)
        else:
            self.previous_frames.clear()
            self.last_alert_times.clear()
