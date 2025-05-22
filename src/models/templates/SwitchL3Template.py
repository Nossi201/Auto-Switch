# src/models/templates/SwitchL3Template.py
"""Szablon konfiguracyjny dla przełącznika warstwy 3 (L3) z obsługą funkcji routingu.

Klasa dziedziczy po SwitchTemplate i rozszerza ją o funkcje routingu:
- Interfejsy SVI (Switch Virtual Interface) do komunikacji międzysieciowej
- Statyczne trasy routingu
- Obsługa protokołów routingu (OSPF, EIGRP, BGP)
- Obsługa ACL (Access Control Lists)
- Funkcje DHCP relay i NAT
- Zaawansowane funkcje warstwy 3 (PBR, VRF, VRRP/HSRP)

Metoda generate_config() generuje pełną konfigurację IOS obejmującą zarówno
funkcje przełącznika L2, jak i funkcje routingu L3.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Union
from enum import Enum

from src.models.templates.SwitchL2Template import SwitchL2Template, VLAN, SpanningTreeMode, VTPMode


class RoutingProtocol(str, Enum):
    """Obsługiwane protokoły routingu."""
    STATIC = "static"
    RIP = "rip"
    OSPF = "ospf"
    EIGRP = "eigrp"
    BGP = "bgp"


@dataclass
class SwitchVirtualInterface:
    """Interfejs wirtualny (SVI) z konfiguracją IP."""
    vlan_id: int
    ip_address: str
    subnet_mask: str
    description: Optional[str] = None
    secondary_ips: List[Tuple[str, str]] = field(default_factory=list)
    shutdown: bool = False
    helper_addresses: List[str] = field(default_factory=list)  # DHCP relay
    ospf_area: Optional[str] = None
    eigrp_as: Optional[int] = None
    acl_in: Optional[str] = None
    acl_out: Optional[str] = None


@dataclass
class StaticRoute:
    """Statyczna trasa."""
    prefix: str
    mask: str
    next_hop: str
    distance: Optional[int] = None
    name: Optional[str] = None


@dataclass
class ACLEntry:
    """Wpis Access Control List."""
    name: str
    sequence: int
    action: str  # permit, deny
    protocol: str  # ip, tcp, udp, icmp...
    source: str
    source_wildcard: Optional[str] = None
    destination: str = "any"
    destination_wildcard: Optional[str] = None
    port_operator: Optional[str] = None  # eq, gt, lt, neq, range
    port: Optional[Union[int, str]] = None
    port_end: Optional[int] = None  # dla operatora range


@dataclass
class SwitchL3Template(SwitchL2Template):
    """Kompletny szablon konfiguracyjny do przełączników warstwy 3."""

    # Interfejsy SVI (Switch Virtual Interface)
    svi_interfaces: List[SwitchVirtualInterface] = field(default_factory=list)

    # Statyczne trasy
    static_routes: List[StaticRoute] = field(default_factory=list)

    # Protokoły routingu
    routing_enabled: bool = True
    ospf_process_id: int = 1
    ospf_router_id: Optional[str] = None
    ospf_networks: List[Tuple[str, str, str]] = field(default_factory=list)  # (net, wildcard, area)
    ospf_passive_interfaces: List[str] = field(default_factory=list)

    eigrp_as: Optional[int] = None
    eigrp_networks: List[Tuple[str, str]] = field(default_factory=list)  # (net, wildcard)
    eigrp_passive_interfaces: List[str] = field(default_factory=list)

    # ACLs
    acl_entries: List[ACLEntry] = field(default_factory=list)

    # NAT
    nat_inside_interfaces: List[str] = field(default_factory=list)
    nat_outside_interfaces: List[str] = field(default_factory=list)
    nat_pool: Optional[Dict[str, str]] = None
    nat_acl_to_pool: Optional[Dict[str, str]] = None

    # DHCP Server
    dhcp_pools: Dict[str, Dict[str, str]] = field(default_factory=dict)
    dhcp_excluded_addresses: List[str] = field(default_factory=list)

    # HSRP/VRRP
    hsrp_groups: Dict[str, Dict[str, Union[int, str]]] = field(default_factory=dict)

    # VRF
    vrf_definitions: Dict[str, Dict[str, str]] = field(default_factory=dict)

    # Rozszerzenia
    ip_routing: bool = True
    ipv6_routing: bool = False
    policy_routing: Dict[str, str] = field(default_factory=dict)  # interfejs -> policy-map

    # ------------------------------------------------------------------ #
    def generate_config(
            self,
            nested_templates: Optional[List[object]] = None,
    ) -> List[str]:
        """Wygeneruj pełną konfigurację IOS CLI dla przełącznika L3.

        Args:
            nested_templates: Opcjonalna lista szablonów portów (Access lub Trunk)
                              do wstawienia w konfiguracji.

        Returns:
            Lista komend IOS CLI.
        """
        # Najpierw generujemy bazową konfigurację przełącznika L2
        cfg = super().generate_config(nested_templates)

        # Usuwamy komendę 'end' i 'write memory' z końca, aby dodać funkcje L3
        if cfg[-1] == "write memory":
            cfg.pop()
        if cfg[-2] == "end":
            cfg.pop(-2)

        # Włączenie routingu IP
        if self.ip_routing:
            cfg.append("ip routing")
        if self.ipv6_routing:
            cfg.append("ipv6 unicast-routing")

        # Konfiguracja interfejsów SVI
        for svi in self.svi_interfaces:
            cfg.append(f"interface Vlan{svi.vlan_id}")
            if svi.description:
                cfg.append(f" description {svi.description}")
            cfg.append(f" ip address {svi.ip_address} {svi.subnet_mask}")

            for sec_ip, sec_mask in svi.secondary_ips:
                cfg.append(f" ip address {sec_ip} {sec_mask} secondary")

            for helper in svi.helper_addresses:
                cfg.append(f" ip helper-address {helper}")

            if svi.acl_in:
                cfg.append(f" ip access-group {svi.acl_in} in")
            if svi.acl_out:
                cfg.append(f" ip access-group {svi.acl_out} out")

            # Dodajemy do OSPF
            if svi.ospf_area:
                cfg.append(f" ip ospf {self.ospf_process_id} area {svi.ospf_area}")

            # Dodajemy do EIGRP
            if svi.eigrp_as:
                cfg.append(f" ip eigrp {svi.eigrp_as}")

            # Status interfejsu
            if svi.shutdown:
                cfg.append(" shutdown")
            else:
                cfg.append(" no shutdown")

            cfg.append(" exit")

        # Statyczne trasy
        for route in self.static_routes:
            distance = f" {route.distance}" if route.distance else ""
            name = f" name {route.name}" if route.name else ""
            cfg.append(f"ip route {route.prefix} {route.mask} {route.next_hop}{distance}{name}")

        # OSPF
        if self.ospf_networks:
            cfg.append(f"router ospf {self.ospf_process_id}")
            if self.ospf_router_id:
                cfg.append(f" router-id {self.ospf_router_id}")

            for net, wildcard, area in self.ospf_networks:
                cfg.append(f" network {net} {wildcard} area {area}")

            for intf in self.ospf_passive_interfaces:
                cfg.append(f" passive-interface {intf}")

            cfg.append(" exit")

        # EIGRP
        if self.eigrp_as and self.eigrp_networks:
            cfg.append(f"router eigrp {self.eigrp_as}")

            for net, wildcard in self.eigrp_networks:
                cfg.append(f" network {net} {wildcard}")

            for intf in self.eigrp_passive_interfaces:
                cfg.append(f" passive-interface {intf}")

            cfg.append(" exit")

        # ACLs
        current_acl = None
        for entry in sorted(self.acl_entries, key=lambda x: (x.name, x.sequence)):
            if current_acl != entry.name:
                if current_acl:
                    cfg.append(" exit")
                cfg.append(f"ip access-list extended {entry.name}")
                current_acl = entry.name

            # Tworzymy komendę ACL
            cmd = f" {entry.sequence} {entry.action} {entry.protocol} {entry.source}"
            if entry.source_wildcard:
                cmd += f" {entry.source_wildcard}"

            cmd += f" {entry.destination}"
            if entry.destination_wildcard:
                cmd += f" {entry.destination_wildcard}"

            if entry.port_operator:
                cmd += f" {entry.port_operator} {entry.port}"
                if entry.port_operator == "range" and entry.port_end:
                    cmd += f" {entry.port_end}"

            cfg.append(cmd)

        if current_acl:
            cfg.append(" exit")

        # NAT
        if self.nat_inside_interfaces or self.nat_outside_interfaces:
            for intf in self.nat_inside_interfaces:
                cfg.append(f"interface {intf}")
                cfg.append(" ip nat inside")
                cfg.append(" exit")

            for intf in self.nat_outside_interfaces:
                cfg.append(f"interface {intf}")
                cfg.append(" ip nat outside")
                cfg.append(" exit")

            if self.nat_pool and self.nat_acl_to_pool:
                for pool_name, pool_config in self.nat_pool.items():
                    cfg.append(f"ip nat pool {pool_name} {pool_config}")

                for acl_name, pool_name in self.nat_acl_to_pool.items():
                    cfg.append(f"ip nat inside source list {acl_name} pool {pool_name}")

        # DHCP Server
        if self.dhcp_excluded_addresses:
            for addr in self.dhcp_excluded_addresses:
                cfg.append(f"ip dhcp excluded-address {addr}")

        for pool_name, pool_config in self.dhcp_pools.items():
            cfg.append(f"ip dhcp pool {pool_name}")
            for key, value in pool_config.items():
                cfg.append(f" {key} {value}")
            cfg.append(" exit")

        # HSRP
        for intf, group_config in self.hsrp_groups.items():
            cfg.append(f"interface {intf}")
            for group_id, config in group_config.items():
                cfg.append(f" standby {group_id} ip {config['ip']}")
                if 'priority' in config:
                    cfg.append(f" standby {group_id} priority {config['priority']}")
                if 'preempt' in config and config['preempt']:
                    cfg.append(f" standby {group_id} preempt")
                if 'track' in config:
                    cfg.append(f" standby {group_id} track {config['track']}")
            cfg.append(" exit")

        # VRF
        for vrf_name, vrf_config in self.vrf_definitions.items():
            cfg.append(f"vrf definition {vrf_name}")
            for key, value in vrf_config.items():
                cfg.append(f" {key} {value}")
            cfg.append(" exit")

        # Policy-Based Routing
        for intf, policy in self.policy_routing.items():
            cfg.append(f"interface {intf}")
            cfg.append(f" ip policy route-map {policy}")
            cfg.append(" exit")

        # Dodajemy z powrotem end i write memory
        cfg.append("end")
        cfg.append("write memory")

        return cfg