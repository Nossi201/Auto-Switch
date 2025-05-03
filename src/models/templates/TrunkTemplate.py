"""Full-featured *trunk-port* template dataclass.

Implements every option available to AccessTemplate, adapted for trunk links:

* VLAN handling (allowed/native, pruning)
* Encapsulation, DTP, nonegotiate, STP PortFast
* Root-Guard, DHCP-snooping trust, QoS trust
* Storm-Control (broadcast / multicast / unknown-unicast, % or PPS)
* EtherChannel (channel-group, mode)
* Speed / duplex / auto-MDIX
* Errdisable timeout
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TrunkTemplate:
    """Blueprint for configuring multiple trunk interfaces."""
    # ------------- BASIC ------------- #
    interfaces: List[str] = field(default_factory=list)
    description: Optional[str] = None

    allowed_vlans: List[int] = field(default_factory=list)
    native_vlan: int = 1
    pruning_enabled: bool = False

    encapsulation: str = "dot1q"          # dot1q | isl
    dtp_mode: Optional[str] = None        # auto | desirable
    nonegotiate: bool = False
    spanning_tree_portfast: bool = False

    # ------------- SECURITY ---------- #
    spanning_tree_guard_root: bool = False
    dhcp_snooping_trust: bool = False
    qos_trust: Optional[str] = None       # cos | dscp

    # ------------- STORM-CONTROL ----- #
    storm_control_broadcast_min: Optional[float] = None
    storm_control_broadcast_max: Optional[float] = None
    storm_control_multicast_min: Optional[float] = None
    storm_control_multicast_max: Optional[float] = None
    storm_control_unknown_unicast_min: Optional[float] = None
    storm_control_unknown_unicast_max: Optional[float] = None
    storm_control_unit_pps: bool = False

    # ------------- L1 / TIMER -------- #
    speed: str = "auto"                   # auto | 10 | 100 | 1000
    duplex: str = "auto"                  # auto | half | full
    auto_mdix: bool = False
    errdisable_timeout: Optional[int] = None

    # ------------- ETHERCHANNEL ----- #
    channel_group: Optional[int] = None
    channel_group_mode: Optional[str] = None   # on | active | passive

    # ------------------------------------------------------------------ #
    def _fmt_storm_line(self, traffic: str,
                        mn: Optional[float],
                        mx: Optional[float]) -> Optional[str]:
        if mn is None:
            return None
        unit = " pps" if self.storm_control_unit_pps else ""
        line = f" storm-control {traffic} level {mn}"
        if mx is not None:
            line += f" {mx}"
        return line + unit

    # ------------------------------------------------------------------ #
    def _format_allowed_vlans(self) -> str:
        """Return CSV list with native VLAN forced as last token."""
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
        ranges.append(str(self.native_vlan))
        return ",".join(ranges) if ranges else str(self.native_vlan)

    # ------------------------------------------------------------------ #
    def generate_config(self) -> List[str]:
        """Return Cisco IOS CLI commands for the trunk template."""
        if not self.interfaces:
            return []

        cfg: List[str] = [f"interface range {','.join(self.interfaces)}",
                          " switchport mode trunk",
                          f" switchport trunk native vlan {self.native_vlan}",
                          f" switchport trunk allowed vlan {self._format_allowed_vlans()}"]

        if self.description:
            cfg.append(f" description {self.description}")

        # Encapsulation & DTP
        if self.encapsulation == "isl":
            cfg.append(" switchport trunk encapsulation isl")
        if self.dtp_mode:
            cfg.append(f" switchport trunk {self.dtp_mode}")
        if self.nonegotiate:
            cfg.append(" switchport nonegotiate")

        # STP / guards
        if self.spanning_tree_portfast:
            cfg.append(" spanning-tree portfast")
        if self.spanning_tree_guard_root:
            cfg.append(" spanning-tree guard root")

        # Pruning
        if self.pruning_enabled:
            cfg.append(" switchport trunk pruning vlan all")

        # Trusts
        if self.dhcp_snooping_trust:
            cfg.append(" ip dhcp snooping trust")
        if self.qos_trust in {"cos", "dscp"}:
            cfg.append(f" mls qos trust {self.qos_trust}")

        # Storm-Control
        for t, mn, mx in (
            ("broadcast", self.storm_control_broadcast_min, self.storm_control_broadcast_max),
            ("multicast", self.storm_control_multicast_min, self.storm_control_multicast_max),
            ("unknown-unicast", self.storm_control_unknown_unicast_min, self.storm_control_unknown_unicast_max),
        ):
            line = self._fmt_storm_line(t, mn, mx)
            if line:
                cfg.append(line)

        # Layer-1
        if self.speed != "auto":
            cfg.append(f" speed {self.speed}")
        if self.duplex != "auto":
            cfg.append(f" duplex {self.duplex}")
        if self.auto_mdix:
            cfg.append(" mdix auto")

        # Errdisable
        if self.errdisable_timeout:
            cfg.append(f" errdisable timeout {self.errdisable_timeout}")

        # EtherChannel
        if self.channel_group:
            mode = f" mode {self.channel_group_mode}" if self.channel_group_mode else ""
            cfg.append(f" channel-group {self.channel_group}{mode}")

        cfg.append(" exit")  # end interface block
        return cfg
