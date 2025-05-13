# src/models/templates/AccessTemplate.py
"""Enhanced dataclass for an *access-port* template with comprehensive feature-set.

Implements every option available in Cisco IOS/IOS-XE for access ports:
* Layer 1 features (speed, duplex, mdix, EEE)
* MAC address table (limit, secure, sticky)
* Basic switching (VLAN assignments, voice VLAN)
* Spanning Tree features (PortFast, guards, filters)
* QoS (trust, marking, policing, shaping, queuing)
* Storm Control (broadcast/multicast/unicast)
* Security (port security, 802.1X, MAB, WebAuth)
* Monitoring and error recovery
* PoE (power inline modes, prioritization)
* DHCP/ARP security and rate limiting
* Private VLANs and protected ports
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union, Set
from enum import Enum


class PowerInlineMode(str, Enum):
    """PoE modes for Cisco IOS."""
    AUTO = "auto"
    STATIC = "static"
    NEVER = "never"
    MAXIMUM = "maximum"
    PERPETUAL = "perpetual-poe"


class AuthenticationMode(str, Enum):
    """Authentication modes for 802.1X."""
    AUTO = "auto"
    FORCE_AUTHORIZED = "force-authorized"
    FORCE_UNAUTHORIZED = "force-unauthorized"


class ViolationAction(str, Enum):
    """Actions for port security violations."""
    SHUTDOWN = "shutdown"
    RESTRICT = "restrict"
    PROTECT = "protect"


class QoSTrustState(str, Enum):
    """QoS trust states."""
    NONE = "none"
    COS = "cos"
    DSCP = "dscp"


@dataclass
class AccessTemplate:
    """Full-featured access-port configuration blueprint."""
    # ---------- identifiers ---------- #
    interfaces: List[str] = field(default_factory=list)
    vlan_id: int = 1
    description: Optional[str] = None
    color: Optional[str] = None  # UI display color (backward compatibility)

    # ---------- physical layer -------- #
    speed: str = "auto"                        # auto | 10 | 100 | 1000 | 10000
    duplex: str = "auto"                       # auto | half | full
    auto_mdix: bool = False
    energy_efficient_ethernet: bool = False    # EEE

    # ---------- port security -------- #
    port_security_enabled: bool = False
    max_mac_addresses: int = 1
    violation_action: ViolationAction = ViolationAction.SHUTDOWN
    sticky_mac: bool = False
    restricted_mac_addresses: List[str] = field(default_factory=list)

    # ---------- voice - vlan ---------- #
    voice_vlan: Optional[int] = None
    voice_vlan_dot1p: bool = False           # Use 802.1p priority tagging
    voice_vlan_none: bool = False            # Use "none" instead of VLAN ID

    # ---------- STP tweaks ------------ #
    spanning_tree_portfast: bool = True
    spanning_tree_portfast_trunk: bool = False  # PortFast on trunk ports
    bpdu_guard: bool = False
    bpdu_filter: bool = False
    loop_guard: bool = False
    root_guard: bool = False
    spanning_tree_link_type: Optional[str] = None  # point-to-point | shared

    # ---------- QoS / NAC ------------- #
    qos_trust: Optional[QoSTrustState] = None  # cos | dscp | None
    service_policy_input: Optional[str] = None  # service-policy input name
    service_policy_output: Optional[str] = None  # service-policy output name
    qos_cos_override: Optional[int] = None    # Set CoS value 0-7
    qos_dscp_override: Optional[int] = None   # Set DSCP value 0-63
    priority_queue_out: bool = False          # Enable priority queue
    shape_average: Optional[int] = None       # Rate in bps
    police_rate: Optional[int] = None         # Rate in bps
    police_burst: Optional[int] = None        # Burst in bytes

    # ---------- Authentication -------- #
    authentication_host_mode: str = "single-host"  # single-host | multi-auth | multi-domain | multi-host
    authentication_open: bool = False          # Allow traffic before authentication
    authentication_order: List[str] = field(default_factory=lambda: ["dot1x", "mab"])
    authentication_priority: List[str] = field(default_factory=lambda: ["dot1x", "mab"])
    authentication_periodic: bool = False      # Reauthentication
    authentication_timer_reauthenticate: int = 3600

    mab: bool = False                         # MAC Authentication Bypass
    dot1x: bool = False                       # 802.1X auto-auth
    dot1x_timeout_quiet_period: int = 60      # Seconds
    dot1x_timeout_tx_period: int = 30         # Seconds
    dot1x_max_req: int = 2                    # Max EAP retries

    webauth: bool = False                     # Web Authentication
    webauth_local: bool = True                # Use local user database

    authentication_control_direction: str = "both"  # both | in
    authentication_fallback: Optional[str] = None  # Fallback method
    authentication_violation: str = "restrict"     # restrict | protect | shutdown

    # ---------- PoE ------------------- #
    poe_enabled: bool = True                  # Power over Ethernet enabled/disabled
    poe_inline: PowerInlineMode = PowerInlineMode.AUTO  # auto | static | never | max | perpetual
    poe_priority: str = "low"                 # low | medium | high | critical
    poe_limit: Optional[int] = None           # Power limit in milliwatts

    # ---------- storm-control ---------- #
    storm_control_broadcast_min: Optional[float] = None
    storm_control_broadcast_max: Optional[float] = None
    storm_control_multicast_min: Optional[float] = None
    storm_control_multicast_max: Optional[float] = None
    storm_control_unknown_unicast_min: Optional[float] = None
    storm_control_unknown_unicast_max: Optional[float] = None
    storm_control_unit_pps: bool = False       # False → percent, True → pps
    storm_control_action: Optional[str] = None # shutdown | trap | none

    # ---------- private VLAN ---------- #
    private_vlan_host: bool = False
    private_vlan_mapping: Optional[str] = None  # primary-secondary VLAN mapping
    protected_port: bool = False
    no_neighbor: bool = False                  # Equivalent to protected port

    # ---------- CDP/LLDP -------------- #
    cdp_enabled: bool = True                   # Cisco Discovery Protocol
    lldp_transmit: bool = True                 # LLDP transmit
    lldp_receive: bool = True                  # LLDP receive

    # ---------- errdisable ------------ #
    errdisable_timeout: Optional[int] = None   # seconds
    errdisable_recovery_cause: List[str] = field(default_factory=list)

    # ---------- misc limits ----------- #
    dhcp_snoop_rate: Optional[int] = None      # pkts/s
    dhcp_snoop_trust: bool = False             # Trust DHCP packets from this port
    arp_inspection_rate: Optional[int] = None  # pkts/s
    arp_inspection_trust: bool = False         # Trust ARP packets from this port
    ip_source_guard: bool = False              # Enable IP source guard

    # ---------- Additional Features ---- #
    udld_enable: bool = False                  # Enable UDLD
    udld_aggressive: bool = False              # UDLD aggressive mode

    flow_control_receive: bool = False         # Flow control receive
    flow_control_send: bool = False            # Flow control send

    load_interval: int = 300                   # Load interval for statistics

    # ---------- Network Services ------- #
    device_tracking: bool = False              # Enable device tracking
    ip_dhcp_relay_information: bool = False    # DHCP option 82
    ipv6_nd_inspection: bool = False           # IPv6 ND inspection
    ipv6_ra_guard: bool = False                # IPv6 RA guard

    # ------------------------------------------------------------------ #
    def _fmt_storm_line(self,
                        traffic_type: str,
                        mn: Optional[float],
                        mx: Optional[float]) -> Optional[str]:
        """Return single storm-control CLI or *None* when disabled."""
        if mn is None:
            return None
        unit = "pps" if self.storm_control_unit_pps else ""
        line = f" storm-control {traffic_type} level {mn}"
        if mx is not None:
            line += f" {mx}"
        if unit:
            line += f" {unit}"
        return line

    # ------------------------------------------------------------------ #
    def generate_config(self) -> List[str]:
        """Render IOS CLI lines for the template."""
        if not self.interfaces:
            return []

        cfg: List[str] = []

        # VLAN definition (simple bookkeeping)
        cfg.append(f"vlan {self.vlan_id}")
        if self.description:
            cfg.append(f" name {self.description}")
        cfg.append(" exit")

        # Interface range
        iface_range = ",".join(self.interfaces)
        cfg.append(f"interface range {iface_range}")
        cfg.append(" switchport mode access")
        cfg.append(f" switchport access vlan {self.vlan_id}")

        if self.description:
            cfg.append(f" description {self.description}")

        # Voice-VLAN
        if self.voice_vlan_none:
            cfg.append(" switchport voice vlan none")
        elif self.voice_vlan_dot1p:
            cfg.append(" switchport voice vlan dot1p")
        elif self.voice_vlan:
            cfg.append(f" switchport voice vlan {self.voice_vlan}")

        # Private-VLAN / protected-port
        if self.private_vlan_host:
            cfg.append(" switchport private-vlan host")
        if self.private_vlan_mapping:
            cfg.append(f" switchport private-vlan mapping {self.private_vlan_mapping}")
        if self.protected_port or self.no_neighbor:
            cfg.append(" switchport protected")

        # STP features
        if self.spanning_tree_portfast:
            if self.spanning_tree_portfast_trunk:
                cfg.append(" spanning-tree portfast trunk")
            else:
                cfg.append(" spanning-tree portfast")

        if self.bpdu_guard:
            cfg.append(" spanning-tree bpduguard enable")
        if self.bpdu_filter:
            cfg.append(" spanning-tree bpdufilter enable")
        if self.loop_guard:
            cfg.append(" spanning-tree guard loop")
        if self.root_guard:
            cfg.append(" spanning-tree guard root")

        if self.spanning_tree_link_type:
            cfg.append(f" spanning-tree link-type {self.spanning_tree_link_type}")

        # QoS / NAC
        if self.qos_trust and self.qos_trust != QoSTrustState.NONE:
            cfg.append(f" mls qos trust {self.qos_trust.value}")

        if self.qos_cos_override is not None:
            cfg.append(f" mls qos cos {self.qos_cos_override}")

        if self.qos_dscp_override is not None:
            cfg.append(f" mls qos dscp {self.qos_dscp_override}")

        if self.service_policy_input:
            cfg.append(f" service-policy input {self.service_policy_input}")

        if self.service_policy_output:
            cfg.append(f" service-policy output {self.service_policy_output}")

        if self.priority_queue_out:
            cfg.append(" priority-queue out")

        if self.shape_average:
            cfg.append(f" shape average {self.shape_average}")

        if self.police_rate:
            if self.police_burst:
                cfg.append(f" police {self.police_rate} {self.police_burst}")
            else:
                cfg.append(f" police {self.police_rate}")

        # Authentication
        if self.dot1x:
            auth_mode = "auto" if self.dot1x and self.mab else "auto"  # Set proper mode
            cfg.append(f" authentication port-control {auth_mode}")
            cfg.append(f" authentication host-mode {self.authentication_host_mode}")

            if self.authentication_open:
                cfg.append(" authentication open")

            if self.authentication_order:
                cfg.append(" authentication order " + " ".join(self.authentication_order))

            if self.authentication_priority:
                cfg.append(" authentication priority " + " ".join(self.authentication_priority))

            if self.authentication_periodic:
                cfg.append(" authentication periodic")
                cfg.append(f" authentication timer reauthenticate {self.authentication_timer_reauthenticate}")

            cfg.append(f" authentication control-direction {self.authentication_control_direction}")
            cfg.append(f" authentication violation {self.authentication_violation}")

            if self.authentication_fallback:
                cfg.append(f" authentication fallback {self.authentication_fallback}")

            # 802.1X specific settings
            cfg.append(f" dot1x timeout quiet-period {self.dot1x_timeout_quiet_period}")
            cfg.append(f" dot1x timeout tx-period {self.dot1x_timeout_tx_period}")
            cfg.append(f" dot1x max-req {self.dot1x_max_req}")

        if self.mab:
            cfg.append(" mab")

        if self.webauth:
            if self.webauth_local:
                cfg.append(" web-auth")
            else:
                cfg.append(" web-auth authentication-list default")

        # PoE
        if not self.poe_enabled:
            cfg.append(" power inline never")
        else:
            cfg.append(f" power inline {self.poe_inline.value}")
            cfg.append(f" power inline priority {self.poe_priority}")

            if self.poe_limit:
                cfg.append(f" power inline max {self.poe_limit}")

        # Storm-control
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

        # Physical layer
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

        # Errdisable
        if self.errdisable_timeout:
            cfg.append(f" errdisable timeout {self.errdisable_timeout}")

        for cause in self.errdisable_recovery_cause:
            cfg.append(f" errdisable recovery cause {cause}")

        # DHCP snooping / ARP inspection limits
        if self.dhcp_snoop_rate:
            cfg.append(f" ip dhcp snooping limit rate {self.dhcp_snoop_rate}")

        if self.dhcp_snoop_trust:
            cfg.append(" ip dhcp snooping trust")

        if self.ip_dhcp_relay_information:
            cfg.append(" ip dhcp relay information trusted")

        if self.arp_inspection_rate:
            cfg.append(f" ip arp inspection limit rate {self.arp_inspection_rate}")

        if self.arp_inspection_trust:
            cfg.append(" ip arp inspection trust")

        if self.ip_source_guard:
            cfg.append(" ip verify source")

        # IPv6 Security
        if self.ipv6_nd_inspection:
            cfg.append(" ipv6 nd inspection")

        if self.ipv6_ra_guard:
            cfg.append(" ipv6 ra guard")

        if self.device_tracking:
            cfg.append(" device-tracking")

        # Port-Security
        if self.port_security_enabled:
            cfg.append(" switchport port-security")
            cfg.append(f" switchport port-security maximum {self.max_mac_addresses}")
            cfg.append(f" switchport port-security violation {self.violation_action.value}")

            if self.sticky_mac:
                cfg.append(" switchport port-security mac-address sticky")

            for mac in self.restricted_mac_addresses:
                cfg.append(f" switchport port-security mac-address {mac}")

        cfg.append(" exit")   # End of interface block
        return cfg