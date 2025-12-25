"""
Windows-specific Hotkey Manager
Uses Windows API RegisterHotKey instead of Linux hotkey libraries
"""
import logging
from typing import Dict, Callable, Optional
from PySide6.QtCore import QObject, Signal, QTimer
import win32con
import win32api
import win32gui


class HotkeyManager(QObject):
    """
    Global hotkey manager for Windows
    Uses Windows RegisterHotKey API
    """
    hotkey_triggered = Signal(str)  # hotkey_name

    # Modifier mapping
    MOD_MAP = {
        'ctrl': win32con.MOD_CONTROL,
        'alt': win32con.MOD_ALT,
        'shift': win32con.MOD_SHIFT,
        'win': win32con.MOD_WIN
    }

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.hotkeys: Dict[int, str] = {}  # hotkey_id -> name
        self.next_id = 1
        self.running = False
        self.hwnd = None

        # Timer to check for hotkey messages
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_messages)

    def start(self):
        """Start hotkey manager"""
        if self.running:
            return

        try:
            # Create invisible window for receiving hotkey messages
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._wnd_proc
            wc.lpszClassName = "EVEOverviewProHotkeys"
            wc.hInstance = win32api.GetModuleHandle(None)

            class_atom = win32gui.RegisterClass(wc)
            self.hwnd = win32gui.CreateWindow(
                class_atom, "EVE Overview Pro Hotkeys",
                0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
            )

            self.running = True
            self.timer.start(50)  # Check every 50ms
            self.logger.info("Hotkey manager started")

        except Exception as e:
            self.logger.error(f"Failed to start hotkey manager: {e}")

    def stop(self):
        """Stop hotkey manager and unregister all hotkeys"""
        if not self.running:
            return

        self.running = False
        self.timer.stop()

        # Unregister all hotkeys
        for hotkey_id in list(self.hotkeys.keys()):
            try:
                win32gui.UnregisterHotKey(self.hwnd, hotkey_id)
            except:
                pass

        if self.hwnd:
            try:
                win32gui.DestroyWindow(self.hwnd)
            except:
                pass
            self.hwnd = None

        self.hotkeys.clear()
        self.logger.info("Hotkey manager stopped")

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """Window procedure to handle hotkey messages"""
        if msg == win32con.WM_HOTKEY:
            hotkey_id = wparam
            if hotkey_id in self.hotkeys:
                hotkey_name = self.hotkeys[hotkey_id]
                self.hotkey_triggered.emit(hotkey_name)
                self.logger.debug(f"Hotkey triggered: {hotkey_name}")

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _check_messages(self):
        """Check for Windows messages (hotkey events)"""
        if not self.hwnd:
            return

        try:
            # Process pending messages
            if win32gui.PeekMessage(self.hwnd, 0, 0, win32con.PM_REMOVE):
                win32gui.TranslateMessage(msg)
                win32gui.DispatchMessage(msg)
        except:
            pass

    def register_hotkey(self, name: str, combo: str, callback: Optional[Callable] = None) -> bool:
        """
        Register a global hotkey

        Args:
            name: Hotkey name
            combo: Key combination (e.g., "<ctrl>+<alt>+1")
            callback: Optional callback function

        Returns:
            bool: Success
        """
        if not self.running or not self.hwnd:
            self.logger.warning("Hotkey manager not started")
            return False

        try:
            # Parse combo string
            modifiers, vk_code = self._parse_combo(combo)

            # Register hotkey
            hotkey_id = self.next_id
            self.next_id += 1

            success = win32gui.RegisterHotKey(self.hwnd, hotkey_id, modifiers, vk_code)

            if success:
                self.hotkeys[hotkey_id] = name
                if callback:
                    self.hotkey_triggered.connect(
                        lambda n: callback() if n == name else None
                    )
                self.logger.info(f"Registered hotkey: {name} = {combo}")
                return True
            else:
                self.logger.error(f"Failed to register hotkey: {name}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to register hotkey {name}: {e}")
            return False

    def unregister_hotkey(self, name: str) -> bool:
        """
        Unregister a hotkey

        Args:
            name: Hotkey name

        Returns:
            bool: Success
        """
        try:
            # Find hotkey ID by name
            hotkey_id = next((hid for hid, n in self.hotkeys.items() if n == name), None)

            if hotkey_id:
                win32gui.UnregisterHotKey(self.hwnd, hotkey_id)
                del self.hotkeys[hotkey_id]
                self.logger.info(f"Unregistered hotkey: {name}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to unregister hotkey {name}: {e}")
            return False

    def _parse_combo(self, combo: str) -> tuple:
        """
        Parse key combination string

        Args:
            combo: String like "<ctrl>+<alt>+1"

        Returns:
            Tuple of (modifiers, vk_code)
        """
        parts = combo.lower().replace('<', '').replace('>', '').split('+')

        modifiers = 0
        key = None

        for part in parts:
            part = part.strip()
            if part in self.MOD_MAP:
                modifiers |= self.MOD_MAP[part]
            else:
                key = part

        if not key:
            raise ValueError(f"No key specified in combo: {combo}")

        # Convert key to virtual key code
        vk_code = self._get_vk_code(key)

        return modifiers, vk_code

    def _get_vk_code(self, key: str) -> int:
        """
        Get Windows virtual key code for a key

        Args:
            key: Key string (e.g., "1", "f5", "a")

        Returns:
            Virtual key code
        """
        # Number keys
        if key.isdigit():
            return ord(key)

        # Letter keys
        if len(key) == 1 and key.isalpha():
            return ord(key.upper())

        # Function keys
        if key.startswith('f') and key[1:].isdigit():
            fn = int(key[1:])
            if 1 <= fn <= 24:
                return win32con.VK_F1 + fn - 1

        # Special keys
        special_keys = {
            'space': win32con.VK_SPACE,
            'enter': win32con.VK_RETURN,
            'tab': win32con.VK_TAB,
            'esc': win32con.VK_ESCAPE,
            'backspace': win32con.VK_BACK,
            'delete': win32con.VK_DELETE,
            'insert': win32con.VK_INSERT,
            'home': win32con.VK_HOME,
            'end': win32con.VK_END,
            'pageup': win32con.VK_PRIOR,
            'pagedown': win32con.VK_NEXT,
            'up': win32con.VK_UP,
            'down': win32con.VK_DOWN,
            'left': win32con.VK_LEFT,
            'right': win32con.VK_RIGHT,
        }

        if key in special_keys:
            return special_keys[key]

        raise ValueError(f"Unknown key: {key}")

    def get_registered_hotkeys(self) -> Dict[str, str]:
        """
        Get all registered hotkeys

        Returns:
            Dict mapping name to combo string
        """
        # This is a simplified version - we'd need to store combos
        return {name: "registered" for name in self.hotkeys.values()}
