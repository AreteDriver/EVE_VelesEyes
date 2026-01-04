"""Tests for HotkeyEdit widget."""

import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication

from eve_overview_pro.ui.hotkey_edit import HotkeyEdit


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestHotkeyEditInit:
    """Tests for HotkeyEdit initialization."""

    def test_init_creates_widgets(self, qapp):
        """Test that init creates display and buttons."""
        widget = HotkeyEdit()
        assert widget.display is not None
        assert widget.record_btn is not None
        assert widget.clear_btn is not None

    def test_init_display_is_readonly(self, qapp):
        """Test that display is read-only."""
        widget = HotkeyEdit()
        assert widget.display.isReadOnly()

    def test_init_hotkey_empty(self, qapp):
        """Test that initial hotkey is empty."""
        widget = HotkeyEdit()
        assert widget.text() == ""


class TestHotkeyEditText:
    """Tests for text get/set methods."""

    def test_set_text(self, qapp):
        """Test setting hotkey text."""
        widget = HotkeyEdit()
        widget.setText("<ctrl>+<f13>")
        assert widget.text() == "<ctrl>+<f13>"
        assert widget.display.text() == "<ctrl>+<f13>"

    def test_get_text_returns_hotkey(self, qapp):
        """Test getting hotkey text."""
        widget = HotkeyEdit()
        widget._hotkey = "<alt>+<f14>"
        assert widget.text() == "<alt>+<f14>"


class TestHotkeyEditClear:
    """Tests for clear functionality."""

    def test_clear_hotkey(self, qapp):
        """Test clearing the hotkey."""
        widget = HotkeyEdit()
        widget.setText("<ctrl>+a")
        widget._clear_hotkey()
        assert widget.text() == ""
        assert widget.display.text() == ""


class TestHotkeyEditRecording:
    """Tests for recording functionality."""

    def test_start_recording_changes_button_text(self, qapp):
        """Test that start recording changes button."""
        widget = HotkeyEdit()
        widget._start_recording()
        assert "Press" in widget.record_btn.text()
        widget._stop_recording()

    def test_stop_recording_restores_button(self, qapp):
        """Test that stop recording restores button."""
        widget = HotkeyEdit()
        widget._start_recording()
        widget._stop_recording()
        assert widget.record_btn.text() == "Record"

    def test_toggle_recording_starts_then_stops(self, qapp):
        """Test toggle behavior."""
        widget = HotkeyEdit()
        assert not widget._recording

        widget._toggle_recording()
        assert widget._recording

        widget._toggle_recording()
        assert not widget._recording


class TestHotkeyEditKeyConversion:
    """Tests for key-to-string conversion."""

    def test_key_to_string_modifier_ctrl(self, qapp):
        """Test ctrl key conversion."""
        widget = HotkeyEdit()
        try:
            from pynput import keyboard
            result = widget._key_to_string(keyboard.Key.ctrl)
            assert result == "ctrl"
        except ImportError:
            pytest.skip("pynput not available")

    def test_key_to_string_modifier_shift(self, qapp):
        """Test shift key conversion."""
        widget = HotkeyEdit()
        try:
            from pynput import keyboard
            result = widget._key_to_string(keyboard.Key.shift)
            assert result == "shift"
        except ImportError:
            pytest.skip("pynput not available")

    def test_key_to_string_function_key(self, qapp):
        """Test function key conversion."""
        widget = HotkeyEdit()
        try:
            from pynput import keyboard
            result = widget._key_to_string(keyboard.Key.f13)
            assert result == "f13"
        except ImportError:
            pytest.skip("pynput not available")


class TestHotkeyEditFinalize:
    """Tests for hotkey finalization."""

    def test_finalize_hotkey_single_key(self, qapp):
        """Test finalizing a single key."""
        widget = HotkeyEdit()
        widget._pressed_keys = {"f13"}
        widget._recording = True
        widget._finalize_hotkey()
        assert widget.text() == "<f13>"

    def test_finalize_hotkey_with_modifier(self, qapp):
        """Test finalizing a combo with modifier."""
        widget = HotkeyEdit()
        widget._pressed_keys = {"ctrl", "f13"}
        widget._recording = True
        widget._finalize_hotkey()
        # Modifiers should come first
        assert "ctrl" in widget.text()
        assert "f13" in widget.text()

    def test_finalize_emits_signal(self, qapp):
        """Test that finalize emits hotkeyChanged signal."""
        widget = HotkeyEdit()
        signal_received = []
        widget.hotkeyChanged.connect(lambda x: signal_received.append(x))

        widget._pressed_keys = {"f14"}
        widget._recording = True
        widget._finalize_hotkey()

        assert len(signal_received) == 1
        assert "<f14>" in signal_received[0]


class TestHotkeyEditUpdateDisplay:
    """Tests for display updates."""

    def test_update_display_modifiers_first(self, qapp):
        """Test that modifiers appear before other keys."""
        widget = HotkeyEdit()
        widget._pressed_keys = {"a", "ctrl", "shift"}
        widget._update_display()

        text = widget.display.text()
        ctrl_pos = text.find("ctrl")
        shift_pos = text.find("shift")
        a_pos = text.find("<a>")

        # Modifiers should come before 'a'
        assert ctrl_pos < a_pos
        assert shift_pos < a_pos
