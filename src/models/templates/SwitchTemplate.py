#src/models/templates/SwitchTemplate.py
"""Global Cisco switch template with hierarchical CLI generator.

`generate_config()` now accepts an **optional positional list** of template
instances (AccessTemplate, TrunkTemplate, etc.).  Those child templates are
rendered *inside* configuration mode, indented two spaces, **after** the
device-wide commands and before the final `end / copy` block.

Call signature
--------------
generate_config(nested_templates: list | None = None) -> list[str]

Ordering rule applied by callers:
* AccessTemplate objects first
* then TrunkTemplate objects
* (any future template types could follow)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Sequence


@dataclass
class SwitchTemplate:
    """Device-level settings for a Cisco switch chassis."""
    hostname: str = "Switch"

    # VLAN list is bookkeeping only (AccessTemplate provisions VLANs)
    vlan_list: List[int] = field(default_factory=lambda: [1])

    # Spanning-tree
    spanning_tree_mode: str = "pvst"            # pvst | rapid-pvst | mst

    # Management SVI
    manager_vlan_id: int = 1
    manager_ip: str = "192.168.1.1 255.255.255.0"
    default_gateway: str = "192.168.1.254"

    # ------------------------------------------------------------------ #
    def generate_config(self,
                        nested_templates: Optional[Sequence[object]] = None
                        ) -> List[str]:
        """
        Produce a ready-to-paste block of CLI commands.

        Parameters
        ----------
        nested_templates : Sequence[object] | None
            Templates whose configs should be embedded within *configure
            terminal* (interfaces, trunks, etc.).  The caller is expected to
            sort them in the desired order.
        """
        cfg: List[str] = [
            "enable",
            "configure terminal",
            f"  hostname {self.hostname}",
            f"  spanning-tree mode {self.spanning_tree_mode}",
            f"  vlan {self.manager_vlan_id}",
            "   exit",
            f"  interface vlan {self.manager_vlan_id}",
            f"    ip address {self.manager_ip}",
            "    no shutdown",
            "   exit",
            f"  ip default-gateway {self.default_gateway}",
        ]

        # ----- embed child templates (indented) -------------------- #
        if nested_templates:
            for tmpl in nested_templates:
                if not hasattr(tmpl, "generate_config"):
                    continue
                for line in tmpl.generate_config():
                    cfg.append(f"  {line}")        # 2-space indent inside conf-t

        # ----- exit & save ---------------------------------------- #
        cfg.extend([
            "end",
            "copy running-config startup-config",
        ])
        return cfg
