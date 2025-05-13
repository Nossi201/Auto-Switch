# src/models/templates/TrunkTemplate.py
"""Enhanced dataclass for trunk-port template with comprehensive feature-set.

Implements all available trunk port configuration options in Cisco IOS/IOS-XE:
* VLAN handling (allowed/native/pruning)
* Encapsulation (dot1q/isl), DTP modes, auto-negotiation
* Spanning Tree features (PortFast trunk, Loop/Root guards)
* QoS (trust, priority queue, shaping, policing)
* Storm-Control for all traffic types
* EtherChannel with full mode support
* Layer 1 features (speed, duplex, mdix, energy efficiency)
* Security features (DHCP snooping trust, ARP inspection)
* Monitoring and error recovery
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Union
from enum import Enum


class EncapsulationType(str, Enum):
    """Trunk encapsulation types."""
    DOT1Q = "dot1q"
    ISL = "isl"


class DTPMode(str, Enum):
    """Dynamic Trunking Protocol modes."""
    AUTO = "auto"
    DESIRABLE = "desirable"
    ON = "on"
    NONEGOTIATE = "nonegotiate"


class ChannelMode(str, Enum):
    """EtherChannel modes."""
    ON = "on"
    ACTIVE = "active"  # LACP
    PASSIVE = "passive"  # LACP
    AUTO = "auto"  # PAgP
    DESIRABLE = "desirable"  # PAgP


class QoSTrustState(str, Enum):
    """QoS trust states."""
    NONE = "none"
    COS = "cos"
    DSCP = "dscp"


@dataclass
class TrunkTemplate:
    """Comprehensive blueprint for configuring trunk interfaces."""
    # ------------- Basic Configuration ------------- #
    interfaces: List[str] = field(default_factory=list)
    description: Optional[str] = None

    # ------------- VLAN Configuration ------------- #
    allowed_vlans: List[int] = field(default_factory=list)
    native_vlan: int = 1
    pruning_enabled: bool = False
    pruning_vlans: List[int] = field(default_factory=list)  # Empty = all

    # ------------- Trunk Protocol ----------------- #
    encapsulation: EncapsulationType = EncapsulationType.DOT1Q
    dtp_mode: Optional[DTPMode] = None
    nonegotiate: bool = False

    # ------------- Spanning Tree ----------------- #
    spanning_tree_portfast: bool = False  # PortFast (trunk)
    spanning_tree_guard_root: bool = False
    spanning_tree_guard_loop: bool = False
    spanning_tree_link_type: Optional[str] = None  # point-to-point | shared
    bpdu_filter_enable: bool = False

    # ------------- Security Features ------------- #
    dhcp_snooping_trust: bool = False
    dhcp_snooping_rate_limit: Optional[int] = None  # Packets per second
    arp_inspection_trust: bool = False
    arp_inspection_rate_limit: Optional[int] = None  # Packets per second
    ip_source_guard: bool = False
    ipv6_source_guard: bool = False
    ipv6_ra_guard: bool = False

    # ------------- QoS Features ----------------- #
    qos_trust: Optional[QoSTrustState] = None
    priority_queue_out: bool = False
    service_policy_input: Optional[str] = None
    service_policy_output: Optional[str] = None
    shape_average: Optional[int] = None  # Rate in bps
    police_rate: Optional[int] = None  # Rate in bps
    police_burst: Optional[int] = None  # Burst in bytes

    # ------------- Storm Control ---------------- #
    storm_control_broadcast_min: Optional[float] = None
    storm_control_broadcast_max: Optional[float] = None
    storm_control_multicast_min: Optional[float] = None
    storm_control_multicast_max: Optional[float] = None
    storm_control_unknown_unicast_min: Optional[float] = None
    storm_control_unknown_unicast_max: Optional[float] = None
    storm_control_unit_pps: bool = False  # False → percent, True → pps
    storm_control_action: Optional[str] = None  # shutdown | trap

    # ------------- Layer 1 Settings ------------- #
    speed: str = "auto"  # auto | 10 | 100 | 1000 | 10000
    duplex: str = "auto"  # auto | half | full
    auto_mdix: bool = False
    flow_control_receive: bool = False
    flow_control_send: bool = False
    energy_efficient_ethernet: bool = False

    # ------------- Error Recovery -------------- #
    errdisable_timeout: Optional[int] = None  # Seconds
    errdisable_recovery_cause: List[str] = field(default_factory=list)

    # ------------- EtherChannel --------------- #
    channel_group: Optional[int] = None  # Group number (0 means disabled)
    channel_group_mode: Optional[ChannelMode] = None
    channel_protocol: Optional[str] = None  # lacp | pagp
    lacp_port_priority: Optional[int] = None
    lacp_rate: Optional[str] = None  # normal | fast

    # ------------- CDP/LLDP ------------------ #
    cdp_enabled: bool = True
    lldp_transmit: bool = True
    lldp_receive: bool = True

    # ------------- Load Balancing ------------ #
    port_channel_load_balance: Optional[str] = None  # src-ip, dst-mac, etc.

    # ------------- Misc Settings ------------- #
    load_interval: int = 300  # Load interval for statistics
    udld_enable: bool = False
    udld_aggressive: bool = False

    # ------------------------------------------------------------------ #
    def _fmt_storm_line(self, traffic: str,
                        mn: Optional[float],
                        mx: Optional[float]) -> Optional[str]:
        """Format storm control command line."""
        if mn is None:
            return None
        unit = " pps" if self.storm_control_unit_pps else ""
        line = f" storm-control {traffic} level {mn}"
        if mx is not None:
            line += f" {mx}"
        return line + unit

    # ------------------------------------------------------------------ #
    def _format_vlan_range(self, vlan_list: List[int]) -> str:
        """Convert a list of VLAN IDs to a condensed range format."""
        if not vlan_list:
            return "1-4094"  # Default to all VLANs

        sorted_vlans = sorted(set(vlan_list))
        ranges = []
        start = sorted_vlans[0]
        end = start

        for vlan in sorted_vlans[1:]:
            if vlan == end + 1:
                end = vlan
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = end = vlan

        # Add the last range
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")

        return ",".join(ranges)

    # ------------------------------------------------------------------ #
    def generate_config(self) -> List[str]:
        """Return Cisco IOS CLI commands for the trunk template."""
        if not self.interfaces:
            return []

        cfg: List[str] = []

        # Interface range
        iface_range = ",".join(self.interfaces)
        cfg.append(f"interface range {iface_range}")

        # Basic configuration
        cfg.append(" switchport mode trunk")
        cfg.append(f" switchport trunk native vlan {self.native_vlan}")

        allowed_vlans = self._format_vlan_range(self.allowed_vlans)
        cfg.append(f" switchport trunk allowed vlan {allowed_vlans}")

        if self.description:
            cfg.append(f" description {self.description}")

        # Encapsulation & DTP
        if self.encapsulation == EncapsulationType.ISL:
            cfg.append(" switchport trunk encapsulation isl")
        else:
            cfg.append(" switchport trunk encapsulation dot1q")

        if self.dtp_mode and not self.nonegotiate:
            cfg.append(f" switchport mode {self.dtp_mode.value}")

        if self.nonegotiate:
            cfg.append(" switchport nonegotiate")

        # Pruning
        if self.pruning_enabled:
            pruning_vlans = self._format_vlan_range(self.pruning_vlans)
            cfg.append(f" switchport trunk pruning vlan {pruning_vlans}")

        # Spanning Tree
        if self.spanning_tree_portfast:
            cfg.append(" spanning-tree portfast trunk")

        if self.spanning_tree_guard_root:
            cfg.append(" spanning-tree guard root")

        if self.spanning_tree_guard_loop:
            cfg.append(" spanning-tree guard loop")

        if self.spanning_tree_link_type:
            cfg.append(f" spanning-tree link-type {self.spanning_tree_link_type}")

        if self.bpdu_filter_enable:
            cfg.append(" spanning-tree bpdufilter enable")

        # Security
        if self.dhcp_snooping_trust:
            cfg.append(" ip dhcp snooping trust")

        if self.dhcp_snooping_rate_limit:
            cfg.append(f" ip dhcp snooping limit rate {self.dhcp_snooping_rate_limit}")

        if self.arp_inspection_trust:
            cfg.append(" ip arp inspection trust")

        if self.arp_inspection_rate_limit:
            cfg.append(f" ip arp inspection limit rate {self.arp_inspection_rate_limit}")

        if self.ip_source_guard:
            cfg.append(" ip verify source")

        if self.ipv6_source_guard:
            cfg.append(" ipv6 verify source")

        if self.ipv6_ra_guard:
            cfg.append(" ipv6 ra guard")

        # QoS
        if self.qos_trust and self.qos_trust != QoSTrustState.NONE:
            cfg.append(f" mls qos trust {self.qos_trust.value}")

        if self.priority_queue_out:
            cfg.append(" priority-queue out")

        if self.service_policy_input:
            cfg.append(f" service-policy input {self.service_policy_input}")

        if self.service_policy_output:
            cfg.append(f" service-policy output {self.service_policy_output}")

        if self.shape_average:
            cfg.append(f" shape average {self.shape_average}")

        if self.police_rate:
            if self.police_burst:
                cfg.append(f" police {self.police_rate} {self.police_burst}")
            else:
                cfg.append(f" police {self.police_rate}")

        # Storm Control
        for t, mn, mx in (
            ("broadcast", self.storm_control_broadcast_min, self.storm_control_broadcast_max),
            ("multicast", self.storm_control_multicast_min, self.storm_control_multicast_max),
            ("unknown-unicast", self.storm_control_unknown_unicast_min, self.storm_control_unknown_unicast_max),
        ):
            line = self._fmt_storm_line(t, mn, mx)
            if line:
                cfg.append(line)

        if self.storm_control_action:
            cfg.append(f" storm-control action {self.storm_control_action}")

        # Layer 1
        if self.speed != "auto":
            cfg.append(f" speed {self.speed}")

        if self.duplex != "auto":
            cfg.append(f" duplex {self.duplex}")

        if self.auto_mdix:
            cfg.append(" mdix auto")

        if self.energy_efficient_ethernet:
            cfg.append(" power efficient-ethernet auto")

        # Flow control
        if self.flow_control_receive:
            cfg.append(" flowcontrol receive on")

        if self.flow_control_send:
            cfg.append(" flowcontrol send on")

        # Error Recovery
        if self.errdisable_timeout:
            cfg.append(f" errdisable timeout {self.errdisable_timeout}")

        for cause in self.errdisable_recovery_cause:
            cfg.append(f" errdisable recovery cause {cause}")

        # EtherChannel
        if self.channel_group:
            mode_str = f" mode {self.channel_group_mode.value}" if self.channel_group_mode else ""
            cfg.append(f" channel-group {self.channel_group}{mode_str}")

            if self.channel_protocol:
                cfg.append(f" channel-protocol {self.channel_protocol}")

            if self.lacp_port_priority:
                cfg.append(f" lacp port-priority {self.lacp_port_priority}")

            if self.lacp_rate:
                cfg.append(f" lacp rate {self.lacp_rate}")

            if self.port_channel_load_balance:
                cfg.append(f" port-channel load-balance {self.port_channel_load_balance}")

        # CDP/LLDP
        if not self.cdp_enabled:
            cfg.append(" no cdp enable")

        if not self.lldp_transmit:
            cfg.append(" no lldp transmit")

        if not self.lldp_receive:
            cfg.append(" no lldp receive")

        # Load interval
        if self.load_interval != 300:
            cfg.append(f" load-interval {self.load_interval}")

        # UDLD
        if self.udld_enable:
            if self.udld_aggressive:
                cfg.append(" udld port aggressive")
            else:
                cfg.append(" udld port")

        cfg.append(" exit")  # End interface block
        return cfg