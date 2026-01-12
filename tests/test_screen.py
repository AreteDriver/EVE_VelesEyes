"""
Unit tests for screen geometry utilities
Tests get_screen_geometry and get_all_monitors functions
"""

from unittest.mock import MagicMock, patch

from eve_overview_pro.utils.screen import ScreenGeometry, get_all_monitors, get_screen_geometry


class TestScreenGeometry:
    """Tests for ScreenGeometry dataclass"""

    def test_screen_geometry_defaults(self):
        """Test ScreenGeometry with default is_primary"""
        geom = ScreenGeometry(0, 0, 1920, 1080)
        assert geom.x == 0
        assert geom.y == 0
        assert geom.width == 1920
        assert geom.height == 1080
        assert geom.is_primary is False

    def test_screen_geometry_with_primary(self):
        """Test ScreenGeometry with is_primary=True"""
        geom = ScreenGeometry(100, 200, 2560, 1440, True)
        assert geom.x == 100
        assert geom.y == 200
        assert geom.width == 2560
        assert geom.height == 1440
        assert geom.is_primary is True


class TestGetScreenGeometry:
    """Tests for get_screen_geometry function"""

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_screen_geometry_single_monitor(self, mock_run):
        """Test with single monitor output"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="eDP-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 344mm x 194mm\n",
        )

        geom = get_screen_geometry(0)

        assert geom.width == 1920
        assert geom.height == 1080
        assert geom.x == 0
        assert geom.y == 0
        assert geom.is_primary is True

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_screen_geometry_multi_monitor(self, mock_run):
        """Test with multiple monitors"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "eDP-1 connected primary 1920x1080+0+0\n"
                "HDMI-1 connected 2560x1440+1920+0\n"
                "DP-1 connected 1920x1200+4480+0\n"
            ),
        )

        # First monitor
        geom0 = get_screen_geometry(0)
        assert geom0.width == 1920
        assert geom0.height == 1080
        assert geom0.is_primary is True

        # Second monitor
        geom1 = get_screen_geometry(1)
        assert geom1.width == 2560
        assert geom1.height == 1440
        assert geom1.x == 1920
        assert geom1.is_primary is False

        # Third monitor
        geom2 = get_screen_geometry(2)
        assert geom2.width == 1920
        assert geom2.height == 1200
        assert geom2.x == 4480

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_screen_geometry_out_of_range_index(self, mock_run):
        """Test with monitor index out of range returns first monitor"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="eDP-1 connected primary 1920x1080+0+0\n",
        )

        geom = get_screen_geometry(5)  # Out of range

        assert geom.width == 1920
        assert geom.height == 1080

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_screen_geometry_xrandr_failure(self, mock_run):
        """Test xrandr command failure returns default"""
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        geom = get_screen_geometry()

        assert geom.width == 1920
        assert geom.height == 1080
        assert geom.is_primary is True

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_screen_geometry_no_geometry_in_output(self, mock_run):
        """Test xrandr output with no parseable geometry"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="eDP-1 connected (no geometry info)\n",
        )

        geom = get_screen_geometry()

        assert geom.width == 1920
        assert geom.height == 1080

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_screen_geometry_exception(self, mock_run):
        """Test exception handling returns default"""
        mock_run.side_effect = Exception("xrandr not found")

        geom = get_screen_geometry()

        assert geom.width == 1920
        assert geom.height == 1080
        assert geom.is_primary is True

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_screen_geometry_timeout(self, mock_run):
        """Test timeout exception returns default"""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="xrandr", timeout=5)

        geom = get_screen_geometry()

        assert geom.width == 1920
        assert geom.height == 1080


class TestGetAllMonitors:
    """Tests for get_all_monitors function"""

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_all_monitors_single(self, mock_run):
        """Test with single monitor"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="eDP-1 connected primary 1920x1080+0+0\n",
        )

        monitors = get_all_monitors()

        assert len(monitors) == 1
        assert monitors[0].width == 1920
        assert monitors[0].height == 1080
        assert monitors[0].is_primary is True

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_all_monitors_multiple(self, mock_run):
        """Test with multiple monitors"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "eDP-1 connected primary 1920x1080+0+0\n"
                "HDMI-1 connected 2560x1440+1920+0\n"
                "DP-1 connected 3840x2160+4480+0\n"
            ),
        )

        monitors = get_all_monitors()

        assert len(monitors) == 3
        assert monitors[0].width == 1920
        assert monitors[0].is_primary is True
        assert monitors[1].width == 2560
        assert monitors[1].x == 1920
        assert monitors[2].width == 3840
        assert monitors[2].x == 4480

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_all_monitors_xrandr_failure(self, mock_run):
        """Test xrandr failure returns default single monitor"""
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        monitors = get_all_monitors()

        assert len(monitors) == 1
        assert monitors[0].width == 1920
        assert monitors[0].height == 1080
        assert monitors[0].is_primary is True

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_all_monitors_no_geometry(self, mock_run):
        """Test no parseable geometry returns default"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="eDP-1 connected (no geometry)\nHDMI-1 disconnected\n",
        )

        monitors = get_all_monitors()

        assert len(monitors) == 1
        assert monitors[0].width == 1920
        assert monitors[0].height == 1080

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_all_monitors_exception(self, mock_run):
        """Test exception returns default single monitor"""
        mock_run.side_effect = Exception("xrandr crashed")

        monitors = get_all_monitors()

        assert len(monitors) == 1
        assert monitors[0].width == 1920
        assert monitors[0].height == 1080
        assert monitors[0].is_primary is True

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_all_monitors_timeout(self, mock_run):
        """Test timeout returns default"""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="xrandr", timeout=5)

        monitors = get_all_monitors()

        assert len(monitors) == 1
        assert monitors[0].width == 1920

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_all_monitors_disconnected_ignored(self, mock_run):
        """Test disconnected monitors are ignored"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "eDP-1 connected primary 1920x1080+0+0\n"
                "HDMI-1 disconnected\n"
                "DP-1 disconnected (normal left inverted right x axis y axis)\n"
            ),
        )

        monitors = get_all_monitors()

        assert len(monitors) == 1
        assert monitors[0].width == 1920

    @patch("eve_overview_pro.utils.screen.subprocess.run")
    def test_get_all_monitors_vertical_stacking(self, mock_run):
        """Test monitors stacked vertically"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=("eDP-1 connected primary 1920x1080+0+0\nHDMI-1 connected 1920x1080+0+1080\n"),
        )

        monitors = get_all_monitors()

        assert len(monitors) == 2
        assert monitors[0].y == 0
        assert monitors[1].y == 1080
