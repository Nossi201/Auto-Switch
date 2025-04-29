# src/models/templates/AccessTemplate.py
"""Access port template configuration for multiple interfaces."""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AccessTemplate:
    """Template for configuring multiple Access ports."""
    interfaces: List[str] = field(default_factory=list)  # e.g., ["Gig1/0/1", "Gig1/0/2"]
    vlan_id: int = 1
    description: Optional[str] = None
    port_security_enabled: bool = False
    max_mac_addresses: int = 1
    violation_action: str = "shutdown"  # shutdown, restrict, protect
    voice_vlan: Optional[int] = None
    storm_control_broadcast: Optional[float] = None  # e.g., 0.5%
    spanning_tree_portfast: bool = True
