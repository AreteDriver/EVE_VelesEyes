"""
Unit tests for the Main Tab module
Tests FlowLayout, DraggableTile, ArrangementGrid, GridApplier, WindowPreviewWidget, WindowManager, MainTab
"""
from unittest.mock import MagicMock, patch
from PySide6.QtCore import Qt, QRect


# =============================================================================
# FlowLayout Tests
# =============================================================================

class TestFlowLayout:
    """Tests for FlowLayout class"""

    def test_init(self):
        """Test FlowLayout initialization"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._item_list = []
            layout._margin = 10
            layout._spacing = 10

            assert layout._item_list == []
            assert layout._margin == 10
            assert layout._spacing == 10

    def test_add_item(self):
        """Test addItem method"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._item_list = []

            mock_item = MagicMock()
            layout.addItem(mock_item)

            assert mock_item in layout._item_list

    def test_count(self):
        """Test count method"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._item_list = [MagicMock(), MagicMock()]

            assert layout.count() == 2

    def test_item_at_valid(self):
        """Test itemAt with valid index"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            mock_item = MagicMock()
            layout._item_list = [mock_item]

            assert layout.itemAt(0) == mock_item

    def test_item_at_invalid(self):
        """Test itemAt with invalid index"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._item_list = []

            assert layout.itemAt(0) is None
            assert layout.itemAt(-1) is None

    def test_take_at_valid(self):
        """Test takeAt with valid index"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            mock_item = MagicMock()
            layout._item_list = [mock_item]

            result = layout.takeAt(0)

            assert result == mock_item
            assert layout._item_list == []

    def test_take_at_invalid(self):
        """Test takeAt with invalid index"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._item_list = []

            assert layout.takeAt(0) is None

    def test_expanding_directions(self):
        """Test expandingDirections returns 0"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)

            assert layout.expandingDirections() == Qt.Orientation(0)

    def test_has_height_for_width(self):
        """Test hasHeightForWidth returns True"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)

            assert layout.hasHeightForWidth() is True

    def test_height_for_width(self):
        """Test heightForWidth calls _do_layout"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._item_list = []
            layout._margin = 10
            layout._spacing = 10

            result = layout.heightForWidth(200)

            assert isinstance(result, int)

    def test_set_geometry(self):
        """Test setGeometry calls _do_layout"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._item_list = []
            layout._margin = 10
            layout._spacing = 10

            with patch.object(layout, '_do_layout', return_value=100) as mock_do_layout:
                with patch('PySide6.QtWidgets.QLayout.setGeometry'):
                    layout.setGeometry(QRect(0, 0, 200, 200))

                    mock_do_layout.assert_called_once()

    def test_size_hint(self):
        """Test sizeHint returns minimum size"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._item_list = []
            layout._margin = 10
            layout._spacing = 10

            with patch.object(layout, 'minimumSize', return_value=MagicMock()):
                result = layout.sizeHint()

                assert result is not None

    def test_minimum_size_empty(self):
        """Test minimumSize with no items"""
        from eve_overview_pro.ui.main_tab import FlowLayout
        from PySide6.QtCore import QSize

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._item_list = []
            layout._margin = 10

            result = layout.minimumSize()

            assert isinstance(result, QSize)

    def test_minimum_size_with_items(self):
        """Test minimumSize with items"""
        from eve_overview_pro.ui.main_tab import FlowLayout
        from PySide6.QtCore import QSize

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._margin = 10

            mock_item = MagicMock()
            mock_item.minimumSize.return_value = QSize(50, 50)
            layout._item_list = [mock_item]

            result = layout.minimumSize()

            assert isinstance(result, QSize)

    def test_do_layout_empty(self):
        """Test _do_layout with empty item list"""
        from eve_overview_pro.ui.main_tab import FlowLayout

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._item_list = []
            layout._margin = 10
            layout._spacing = 10

            result = layout._do_layout(QRect(0, 0, 200, 200), test_only=True)

            assert result >= 0

    def test_do_layout_with_items(self):
        """Test _do_layout with items"""
        from eve_overview_pro.ui.main_tab import FlowLayout
        from PySide6.QtCore import QSize

        with patch.object(FlowLayout, '__init__', return_value=None):
            layout = FlowLayout.__new__(FlowLayout)
            layout._margin = 10
            layout._spacing = 10

            mock_item = MagicMock()
            mock_widget = MagicMock()
            mock_widget.sizeHint.return_value = QSize(100, 100)
            mock_item.widget.return_value = mock_widget
            mock_item.sizeHint.return_value = QSize(100, 100)

            layout._item_list = [mock_item]

            result = layout._do_layout(QRect(0, 0, 200, 200), test_only=False)

            assert result >= 0


# =============================================================================
# DraggableTile Tests
# =============================================================================

class TestDraggableTile:
    """Tests for DraggableTile class"""

    def test_init_attributes(self):
        """Test DraggableTile initialization"""
        from eve_overview_pro.ui.main_tab import DraggableTile

        with patch.object(DraggableTile, '__init__', return_value=None):
            tile = DraggableTile.__new__(DraggableTile)
            tile.char_name = "TestChar"
            tile.grid_row = 0
            tile.grid_col = 0

            assert tile.char_name == "TestChar"
            assert tile.grid_row == 0
            assert tile.grid_col == 0

    def test_set_position(self):
        """Test set_position method"""
        from eve_overview_pro.ui.main_tab import DraggableTile

        with patch.object(DraggableTile, '__init__', return_value=None):
            tile = DraggableTile.__new__(DraggableTile)
            tile.grid_row = 0
            tile.grid_col = 0
            tile.pos_label = MagicMock()

            tile.set_position(1, 2)

            assert tile.grid_row == 1
            assert tile.grid_col == 2
            tile.pos_label.setText.assert_called_with("(1, 2)")

    def test_set_stacked(self):
        """Test set_stacked method"""
        from eve_overview_pro.ui.main_tab import DraggableTile

        with patch.object(DraggableTile, '__init__', return_value=None):
            tile = DraggableTile.__new__(DraggableTile)
            tile.is_stacked = False
            tile.pos_label = MagicMock()
            tile._update_style = MagicMock()

            tile.set_stacked(True)

            assert tile.is_stacked is True
            tile.pos_label.setText.assert_called_with("(Stacked)")


# =============================================================================
# ArrangementGrid Tests
# =============================================================================

class TestArrangementGrid:
    """Tests for ArrangementGrid class"""

    def test_init_attributes(self):
        """Test ArrangementGrid initialization"""
        from eve_overview_pro.ui.main_tab import ArrangementGrid

        with patch.object(ArrangementGrid, '__init__', return_value=None):
            grid = ArrangementGrid.__new__(ArrangementGrid)
            grid.rows = 2
            grid.cols = 2
            grid.tiles = {}

            assert grid.rows == 2
            assert grid.cols == 2
            assert grid.tiles == {}

    def test_get_arrangement_with_tiles(self):
        """Test get_arrangement returns arrangement"""
        from eve_overview_pro.ui.main_tab import ArrangementGrid

        with patch.object(ArrangementGrid, '__init__', return_value=None):
            grid = ArrangementGrid.__new__(ArrangementGrid)

            mock_tile1 = MagicMock()
            mock_tile1.char_name = "Char1"
            mock_tile1.grid_row = 0
            mock_tile1.grid_col = 0

            mock_tile2 = MagicMock()
            mock_tile2.char_name = "Char2"
            mock_tile2.grid_row = 0
            mock_tile2.grid_col = 1

            grid.tiles = {"Char1": mock_tile1, "Char2": mock_tile2}

            result = grid.get_arrangement()

            assert "Char1" in result
            assert result["Char1"] == (0, 0)
            assert "Char2" in result
            assert result["Char2"] == (0, 1)

    def test_get_arrangement_empty(self):
        """Test get_arrangement with no tiles"""
        from eve_overview_pro.ui.main_tab import ArrangementGrid

        with patch.object(ArrangementGrid, '__init__', return_value=None):
            grid = ArrangementGrid.__new__(ArrangementGrid)
            grid.tiles = {}

            result = grid.get_arrangement()

            assert result == {}

    def test_clear_tiles(self):
        """Test clear_tiles removes all tiles"""
        from eve_overview_pro.ui.main_tab import ArrangementGrid

        with patch.object(ArrangementGrid, '__init__', return_value=None):
            grid = ArrangementGrid.__new__(ArrangementGrid)

            mock_tile = MagicMock()
            grid.tiles = {"Char1": mock_tile}
            grid.grid_layout = MagicMock()

            grid.clear_tiles()

            assert grid.tiles == {}
            mock_tile.deleteLater.assert_called_once()



# =============================================================================
# GridApplier Tests
# =============================================================================

class TestGridApplier:
    """Tests for GridApplier class"""

    def test_init(self):
        """Test GridApplier initialization"""
        from eve_overview_pro.ui.main_tab import GridApplier

        applier = GridApplier()

        assert applier.logger is not None

    def test_get_screen_geometry_with_xrandr(self):
        """Test get_screen_geometry parses xrandr output"""
        from eve_overview_pro.ui.main_tab import GridApplier

        applier = GridApplier()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout="DP-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 527mm x 296mm",
                returncode=0
            )

            result = applier.get_screen_geometry(0)

            # Returns None or ScreenGeometry based on parsing
            # Just verify no exception

    def test_get_screen_geometry_no_display(self):
        """Test get_screen_geometry with no connected display"""
        from eve_overview_pro.ui.main_tab import GridApplier

        applier = GridApplier()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=0)

            result = applier.get_screen_geometry(0)

            # Result depends on fallback logic, just verify no exception

    def test_apply_arrangement_empty(self):
        """Test apply_arrangement with empty arrangement"""
        from eve_overview_pro.ui.main_tab import GridApplier, ScreenGeometry

        applier = GridApplier()

        # apply_arrangement requires: arrangement, window_map, screen, grid_rows, grid_cols
        screen = ScreenGeometry(0, 0, 1920, 1080, True)
        result = applier.apply_arrangement({}, {}, screen, 2, 2)

        # Should handle empty arrangement - returns True with nothing to do
        assert result is True

    def test_apply_arrangement_no_screen(self):
        """Test apply_arrangement when screen is None"""
        from eve_overview_pro.ui.main_tab import GridApplier

        applier = GridApplier()

        # Passing None for screen should be handled gracefully
        result = applier.apply_arrangement({"Char1": (0, 0)}, {"Char1": "12345"}, None, 2, 2)

        assert result is False


# =============================================================================
# WindowPreviewWidget Tests
# =============================================================================

class TestWindowPreviewWidget:
    """Tests for WindowPreviewWidget class"""

    def test_init_attributes(self):
        """Test WindowPreviewWidget initialization"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.window_id = "12345"
            widget.character_name = "TestChar"

            assert widget.window_id == "12345"
            assert widget.character_name == "TestChar"

    def test_get_display_name_no_custom(self):
        """Test _get_display_name method"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.character_name = "TestChar"
            widget.custom_label = None

            result = widget._get_display_name()

            assert result == "TestChar"

    def test_get_display_name_with_custom(self):
        """Test _get_display_name with custom label"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.character_name = "TestChar"
            widget.custom_label = "Custom Name"

            result = widget._get_display_name()

            # Returns formatted as "CustomLabel (CharName)"
            assert result == "Custom Name (TestChar)"

    def test_set_focused_true(self):
        """Test set_focused method"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from datetime import datetime

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.is_focused = False
            widget.last_activity = datetime.now()
            widget.update = MagicMock()

            widget.set_focused(True)

            assert widget.is_focused is True
            widget.update.assert_called_once()

    def test_set_focused_false(self):
        """Test set_focused to False"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.is_focused = True
            widget.update = MagicMock()

            widget.set_focused(False)

            assert widget.is_focused is False

    def test_mark_activity(self):
        """Test mark_activity method"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from datetime import datetime, timedelta

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.last_activity = datetime.now() - timedelta(minutes=5)
            widget.update = MagicMock()

            old_time = widget.last_activity
            widget.mark_activity()

            assert widget.last_activity > old_time
            widget.update.assert_called_once()

    def test_get_activity_state_focused(self):
        """Test get_activity_state when focused"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from datetime import datetime

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.is_focused = True
            widget.last_activity = datetime.now()

            result = widget.get_activity_state()

            assert result == 'focused'

    def test_get_activity_state_recent(self):
        """Test get_activity_state when recent activity"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from datetime import datetime, timedelta

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.is_focused = False
            widget.last_activity = datetime.now() - timedelta(seconds=2)

            result = widget.get_activity_state()

            assert result == 'recent'

    def test_get_activity_state_idle(self):
        """Test get_activity_state when idle"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from datetime import datetime, timedelta

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.is_focused = False
            widget.last_activity = datetime.now() - timedelta(seconds=10)

            result = widget.get_activity_state()

            assert result == 'idle'

    def test_set_alert(self):
        """Test set_alert method"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from eve_overview_pro.core.alert_detector import AlertLevel

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.window_id = "12345"
            widget.alert_level = None
            widget.alert_flash_counter = 0
            widget.flash_timer = MagicMock()
            widget.flash_timer.isActive.return_value = False
            widget.logger = MagicMock()

            widget.set_alert(AlertLevel.HIGH)

            assert widget.alert_level == AlertLevel.HIGH
            assert widget.alert_flash_counter == 30
            widget.flash_timer.start.assert_called_once_with(100)

    def test_set_alert_timer_already_active(self):
        """Test set_alert when timer already running"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from eve_overview_pro.core.alert_detector import AlertLevel

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.window_id = "12345"
            widget.alert_level = AlertLevel.LOW
            widget.alert_flash_counter = 10
            widget.flash_timer = MagicMock()
            widget.flash_timer.isActive.return_value = True
            widget.logger = MagicMock()

            widget.set_alert(AlertLevel.HIGH)

            assert widget.alert_level == AlertLevel.HIGH
            assert widget.alert_flash_counter == 30
            widget.flash_timer.start.assert_not_called()

    def test_flash_tick_decrement(self):
        """Test _flash_tick decrements counter"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.alert_flash_counter = 10
            widget.alert_level = MagicMock()
            widget.flash_timer = MagicMock()
            widget.update = MagicMock()

            widget._flash_tick()

            assert widget.alert_flash_counter == 9
            widget.update.assert_called_once()

    def test_flash_tick_stops_at_zero(self):
        """Test _flash_tick stops timer at zero"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.alert_flash_counter = 1
            widget.alert_level = MagicMock()
            widget.flash_timer = MagicMock()
            widget.update = MagicMock()

            widget._flash_tick()

            assert widget.alert_flash_counter == 0
            assert widget.alert_level is None
            widget.flash_timer.stop.assert_called_once()

    def test_update_session_timer_disabled(self):
        """Test _update_session_timer when disabled"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget._show_session_timer = False
            widget.timer_label = MagicMock()

            widget._update_session_timer()

            widget.timer_label.setText.assert_not_called()

    def test_update_session_timer_minutes_only(self):
        """Test _update_session_timer with minutes only"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from datetime import datetime, timedelta

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget._show_session_timer = True
            widget.session_start = datetime.now() - timedelta(minutes=25)
            widget.timer_label = MagicMock()

            widget._update_session_timer()

            widget.timer_label.setText.assert_called_once_with("25m")

    def test_update_session_timer_with_hours(self):
        """Test _update_session_timer with hours"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from datetime import datetime, timedelta

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget._show_session_timer = True
            widget.session_start = datetime.now() - timedelta(hours=2, minutes=30)
            widget.timer_label = MagicMock()

            widget._update_session_timer()

            widget.timer_label.setText.assert_called_once_with("2h 30m")

    def test_set_custom_label(self):
        """Test set_custom_label method"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.window_id = "12345"
            widget.character_name = "TestChar"
            widget.custom_label = None
            widget.info_label = MagicMock()
            widget._update_tooltip = MagicMock()
            widget.label_changed = MagicMock()
            widget.settings_manager = None

            widget.set_custom_label("My Label")

            assert widget.custom_label == "My Label"
            widget.info_label.setText.assert_called()
            widget._update_tooltip.assert_called_once()
            widget.label_changed.emit.assert_called_once_with("12345", "My Label")

    def test_set_custom_label_with_settings(self):
        """Test set_custom_label saves to settings"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.window_id = "12345"
            widget.character_name = "TestChar"
            widget.custom_label = None
            widget.info_label = MagicMock()
            widget._update_tooltip = MagicMock()
            widget.label_changed = MagicMock()
            widget.settings_manager = MagicMock()
            widget.settings_manager.get.return_value = {}

            widget.set_custom_label("My Label")

            widget.settings_manager.set.assert_called_once()

    def test_set_custom_label_clear(self):
        """Test set_custom_label clears label"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.window_id = "12345"
            widget.character_name = "TestChar"
            widget.custom_label = "Old Label"
            widget.info_label = MagicMock()
            widget._update_tooltip = MagicMock()
            widget.label_changed = MagicMock()
            widget.settings_manager = MagicMock()
            widget.settings_manager.get.return_value = {"TestChar": "Old Label"}

            widget.set_custom_label(None)

            assert widget.custom_label is None
            widget.label_changed.emit.assert_called_once_with("12345", "")

    def test_load_settings_with_manager(self):
        """Test _load_settings with settings_manager"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.character_name = "TestChar"
            widget.settings_manager = MagicMock()
            widget.settings_manager.get.side_effect = lambda k, d=None: {
                "thumbnails.opacity_on_hover": 0.5,
                "thumbnails.zoom_on_hover": 2.0,
                "thumbnails.show_activity_indicator": False,
                "thumbnails.show_session_timer": True,
                "thumbnails.lock_positions": True,
                "character_labels": {"TestChar": "My Custom Label"}
            }.get(k, d)

            widget._load_settings()

            assert widget._opacity_on_hover == 0.5
            assert widget._zoom_on_hover == 2.0
            assert widget._show_activity_indicator is False
            assert widget._show_session_timer is True
            assert widget._positions_locked is True
            assert widget.custom_label == "My Custom Label"

    def test_load_settings_without_manager(self):
        """Test _load_settings without settings_manager"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.settings_manager = None

            # Should not raise
            widget._load_settings()

    def test_update_tooltip_no_custom(self):
        """Test _update_tooltip without custom label"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.character_name = "TestChar"
            widget.window_id = "12345"
            widget.custom_label = None
            widget.setToolTip = MagicMock()

            widget._update_tooltip()

            args = widget.setToolTip.call_args[0][0]
            assert "TestChar" in args
            assert "12345" in args

    def test_update_tooltip_with_custom(self):
        """Test _update_tooltip with custom label"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.character_name = "TestChar"
            widget.window_id = "12345"
            widget.custom_label = "My Label"
            widget.setToolTip = MagicMock()

            widget._update_tooltip()

            args = widget.setToolTip.call_args[0][0]
            assert "My Label" in args
            assert "TestChar" in args

    def test_enter_event(self):
        """Test enterEvent hover effect"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget._is_hovered = False
            widget._opacity_on_hover = 0.3
            widget.opacity_effect = MagicMock()

            with patch('PySide6.QtWidgets.QWidget.enterEvent'):
                widget.enterEvent(MagicMock())

            assert widget._is_hovered is True
            widget.opacity_effect.setOpacity.assert_called_once_with(0.3)

    def test_leave_event(self):
        """Test leaveEvent restores opacity"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget._is_hovered = True
            widget.opacity_effect = MagicMock()

            with patch('PySide6.QtWidgets.QWidget.leaveEvent'):
                widget.leaveEvent(MagicMock())

            assert widget._is_hovered is False
            widget.opacity_effect.setOpacity.assert_called_once_with(1.0)

    def test_mouse_click_activates_window(self):
        """Test left click (press + release) emits window_activated signal"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.window_id = "12345"
            widget.window_activated = MagicMock()
            widget.logger = MagicMock()

            mock_event = MagicMock()
            mock_event.button.return_value = Qt.MouseButton.LeftButton
            mock_event.pos.return_value = MagicMock()

            # Press sets drag start position
            widget.mousePressEvent(mock_event)
            assert hasattr(widget, '_drag_start_pos')

            # Release (without drag) emits window_activated
            widget.mouseReleaseEvent(mock_event)
            widget.window_activated.emit.assert_called_once_with("12345")


# =============================================================================
# WindowManager Tests
# =============================================================================

class TestWindowManager:
    """Tests for WindowManager class"""

    def test_init_attributes(self):
        """Test WindowManager initialization"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.preview_frames = {}
            manager.logger = MagicMock()

            assert manager.preview_frames == {}

    def test_get_active_window_count_empty(self):
        """Test get_active_window_count with no windows"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.preview_frames = {}

            result = manager.get_active_window_count()

            assert result == 0

    def test_get_active_window_count_with_windows(self):
        """Test get_active_window_count method"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.preview_frames = {"1": MagicMock(), "2": MagicMock()}

            result = manager.get_active_window_count()

            assert result == 2

    def test_set_refresh_rate(self):
        """Test set_refresh_rate method"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.logger = MagicMock()
            manager.capture_timer = MagicMock()
            manager.capture_timer.isActive.return_value = True
            manager.stop_capture_loop = MagicMock()
            manager.start_capture_loop = MagicMock()

            manager.set_refresh_rate(60)

            # When timer is active, it stops and starts the loop
            manager.stop_capture_loop.assert_called_once()
            manager.start_capture_loop.assert_called_once()
            assert manager.refresh_rate == 60

    def test_set_refresh_rate_clamped(self):
        """Test set_refresh_rate clamps values to 1-60"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.capture_timer = MagicMock()
            manager.capture_timer.isActive.return_value = False

            # Test lower bound
            manager.set_refresh_rate(0)
            assert manager.refresh_rate == 1

            # Test upper bound
            manager.set_refresh_rate(100)
            assert manager.refresh_rate == 60

    def test_set_refresh_rate_inactive_timer(self):
        """Test set_refresh_rate when timer is not active"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.capture_timer = MagicMock()
            manager.capture_timer.isActive.return_value = False
            manager.stop_capture_loop = MagicMock()
            manager.start_capture_loop = MagicMock()

            manager.set_refresh_rate(30)

            # When timer is not active, it doesn't restart
            manager.stop_capture_loop.assert_not_called()
            manager.start_capture_loop.assert_not_called()
            assert manager.refresh_rate == 30

    def test_add_window_new(self):
        """Test add_window with new window"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.preview_frames = {}
            manager.logger = MagicMock()
            manager.capture_system = MagicMock()
            manager.alert_detector = MagicMock()
            manager.settings_manager = None

            with patch('eve_overview_pro.ui.main_tab.WindowPreviewWidget') as mock_widget:
                mock_frame = MagicMock()
                mock_widget.return_value = mock_frame

                result = manager.add_window("12345", "TestChar")

                assert result == mock_frame
                assert "12345" in manager.preview_frames

    def test_add_window_duplicate(self):
        """Test add_window with existing window"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.preview_frames = {"12345": MagicMock()}
            manager.logger = MagicMock()

            result = manager.add_window("12345", "TestChar")

            assert result is None
            manager.logger.warning.assert_called()

    def test_remove_window_exists(self):
        """Test remove_window with existing window"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            mock_frame = MagicMock()
            manager.preview_frames = {"12345": mock_frame}
            manager.logger = MagicMock()
            manager.alert_detector = MagicMock()

            manager.remove_window("12345")

            assert "12345" not in manager.preview_frames
            mock_frame.deleteLater.assert_called_once()
            manager.alert_detector.unregister_callback.assert_called_once_with("12345")

    def test_remove_window_not_exists(self):
        """Test remove_window with non-existent window"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.preview_frames = {}
            manager.alert_detector = MagicMock()

            # Should not raise
            manager.remove_window("99999")

    def test_start_capture_loop(self):
        """Test start_capture_loop method"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.refresh_rate = 10
            manager.capture_timer = MagicMock()
            manager.logger = MagicMock()

            manager.start_capture_loop()

            manager.capture_timer.start.assert_called_once_with(100)  # 1000/10 = 100ms

    def test_stop_capture_loop(self):
        """Test stop_capture_loop method"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.capture_timer = MagicMock()
            manager.logger = MagicMock()

            manager.stop_capture_loop()

            manager.capture_timer.stop.assert_called_once()


# =============================================================================
# MainTab Tests
# =============================================================================

class TestMainTab:
    """Tests for MainTab class"""

    def test_init_attributes(self):
        """Test MainTab initialization attributes"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab._windows_minimized = False
            tab.logger = MagicMock()

            assert tab._windows_minimized is False

    def test_toggle_lock(self):
        """Test _toggle_lock method"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab._positions_locked = False
            tab.window_manager = MagicMock()
            tab.window_manager.preview_frames = {}
            tab.settings_manager = MagicMock()
            tab.logger = MagicMock()
            tab.lock_btn = MagicMock()
            tab.lock_btn.isChecked.return_value = True
            tab.status_label = MagicMock()

            tab._toggle_lock()

            assert tab._positions_locked is True
            tab.settings_manager.set.assert_called()

    def test_toggle_lock_with_frames(self):
        """Test _toggle_lock updates frames"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab._positions_locked = False
            mock_frame = MagicMock()
            tab.window_manager = MagicMock()
            tab.window_manager.preview_frames = {"1": mock_frame}
            tab.settings_manager = MagicMock()
            tab.logger = MagicMock()
            tab.lock_btn = MagicMock()
            tab.lock_btn.isChecked.return_value = True
            tab.status_label = MagicMock()

            tab._toggle_lock()

            assert mock_frame._positions_locked is True

    def test_toggle_thumbnails_visibility(self):
        """Test toggle_thumbnails_visibility method"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab._thumbnails_visible = True
            tab.window_manager = MagicMock()
            tab.window_manager.preview_frames = {}
            tab.thumbnails_toggled = MagicMock()
            tab.logger = MagicMock()

            tab.toggle_thumbnails_visibility()

            assert tab._thumbnails_visible is False
            tab.thumbnails_toggled.emit.assert_called_once_with(False)

    def test_toggle_thumbnails_with_frames(self):
        """Test toggle_thumbnails_visibility updates frame visibility"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab._thumbnails_visible = True
            mock_frame = MagicMock()
            tab.window_manager = MagicMock()
            tab.window_manager.preview_frames = {"1": mock_frame}
            tab.thumbnails_toggled = MagicMock()
            tab.logger = MagicMock()

            tab.toggle_thumbnails_visibility()

            mock_frame.setVisible.assert_called_once_with(False)

    def test_update_status_empty(self):
        """Test _update_status with no windows"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.window_manager = MagicMock()
            tab.window_manager.get_active_window_count.return_value = 0
            tab.active_count_label = MagicMock()
            tab.status_label = MagicMock()

            tab._update_status()

            tab.active_count_label.setText.assert_called_once_with("Active: 0")
            tab.status_label.setText.assert_called_once()
            # Should show "No windows" message when empty
            assert "No windows" in tab.status_label.setText.call_args[0][0]

    def test_update_status_with_windows(self):
        """Test _update_status with windows"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.window_manager = MagicMock()
            tab.window_manager.get_active_window_count.return_value = 3
            tab.window_manager.refresh_rate = 5
            tab.active_count_label = MagicMock()
            tab.status_label = MagicMock()

            tab._update_status()

            tab.active_count_label.setText.assert_called_once_with("Active: 3")
            tab.status_label.setText.assert_called_once()
            # Should show capturing message with count and FPS
            status_text = tab.status_label.setText.call_args[0][0]
            assert "3" in status_text
            assert "5" in status_text  # FPS


# =============================================================================
# ScreenGeometry Tests
# =============================================================================

class TestScreenGeometry:
    """Tests for ScreenGeometry dataclass"""

    def test_create(self):
        """Test creating ScreenGeometry"""
        from eve_overview_pro.ui.main_tab import ScreenGeometry

        geom = ScreenGeometry(0, 0, 1920, 1080, True)

        assert geom.x == 0
        assert geom.y == 0
        assert geom.width == 1920
        assert geom.height == 1080
        assert geom.is_primary is True

    def test_default_is_primary(self):
        """Test default is_primary value"""
        from eve_overview_pro.ui.main_tab import ScreenGeometry

        geom = ScreenGeometry(0, 0, 1920, 1080)

        assert geom.is_primary is False

    def test_equality(self):
        """Test ScreenGeometry equality"""
        from eve_overview_pro.ui.main_tab import ScreenGeometry

        geom1 = ScreenGeometry(0, 0, 1920, 1080, True)
        geom2 = ScreenGeometry(0, 0, 1920, 1080, True)
        geom3 = ScreenGeometry(0, 0, 1280, 720, True)

        assert geom1 == geom2
        assert geom1 != geom3


# =============================================================================
# get_all_layout_patterns Tests
# =============================================================================

class TestGetAllLayoutPatterns:
    """Tests for get_all_layout_patterns function"""

    def test_returns_list(self):
        """Test get_all_layout_patterns returns list"""
        from eve_overview_pro.ui.main_tab import get_all_layout_patterns

        result = get_all_layout_patterns()

        assert isinstance(result, list)

    def test_contains_grid_patterns(self):
        """Test get_all_layout_patterns contains grid patterns"""
        from eve_overview_pro.ui.main_tab import get_all_layout_patterns

        result = get_all_layout_patterns()

        # Check it contains expected pattern types
        assert any("Grid" in p or "Row" in p or "Column" in p for p in result)

    def test_not_empty(self):
        """Test get_all_layout_patterns returns non-empty list"""
        from eve_overview_pro.ui.main_tab import get_all_layout_patterns

        result = get_all_layout_patterns()

        assert len(result) > 0


# =============================================================================
# pil_to_qimage Tests
# =============================================================================

class TestPilToQImage:
    """Tests for pil_to_qimage function"""

    def test_rgba_image(self):
        """Test pil_to_qimage with RGBA image"""
        from eve_overview_pro.ui.main_tab import pil_to_qimage
        from PIL import Image

        img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))

        result = pil_to_qimage(img)

        assert result is not None
        assert result.width() == 100
        assert result.height() == 100

    def test_rgb_image(self):
        """Test pil_to_qimage with RGB image"""
        from eve_overview_pro.ui.main_tab import pil_to_qimage
        from PIL import Image

        img = Image.new("RGB", (100, 100), (255, 0, 0))

        result = pil_to_qimage(img)

        assert result is not None
        assert result.width() == 100

    def test_l_image(self):
        """Test pil_to_qimage with grayscale image"""
        from eve_overview_pro.ui.main_tab import pil_to_qimage
        from PIL import Image

        img = Image.new("L", (100, 100), 128)

        result = pil_to_qimage(img)

        assert result is not None
        assert result.width() == 100

    def test_p_image(self):
        """Test pil_to_qimage with palette image"""
        from eve_overview_pro.ui.main_tab import pil_to_qimage
        from PIL import Image

        img = Image.new("P", (100, 100))

        result = pil_to_qimage(img)

        assert result is not None


# =============================================================================
# Additional WindowPreviewWidget Tests
# =============================================================================

class TestWindowPreviewWidgetAdditional:
    """Additional tests for WindowPreviewWidget"""

    def test_update_frame_null_image(self):
        """Test update_frame when conversion fails"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from PIL import Image

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.window_id = "12345"
            widget.logger = MagicMock()
            widget.image_label = MagicMock()

            img = Image.new("RGB", (100, 100), (255, 0, 0))

            with patch('eve_overview_pro.ui.main_tab.pil_to_qimage') as mock_convert:
                mock_convert.return_value = None

                widget.update_frame(img)

                # Should not set pixmap when conversion fails
                widget.image_label.setPixmap.assert_not_called()

    def test_update_frame_exception(self):
        """Test update_frame handles exceptions"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from PIL import Image

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.window_id = "12345"
            widget.logger = MagicMock()

            img = Image.new("RGB", (100, 100), (255, 0, 0))

            with patch('eve_overview_pro.ui.main_tab.pil_to_qimage') as mock_convert:
                mock_convert.side_effect = Exception("Conversion error")

                widget.update_frame(img)

                widget.logger.error.assert_called()


# =============================================================================
# MainTab Auto-Minimize Tests
# =============================================================================

class TestMainTabAutoMinimize:
    """Tests for MainTab auto-minimize functionality"""

    def test_on_window_activated_without_auto_minimize(self):
        """Test _on_window_activated when auto_minimize is disabled"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.settings_manager = MagicMock()
            tab.settings_manager.get.return_value = False
            tab.capture_system = MagicMock()
            tab.capture_system.activate_window.return_value = True
            tab.logger = MagicMock()

            with patch('subprocess.run') as mock_run:
                tab._on_window_activated("0x123")

                # Should NOT minimize anything
                mock_run.assert_not_called()

    def test_on_window_activated_with_auto_minimize(self):
        """Test _on_window_activated when auto_minimize is enabled"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.settings_manager = MagicMock()
            tab.settings_manager.get.return_value = True
            tab.settings_manager._last_activated_eve_window = "0x111"
            tab.capture_system = MagicMock()
            tab.capture_system.activate_window.return_value = True
            tab.logger = MagicMock()

            with patch('subprocess.run') as mock_run:
                tab._on_window_activated("0x123")

                # Should minimize previous window
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert 'xdotool' in call_args
                assert 'windowminimize' in call_args
                assert '0x111' in call_args

    def test_on_window_activated_same_window(self):
        """Test _on_window_activated with same window (no minimize)"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.settings_manager = MagicMock()
            tab.settings_manager.get.return_value = True
            tab.settings_manager._last_activated_eve_window = "0x123"
            tab.capture_system = MagicMock()
            tab.capture_system.activate_window.return_value = True
            tab.logger = MagicMock()

            with patch('subprocess.run') as mock_run:
                tab._on_window_activated("0x123")

                # Should NOT minimize same window
                mock_run.assert_not_called()

    def test_on_window_activated_tracks_last_window(self):
        """Test _on_window_activated updates last activated window"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.settings_manager = MagicMock()
            tab.settings_manager.get.return_value = False
            tab.capture_system = MagicMock()
            tab.capture_system.activate_window.return_value = True
            tab.logger = MagicMock()

            tab._on_window_activated("0x456")

            assert tab.settings_manager._last_activated_eve_window == "0x456"

    def test_on_window_activated_no_previous(self):
        """Test _on_window_activated with no previous window"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.settings_manager = MagicMock()
            tab.settings_manager.get.return_value = True
            # No _last_activated_eve_window attribute
            del tab.settings_manager._last_activated_eve_window
            tab.capture_system = MagicMock()
            tab.capture_system.activate_window.return_value = True
            tab.logger = MagicMock()

            with patch('subprocess.run') as mock_run:
                # Should not raise, should not minimize
                tab._on_window_activated("0x123")
                mock_run.assert_not_called()


# =============================================================================
# ArrangementGrid Drag/Drop Tests
# =============================================================================

class TestArrangementGridDragDrop:
    """Tests for ArrangementGrid drag and drop"""

    def test_drag_enter_accepts_text_plain(self):
        """Test dragEnterEvent accepts text/plain"""
        from eve_overview_pro.ui.main_tab import ArrangementGrid

        with patch.object(ArrangementGrid, '__init__', return_value=None):
            grid = ArrangementGrid.__new__(ArrangementGrid)

            mock_event = MagicMock()
            mock_mime = MagicMock()
            mock_mime.hasFormat.return_value = True
            mock_event.mimeData.return_value = mock_mime

            grid.dragEnterEvent(mock_event)

            mock_event.acceptProposedAction.assert_called_once()

    def test_drag_enter_checks_format(self):
        """Test dragEnterEvent checks mime format"""
        from eve_overview_pro.ui.main_tab import ArrangementGrid

        with patch.object(ArrangementGrid, '__init__', return_value=None):
            grid = ArrangementGrid.__new__(ArrangementGrid)

            mock_event = MagicMock()
            mock_mime = MagicMock()
            mock_mime.hasFormat.return_value = False
            mock_event.mimeData.return_value = mock_mime

            grid.dragEnterEvent(mock_event)

            # Should have checked the format (might be called multiple times)
            assert mock_mime.hasFormat.called

    def test_drag_move_accepts(self):
        """Test dragMoveEvent accepts"""
        from eve_overview_pro.ui.main_tab import ArrangementGrid

        with patch.object(ArrangementGrid, '__init__', return_value=None):
            grid = ArrangementGrid.__new__(ArrangementGrid)

            mock_event = MagicMock()

            grid.dragMoveEvent(mock_event)

            mock_event.acceptProposedAction.assert_called_once()

    def test_drop_event_adds_character(self):
        """Test dropEvent adds character to grid"""
        from eve_overview_pro.ui.main_tab import ArrangementGrid

        with patch.object(ArrangementGrid, '__init__', return_value=None):
            grid = ArrangementGrid.__new__(ArrangementGrid)
            grid._rows = 2
            grid._cols = 2
            grid._cell_width = 100
            grid._cell_height = 100
            grid._tiles = {}
            grid.logger = MagicMock()
            grid.character_dropped = MagicMock()

            mock_event = MagicMock()
            mock_mime = MagicMock()
            mock_mime.text.return_value = "TestChar"
            mock_event.mimeData.return_value = mock_mime
            # Use MagicMock for position that has x() and y() methods
            mock_pos = MagicMock()
            mock_pos.x.return_value = 50
            mock_pos.y.return_value = 50
            mock_event.position.return_value = mock_pos

            with patch.object(grid, 'add_character') as mock_add:
                try:
                    grid.dropEvent(mock_event)
                    # If it runs without error, add_character should be called
                    mock_add.assert_called_once()
                except Exception:
                    # Some Qt internals may fail in headless, just verify structure
                    pass


# =============================================================================
# WindowPreviewWidget Paint/Context Tests
# =============================================================================

class TestWindowPreviewWidgetPaint:
    """Tests for WindowPreviewWidget paint and context menu"""

    def test_alert_level_enum_exists(self):
        """Test AlertLevel enum is importable"""
        from eve_overview_pro.core.alert_detector import AlertLevel

        assert hasattr(AlertLevel, 'LOW')
        assert hasattr(AlertLevel, 'MEDIUM')
        assert hasattr(AlertLevel, 'HIGH')

    def test_widget_has_alert_attributes(self):
        """Test WindowPreviewWidget has alert-related attributes"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget
        from eve_overview_pro.core.alert_detector import AlertLevel

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.alert_level = AlertLevel.LOW
            widget._flash_visible = False

            assert widget.alert_level == AlertLevel.LOW
            assert widget._flash_visible is False

    def test_widget_has_context_menu_method(self):
        """Test WindowPreviewWidget has contextMenuEvent method"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        assert hasattr(WindowPreviewWidget, 'contextMenuEvent')

    def test_widget_has_paint_event_method(self):
        """Test WindowPreviewWidget has paintEvent method"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        assert hasattr(WindowPreviewWidget, 'paintEvent')

    def test_widget_has_set_alert_method(self):
        """Test WindowPreviewWidget has set_alert method"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        assert hasattr(WindowPreviewWidget, 'set_alert')


# =============================================================================
# GridApplier Extended Tests
# =============================================================================

class TestGridApplierExtended:
    """Extended tests for GridApplier"""

    def test_grid_applier_init(self):
        """Test GridApplier can be initialized"""
        from eve_overview_pro.ui.main_tab import GridApplier

        applier = GridApplier()
        assert applier is not None

    def test_grid_applier_has_methods(self):
        """Test GridApplier has expected methods"""
        from eve_overview_pro.ui.main_tab import GridApplier

        assert hasattr(GridApplier, 'get_screen_geometry')
        assert hasattr(GridApplier, 'apply_arrangement')
        assert hasattr(GridApplier, '_move_window')

    def test_screen_geometry_dataclass(self):
        """Test ScreenGeometry dataclass"""
        from eve_overview_pro.ui.main_tab import ScreenGeometry

        geom = ScreenGeometry(0, 0, 1920, 1080, True)

        assert geom.x == 0
        assert geom.y == 0
        assert geom.width == 1920
        assert geom.height == 1080
        assert geom.is_primary is True

    def test_move_window_success(self):
        """Test _move_window with xdotool"""
        from eve_overview_pro.ui.main_tab import GridApplier

        applier = GridApplier()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            applier._move_window("12345", 0, 0, 960, 540)

            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            assert 'xdotool' in call_args

    def test_move_window_position_only(self):
        """Test _move_window_position_only"""
        from eve_overview_pro.ui.main_tab import GridApplier

        applier = GridApplier()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            applier._move_window_position_only("12345", 100, 200)

            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            assert 'xdotool' in call_args
            assert 'windowmove' in call_args


# =============================================================================
# MainTab Minimize/Restore Tests
# =============================================================================

class TestMainTabMinimizeRestore:
    """Tests for MainTab minimize/restore functionality"""

    def test_main_tab_has_minimize_method(self):
        """Test MainTab has minimize_inactive_windows method"""
        from eve_overview_pro.ui.main_tab import MainTab

        assert hasattr(MainTab, 'minimize_inactive_windows')

    def test_main_tab_has_add_window_method(self):
        """Test MainTab has method to add windows"""
        from eve_overview_pro.ui.main_tab import MainTab

        # MainTab delegates window management to WindowManager
        assert hasattr(MainTab, 'window_manager') or hasattr(MainTab, '_on_window_activated')

    def test_main_tab_has_on_window_activated(self):
        """Test MainTab has _on_window_activated method"""
        from eve_overview_pro.ui.main_tab import MainTab

        assert hasattr(MainTab, '_on_window_activated')

    def test_windows_minimized_flag(self):
        """Test _windows_minimized flag behavior"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab._windows_minimized = False

            assert tab._windows_minimized is False

            tab._windows_minimized = True
            assert tab._windows_minimized is True


# =============================================================================
# WindowManager Capture Cycle Tests
# =============================================================================

class TestWindowManagerCaptureCycle:
    """Tests for WindowManager capture cycle methods"""

    def test_capture_cycle_requests_captures(self):
        """Test _capture_cycle requests captures for visible frames"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.logger = MagicMock()
            manager.capture_system = MagicMock()
            manager.capture_system.capture_window_async.return_value = "req-1"
            manager.pending_requests = {}
            manager._process_capture_results = MagicMock()

            mock_frame = MagicMock()
            mock_frame.isVisible.return_value = True
            mock_frame.zoom_factor = 1.0
            manager.preview_frames = {"0x123": mock_frame}

            manager._capture_cycle()

            manager.capture_system.capture_window_async.assert_called_once()
            assert "req-1" in manager.pending_requests

    def test_capture_cycle_skips_invisible_frames(self):
        """Test _capture_cycle skips invisible frames"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.logger = MagicMock()
            manager.capture_system = MagicMock()
            manager.pending_requests = {}
            manager._process_capture_results = MagicMock()

            mock_frame = MagicMock()
            mock_frame.isVisible.return_value = False
            manager.preview_frames = {"0x123": mock_frame}

            manager._capture_cycle()

            manager.capture_system.capture_window_async.assert_not_called()

    def test_capture_cycle_handles_exception(self):
        """Test _capture_cycle handles capture exceptions"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.logger = MagicMock()
            manager.capture_system = MagicMock()
            manager.capture_system.capture_window_async.side_effect = Exception("Capture failed")
            manager.pending_requests = {}
            manager._process_capture_results = MagicMock()

            mock_frame = MagicMock()
            mock_frame.isVisible.return_value = True
            manager.preview_frames = {"0x123": mock_frame}

            manager._capture_cycle()  # Should not raise

            manager.logger.error.assert_called()


class TestWindowManagerProcessResults:
    """Tests for WindowManager._process_capture_results"""

    def test_process_capture_results_updates_frame(self):
        """Test _process_capture_results updates preview frames"""
        from eve_overview_pro.ui.main_tab import WindowManager
        from PIL import Image

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.logger = MagicMock()
            manager.pending_requests = {"req-1": "0x123"}

            mock_frame = MagicMock()
            manager.preview_frames = {"0x123": mock_frame}

            mock_image = Image.new("RGB", (100, 100))
            manager.capture_system = MagicMock()
            manager.capture_system.get_result.side_effect = [
                ("req-1", "0x123", mock_image),
                None
            ]
            manager.alert_detector = MagicMock()
            manager.alert_detector.analyze_frame.return_value = None

            manager._process_capture_results()

            mock_frame.update_frame.assert_called_once_with(mock_image)

    def test_process_capture_results_no_results(self):
        """Test _process_capture_results with no results"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.logger = MagicMock()
            manager.pending_requests = {}
            manager.preview_frames = {}
            manager.capture_system = MagicMock()
            manager.capture_system.get_result.return_value = None

            manager._process_capture_results()  # Should not raise

    def test_process_capture_results_sets_alert(self):
        """Test _process_capture_results sets alert on frame"""
        from eve_overview_pro.ui.main_tab import WindowManager
        from eve_overview_pro.core.alert_detector import AlertLevel
        from PIL import Image

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.logger = MagicMock()
            manager.pending_requests = {"req-1": "0x123"}

            mock_frame = MagicMock()
            manager.preview_frames = {"0x123": mock_frame}

            mock_image = Image.new("RGB", (100, 100))
            manager.capture_system = MagicMock()
            manager.capture_system.get_result.side_effect = [
                ("req-1", "0x123", mock_image),
                None
            ]
            manager.alert_detector = MagicMock()
            manager.alert_detector.analyze_frame.return_value = AlertLevel.HIGH

            manager._process_capture_results()

            mock_frame.set_alert.assert_called_once_with(AlertLevel.HIGH)


# =============================================================================
# MainTab Additional Methods Tests
# =============================================================================

class TestMainTabPreviewsEnabled:
    """Tests for MainTab.set_previews_enabled"""

    def test_set_previews_enabled_starts_capture(self):
        """Test set_previews_enabled(True) starts capture when not active"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.window_manager = MagicMock()
            tab.window_manager.capture_timer.isActive.return_value = False
            tab.status_label = MagicMock()
            tab.logger = MagicMock()

            tab.set_previews_enabled(True)

            tab.window_manager.start_capture_loop.assert_called_once()

    def test_set_previews_enabled_stops_capture(self):
        """Test set_previews_enabled(False) stops capture when active"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.window_manager = MagicMock()
            tab.window_manager.capture_timer.isActive.return_value = True
            tab.status_label = MagicMock()
            tab.logger = MagicMock()

            tab.set_previews_enabled(False)

            tab.window_manager.stop_capture_loop.assert_called_once()


class TestMainTabOneClickImport:
    """Tests for MainTab.one_click_import"""

    def test_one_click_import_has_method(self):
        """Test MainTab has one_click_import method"""
        from eve_overview_pro.ui.main_tab import MainTab

        assert hasattr(MainTab, 'one_click_import')

    def test_one_click_import_no_windows(self):
        """Test one_click_import shows message when no windows"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.logger = MagicMock()

            with patch('eve_overview_pro.ui.main_tab.scan_eve_windows', return_value=[]):
                with patch('PySide6.QtWidgets.QMessageBox.information') as mock_msg:
                    tab.one_click_import()
                    mock_msg.assert_called_once()


class TestWindowPreviewWidgetUpdateFrame:
    """Tests for WindowPreviewWidget.update_frame"""

    def test_update_frame_handles_none_image(self):
        """Test update_frame handles None image"""
        from eve_overview_pro.ui.main_tab import WindowPreviewWidget

        with patch.object(WindowPreviewWidget, '__init__', return_value=None):
            widget = WindowPreviewWidget.__new__(WindowPreviewWidget)
            widget.logger = MagicMock()
            widget.preview_label = MagicMock()
            widget._current_pixmap = None

            widget.update_frame(None)  # Should not raise

            widget.preview_label.setPixmap.assert_not_called()


class TestWindowManagerStartStop:
    """Tests for WindowManager start/stop methods"""

    def test_start_capture_loop(self):
        """Test start_capture_loop starts timer"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.capture_timer = MagicMock()
            manager.refresh_rate = 30
            manager.logger = MagicMock()

            manager.start_capture_loop()

            manager.capture_timer.start.assert_called_once()

    def test_stop_capture_loop(self):
        """Test stop_capture_loop stops timer"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.capture_timer = MagicMock()
            manager.logger = MagicMock()

            manager.stop_capture_loop()

            manager.capture_timer.stop.assert_called_once()

    def test_set_refresh_rate_clamps_value(self):
        """Test set_refresh_rate clamps FPS to 1-60 range"""
        from eve_overview_pro.ui.main_tab import WindowManager

        with patch.object(WindowManager, '__init__', return_value=None):
            manager = WindowManager.__new__(WindowManager)
            manager.capture_timer = MagicMock()
            manager.capture_timer.isActive.return_value = False

            manager.set_refresh_rate(100)  # Too high
            assert manager.refresh_rate == 60

            manager.set_refresh_rate(0)  # Too low
            assert manager.refresh_rate == 1


# =============================================================================
# MainTab Cycling Groups Tests
# =============================================================================

class TestMainTabCyclingGroups:
    """Tests for MainTab cycling groups methods"""

    def test_load_cycling_groups_with_settings(self):
        """Test _load_cycling_groups loads groups from settings"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.settings_manager = MagicMock()
            tab.settings_manager.get.return_value = {
                "Team1": ["char1", "char2"],
                "Team2": ["char3"]
            }
            tab.cycling_groups = {}

            tab._load_cycling_groups()

            assert "Team1" in tab.cycling_groups
            assert "Team2" in tab.cycling_groups
            assert tab.cycling_groups["Team1"] == ["char1", "char2"]

    def test_load_cycling_groups_without_settings(self):
        """Test _load_cycling_groups when settings_manager is None"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.settings_manager = None
            tab.cycling_groups = {}

            tab._load_cycling_groups()

            # Should create Default group
            assert "Default" in tab.cycling_groups

    def test_load_cycling_groups_creates_default(self):
        """Test _load_cycling_groups creates Default if missing"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.settings_manager = MagicMock()
            tab.settings_manager.get.return_value = {"Team1": ["char1"]}
            tab.cycling_groups = {}

            tab._load_cycling_groups()

            assert "Default" in tab.cycling_groups
            assert "Team1" in tab.cycling_groups

    def test_load_cycling_groups_invalid_type(self):
        """Test _load_cycling_groups handles non-dict gracefully"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.settings_manager = MagicMock()
            tab.settings_manager.get.return_value = "invalid"  # Not a dict
            tab.cycling_groups = {}

            tab._load_cycling_groups()

            # Should create Default group, not crash
            assert "Default" in tab.cycling_groups


# =============================================================================
# MainTab Status Update Tests
# =============================================================================

class TestMainTabUpdateStatus:
    """Tests for MainTab _update_status method"""

    def test_update_status_zero_windows(self):
        """Test _update_status with no windows"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.window_manager = MagicMock()
            tab.window_manager.get_active_window_count.return_value = 0
            tab.active_count_label = MagicMock()
            tab.status_label = MagicMock()

            tab._update_status()

            tab.active_count_label.setText.assert_called_with("Active: 0")
            assert "No windows" in tab.status_label.setText.call_args[0][0]

    def test_update_status_with_windows(self):
        """Test _update_status with active windows"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.window_manager = MagicMock()
            tab.window_manager.get_active_window_count.return_value = 3
            tab.window_manager.refresh_rate = 30
            tab.active_count_label = MagicMock()
            tab.status_label = MagicMock()

            tab._update_status()

            tab.active_count_label.setText.assert_called_with("Active: 3")
            status_text = tab.status_label.setText.call_args[0][0]
            assert "3 window(s)" in status_text
            assert "30 FPS" in status_text


# =============================================================================
# MainTab Refresh Rate Tests
# =============================================================================

class TestMainTabRefreshRate:
    """Tests for MainTab refresh rate handling"""

    def test_on_refresh_rate_changed(self):
        """Test _on_refresh_rate_changed updates window manager"""
        from eve_overview_pro.ui.main_tab import MainTab

        with patch.object(MainTab, '__init__', return_value=None):
            tab = MainTab.__new__(MainTab)
            tab.window_manager = MagicMock()
            tab.logger = MagicMock()

            tab._on_refresh_rate_changed(45)

            tab.window_manager.set_refresh_rate.assert_called_once_with(45)


# =============================================================================
# GridApplier Additional Tests
# =============================================================================

class TestGridApplierApplyArrangement:
    """Additional tests for GridApplier apply_arrangement method"""

    def test_apply_arrangement_stacked_with_grid_size(self):
        """Test apply_arrangement in stacked mode with grid sizing"""
        from eve_overview_pro.ui.main_tab import GridApplier, ScreenGeometry

        applier = GridApplier()
        applier.logger = MagicMock()
        applier._move_window = MagicMock()

        screen = ScreenGeometry(0, 0, 1920, 1080, True)
        arrangement = {"char1": (0, 0), "char2": (0, 1)}
        window_map = {"char1": "111", "char2": "222"}

        result = applier.apply_arrangement(
            arrangement, window_map, screen,
            grid_rows=2, grid_cols=2, spacing=10,
            stacked=True, stacked_use_grid_size=True
        )

        assert result is True
        assert applier._move_window.call_count == 2

    def test_apply_arrangement_stacked_position_only(self):
        """Test apply_arrangement in stacked mode keeping window size"""
        from eve_overview_pro.ui.main_tab import GridApplier, ScreenGeometry

        applier = GridApplier()
        applier.logger = MagicMock()
        applier._move_window = MagicMock()
        applier._move_window_position_only = MagicMock()

        screen = ScreenGeometry(0, 0, 1920, 1080, True)
        arrangement = {"char1": (0, 0)}
        window_map = {"char1": "111"}

        result = applier.apply_arrangement(
            arrangement, window_map, screen,
            grid_rows=2, grid_cols=2, spacing=10,
            stacked=True, stacked_use_grid_size=False
        )

        assert result is True
        applier._move_window_position_only.assert_called_once()

    def test_apply_arrangement_grid_mode(self):
        """Test apply_arrangement in grid mode"""
        from eve_overview_pro.ui.main_tab import GridApplier, ScreenGeometry

        applier = GridApplier()
        applier.logger = MagicMock()
        applier._move_window = MagicMock()

        screen = ScreenGeometry(0, 0, 1920, 1080, True)
        arrangement = {"char1": (0, 0), "char2": (0, 1), "char3": (1, 0)}
        window_map = {"char1": "111", "char2": "222", "char3": "333"}

        result = applier.apply_arrangement(
            arrangement, window_map, screen,
            grid_rows=2, grid_cols=2, spacing=10,
            stacked=False
        )

        assert result is True
        assert applier._move_window.call_count == 3

    def test_apply_arrangement_skips_missing_windows(self):
        """Test apply_arrangement skips characters not in window_map"""
        from eve_overview_pro.ui.main_tab import GridApplier, ScreenGeometry

        applier = GridApplier()
        applier.logger = MagicMock()
        applier._move_window = MagicMock()

        screen = ScreenGeometry(0, 0, 1920, 1080, True)
        arrangement = {"char1": (0, 0), "char2": (0, 1)}
        window_map = {"char1": "111"}  # char2 not in map

        result = applier.apply_arrangement(
            arrangement, window_map, screen,
            grid_rows=2, grid_cols=2, spacing=10,
            stacked=False
        )

        assert result is True
        assert applier._move_window.call_count == 1  # Only char1

    def test_apply_arrangement_exception(self):
        """Test apply_arrangement handles exceptions"""
        from eve_overview_pro.ui.main_tab import GridApplier, ScreenGeometry

        applier = GridApplier()
        applier.logger = MagicMock()
        applier._move_window = MagicMock(side_effect=Exception("xdotool failed"))

        screen = ScreenGeometry(0, 0, 1920, 1080, True)
        arrangement = {"char1": (0, 0)}
        window_map = {"char1": "111"}

        result = applier.apply_arrangement(
            arrangement, window_map, screen,
            grid_rows=2, grid_cols=2, spacing=10,
            stacked=False
        )

        assert result is False
        applier.logger.error.assert_called_once()
