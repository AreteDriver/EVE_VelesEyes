"""
Main Tab - Window Preview Management System
Implements 30 FPS capture loop with window previews, alerts, and interactions
"""
import logging
import subprocess
from typing import Dict, Optional
from PIL import Image

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QCheckBox, QScrollArea, QDialog, QListWidget,
    QListWidgetItem, QDialogButtonBox, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QAction

from eve_overview_pro.core.alert_detector import AlertLevel


def pil_to_qimage(pil_image: Image.Image) -> QImage:
    """
    Convert PIL Image to QImage

    Args:
        pil_image: PIL Image object

    Returns:
        QImage: Converted image
    """
    if pil_image.mode == "RGB":
        bytes_per_line = 3 * pil_image.width
        return QImage(
            pil_image.tobytes(),
            pil_image.width,
            pil_image.height,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )
    elif pil_image.mode == "RGBA":
        bytes_per_line = 4 * pil_image.width
        return QImage(
            pil_image.tobytes(),
            pil_image.width,
            pil_image.height,
            bytes_per_line,
            QImage.Format.Format_RGBA8888
        )
    elif pil_image.mode == "L":
        bytes_per_line = pil_image.width
        return QImage(
            pil_image.tobytes(),
            pil_image.width,
            pil_image.height,
            bytes_per_line,
            QImage.Format.Format_Grayscale8
        )
    else:
        # Convert to RGB if unknown mode
        rgb_image = pil_image.convert("RGB")
        bytes_per_line = 3 * rgb_image.width
        return QImage(
            rgb_image.tobytes(),
            rgb_image.width,
            rgb_image.height,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )


class WindowPreviewWidget(QWidget):
    """
    Individual window preview with alerts and interactions
    """
    window_activated = Signal(str)  # window_id
    window_removed = Signal(str)  # window_id

    def __init__(self, window_id: str, character_name: str, capture_system, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.window_id = window_id
        self.character_name = character_name
        self.capture_system = capture_system

        # State
        self.current_pixmap = None
        self.alert_level = None
        self.alert_flash_counter = 0
        self.zoom_factor = 0.3  # 30% scale

        # Setup UI
        self.setMinimumSize(200, 150)
        self.setMaximumSize(600, 450)
        self.setToolTip(f"{character_name}\nWindow ID: {window_id}\nClick to activate\nRight-click for menu")

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
        self.image_label.setText("Loading...")
        layout.addWidget(self.image_label)

        # Info label
        self.info_label = QLabel(f"{character_name}")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-weight: bold; padding: 2px;")
        layout.addWidget(self.info_label)

        # Alert flash timer
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self._flash_tick)

    def update_frame(self, image: Image.Image):
        """
        Update preview with new captured frame

        Args:
            image: PIL Image
        """
        try:
            # Convert PIL to QImage
            qimage = pil_to_qimage(image)

            # Convert to pixmap
            self.current_pixmap = QPixmap.fromImage(qimage)

            # Scale to fit widget while maintaining aspect ratio
            scaled_pixmap = self.current_pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation
            )

            self.image_label.setPixmap(scaled_pixmap)

        except Exception as e:
            self.logger.error(f"Failed to update frame for {self.window_id}: {e}")

    def set_alert(self, level: AlertLevel):
        """
        Set alert and start border flash

        Args:
            level: AlertLevel enum
        """
        self.alert_level = level
        self.alert_flash_counter = 30  # 3 seconds at 10 Hz
        if not self.flash_timer.isActive():
            self.flash_timer.start(100)  # 100ms = 10 Hz flash

        self.logger.debug(f"Alert set for {self.window_id}: {level}")

    def _flash_tick(self):
        """Flash timer tick"""
        self.alert_flash_counter -= 1
        if self.alert_flash_counter <= 0:
            self.flash_timer.stop()
            self.alert_level = None

        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Custom paint for alert border"""
        super().paintEvent(event)

        if self.alert_level and self.alert_flash_counter > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Choose color based on alert level
            if self.alert_level == AlertLevel.HIGH:
                color = QColor(255, 0, 0, 200)  # Red
            elif self.alert_level == AlertLevel.MEDIUM:
                color = QColor(255, 255, 0, 200)  # Yellow
            else:
                color = QColor(0, 255, 0, 200)  # Green

            # Draw thick border
            pen = QPen(color)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawRect(2, 2, self.width() - 4, self.height() - 4)

    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Activate window
            self.window_activated.emit(self.window_id)
            self.logger.info(f"Activating window: {self.window_id}")

    def contextMenuEvent(self, event):
        """Handle right-click context menu"""
        menu = QMenu(self)

        activate_action = QAction("Activate Window", self)
        activate_action.triggered.connect(lambda: self.window_activated.emit(self.window_id))
        menu.addAction(activate_action)

        minimize_action = QAction("Minimize Window", self)
        minimize_action.triggered.connect(self._minimize_window)
        menu.addAction(minimize_action)

        menu.addSeparator()

        remove_action = QAction("Remove from Preview", self)
        remove_action.triggered.connect(lambda: self.window_removed.emit(self.window_id))
        menu.addAction(remove_action)

        menu.addSeparator()

        # Zoom submenu
        zoom_menu = menu.addMenu("Zoom Level")
        for zoom in [0.2, 0.3, 0.4, 0.5]:
            zoom_action = QAction(f"{int(zoom*100)}%", self)
            zoom_action.triggered.connect(lambda checked, z=zoom: self._set_zoom(z))
            if zoom == self.zoom_factor:
                zoom_action.setCheckable(True)
                zoom_action.setChecked(True)
            zoom_menu.addAction(zoom_action)

        menu.exec(event.globalPos())

    def _minimize_window(self):
        """Minimize the window"""
        try:
            result = self.capture_system.minimize_window(self.window_id)
            if result:
                self.logger.info(f"Minimized window: {self.window_id}")
            else:
                self.logger.warning(f"Failed to minimize window: {self.window_id}")
        except Exception as e:
            self.logger.error(f"Error minimizing window: {e}")

    def _set_zoom(self, zoom: float):
        """Set zoom factor"""
        self.zoom_factor = zoom
        self.logger.debug(f"Zoom set to {int(zoom*100)}% for {self.window_id}")


class WindowManager:
    """
    Orchestrates 30 FPS capture loop for all preview widgets
    """

    def __init__(self, character_manager, capture_system, alert_detector):
        self.logger = logging.getLogger(__name__)
        self.character_manager = character_manager
        self.capture_system = capture_system
        self.alert_detector = alert_detector

        # State
        self.preview_frames: Dict[str, WindowPreviewWidget] = {}
        self.pending_requests: Dict[str, str] = {}  # request_id -> window_id
        self.refresh_rate = 30  # FPS

        # Timer for capture loop
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self._capture_cycle)

        self.logger.info("WindowManager initialized")

    def start_capture_loop(self):
        """Start the 30 FPS capture loop"""
        interval = 1000 // self.refresh_rate  # ms
        self.capture_timer.start(interval)
        self.logger.info(f"Capture loop started at {self.refresh_rate} FPS ({interval}ms interval)")

    def stop_capture_loop(self):
        """Stop the capture loop"""
        self.capture_timer.stop()
        self.logger.info("Capture loop stopped")

    def set_refresh_rate(self, fps: int):
        """
        Set refresh rate

        Args:
            fps: Frames per second (1-60)
        """
        self.refresh_rate = max(1, min(60, fps))
        if self.capture_timer.isActive():
            self.stop_capture_loop()
            self.start_capture_loop()

    def add_window(self, window_id: str, character_name: str) -> Optional[WindowPreviewWidget]:
        """
        Add window to preview

        Args:
            window_id: X11 window ID
            character_name: Character name

        Returns:
            WindowPreviewWidget or None
        """
        if window_id in self.preview_frames:
            self.logger.warning(f"Window {window_id} already in preview")
            return None

        # Create preview widget
        frame = WindowPreviewWidget(window_id, character_name, self.capture_system)
        self.preview_frames[window_id] = frame

        # Register alert callback
        def alert_callback(level: AlertLevel):
            if window_id in self.preview_frames:
                self.preview_frames[window_id].set_alert(level)

        self.alert_detector.register_callback(window_id, alert_callback)

        self.logger.info(f"Added window {window_id} ({character_name}) to preview")
        return frame

    def remove_window(self, window_id: str):
        """
        Remove window from preview

        Args:
            window_id: X11 window ID
        """
        if window_id in self.preview_frames:
            # Unregister alert callback
            self.alert_detector.unregister_callback(window_id)

            # Remove from dict
            frame = self.preview_frames.pop(window_id)
            frame.deleteLater()

            self.logger.info(f"Removed window {window_id} from preview")

    def _capture_cycle(self):
        """
        Capture cycle - called by timer

        Requests captures for all visible frames, then polls for results
        """
        # Request captures for all visible preview frames
        for window_id, frame in self.preview_frames.items():
            if frame.isVisible():
                try:
                    request_id = self.capture_system.capture_window_async(
                        window_id,
                        scale=frame.zoom_factor
                    )
                    self.pending_requests[request_id] = window_id
                except Exception as e:
                    self.logger.error(f"Failed to request capture for {window_id}: {e}")

        # Poll for results (non-blocking)
        self._process_capture_results()

    def _process_capture_results(self):
        """Poll and process capture results from worker threads"""
        processed = 0

        while True:
            result = self.capture_system.get_result(timeout=0.001)
            if not result:
                break

            request_id, window_id, image = result
            processed += 1

            # Update preview
            if window_id in self.preview_frames:
                try:
                    self.preview_frames[window_id].update_frame(image)

                    # Analyze for alerts
                    if image:
                        alert_level = self.alert_detector.analyze_frame(window_id, image)
                        if alert_level:
                            self.preview_frames[window_id].set_alert(alert_level)

                except Exception as e:
                    self.logger.error(f"Failed to process frame for {window_id}: {e}")

            # Remove from pending
            self.pending_requests.pop(request_id, None)

        if processed > 0:
            self.logger.debug(f"Processed {processed} capture results")

    def get_active_window_count(self) -> int:
        """Get count of active preview windows"""
        return len(self.preview_frames)


class MainTab(QWidget):
    """
    Main Tab - Window Preview Management
    """
    character_detected = Signal(str, str)  # window_id, char_name

    def __init__(self, capture_system, character_manager, alert_detector, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.capture_system = capture_system
        self.character_manager = character_manager
        self.alert_detector = alert_detector

        # Create window manager
        self.window_manager = WindowManager(
            character_manager,
            capture_system,
            alert_detector
        )

        self._setup_ui()

        # Start capture loop
        self.window_manager.start_capture_loop()

        self.logger.info("Main tab initialized")

    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Scroll area for preview frames
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Container for preview frames
        self.preview_container = QWidget()
        self.preview_layout = QHBoxLayout()  # Simple horizontal layout
        self.preview_layout.setSpacing(10)
        self.preview_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.preview_container.setLayout(self.preview_layout)

        scroll.setWidget(self.preview_container)
        layout.addWidget(scroll)

        # Status bar
        status_bar = self._create_status_bar()
        layout.addWidget(status_bar)

    def _create_toolbar(self) -> QWidget:
        """Create toolbar"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 5)
        toolbar.setLayout(toolbar_layout)

        # Add Window button
        add_btn = QPushButton("Add Window")
        add_btn.setToolTip("Add EVE window to preview")
        add_btn.clicked.connect(self.show_add_window_dialog)
        toolbar_layout.addWidget(add_btn)

        # Remove Selected button
        remove_btn = QPushButton("Remove All")
        remove_btn.setToolTip("Remove all windows from preview")
        remove_btn.clicked.connect(self._remove_all_windows)
        toolbar_layout.addWidget(remove_btn)

        # Minimize Inactive button
        minimize_btn = QPushButton("Minimize Inactive")
        minimize_btn.setToolTip("Minimize all windows except the currently focused one (saves GPU)")
        minimize_btn.clicked.connect(self.minimize_inactive_windows)
        toolbar_layout.addWidget(minimize_btn)

        # Refresh All button
        refresh_btn = QPushButton("Refresh All")
        refresh_btn.setToolTip("Restart capture for all windows")
        refresh_btn.clicked.connect(self._refresh_all)
        toolbar_layout.addWidget(refresh_btn)

        toolbar_layout.addStretch()

        # Refresh Rate
        toolbar_layout.addWidget(QLabel("Refresh Rate:"))
        self.refresh_rate_spin = QSpinBox()
        self.refresh_rate_spin.setRange(1, 60)
        self.refresh_rate_spin.setValue(30)
        self.refresh_rate_spin.setSuffix(" FPS")
        self.refresh_rate_spin.setToolTip("Capture framerate (higher = smoother but more CPU)")
        self.refresh_rate_spin.valueChanged.connect(self._on_refresh_rate_changed)
        toolbar_layout.addWidget(self.refresh_rate_spin)

        return toolbar

    def _create_status_bar(self) -> QWidget:
        """Create status bar"""
        status_bar = QWidget()
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 5, 0, 0)
        status_bar.setLayout(status_layout)

        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.active_count_label = QLabel("Active: 0")
        status_layout.addWidget(self.active_count_label)

        # Update status every second
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(1000)

        return status_bar

    def show_add_window_dialog(self):
        """Show dialog to add windows"""
        # Get window list
        try:
            windows = self.capture_system.get_window_list()
        except Exception as e:
            self.logger.error(f"Failed to get window list: {e}")
            QMessageBox.critical(self, "Error", f"Failed to get window list:\n{e}")
            return

        if not windows:
            QMessageBox.information(self, "No Windows", "No windows found.\n\nMake sure EVE Online clients are running.")
            return

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Windows to Preview")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        layout.addWidget(QLabel("Select EVE Online windows to add to preview:"))

        # List widget
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        for window_id, window_title in windows:
            # Skip if already in preview
            if window_id in self.window_manager.preview_frames:
                continue

            # Add to list
            item = QListWidgetItem(f"{window_title} ({window_id})")
            item.setData(Qt.ItemDataRole.UserRole, (window_id, window_title))
            list_widget.addItem(item)

        layout.addWidget(list_widget)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get selected items
            selected_items = list_widget.selectedItems()

            if not selected_items:
                return

            # Add selected windows
            added_count = 0
            for item in selected_items:
                window_id, window_title = item.data(Qt.ItemDataRole.UserRole)

                # Extract character name from window title
                char_name = window_title.replace("EVE -", "").replace("EVE Online -", "").strip()

                # Try auto-assign to character
                assignments = self.character_manager.auto_assign_windows([(window_id, window_title)])

                if assignments:
                    # Use detected character name
                    for detected_name, wid in assignments.items():
                        if wid == window_id:
                            char_name = detected_name
                            self.character_detected.emit(window_id, char_name)
                            break

                # Add to window manager
                frame = self.window_manager.add_window(window_id, char_name)
                if frame:
                    # Connect signals
                    frame.window_activated.connect(self._on_window_activated)
                    frame.window_removed.connect(self._on_window_removed)

                    # Add to layout
                    self.preview_layout.addWidget(frame)
                    added_count += 1

            self.logger.info(f"Added {added_count} windows to preview")
            self._update_status()

    def _on_window_activated(self, window_id: str):
        """Handle window activation"""
        try:
            result = self.capture_system.activate_window(window_id)
            if result:
                self.logger.info(f"Activated window: {window_id}")
            else:
                self.logger.warning(f"Failed to activate window: {window_id}")
        except Exception as e:
            self.logger.error(f"Error activating window: {e}")

    def _on_window_removed(self, window_id: str):
        """Handle window removal"""
        self.window_manager.remove_window(window_id)
        self._update_status()

    def _remove_all_windows(self):
        """Remove all windows from preview"""
        if not self.window_manager.preview_frames:
            return

        reply = QMessageBox.question(
            self,
            "Remove All Windows",
            "Remove all windows from preview?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Copy list to avoid modification during iteration
            window_ids = list(self.window_manager.preview_frames.keys())
            for window_id in window_ids:
                self.window_manager.remove_window(window_id)

            self._update_status()

    def minimize_inactive_windows(self):
        """Minimize all windows except focused one"""
        try:
            # Get currently focused window
            result = subprocess.run(['xdotool', 'getwindowfocus'], capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                focused_id = result.stdout.strip()

                minimized_count = 0
                for window_id in self.window_manager.preview_frames.keys():
                    if window_id != focused_id:
                        if self.capture_system.minimize_window(window_id):
                            minimized_count += 1

                self.logger.info(f"Minimized {minimized_count} inactive windows")
                self.status_label.setText(f"Minimized {minimized_count} windows (GPU savings!)")
            else:
                self.logger.warning("Failed to get focused window")

        except Exception as e:
            self.logger.error(f"Error minimizing windows: {e}")

    def _refresh_all(self):
        """Refresh all captures"""
        self.logger.info("Refreshing all captures")
        self.status_label.setText("Refreshed all captures")

    def _on_refresh_rate_changed(self, value):
        """Handle refresh rate change"""
        self.window_manager.set_refresh_rate(value)
        self.logger.info(f"Refresh rate changed to {value} FPS")

    def _update_status(self):
        """Update status bar"""
        count = self.window_manager.get_active_window_count()
        self.active_count_label.setText(f"Active: {count}")

        if count == 0:
            self.status_label.setText("No windows in preview - Click 'Add Window' to start")
        else:
            self.status_label.setText(f"Capturing {count} window(s) at {self.window_manager.refresh_rate} FPS")
