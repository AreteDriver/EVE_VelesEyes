"""
Layouts Tab - Layout preset management and grid patterns
Allows saving/loading window arrangements and applying grid patterns
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QGroupBox, QLabel, QComboBox, QSpinBox, QDialog,
    QLineEdit, QTextEdit, QMessageBox, QSplitter, QGraphicsView,
    QGraphicsScene, QGraphicsRectItem, QDialogButtonBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QColor, QPen, QBrush, QFont
import logging
import subprocess
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Import GridPattern from core module
from eve_overview_pro.core.layout_manager import GridPattern


@dataclass
class ScreenGeometry:
    """Screen/monitor geometry"""
    x: int
    y: int
    width: int
    height: int
    is_primary: bool = False


def get_all_patterns():
    """Get all available grid patterns as display strings"""
    return [
        "2x2 Grid",
        "3x1 Row",
        "1x3 Column",
        "4x1 Row",
        "Main + Sides",
        "Cascade",
        "Custom"
    ]


def pattern_display_to_enum(display_name: str) -> GridPattern:
    """Convert display name to GridPattern enum"""
    mapping = {
        "2x2 Grid": GridPattern.GRID_2X2,
        "3x1 Row": GridPattern.GRID_3X1,
        "1x3 Column": GridPattern.GRID_1X3,
        "4x1 Row": GridPattern.GRID_4X1,
        "Main + Sides": GridPattern.MAIN_PLUS_SIDES,
        "Cascade": GridPattern.CASCADE,
        "Custom": GridPattern.CUSTOM
    }
    return mapping.get(display_name, GridPattern.CUSTOM)


def pattern_enum_to_display(pattern: GridPattern) -> str:
    """Convert GridPattern enum to display name"""
    mapping = {
        GridPattern.GRID_2X2: "2x2 Grid",
        GridPattern.GRID_3X1: "3x1 Row",
        GridPattern.GRID_1X3: "1x3 Column",
        GridPattern.GRID_4X1: "4x1 Row",
        GridPattern.MAIN_PLUS_SIDES: "Main + Sides",
        GridPattern.CASCADE: "Cascade",
        GridPattern.CUSTOM: "Custom"
    }
    return mapping.get(pattern, "Custom")


class LayoutListItem(QWidget):
    """Custom widget for layout list item with rich display"""

    def __init__(self, preset, parent=None):
        super().__init__(parent)
        self.preset = preset
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Name (bold)
        name_label = QLabel(self.preset.name)
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        name_label.setFont(font)
        layout.addWidget(name_label)

        # Description (2 lines max)
        if self.preset.description:
            desc_label = QLabel(self.preset.description[:100] + "..." if len(self.preset.description) > 100 else self.preset.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #888;")
            layout.addWidget(desc_label)

        # Window count and pattern
        info_layout = QHBoxLayout()
        window_count = len(self.preset.windows)
        pattern_display = pattern_enum_to_display(self.preset.grid_pattern) if self.preset.grid_pattern else 'Custom'
        info_label = QLabel(f"{window_count} windows | Pattern: {pattern_display}")
        info_label.setStyleSheet("color: #666; font-size: 9pt;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        self.setLayout(layout)


class SaveLayoutDialog(QDialog):
    """Dialog for saving current window layout as preset"""

    def __init__(self, layout_manager, current_windows: Dict, parent=None):
        super().__init__(parent)
        self.layout_manager = layout_manager
        self.current_windows = current_windows
        self.logger = logging.getLogger(__name__)

        self.setWindowTitle("Save Layout Preset")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Form fields
        form_layout = QFormLayout()

        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Mining Fleet 2x2")
        form_layout.addRow("Name:", self.name_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Optional description of this layout...")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)

        # Refresh rate
        self.refresh_rate_spin = QSpinBox()
        self.refresh_rate_spin.setRange(1, 60)
        self.refresh_rate_spin.setValue(30)
        self.refresh_rate_spin.setSuffix(" FPS")
        form_layout.addRow("Refresh Rate:", self.refresh_rate_spin)

        # Grid pattern (auto-detected or custom)
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(get_all_patterns())
        detected_pattern = self._detect_pattern()
        if detected_pattern:
            index = self.pattern_combo.findText(detected_pattern)
            if index >= 0:
                self.pattern_combo.setCurrentIndex(index)
        form_layout.addRow("Grid Pattern:", self.pattern_combo)

        layout.addLayout(form_layout)

        # Window count info
        info_label = QLabel(f"Capturing positions for {len(self.current_windows)} windows")
        info_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(info_label)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_layout)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def _detect_pattern(self) -> Optional[str]:
        """Try to detect grid pattern from window positions"""
        if len(self.current_windows) == 0:
            return None

        # Simple heuristic: check window count and rough alignment
        count = len(self.current_windows)

        if count == 4:
            return "2x2 Grid"
        elif count == 3:
            return "3x1 Row"
        elif count == 2:
            return "Main + Sides"

        return "Custom"

    def _save_layout(self):
        """Validate and save layout"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Layout name is required.")
            return

        # Check uniqueness
        existing = self.layout_manager.get_all_presets()
        if any(p.name == name for p in existing):
            reply = QMessageBox.question(
                self,
                "Overwrite?",
                f"Layout '{name}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Create preset
        description = self.description_edit.toPlainText().strip()
        refresh_rate = self.refresh_rate_spin.value()
        pattern_display = self.pattern_combo.currentText()
        pattern_enum = pattern_display_to_enum(pattern_display)

        try:
            preset = self.layout_manager.create_preset_from_current(
                name=name,
                description=description,
                windows=self.current_windows,
                grid_pattern=pattern_enum,
                refresh_rate=refresh_rate
            )
            self.logger.info(f"Created layout preset: {name}")
            self.accept()

        except Exception as e:
            self.logger.error(f"Failed to save layout: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save layout: {e}")


class GridPatternVisualizer(QGraphicsView):
    """Visual preview of grid pattern layout"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.logger = logging.getLogger(__name__)

        # Visual settings
        from PySide6.QtGui import QPainter
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setMinimumHeight(300)

    def preview_layout(self, geometry_dict: Dict[str, Dict]):
        """
        Preview a layout from geometry dictionary

        Args:
            geometry_dict: {window_id: {"x": x, "y": y, "width": w, "height": h}}
        """
        self.scene.clear()

        if not geometry_dict:
            return

        # Find bounds
        min_x = min(g["x"] for g in geometry_dict.values())
        min_y = min(g["y"] for g in geometry_dict.values())
        max_x = max(g["x"] + g["width"] for g in geometry_dict.values())
        max_y = max(g["y"] + g["height"] for g in geometry_dict.values())

        # Scale to fit view
        view_width = self.viewport().width() - 20
        view_height = self.viewport().height() - 20

        layout_width = max_x - min_x
        layout_height = max_y - min_y

        scale_x = view_width / layout_width if layout_width > 0 else 1
        scale_y = view_height / layout_height if layout_height > 0 else 1
        scale = min(scale_x, scale_y) * 0.9  # 90% to add margins

        # Draw screen boundary
        screen_rect = QGraphicsRectItem(
            0, 0,
            layout_width * scale,
            layout_height * scale
        )
        screen_rect.setPen(QPen(QColor(100, 100, 100), 2))
        screen_rect.setBrush(QBrush(QColor(40, 40, 40)))
        self.scene.addItem(screen_rect)

        # Draw windows
        colors = [
            QColor(255, 100, 100, 150),
            QColor(100, 255, 100, 150),
            QColor(100, 100, 255, 150),
            QColor(255, 255, 100, 150),
            QColor(255, 100, 255, 150),
            QColor(100, 255, 255, 150),
        ]

        for idx, (window_id, geom) in enumerate(geometry_dict.items()):
            x = (geom["x"] - min_x) * scale
            y = (geom["y"] - min_y) * scale
            w = geom["width"] * scale
            h = geom["height"] * scale

            rect = QGraphicsRectItem(x, y, w, h)
            color = colors[idx % len(colors)]
            rect.setPen(QPen(color.darker(150), 2))
            rect.setBrush(QBrush(color))
            self.scene.addItem(rect)

            # Add window number label
            from PySide6.QtWidgets import QGraphicsTextItem
            label = QGraphicsTextItem(f"Window {idx + 1}")
            label.setDefaultTextColor(QColor(255, 255, 255))
            label.setPos(x + 5, y + 5)
            self.scene.addItem(label)

        # Fit in view
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def set_pattern_preview(self, pattern: str, window_count: int,
                           screen_geometry: ScreenGeometry, spacing: int = 10):
        """
        Preview a grid pattern before applying

        Args:
            pattern: Grid pattern name
            window_count: Number of windows
            screen_geometry: Screen dimensions
            spacing: Spacing between windows in pixels
        """
        self.scene.clear()

        # Calculate positions based on pattern
        positions = self._calculate_pattern_positions(
            pattern, window_count, screen_geometry, spacing
        )

        if not positions:
            return

        # Create geometry dict
        geometry_dict = {}
        for idx, (x, y, w, h) in enumerate(positions):
            geometry_dict[f"window_{idx}"] = {
                "x": x, "y": y, "width": w, "height": h
            }

        self.preview_layout(geometry_dict)

    def _calculate_pattern_positions(self, pattern: str, window_count: int,
                                    screen: ScreenGeometry, spacing: int) -> List[Tuple[int, int, int, int]]:
        """Calculate window positions for a pattern"""
        positions = []

        if pattern == "2x2 Grid":
            # 2x2 grid
            cols, rows = 2, 2
            w = (screen.width - spacing * 3) // cols
            h = (screen.height - spacing * 3) // rows

            for i in range(min(window_count, 4)):
                row = i // cols
                col = i % cols
                x = screen.x + spacing + col * (w + spacing)
                y = screen.y + spacing + row * (h + spacing)
                positions.append((x, y, w, h))

        elif pattern == "3x1 Row":
            # 3 windows in a row
            cols = 3
            w = (screen.width - spacing * 4) // cols
            h = screen.height - spacing * 2

            for i in range(min(window_count, 3)):
                x = screen.x + spacing + i * (w + spacing)
                y = screen.y + spacing
                positions.append((x, y, w, h))

        elif pattern == "1x3 Column":
            # 3 windows in a column
            rows = 3
            w = screen.width - spacing * 2
            h = (screen.height - spacing * 4) // rows

            for i in range(min(window_count, 3)):
                x = screen.x + spacing
                y = screen.y + spacing + i * (h + spacing)
                positions.append((x, y, w, h))

        elif pattern == "4x1 Row":
            # 4 windows in a row
            cols = 4
            w = (screen.width - spacing * 5) // cols
            h = screen.height - spacing * 2

            for i in range(min(window_count, 4)):
                x = screen.x + spacing + i * (w + spacing)
                y = screen.y + spacing
                positions.append((x, y, w, h))

        elif pattern == "Main + Sides":
            # Large main window + smaller side windows
            if window_count >= 1:
                # Main window (70% width)
                main_w = int((screen.width - spacing * 3) * 0.7)
                main_h = screen.height - spacing * 2
                positions.append((screen.x + spacing, screen.y + spacing, main_w, main_h))

            if window_count >= 2:
                # Side windows (30% width, split vertically)
                side_w = screen.width - main_w - spacing * 3
                side_h = (screen.height - spacing * 3) // (window_count - 1)

                for i in range(1, window_count):
                    x = screen.x + main_w + spacing * 2
                    y = screen.y + spacing + (i - 1) * (side_h + spacing)
                    positions.append((x, y, side_w, side_h))

        elif pattern == "Cascade":
            # Cascading windows with offset
            offset = 40
            w = screen.width - spacing * 2 - offset * (window_count - 1)
            h = screen.height - spacing * 2 - offset * (window_count - 1)

            for i in range(window_count):
                x = screen.x + spacing + i * offset
                y = screen.y + spacing + i * offset
                positions.append((x, y, w, h))

        return positions


class GridApplier:
    """Applies grid patterns to actual windows using xdotool"""

    def __init__(self, layout_manager):
        self.layout_manager = layout_manager
        self.logger = logging.getLogger(__name__)

    def get_screen_geometry(self, monitor: int = 0) -> Optional[ScreenGeometry]:
        """Get screen geometry using xrandr"""
        try:
            result = subprocess.run(
                ['xrandr', '--query'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                self.logger.error("xrandr failed")
                return None

            # Parse xrandr output
            # Looking for lines like: "HDMI-1 connected primary 1920x1080+0+0"
            monitors = []
            for line in result.stdout.split('\n'):
                if ' connected' in line:
                    match = re.search(r'(\d+)x(\d+)\+(\d+)\+(\d+)', line)
                    if match:
                        w, h, x, y = map(int, match.groups())
                        is_primary = 'primary' in line
                        monitors.append(ScreenGeometry(x, y, w, h, is_primary))

            if monitor < len(monitors):
                return monitors[monitor]
            elif monitors:
                return monitors[0]  # Default to first monitor

            # Fallback: assume 1920x1080 at 0,0
            self.logger.warning("Could not parse xrandr output, using default geometry")
            return ScreenGeometry(0, 0, 1920, 1080, True)

        except Exception as e:
            self.logger.error(f"Failed to get screen geometry: {e}")
            return ScreenGeometry(0, 0, 1920, 1080, True)

    def apply_grid(self, pattern: str, window_ids: List[str],
                   monitor: int = 0, spacing: int = 10) -> bool:
        """
        Apply grid pattern to windows

        Args:
            pattern: Grid pattern display name
            window_ids: List of X11 window IDs
            monitor: Monitor index
            spacing: Spacing between windows

        Returns:
            bool: Success
        """
        screen = self.get_screen_geometry(monitor)
        if not screen:
            return False

        # Convert display name to enum
        pattern_enum = pattern_display_to_enum(pattern)

        # Calculate layout
        try:
            geometry_dict = self.layout_manager.calculate_grid_layout(
                pattern_enum, window_ids, screen.__dict__, spacing
            )

            # Apply to windows
            return self.move_windows(geometry_dict)

        except Exception as e:
            self.logger.error(f"Failed to apply grid: {e}")
            return False

    def move_windows(self, geometry_dict: Dict[str, Dict]) -> bool:
        """
        Move windows to specified positions using xdotool

        Args:
            geometry_dict: {window_id: {"x": x, "y": y, "width": w, "height": h}}

        Returns:
            bool: Success
        """
        try:
            for window_id, geom in geometry_dict.items():
                # Move window
                subprocess.run(
                    ['xdotool', 'windowmove', '--sync', window_id,
                     str(geom["x"]), str(geom["y"])],
                    capture_output=True,
                    timeout=2
                )

                # Resize window
                subprocess.run(
                    ['xdotool', 'windowsize', '--sync', window_id,
                     str(geom["width"]), str(geom["height"])],
                    capture_output=True,
                    timeout=2
                )

            self.logger.info(f"Applied layout to {len(geometry_dict)} windows")
            return True

        except Exception as e:
            self.logger.error(f"Failed to move windows: {e}")
            return False


class LayoutsTab(QWidget):
    """Main Layouts Tab widget"""
    layout_applied = Signal(str)  # preset name

    def __init__(self, layout_manager, main_tab):
        super().__init__()
        self.layout_manager = layout_manager
        self.main_tab = main_tab
        self.logger = logging.getLogger(__name__)

        self.grid_applier = GridApplier(layout_manager)

        self._setup_ui()
        self._populate_layouts()

    def _setup_ui(self):
        layout = QHBoxLayout()

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Layout list
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel: Grid options and visualizer
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([400, 600])
        layout.addWidget(splitter)

        self.setLayout(layout)

    def _create_left_panel(self) -> QWidget:
        """Create layout list panel"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Saved Layouts")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Toolbar
        toolbar = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._populate_layouts)
        toolbar.addWidget(self.refresh_btn)

        self.save_btn = QPushButton("Save Current")
        self.save_btn.setToolTip("Save current window positions as new layout")
        self.save_btn.clicked.connect(self._save_current_layout)
        toolbar.addWidget(self.save_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Layout list
        self.layout_list = QListWidget()
        self.layout_list.itemSelectionChanged.connect(self._on_layout_selected)
        self.layout_list.itemDoubleClicked.connect(self._load_selected_layout)
        layout.addWidget(self.layout_list)

        # Action buttons
        action_layout = QHBoxLayout()

        self.load_btn = QPushButton("Load Layout")
        self.load_btn.clicked.connect(self._load_selected_layout)
        self.load_btn.setEnabled(False)
        action_layout.addWidget(self.load_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_selected_layout)
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(self.delete_btn)

        layout.addLayout(action_layout)

        panel.setLayout(layout)
        return panel

    def _create_right_panel(self) -> QWidget:
        """Create grid options and visualizer panel"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Grid pattern options
        options_group = QGroupBox("Grid Pattern Options")
        options_layout = QVBoxLayout()

        # Pattern selector
        pattern_layout = QFormLayout()

        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(get_all_patterns())
        self.pattern_combo.currentTextChanged.connect(self._update_pattern_preview)
        pattern_layout.addRow("Pattern:", self.pattern_combo)

        self.window_count_spin = QSpinBox()
        self.window_count_spin.setRange(1, 16)
        self.window_count_spin.setValue(4)
        self.window_count_spin.valueChanged.connect(self._update_pattern_preview)
        pattern_layout.addRow("Windows:", self.window_count_spin)

        self.spacing_spin = QSpinBox()
        self.spacing_spin.setRange(0, 50)
        self.spacing_spin.setValue(10)
        self.spacing_spin.setSuffix(" px")
        self.spacing_spin.valueChanged.connect(self._update_pattern_preview)
        pattern_layout.addRow("Spacing:", self.spacing_spin)

        self.monitor_spin = QSpinBox()
        self.monitor_spin.setRange(0, 3)
        self.monitor_spin.setValue(0)
        pattern_layout.addRow("Monitor:", self.monitor_spin)

        options_layout.addLayout(pattern_layout)

        # Apply button
        self.apply_pattern_btn = QPushButton("Apply Pattern to Active Windows")
        self.apply_pattern_btn.clicked.connect(self._apply_pattern_to_active)
        options_layout.addWidget(self.apply_pattern_btn)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Visualizer
        visualizer_group = QGroupBox("Layout Preview")
        visualizer_layout = QVBoxLayout()

        self.visualizer = GridPatternVisualizer()
        visualizer_layout.addWidget(self.visualizer)

        visualizer_group.setLayout(visualizer_layout)
        layout.addWidget(visualizer_group)

        panel.setLayout(layout)
        return panel

    def _populate_layouts(self):
        """Populate layout list from LayoutManager"""
        self.layout_list.clear()

        presets = self.layout_manager.get_all_presets()

        for preset in presets:
            item = QListWidgetItem()
            widget = LayoutListItem(preset)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, preset)

            self.layout_list.addItem(item)
            self.layout_list.setItemWidget(item, widget)

        if not presets:
            placeholder = QListWidgetItem("No saved layouts")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.layout_list.addItem(placeholder)

        self.logger.info(f"Loaded {len(presets)} layout presets")

    def _on_layout_selected(self):
        """Handle layout selection"""
        selected = self.layout_list.selectedItems()
        has_selection = len(selected) > 0 and selected[0].data(Qt.ItemDataRole.UserRole) is not None

        self.load_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

        if has_selection:
            preset = selected[0].data(Qt.ItemDataRole.UserRole)
            # Preview the layout
            self.visualizer.preview_layout(preset.windows)

    def _load_selected_layout(self):
        """Load selected layout and apply to windows"""
        selected = self.layout_list.selectedItems()
        if not selected:
            return

        preset = selected[0].data(Qt.ItemDataRole.UserRole)
        if not preset:
            return

        try:
            # Apply layout using GridApplier
            success = self.grid_applier.move_windows(preset.windows)

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Layout '{preset.name}' applied successfully!"
                )
                self.layout_applied.emit(preset.name)
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to apply layout. Check logs for details."
                )

        except Exception as e:
            self.logger.error(f"Failed to load layout: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load layout: {e}")

    def _save_current_layout(self):
        """Save current window positions as new layout"""
        # Get current windows from main tab
        if not hasattr(self.main_tab, 'window_manager'):
            QMessageBox.warning(self, "Error", "Main tab not initialized")
            return

        current_windows = {}
        for window_id, preview_widget in self.main_tab.window_manager.preview_frames.items():
            # Get window geometry using xdotool
            try:
                result = subprocess.run(
                    ['xdotool', 'getwindowgeometry', '--shell', window_id],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0:
                    geom = {}
                    for line in result.stdout.split('\n'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            if key in ['X', 'Y', 'WIDTH', 'HEIGHT']:
                                geom[key.lower()] = int(value)

                    if len(geom) == 4:
                        current_windows[window_id] = {
                            "x": geom["x"],
                            "y": geom["y"],
                            "width": geom["width"],
                            "height": geom["height"]
                        }

            except Exception as e:
                self.logger.warning(f"Failed to get geometry for window {window_id}: {e}")

        if not current_windows:
            QMessageBox.warning(
                self,
                "No Windows",
                "No active windows to save. Add windows in the Main tab first."
            )
            return

        # Show save dialog
        dialog = SaveLayoutDialog(self.layout_manager, current_windows, self)
        if dialog.exec():
            self._populate_layouts()

    def _delete_selected_layout(self):
        """Delete selected layout"""
        selected = self.layout_list.selectedItems()
        if not selected:
            return

        preset = selected[0].data(Qt.ItemDataRole.UserRole)
        if not preset:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete layout '{preset.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.layout_manager.delete_preset(preset.name)
                self._populate_layouts()
                self.logger.info(f"Deleted layout: {preset.name}")
            except Exception as e:
                self.logger.error(f"Failed to delete layout: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete layout: {e}")

    def _update_pattern_preview(self):
        """Update pattern preview based on current settings"""
        pattern = self.pattern_combo.currentText()
        window_count = self.window_count_spin.value()
        spacing = self.spacing_spin.value()
        monitor = self.monitor_spin.value()

        screen = self.grid_applier.get_screen_geometry(monitor)
        if screen:
            self.visualizer.set_pattern_preview(pattern, window_count, screen, spacing)

    def _apply_pattern_to_active(self):
        """Apply selected grid pattern to active windows"""
        # Get active windows from main tab
        if not hasattr(self.main_tab, 'window_manager'):
            QMessageBox.warning(self, "Error", "Main tab not initialized")
            return

        window_ids = list(self.main_tab.window_manager.preview_frames.keys())

        if not window_ids:
            QMessageBox.warning(
                self,
                "No Windows",
                "No active windows to apply pattern to. Add windows in the Main tab first."
            )
            return

        pattern = self.pattern_combo.currentText()
        monitor = self.monitor_spin.value()
        spacing = self.spacing_spin.value()

        try:
            success = self.grid_applier.apply_grid(pattern, window_ids, monitor, spacing)

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Applied {pattern} pattern to {len(window_ids)} windows!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to apply pattern. Check logs for details."
                )

        except Exception as e:
            self.logger.error(f"Failed to apply pattern: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply pattern: {e}")

    def load_layout(self, preset_name: str):
        """
        Load layout by name (called from other tabs)

        Args:
            preset_name: Name of preset to load
        """
        presets = self.layout_manager.get_all_presets()
        preset = next((p for p in presets if p.name == preset_name), None)

        if preset:
            success = self.grid_applier.move_windows(preset.windows)
            if success:
                self.layout_applied.emit(preset.name)
                self.logger.info(f"Loaded layout: {preset_name}")
        else:
            self.logger.warning(f"Layout not found: {preset_name}")
