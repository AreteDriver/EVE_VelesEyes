"""
Menu Builder - Constructs menus from the Action Registry

This module provides utilities to build Qt menus (QMenu, QAction) from the
centralized Action Registry, ensuring all menus are populated from a single
source of truth.
"""
import logging
from typing import Callable, Dict, List, Optional

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from eve_overview_pro.ui.action_registry import (
    ActionRegistry,
    ActionSpec,
    PrimaryHome,
)


class MenuBuilder:
    """
    Builds Qt menus from the Action Registry.

    Usage:
        builder = MenuBuilder(registry)
        tray_menu = builder.build_tray_menu(parent_widget, handlers)
    """

    def __init__(self, registry: Optional[ActionRegistry] = None):
        self.logger = logging.getLogger(__name__)
        self.registry = registry or ActionRegistry.get_instance()

    def build_menu(
        self,
        home: PrimaryHome,
        parent=None,
        handlers: Optional[Dict[str, Callable]] = None,
        menu: Optional[QMenu] = None,
    ) -> QMenu:
        """
        Build a QMenu from actions registered for a specific home.

        Args:
            home: PrimaryHome location to build menu for
            parent: Parent widget for the menu
            handlers: Dict mapping action_id -> handler callable
            menu: Optional existing menu to add to

        Returns:
            QMenu populated with actions
        """
        if menu is None:
            menu = QMenu(parent)

        handlers = handlers or {}
        actions = self.registry.get_by_home(home)

        for action_spec in actions:
            qt_action = self._create_action(action_spec, menu, handlers.get(action_spec.id))
            menu.addAction(qt_action)

        return menu

    def build_tray_menu(
        self,
        parent=None,
        handlers: Optional[Dict[str, Callable]] = None,
        profile_handler: Optional[Callable] = None,
        profiles: Optional[List[str]] = None,
        current_profile: Optional[str] = None,
    ) -> QMenu:
        """
        Build the system tray context menu.

        Args:
            parent: Parent widget
            handlers: Dict mapping action_id -> handler callable
            profile_handler: Callback for profile selection
            profiles: List of available profile names
            current_profile: Currently active profile name

        Returns:
            QMenu for system tray
        """
        menu = QMenu(parent)
        handlers = handlers or {}
        profiles = profiles or []

        # Get tray actions in specific order
        tray_actions = self.registry.get_by_home(PrimaryHome.TRAY_MENU)

        # Order: show_hide, toggle_thumbnails, separator, minimize_all, restore_all,
        #        separator, profiles, separator, settings, reload_config, separator, quit
        action_order = [
            "show_hide",
            "toggle_thumbnails",
            None,  # separator
            "minimize_all",
            "restore_all",
            None,  # separator
            "profiles",  # special: submenu
            None,  # separator
            "settings",
            "reload_config",
            None,  # separator
            "quit",
        ]

        for item in action_order:
            if item is None:
                menu.addSeparator()
            elif item == "profiles":
                # Add profiles submenu
                profiles_menu = menu.addMenu("Profiles")
                self._populate_profiles_menu(
                    profiles_menu,
                    profiles,
                    current_profile,
                    profile_handler
                )
            else:
                action_spec = self.registry.get(item)
                if action_spec:
                    qt_action = self._create_action(
                        action_spec,
                        menu,
                        handlers.get(item)
                    )
                    menu.addAction(qt_action)

        return menu

    def build_help_menu(
        self,
        parent=None,
        handlers: Optional[Dict[str, Callable]] = None,
    ) -> QMenu:
        """
        Build the Help menu for the menu bar.

        Args:
            parent: Parent widget
            handlers: Dict mapping action_id -> handler callable

        Returns:
            QMenu for Help menu
        """
        menu = QMenu("&Help", parent)
        handlers = handlers or {}

        # Order: about, separator, donate, separator, documentation, report_issue
        action_order = [
            "about",
            None,  # separator
            "donate",
            None,  # separator
            "documentation",
            "report_issue",
        ]

        for item in action_order:
            if item is None:
                menu.addSeparator()
            else:
                action_spec = self.registry.get(item)
                if action_spec:
                    qt_action = self._create_action(
                        action_spec,
                        menu,
                        handlers.get(item)
                    )
                    menu.addAction(qt_action)

        return menu

    def _create_action(
        self,
        spec: ActionSpec,
        parent=None,
        handler: Optional[Callable] = None,
    ) -> QAction:
        """
        Create a QAction from an ActionSpec.

        Args:
            spec: ActionSpec defining the action
            parent: Parent widget
            handler: Handler callable to connect

        Returns:
            QAction configured per spec
        """
        action = QAction(spec.label, parent)

        if spec.tooltip:
            action.setToolTip(spec.tooltip)

        if spec.shortcut:
            # Note: shortcut display only, actual hotkey via HotkeyManager
            action.setStatusTip(f"{spec.tooltip} ({spec.shortcut})")

        if spec.checkable:
            action.setCheckable(True)

        if handler:
            action.triggered.connect(handler)
        else:
            self.logger.debug(f"No handler provided for action: {spec.id}")

        return action

    def _populate_profiles_menu(
        self,
        menu: QMenu,
        profiles: List[str],
        current_profile: Optional[str],
        handler: Optional[Callable],
    ):
        """
        Populate profiles submenu.

        Args:
            menu: QMenu to populate
            profiles: List of profile names
            current_profile: Currently active profile
            handler: Callback(profile_name) for selection
        """
        menu.clear()

        if not profiles:
            no_profiles = QAction("(No profiles saved)", menu)
            no_profiles.setEnabled(False)
            menu.addAction(no_profiles)
            return

        for profile in profiles:
            action = QAction(profile, menu)
            action.setCheckable(True)
            action.setChecked(profile == current_profile)

            if handler:
                # Create closure to capture profile name
                def make_callback(p=profile):
                    return lambda: handler(p)
                action.triggered.connect(make_callback())

            menu.addAction(action)


def build_toolbar_actions(
    home: PrimaryHome,
    handlers: Optional[Dict[str, Callable]] = None,
    registry: Optional[ActionRegistry] = None,
) -> List[QAction]:
    """
    Build a list of QActions for a toolbar.

    Args:
        home: PrimaryHome location (must be a toolbar type)
        handlers: Dict mapping action_id -> handler callable
        registry: Optional ActionRegistry instance

    Returns:
        List of QActions for the toolbar
    """
    if registry is None:
        registry = ActionRegistry.get_instance()

    handlers = handlers or {}
    builder = MenuBuilder(registry)
    actions = registry.get_by_home(home)

    return [
        builder._create_action(spec, None, handlers.get(spec.id))
        for spec in actions
    ]
