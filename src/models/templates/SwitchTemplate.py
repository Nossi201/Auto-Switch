"""Global Cisco‐switch template class.

Now supports three feature groups that match the new UI tabs:

* **Basic** – existing hostname / VLAN / SVI options (unchanged)
* **Security** – SSH + AAA, enable‐secret, SNMP, remote syslog
* **Advanced** – global STP guards, DHCP Snooping + DAI, QoS, monitoring

The *generate_config()* method renders only the commands that are explicitly
enabled, keeping the output minimal but deterministic.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, List as LList


@dataclass
class SwitchTemplate:
    """Device-level settings for a Cisco chassis."""
    # ---------------------------- basic -------------------------------- #
    hostname: str = "Switch"
    vlan_list: List[int] = field(default_factory=lambda: [1])
    spanning_tree_mode: str = "pvst"              # pvst | rapid-pvst | mst
    manager_vlan_id: int = 1
    manager_ip: str = "192.168.1.1 255.255.255.0"
    default_gateway: str = "192.168.1.254"

    # --------------------------- security ------------------------------ #
    enable_ssh: bool = False                      # ip ssh / aaa new-model
    enable_secret: bool = False                   # dummy password “Cisco123”
    snmp_enabled: bool = False
    logging_host: Optional[str] = None

    # --------------------------- advanced ------------------------------ #
    bpduguard_default: bool = False               # + loopguard default
    dhcp_snoop_enabled: bool = False              # incl. DAI
    qos_global: bool = False                      # mls qos
    monitoring_enabled: bool = False              # errdisable, EEM stub

    # ------------------------------------------------------------------ #
    def generate_config(
        self,
        nested_templates: Optional[Sequence[object]] = None,
    ) -> LList[str]:
        """Return full IOS CLI ready to paste into the terminal."""
        cfg: LList[str] = [
            "enable",
            "configure terminal",
            f"  hostname {self.hostname}",
            f"  spanning-tree mode {self.spanning_tree_mode}",
        ]

        # ----------- SECURITY ---------------------------------------- #
        if self.enable_ssh:
            cfg.extend(
                [
                    "  ip domain-name local",
                    "  crypto key generate rsa modulus 2048",
                    "  ip ssh version 2",
                    "  aaa new-model",
                ]
            )

        if self.enable_secret:
            cfg.append("  enable secret 0 Cisco123")

        if self.snmp_enabled:
            cfg.extend(
                [
                    "  snmp-server community public RO",
                    "  snmp-server enable traps",
                ]
            )

        if self.logging_host:
            cfg.append(f"  logging host {self.logging_host}")

        # ----------- ADVANCED ---------------------------------------- #
        if self.bpduguard_default:
            cfg.extend(
                [
                    "  spanning-tree portfast default",
                    "  spanning-tree bpduguard default",
                    "  spanning-tree loopguard default",
                ]
            )

        if self.dhcp_snoop_enabled:
            cfg.extend(
                [
                    "  ip dhcp snooping",
                    "  ip dhcp snooping vlan 1-4094",
                    "  ip arp inspection vlan 1-4094",
                ]
            )

        if self.qos_global:
            cfg.append("  mls qos")

        if self.monitoring_enabled:
            cfg.extend(
                [
                    "  errdisable recovery cause all",
                    "  errdisable recovery interval 300",
                ]
            )

        # ----------- MANAGEMENT SVI ---------------------------------- #
        cfg.extend(
            [
                f"  vlan {self.manager_vlan_id}",
                "   exit",
                f"  interface vlan {self.manager_vlan_id}",
                f"    ip address {self.manager_ip}",
                "    no shutdown",
                "   exit",
                f"  ip default-gateway {self.default_gateway}",
            ]
        )

        # ----------- CHILD TEMPLATES --------------------------------- #
        if nested_templates:
            for tmpl in nested_templates:
                if not hasattr(tmpl, "generate_config"):
                    continue
                for line in tmpl.generate_config():
                    cfg.append(f"  {line}")

        # ----------- END & SAVE -------------------------------------- #
        cfg.extend(
            [
                "end",
                "copy running-config startup-config",
            ]
        )
        return cfg
