"""
UI modules for Argus Overview

v2.4: Added ActionRegistry for UI action management
"""

from argus_overview.ui.action_registry import (
    ActionRegistry,
    ActionScope,
    ActionSpec,
    PrimaryHome,
    audit_actions,
    print_audit_report,
)
from argus_overview.ui.menu_builder import (
    ContextMenuBuilder,
    MenuBuilder,
    ToolbarBuilder,
    build_toolbar_actions,
)

__all__ = [
    "ActionRegistry",
    "ActionScope",
    "ActionSpec",
    "PrimaryHome",
    "ContextMenuBuilder",
    "MenuBuilder",
    "ToolbarBuilder",
    "audit_actions",
    "print_audit_report",
    "build_toolbar_actions",
]
