# src/models/templates/SwitchTemplate.py
"""Switch template with general configuration."""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class SwitchTemplate:
    """Template representing a switch's configuration."""
    hostname: str
    vlan_list: List[Dict[str, str]] = field(default_factory=list)  # {id: "10", name: "Users"}
    access_templates: List[str] = field(default_factory=list)  # references to AccessTemplate instances
    trunk_templates: List[str] = field(default_factory=list)  # references to TrunkTemplate instances
    spanning_tree_mode: str = "pvst"  # pvst, rapid-pvst, mst
