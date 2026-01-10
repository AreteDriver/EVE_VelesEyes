"""Tests for main.py - SingleInstance and entry point"""

import tempfile
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestSingleInstance:
    """Tests for SingleInstance class"""

    def test_init_creates_directory(self):
        """Test that __init__ creates config directory"""
        from main import SingleInstance

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                instance = SingleInstance("test-app")

                expected_dir = Path(tmpdir) / ".config" / "argus-overview"
                assert expected_dir.exists()
                assert instance.lock_path == expected_dir / "test-app.lock"

    def test_try_lock_success(self):
        """Test successful lock acquisition"""
        from main import SingleInstance

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                instance = SingleInstance("test-app")
                result = instance.try_lock()

                assert result is True
                assert instance.lock_file is not None
                assert instance.lock_path.exists()

                # Clean up
                instance.release()

    def test_try_lock_fails_when_locked(self):
        """Test that second instance fails to acquire lock"""
        from main import SingleInstance

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                instance1 = SingleInstance("test-app")
                instance2 = SingleInstance("test-app")

                # First instance acquires lock
                assert instance1.try_lock() is True

                # Second instance should fail
                assert instance2.try_lock() is False

                # Clean up
                instance1.release()

    def test_release_unlocks(self):
        """Test that release properly unlocks"""
        from main import SingleInstance

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                instance1 = SingleInstance("test-app")
                instance2 = SingleInstance("test-app")

                # First instance acquires and releases
                assert instance1.try_lock() is True
                instance1.release()

                # Second instance should now succeed
                assert instance2.try_lock() is True
                instance2.release()

    def test_release_without_lock(self):
        """Test release when no lock held"""
        from main import SingleInstance

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                instance = SingleInstance("test-app")
                # Should not raise
                instance.release()
                assert instance.lock_file is None

    def test_release_handles_closed_file(self):
        """Test release handles already closed file"""
        from main import SingleInstance

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                instance = SingleInstance("test-app")
                instance.try_lock()

                # Close file manually
                instance.lock_file.close()

                # Release should handle this gracefully
                instance.release()
                assert instance.lock_file is None

    def test_context_manager_success(self):
        """Test using SingleInstance as context manager"""
        from main import SingleInstance

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                instance = SingleInstance("test-app")

                with instance as locked:
                    assert locked is True
                    assert instance.lock_file is not None

                # After context, lock should be released
                assert instance.lock_file is None

    def test_context_manager_already_locked(self):
        """Test context manager when already locked"""
        from main import SingleInstance

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                instance1 = SingleInstance("test-app")
                instance1.try_lock()

                instance2 = SingleInstance("test-app")
                with instance2 as locked:
                    assert locked is False

                instance1.release()

    def test_lock_writes_pid(self):
        """Test that lock file contains PID"""
        import os

        from main import SingleInstance

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                instance = SingleInstance("test-app")
                instance.try_lock()

                # Read the lock file
                with open(instance.lock_path) as f:
                    content = f.read()

                assert content == str(os.getpid())

                instance.release()


class TestSetupLogging:
    """Tests for setup_logging function"""

    def test_setup_logging_creates_directory(self):
        """Test that setup_logging creates log directory"""
        from main import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                setup_logging()

                log_dir = Path(tmpdir) / ".config" / "argus-overview"
                assert log_dir.exists()


class TestSetupDarkTheme:
    """Tests for setup_dark_theme function"""

    def test_setup_dark_theme(self):
        """Test that setup_dark_theme applies theme without error"""
        from main import setup_dark_theme

        mock_app = MagicMock()
        setup_dark_theme(mock_app)

        mock_app.setStyle.assert_called_once_with("Fusion")
        mock_app.setPalette.assert_called_once()
