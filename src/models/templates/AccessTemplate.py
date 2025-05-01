# src/models/templates/AccessTemplate.py
"""Access port template configuration for multiple interfaces."""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AccessTemplate:
    """Template for configuring multiple Access ports."""
    interfaces: List[str] = field(default_factory=list)
    vlan_id: int = 1
    description: Optional[str] = None
    port_security_enabled: bool = False
    max_mac_addresses: int = 1
    violation_action: str = "shutdown"  # shutdown, restrict, protect
    voice_vlan: Optional[int] = None
    storm_control_broadcast_min: Optional[float] = None
    storm_control_broadcast_max: Optional[float] = None
    storm_control_multicast_min: Optional[float] = None
    storm_control_multicast_max: Optional[float] = None
    spanning_tree_portfast: bool = True
    sticky_mac: bool = False

    def generate_config(self) -> List[str]:
        """Generate Cisco-style configuration commands based on the template data."""
        config = []

        if not self.interfaces:
            return config

        # VLAN definition
        config.append(f"vlan {self.vlan_id}")
        if self.description:
            config.append(f" name {self.description}")
        config.append("!")  # end of VLAN block

        # Interface range configuration
        interface_range = ",".join(self.interfaces)
        config.append(f"interface range {interface_range}")
        config.append(" switchport mode access")
        config.append(f" switchport access vlan {self.vlan_id}")

        if self.description:
            config.append(f" description {self.description}")

        if self.voice_vlan:
            config.append(f" switchport voice vlan {self.voice_vlan}")

        if self.storm_control_broadcast_min is not None:
            line = f" storm-control broadcast level {self.storm_control_broadcast_min}"
            if self.storm_control_broadcast_max is not None:
                line += f" {self.storm_control_broadcast_max}"
            config.append(line)

        if self.storm_control_multicast_min is not None:
            line = f" storm-control multicast level {self.storm_control_multicast_min}"
            if self.storm_control_multicast_max is not None:
                line += f" {self.storm_control_multicast_max}"
            config.append(line)

        if self.spanning_tree_portfast:
            config.append(" spanning-tree portfast")

        if self.port_security_enabled:
            config.append(" switchport port-security")
            config.append(f" switchport port-security maximum {self.max_mac_addresses}")
            config.append(f" switchport port-security violation {self.violation_action}")
            if self.sticky_mac:
                config.append(" switchport port-security mac-address sticky")

        config.append("!")  # End of config block

        return config