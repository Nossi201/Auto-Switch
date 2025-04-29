# src/models/templates/RouterTemplate.py
"""Router template with general configuration."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class RouterTemplate:
    """Template representing a router's configuration."""
    hostname: str
    interfaces: Dict[str, Dict[str, str]] = field(default_factory=dict)  # {interface: {ip: "x.x.x.x", mask: "255.255.255.0"}}
    routing_protocols: List[str] = field(default_factory=list)  # ["OSPF", "BGP"]
    static_routes: List[Dict[str, str]] = field(default_factory=list)  # {destination: "x.x.x.x", next_hop: "x.x.x.x"}
    acl_entries: List[Dict[str, str]] = field(default_factory=list)  # {name: "ACL_NAME", rule: "permit ip any any"}
