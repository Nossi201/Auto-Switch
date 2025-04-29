# src/models/templates/TrunkTemplate.py
"""Trunk port template configuration for multiple interfaces."""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TrunkTemplate:
    """Template for configuring multiple Trunk ports."""
    interfaces: List[str] = field(default_factory=list)  # e.g., ["Gig1/0/23", "Gig1/0/24"]
    allowed_vlans: List[int] = field(default_factory=list)
    native_vlan: int = 1
    description: Optional[str] = None
    pruning_enabled: bool = False
    spanning_tree_guard_root: bool = False
    encapsulation: str = "dot1q"  # dot1q or isl
