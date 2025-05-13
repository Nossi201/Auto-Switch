# src/models/templates/SwitchTemplate.py
"""Comprehensive Cisco‐switch template class with complete L2 feature support.

This class supports eight configuration categories that match the UI tabs:
1. Basic Settings - hostname, domain, management interfaces
2. VLANs - VLAN IDs, names, and VTP configuration
3. Spanning Tree - mode, priorities, timers, and protection features
4. Port Security - DHCP/ARP inspection, storm control, IP source guard
5. QoS - Quality of Service settings and queue configurations
6. Monitoring - logging, SNMP, and span/port mirroring
7. Advanced Layer2 - protocol specific settings, timers, and frame handling
8. System - authentication, AAA, power management

The generate_config() method renders only the commands that are explicitly
enabled, keeping the output minimal but deterministic.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Sequence, Union, Tuple, Set
from enum import Enum


class SpanningTreeMode(str, Enum):
    """Supported spanning-tree modes."""
    PVST = "pvst"
    RAPID_PVST = "rapid-pvst"
    MST = "mst"


class VTPMode(str, Enum):
    """Supported VTP modes."""
    OFF = "off"
    SERVER = "server"
    CLIENT = "client"
    TRANSPARENT = "transparent"


class UDLDMode(str, Enum):
    """UDLD operating modes."""
    DISABLED = "disabled"
    NORMAL = "normal"
    AGGRESSIVE = "aggressive"


class LoggingLevel(str, Enum):
    """Syslog severity levels."""
    EMERGENCIES = "emergencies"
    ALERTS = "alerts"
    CRITICAL = "critical"
    ERRORS = "errors"
    WARNINGS = "warnings"
    NOTIFICATIONS = "notifications"
    INFORMATIONAL = "informational"
    DEBUGGING = "debugging"


class QoSTrustState(str, Enum):
    """QoS trust states."""
    NONE = "none"
    COS = "cos"
    DSCP = "dscp"


@dataclass
class VLAN:
    """VLAN properties."""
    id: int
    name: Optional[str] = None
    state: str = "active"


@dataclass
class QoSQueue:
    """QoS queue configuration."""
    queue_id: int
    priority: int = 0
    bandwidth: int = 0


@dataclass
class MSTPInstance:
    """MST instance configuration."""
    instance_id: int
    priority: int = 32768
    vlans: List[int] = field(default_factory=list)


@dataclass
class SwitchTemplate:
    """Complete device-level settings for a Cisco switch."""

    # ---------------------------- 1. Basic Settings ---------------------------- #
    hostname: str = "Switch"
    domain_name: str = "local"
    manager_vlan_id: int = 1
    manager_ip: str = "192.168.1.1 255.255.255.0"
    default_gateway: str = "192.168.1.254"
    enable_cdp: bool = True
    enable_lldp: bool = False

    # ---------------------------- 2. VLAN Configuration ----------------------- #
    vlans: List[VLAN] = field(default_factory=lambda: [VLAN(id=1, name="default")])

    # Convenience property to extract VLAN IDs for backward compatibility
    @property
    def vlan_list(self) -> List[int]:
        """Return list of VLAN IDs for backward compatibility."""
        return [vlan.id for vlan in self.vlans]

    vtp_mode: VTPMode = VTPMode.OFF
    vtp_domain: Optional[str] = None
    vtp_password: Optional[str] = None

    # ---------------------------- 3. Spanning Tree ---------------------------- #
    spanning_tree_mode: SpanningTreeMode = SpanningTreeMode.RAPID_PVST
    spanning_tree_priority: int = 32768  # Default bridge priority

    # Protection features
    bpduguard_default: bool = False
    bpdufilter_default: bool = False
    loopguard_default: bool = False
    rootguard_default: bool = False

    # Timers
    spanning_tree_hello_time: int = 2
    spanning_tree_forward_time: int = 15
    spanning_tree_max_age: int = 20

    # MST specific
    mst_config_name: Optional[str] = None
    mst_config_revision: int = 0
    mst_instances: List[MSTPInstance] = field(default_factory=list)

    # ---------------------------- 4. Port Security ---------------------------- #
    # DHCP Snooping
    dhcp_snoop_enabled: bool = False
    dhcp_snoop_vlans: List[int] = field(default_factory=list)
    dhcp_option82_enabled: bool = False

    # Dynamic ARP Inspection
    arp_inspection_enabled: bool = False
    arp_inspection_vlans: List[int] = field(default_factory=list)

    # IP Source Guard
    ip_source_guard_default: bool = False

    # Port Security
    port_security_default_violation: str = "shutdown"  # shutdown | restrict | protect

    # Storm Control
    storm_control_default_enabled: bool = False
    storm_control_default_threshold: float = 80.0  # percent
    storm_control_default_unit_pps: bool = False

    # ---------------------------- 5. QoS -------------------------------------- #
    qos_enabled: bool = False  # mls qos
    qos_trust_default: Optional[QoSTrustState] = None
    auto_qos_enabled: bool = False

    qos_dscp_map: Dict[int, int] = field(default_factory=dict)  # maps DSCP to internal DSCP
    qos_cos_map: Dict[int, int] = field(default_factory=dict)   # maps CoS to internal DSCP

    # Queue configuration
    qos_queues: List[QoSQueue] = field(default_factory=list)

    # ---------------------------- 6. Monitoring ------------------------------- #
    # Logging
    logging_enabled: bool = True
    logging_host: Optional[str] = None
    logging_level: LoggingLevel = LoggingLevel.NOTIFICATIONS
    logging_buffer_size: int = 4096

    # SNMP
    snmp_enabled: bool = False
    snmp_community_ro: str = "public"
    snmp_community_rw: Optional[str] = None
    snmp_location: Optional[str] = None
    snmp_contact: Optional[str] = None
    snmp_traps_enabled: bool = False

    # SPAN/RSPAN
    span_enabled: bool = False
    span_source_ports: List[str] = field(default_factory=list)
    span_destination_port: Optional[str] = None

    # NetFlow/sFlow
    netflow_enabled: bool = False
    netflow_collector: Optional[str] = None

    # ---------------------------- 7. Advanced Layer2 -------------------------- #
    # UDLD
    udld_mode: UDLDMode = UDLDMode.DISABLED

    # L2 Protocol Feature Flags
    igmp_snooping_enabled: bool = True
    mld_snooping_enabled: bool = False

    # MAC table
    mac_address_table_aging_time: int = 300  # seconds

    # Frame handling
    jumbo_frames_enabled: bool = False
    system_mtu: int = 1500  # bytes

    # ---------------------------- 8. System Settings -------------------------- #
    # SSH and Authentication
    enable_ssh: bool = False
    enable_secret: bool = False  # dummy password "Cisco123"

    # AAA
    aaa_new_model: bool = False
    aaa_authentication_enabled: bool = False
    aaa_authorization_enabled: bool = False
    aaa_accounting_enabled: bool = False

    # RADIUS/TACACS
    radius_server: Optional[str] = None
    radius_key: Optional[str] = None
    tacacs_server: Optional[str] = None
    tacacs_key: Optional[str] = None

    # Power Management
    poe_power_budget: int = 0  # watts, 0 = auto
    energy_efficient_ethernet: bool = False

    # ---------------------------- Additional Features ------------------------- #
    monitoring_enabled: bool = False  # errdisable recovery, EEM
    errdisable_recovery_interval: int = 300

    # ------------------------------------------------------------------ #
    def generate_config(
        self,
        nested_templates: Optional[Sequence[object]] = None,
    ) -> List[str]:
        """Return full IOS CLI for the switch configuration.

        Args:
            nested_templates: Optional list of port templates (Access or Trunk)
                              to include in the configuration.

        Returns:
            List of IOS CLI commands.
        """
        cfg: List[str] = [
            "enable",
            "configure terminal",
        ]

        # ----------- 1. BASIC SETTINGS ------------------------------------ #
        cfg.append(f"hostname {self.hostname}")

        if self.domain_name:
            cfg.append(f"ip domain-name {self.domain_name}")

        # CDP/LLDP settings
        if self.enable_cdp:
            cfg.append("cdp run")
        else:
            cfg.append("no cdp run")

        if self.enable_lldp:
            cfg.append("lldp run")
        else:
            cfg.append("no lldp run")

        # ----------- 2. VLAN CONFIGURATION ------------------------------- #
        # Define VLANs
        for vlan in self.vlans:
            cfg.append(f"vlan {vlan.id}")
            if vlan.name:
                cfg.append(f" name {vlan.name}")
            if vlan.state != "active":
                cfg.append(f" state {vlan.state}")
            cfg.append(" exit")

        # VTP Configuration
        if self.vtp_mode != VTPMode.OFF:
            cfg.append(f"vtp mode {self.vtp_mode.value}")
            if self.vtp_domain:
                cfg.append(f"vtp domain {self.vtp_domain}")
            if self.vtp_password:
                cfg.append(f"vtp password {self.vtp_password}")

        # ----------- 3. SPANNING TREE ----------------------------------- #
        cfg.append(f"spanning-tree mode {self.spanning_tree_mode.value}")

        # Set bridge priority if not default
        if self.spanning_tree_priority != 32768:
            cfg.append(f"spanning-tree vlan 1-4094 priority {self.spanning_tree_priority}")

        # STP Timers
        if self.spanning_tree_hello_time != 2:
            cfg.append(f"spanning-tree vlan 1-4094 hello-time {self.spanning_tree_hello_time}")
        if self.spanning_tree_forward_time != 15:
            cfg.append(f"spanning-tree vlan 1-4094 forward-time {self.spanning_tree_forward_time}")
        if self.spanning_tree_max_age != 20:
            cfg.append(f"spanning-tree vlan 1-4094 max-age {self.spanning_tree_max_age}")

        # Protection features
        if self.bpduguard_default:
            cfg.append("spanning-tree portfast bpduguard default")
        if self.bpdufilter_default:
            cfg.append("spanning-tree portfast bpdufilter default")
        if self.loopguard_default:
            cfg.append("spanning-tree loopguard default")

        # MST Configuration
        if self.spanning_tree_mode == SpanningTreeMode.MST and self.mst_config_name:
            cfg.append("spanning-tree mst configuration")
            cfg.append(f" name {self.mst_config_name}")
            cfg.append(f" revision {self.mst_config_revision}")

            for instance in self.mst_instances:
                vlan_ranges = self._vlan_list_to_ranges(instance.vlans)
                for vrange in vlan_ranges:
                    cfg.append(f" instance {instance.instance_id} vlan {vrange}")
            cfg.append(" exit")

            # MST instance priorities
            for instance in self.mst_instances:
                if instance.priority != 32768:
                    cfg.append(f"spanning-tree mst {instance.instance_id} priority {instance.priority}")

        # ----------- 4. PORT SECURITY ---------------------------------- #
        # DHCP Snooping
        if self.dhcp_snoop_enabled:
            cfg.append("ip dhcp snooping")
            if self.dhcp_snoop_vlans:
                vlan_ranges = self._vlan_list_to_ranges(self.dhcp_snoop_vlans)
                for vrange in vlan_ranges:
                    cfg.append(f"ip dhcp snooping vlan {vrange}")
            else:
                cfg.append("ip dhcp snooping vlan 1-4094")

            if self.dhcp_option82_enabled:
                cfg.append("ip dhcp snooping information option")

        # ARP Inspection
        if self.arp_inspection_enabled:
            cfg.append("ip arp inspection")
            if self.arp_inspection_vlans:
                vlan_ranges = self._vlan_list_to_ranges(self.arp_inspection_vlans)
                for vrange in vlan_ranges:
                    cfg.append(f"ip arp inspection vlan {vrange}")
            else:
                cfg.append("ip arp inspection vlan 1-4094")

        # Storm Control Default
        if self.storm_control_default_enabled:
            unit = " pps" if self.storm_control_default_unit_pps else ""
            cfg.append(f"storm-control broadcast level {self.storm_control_default_threshold}{unit}")
            cfg.append(f"storm-control multicast level {self.storm_control_default_threshold}{unit}")
            cfg.append(f"storm-control unicast level {self.storm_control_default_threshold}{unit}")

        # ----------- 5. QoS --------------------------------------------- #
        if self.qos_enabled:
            cfg.append("mls qos")

            # Default trust state
            if self.qos_trust_default:
                cfg.append(f"mls qos trust {self.qos_trust_default.value}")

            # DSCP and CoS maps
            for dscp, internal_dscp in self.qos_dscp_map.items():
                cfg.append(f"mls qos map dscp {dscp} to dscp {internal_dscp}")

            for cos, internal_dscp in self.qos_cos_map.items():
                cfg.append(f"mls qos map cos {cos} to dscp {internal_dscp}")

            # Queue configuration
            for queue in self.qos_queues:
                if queue.priority > 0:
                    cfg.append(f"priority-queue out")
                    break

            for queue in self.qos_queues:
                if queue.bandwidth > 0:
                    cfg.append(f"wrr-queue bandwidth {' '.join(str(q.bandwidth) for q in self.qos_queues)}")
                    break

        # ----------- 6. MONITORING ------------------------------------- #
        # Logging
        if self.logging_enabled:
            cfg.append(f"logging buffered {self.logging_buffer_size}")
            cfg.append(f"logging console {self.logging_level.value}")

            if self.logging_host:
                cfg.append(f"logging host {self.logging_host}")
                cfg.append(f"logging trap {self.logging_level.value}")

        # SNMP
        if self.snmp_enabled:
            cfg.append(f"snmp-server community {self.snmp_community_ro} RO")

            if self.snmp_community_rw:
                cfg.append(f"snmp-server community {self.snmp_community_rw} RW")

            if self.snmp_location:
                cfg.append(f"snmp-server location {self.snmp_location}")

            if self.snmp_contact:
                cfg.append(f"snmp-server contact {self.snmp_contact}")

            if self.snmp_traps_enabled:
                cfg.append("snmp-server enable traps")

        # SPAN
        if self.span_enabled and self.span_source_ports and self.span_destination_port:
            cfg.append("monitor session 1 source interface " + ", ".join(self.span_source_ports))
            cfg.append(f"monitor session 1 destination interface {self.span_destination_port}")

        # NetFlow
        if self.netflow_enabled and self.netflow_collector:
            cfg.append("ip flow-export version 9")
            cfg.append(f"ip flow-export destination {self.netflow_collector}")

        # ----------- 7. ADVANCED LAYER2 -------------------------------- #
        # UDLD
        if self.udld_mode != UDLDMode.DISABLED:
            cfg.append(f"udld {self.udld_mode.value}")

        # IGMP/MLD Snooping
        if not self.igmp_snooping_enabled:
            cfg.append("no ip igmp snooping")

        if self.mld_snooping_enabled:
            cfg.append("ipv6 mld snooping")

        # MAC Table
        if self.mac_address_table_aging_time != 300:
            cfg.append(f"mac address-table aging-time {self.mac_address_table_aging_time}")

        # Jumbo Frames
        if self.jumbo_frames_enabled:
            cfg.append(f"system mtu {self.system_mtu}")

        # ----------- 8. SYSTEM SETTINGS -------------------------------- #
        # SSH and Authentication
        if self.enable_ssh:
            cfg.append("crypto key generate rsa modulus 2048")
            cfg.append("ip ssh version 2")

        if self.enable_secret:
            cfg.append("enable secret 0 Cisco123")

        # AAA
        if self.aaa_new_model:
            cfg.append("aaa new-model")

            if self.aaa_authentication_enabled:
                cfg.append("aaa authentication login default local")

            if self.aaa_authorization_enabled:
                cfg.append("aaa authorization exec default local")

            if self.aaa_accounting_enabled:
                cfg.append("aaa accounting exec default start-stop group tacacs+")

        # RADIUS/TACACS
        if self.radius_server:
            cfg.append(f"radius server main")
            cfg.append(f" address ipv4 {self.radius_server} auth-port 1812 acct-port 1813")
            if self.radius_key:
                cfg.append(f" key {self.radius_key}")

        if self.tacacs_server:
            cfg.append(f"tacacs server main")
            cfg.append(f" address ipv4 {self.tacacs_server}")
            if self.tacacs_key:
                cfg.append(f" key {self.tacacs_key}")

        # Energy Settings
        if self.energy_efficient_ethernet:
            cfg.append("power efficient-ethernet auto")

        # Error Recovery
        if self.monitoring_enabled:
            cfg.append("errdisable recovery cause all")
            cfg.append(f"errdisable recovery interval {self.errdisable_recovery_interval}")

        # ----------- MANAGEMENT SVI ---------------------------------- #
        cfg.extend([
            f"interface vlan {self.manager_vlan_id}",
            f" ip address {self.manager_ip}",
            " no shutdown",
            " exit",
            f"ip default-gateway {self.default_gateway}",
        ])

        # ----------- CHILD TEMPLATES --------------------------------- #
        if nested_templates:
            for tmpl in nested_templates:
                if not hasattr(tmpl, "generate_config"):
                    continue
                for line in tmpl.generate_config():
                    cfg.append(f"{line}")

        # ----------- END & SAVE -------------------------------------- #
        cfg.extend([
            "end",
            "write memory",
        ])

        return cfg

    def _vlan_list_to_ranges(self, vlan_list: List[int]) -> List[str]:
        """Convert a list of VLAN IDs to condensed ranges for CLI commands.

        Args:
            vlan_list: List of VLAN IDs

        Returns:
            List of strings in the format "1,2,3-5,7-10"
        """
        if not vlan_list:
            return []

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

        return ranges