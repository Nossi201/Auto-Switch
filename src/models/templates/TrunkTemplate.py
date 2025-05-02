#src/models/templates/TrunkTemplate.py
"""Trunk port template dataclass.

Provides all attributes needed to build a Cisco IOS trunk configuration and
the *generate_config()* helper that returns a list of CLI commands.  Implements:
* forced trunk mode with optional dynamic DTP or nonegotiate
* 802.1Q / ISL encapsulation
* pruning, native‐VLAN auto-append, STP features
* optional security, storm-control and EtherChannel parameters
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TrunkTemplate:
    """Template for configuring multiple Trunk ports."""
    # Basic
    interfaces: List[str] = field(default_factory=list)
    description: Optional[str] = None

    # VLAN handling
    allowed_vlans: List[int] = field(default_factory=list)
    native_vlan: int = 1
    pruning_enabled: bool = False

    # Encapsulation / DTP
    encapsulation: str = "dot1q"            # valid: "dot1q" | "isl"
    dtp_mode: Optional[str] = None          # "auto" | "desirable"
    nonegotiate: bool = False               # disable DTP frames

    # STP
    spanning_tree_portfast: bool = False
    spanning_tree_guard_root: bool = False

    # Security / QoS
    dhcp_snooping_trust: bool = False
    qos_trust: Optional[str] = None         # "dscp" | "cos"
    port_security_enabled: bool = False

    # Storm-control
    storm_control_broadcast_min: Optional[float] = None
    storm_control_broadcast_max: Optional[float] = None
    storm_control_multicast_min: Optional[float] = None
    storm_control_multicast_max: Optional[float] = None

    # EtherChannel
    channel_group: Optional[int] = None
    channel_group_mode: Optional[str] = None  # "on" | "active" | "passive"

    # ------------------------------------------------------------------ #
    def _format_allowed_vlans(self) -> str:
        """
        Return CSV string with *native_vlan* forced as the final element.
        Duplicate values are removed, contiguous sequences are compacted.
        """
        core = sorted({v for v in self.allowed_vlans if v != self.native_vlan})
        ranges: List[str] = []
        if core:
            start = prev = core[0]
            for vid in core[1:]:
                if vid == prev + 1:
                    prev = vid
                else:
                    ranges.append(f"{start}-{prev}" if start != prev else str(start))
                    start = prev = vid
            ranges.append(f"{start}-{prev}" if start != prev else str(start))

        # Always append native VLAN as last token
        ranges.append(str(self.native_vlan))
        return ",".join(ranges) if ranges else str(self.native_vlan)

    # ------------------------------------------------------------------ #
    def generate_config(self) -> List[str]:
        """Generate full Cisco IOS configuration lines for this trunk."""
        if not self.interfaces:
            return []

        cfg: List[str] = []
        cfg.append(f"interface range {','.join(self.interfaces)}")

        if self.description:
            cfg.append(f" description {self.description}")

        # Encapsulation & trunk mode
        cfg.append(f" switchport trunk encapsulation {self.encapsulation}")
        if self.dtp_mode in {"auto", "desirable"}:
            cfg.append(f" switchport mode dynamic {self.dtp_mode}")
        else:
            cfg.append(" switchport mode trunk")

        if self.nonegotiate:
            cfg.append(" switchport nonegotiate")

        # VLAN list & native VLAN
        cfg.append(f" switchport trunk allowed vlan {self._format_allowed_vlans()}")
        if self.native_vlan != 1:
            cfg.append(f" switchport trunk native vlan {self.native_vlan}")

        if self.pruning_enabled:
            cfg.append(" switchport trunk pruning vlan all")

        # STP tuning
        if self.spanning_tree_portfast:
            cfg.append(" spanning-tree portfast trunk")
        if self.spanning_tree_guard_root:
            cfg.append(" spanning-tree guard root")

        # Security & QoS
        if self.dhcp_snooping_trust:
            cfg.append(" ip dhcp snooping trust")
        if self.qos_trust in {"dscp", "cos"}:
            cfg.append(f" mls qos trust {self.qos_trust}")
        if self.port_security_enabled:
            cfg.append(" switchport port-security")
            cfg.append(" switchport port-security trunk")

        # Storm-control
        if self.storm_control_broadcast_min is not None:
            line = f" storm-control broadcast level {self.storm_control_broadcast_min}"
            if self.storm_control_broadcast_max is not None:
                line += f" {self.storm_control_broadcast_max}"
            cfg.append(line)

        if self.storm_control_multicast_min is not None:
            line = f" storm-control multicast level {self.storm_control_multicast_min}"
            if self.storm_control_multicast_max is not None:
                line += f" {self.storm_control_multicast_max}"
            cfg.append(line)

        # EtherChannel
        if self.channel_group:
            mode = self.channel_group_mode or "on"
            cfg.append(f" channel-group {self.channel_group} mode {mode}")

        cfg.append("!")
        return cfg
