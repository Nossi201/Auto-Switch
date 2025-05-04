# 'src/models/templates/AccessTemplate.py'
"""Dataclass for an *access-port* template with full feature-set.

Implements every option requested in issue #42:
* BPDU Guard/Filter, Loop- & Root-Guard
* QoS (trust cos/dscp, service-policy)
* MAB / 802.1X
* PoE (power inline …)
* Storm-Control unknown-unicast + pps-based selector
* Private-VLAN host & protected-port
* Speed / Duplex / Auto-MDIX
* Errdisable timeout
* DHCP snooping per-port limit, ARP inspection limit

Added in 2025-05:
* Color for visual identification in the UI
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AccessTemplate:
    """Full-blown access-port configuration blueprint."""
    # ---------- identifiers ---------- #
    interfaces: List[str] = field(default_factory=list)
    vlan_id: int = 1
    description: Optional[str] = None
    color: str = "#4287f5"  # Default blue color for visual identification

    # ---------- port security -------- #
    port_security_enabled: bool = False
    max_mac_addresses: int = 1
    violation_action: str = "shutdown"         # shutdown | restrict | protect
    sticky_mac: bool = False

    # ---------- voice - vlan ---------- #
    voice_vlan: Optional[int] = None

    # ---------- STP tweaks ------------ #
    spanning_tree_portfast: bool = True
    bpdu_guard: bool = False
    bpdu_filter: bool = False
    loop_guard: bool = False
    root_guard: bool = False

    # ---------- QoS / NAC ------------- #
    qos_trust: Optional[str] = None            # cos | dscp | None
    service_policy: Optional[str] = None       # service-policy name
    mab: bool = False
    dot1x: bool = False                        # 802.1X auto-auth

    # ---------- PoE ------------------- #
    poe_inline: Optional[str] = None           # auto | static | never | monitor...

    # ---------- storm-control ---------- #
    storm_control_broadcast_min: Optional[float] = None
    storm_control_broadcast_max: Optional[float] = None
    storm_control_multicast_min: Optional[float] = None
    storm_control_multicast_max: Optional[float] = None
    storm_control_unknown_unicast_min: Optional[float] = None
    storm_control_unknown_unicast_max: Optional[float] = None
    storm_control_unit_pps: bool = False       # False → percent, True → pps

    # ---------- private VLAN ---------- #
    private_vlan_host: bool = False
    protected_port: bool = False

    # ---------- physical layer -------- #
    speed: str = "auto"                        # auto | 10 | 100 | 1000
    duplex: str = "auto"                       # auto | half | full
    auto_mdix: bool = False

    # ---------- errdisable ------------ #
    errdisable_timeout: Optional[int] = None   # seconds

    # ---------- misc limits ----------- #
    dhcp_snoop_rate: Optional[int] = None      # pkts/s
    arp_inspection_rate: Optional[int] = None  # pkts/s

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
        if self.voice_vlan:
            cfg.append(f" switchport voice vlan {self.voice_vlan}")

        # Private-VLAN / protected-port
        if self.private_vlan_host:
            cfg.append(" switchport private-vlan host")
        if self.protected_port:
            cfg.append(" switchport protected")

        # STP features
        if self.spanning_tree_portfast:
            cfg.append(" spanning-tree portfast")
        if self.bpdu_guard:
            cfg.append(" spanning-tree bpduguard enable")
        if self.bpdu_filter:
            cfg.append(" spanning-tree bpdufilter enable")
        if self.loop_guard:
            cfg.append(" spanning-tree guard loop")
        if self.root_guard:
            cfg.append(" spanning-tree guard root")

        # QoS / NAC
        if self.qos_trust in {"cos", "dscp"}:
            cfg.append(f" mls qos trust {self.qos_trust}")
        if self.service_policy:
            cfg.append(f" service-policy input {self.service_policy}")
        if self.dot1x:
            cfg.append(" authentication port-control auto")
        if self.mab:
            cfg.append(" mab")

        # PoE
        if self.poe_inline:
            cfg.append(f" power inline {self.poe_inline}")

        # Storm-control
        for t, mn, mx in (
            ("broadcast", self.storm_control_broadcast_min, self.storm_control_broadcast_max),
            ("multicast", self.storm_control_multicast_min, self.storm_control_multicast_max),
            ("unknown-unicast", self.storm_control_unknown_unicast_min, self.storm_control_unknown_unicast_max),
        ):
            line = self._fmt_storm_line(t, mn, mx)
            if line:
                cfg.append(line)

        # Physical layer
        if self.speed != "auto":
            cfg.append(f" speed {self.speed}")
        if self.duplex != "auto":
            cfg.append(f" duplex {self.duplex}")
        if self.auto_mdix:
            cfg.append(" mdix auto")

        # Errdisable
        if self.errdisable_timeout:
            cfg.append(f" errdisable timeout {self.errdisable_timeout}")

        # DHCP snooping / ARP inspection limits
        if self.dhcp_snoop_rate:
            cfg.append(f" ip dhcp snooping limit rate {self.dhcp_snoop_rate}")
        if self.arp_inspection_rate:
            cfg.append(f" ip arp inspection limit rate {self.arp_inspection_rate}")

        # Port-Security
        if self.port_security_enabled:
            cfg.append(" switchport port-security")
            cfg.append(f" switchport port-security maximum {self.max_mac_addresses}")
            cfg.append(f" switchport port-security violation {self.violation_action}")
            if self.sticky_mac:
                cfg.append(" switchport port-security mac-address sticky")

        cfg.append(" exit")   # End of interface block
        return cfg