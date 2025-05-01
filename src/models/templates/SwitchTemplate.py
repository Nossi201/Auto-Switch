# src/models/templates/SwitchTemplate.py
"""Switch template with general configuration."""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class SwitchTemplate:
    """Template representing a switch's configuration."""
    hostname: str
    vlan_list: List[int] = field(default_factory=lambda: [1])  # allowed VLAN IDs
    spanning_tree_mode: str = "pvst"  # pvst | rapid-pvst | mst
    manager_vlan_id: int = 1  # management SVI VLAN
    manager_ip: str = "192.168.1.1"  # IP on the management SVI
    default_gateway: str = "192.168.1.254"
