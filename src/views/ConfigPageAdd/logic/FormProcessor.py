# 'src/views/ConfigPageAdd/logic/FormProcessor.py'
"""Builds template instances from PySide6 forms.

Access-Template branch extended with every new checkbox / field so that
no *unexpected-keyword* errors appear.

Updated in 2025-05 to handle new color field for templates and proper enum handling.
"""
from src.models.templates.AccessTemplate import AccessTemplate, PowerInlineMode, ViolationAction, QoSTrustState
from src.models.templates.TrunkTemplate import TrunkTemplate, EncapsulationType, DTPMode
from src.models.templates.RouterTemplate import RouterTemplate
from src.models.templates.SwitchTemplate import SwitchTemplate, SpanningTreeMode, VTPMode


def _bool(form, attr):
    """Return *form.<attr>.isChecked()* safely."""
    return getattr(form, attr).isChecked() if hasattr(form, attr) else False


def build_template_instance(form):
    """Return filled template instance or *None* when form is not recognised."""
    if form is None:
        return None

    # --------------------------- ACCESS --------------------------- #
    if hasattr(form, "interfaces_input") and hasattr(form, "vlan_id_input"):
        # Get color value if the color picker exists
        color_value = form.color_picker.get_value() if hasattr(form, "color_picker") else "#4287f5"

        # Handle PowerInlineMode enum
        poe_inline_mode = PowerInlineMode.AUTO  # Default
        if hasattr(form, "poe_inline_combo"):
            try:
                poe_inline_mode = PowerInlineMode(form.poe_inline_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        # Handle ViolationAction enum
        violation_action = ViolationAction.SHUTDOWN  # Default
        if hasattr(form, "violation_action_combo"):
            try:
                violation_action = ViolationAction(form.violation_action_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        # Handle QoSTrustState enum
        qos_trust = None
        if hasattr(form, "qos_trust_combo") and form.qos_trust_combo.currentText() != "--":
            try:
                qos_trust = QoSTrustState(form.qos_trust_combo.currentText())
            except ValueError:
                pass  # Keep None if invalid

        return AccessTemplate(
            # base
            interfaces=[s.strip() for s in form.interfaces_input.text().split(",") if s.strip()],
            vlan_id=form.vlan_id_input.value(),
            description=form.description_input.text() or None,
            color=color_value,  # Add color field
            voice_vlan=form.voice_vlan_input.value() or None,

            # security
            port_security_enabled=_bool(form, "port_security_checkbox"),
            max_mac_addresses=form.max_mac_input.value(),
            violation_action=violation_action,
            sticky_mac=_bool(form, "sticky_mac_checkbox"),

            # STP
            spanning_tree_portfast=_bool(form, "spanning_tree_portfast_checkbox"),
            bpdu_guard=_bool(form, "bpdu_guard_checkbox"),
            bpdu_filter=_bool(form, "bpdu_filter_checkbox"),
            loop_guard=_bool(form, "loop_guard_checkbox"),
            root_guard=_bool(form, "root_guard_checkbox"),

            # private-VLAN / protected-port
            private_vlan_host=_bool(form, "private_vlan_host_checkbox"),
            protected_port=_bool(form, "protected_port_checkbox"),

            # QoS / NAC
            qos_trust=qos_trust,
            service_policy_input=form.service_policy_input.text() or None,
            mab=_bool(form, "mab_checkbox"),
            dot1x=_bool(form, "dot1x_checkbox"),

            # PoE
            poe_inline=poe_inline_mode,
            poe_enabled=_bool(form, "poe_enabled_checkbox") if hasattr(form, "poe_enabled_checkbox") else True,

            # storm-control
            storm_control_broadcast_min=form.broadcast_min_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_broadcast_max=form.broadcast_max_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_multicast_min=form.multicast_min_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_multicast_max=form.multicast_max_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_unknown_unicast_min=form.unknown_unicast_min_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_unknown_unicast_max=form.unknown_unicast_max_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_unit_pps=_bool(form, "storm_unit_pps"),

            # physical
            speed=form.speed_combo.currentText(),
            duplex=form.duplex_combo.currentText(),
            auto_mdix=_bool(form, "auto_mdix_checkbox"),

            # errdisable / limits
            errdisable_timeout=form.errdisable_timeout_input.value() if hasattr(form,
                                                                                "errdisable_timeout_input") else None,
            dhcp_snoop_rate=form.dhcp_snoop_rate_input.value() if hasattr(form, "dhcp_snoop_rate_input") else None,
            arp_inspection_rate=form.arp_inspection_rate_input.value() if hasattr(form,
                                                                                  "arp_inspection_rate_input") else None,
        )

        # Fragment metody build_template_instance dla obsługi TrunkTemplate

        # ---------------- TRUNK ----------------- #
    if hasattr(form, "native_vlan_input"):
        storm_on = _bool(form, "storm_control_checkbox")
        # Get color value if the color picker exists
        color_value = form.color_picker.get_value() if hasattr(form, "color_picker") else "#8A2BE2"

        # Handle EncapsulationType enum
        encapsulation = EncapsulationType.DOT1Q  # Default
        if hasattr(form, "encapsulation_combo"):
            try:
                encapsulation = EncapsulationType(form.encapsulation_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        # Handle DTPMode enum
        dtp_mode = None
        if hasattr(form, "dtp_mode_combo") and form.dtp_mode_combo.currentText() != "--":
            try:
                dtp_mode = DTPMode(form.dtp_mode_combo.currentText())
            except ValueError:
                pass  # Keep None if invalid

        # Tworzymy instancję TrunkTemplate bez parametru color
        trunk_template = TrunkTemplate(
            interfaces=[s.strip() for s in form.interfaces_input.text().split(",") if s.strip()],
            allowed_vlans=[int(v.strip()) for v in form.allowed_vlans_input.text().split(",") if
                           v.strip().isdigit()],
            native_vlan=form.native_vlan_input.value(),
            description=form.description_input.text() or None,

            # basic flags
            pruning_enabled=_bool(form, "pruning_checkbox"),
            spanning_tree_guard_root=_bool(form, "stp_guard_checkbox"),
            encapsulation=encapsulation,
            dtp_mode=dtp_mode,
            nonegotiate=_bool(form, "nonegotiate_checkbox"),
            spanning_tree_portfast=_bool(form, "portfast_checkbox"),

            # security
            dhcp_snooping_trust=_bool(form, "dhcp_trust_checkbox"),
            qos_trust=(None if form.qos_trust_combo.currentText() == "--" else form.qos_trust_combo.currentText()),

            # storm-control
            storm_control_broadcast_min=form.broadcast_min_input.value() if storm_on else None,
            storm_control_broadcast_max=form.broadcast_max_input.value() if storm_on else None,
            storm_control_multicast_min=form.multicast_min_input.value() if storm_on else None,
            storm_control_multicast_max=form.multicast_max_input.value() if storm_on else None,
            storm_control_unknown_unicast_min=form.unknown_unicast_min_input.value() if storm_on else None,
            storm_control_unknown_unicast_max=form.unknown_unicast_max_input.value() if storm_on else None,
            storm_control_unit_pps=_bool(form, "storm_unit_pps"),

            # L1 / timers
            speed=form.speed_combo.currentText(),
            duplex=form.duplex_combo.currentText(),
            auto_mdix=_bool(form, "auto_mdix_checkbox"),
            errdisable_timeout=form.errdisable_timeout_input.value() or None,

            # etherchannel
            channel_group=(form.channel_group_input.value() or None),
            channel_group_mode=(None if form.channel_mode_combo.currentText() == "--"
                                else form.channel_mode_combo.currentText()),
        )

        # Ustawiamy atrybut color po utworzeniu instancji
        if hasattr(trunk_template, 'color'):
            setattr(trunk_template, 'color', color_value)

        return trunk_template

    # --------------------------- ROUTER --------------------------- #
    if hasattr(form, "hostname_input") and hasattr(form, "manager_vlan_id_combo"):
        # Extract VLAN IDs from the VLAN table if it exists
        vlans = []
        if hasattr(form, "vlan_table"):
            for row in range(form.vlan_table.rowCount()):
                vlan_id_item = form.vlan_table.item(row, 0)
                vlan_name_item = form.vlan_table.item(row, 1)

                if vlan_id_item:
                    try:
                        vlan_id = int(vlan_id_item.text())
                        vlan_name = vlan_name_item.text() if vlan_name_item else f"VLAN{vlan_id}"
                        # Tworzymy obiekt VLAN zamiast słownika
                        from src.models.templates.SwitchTemplate import VLAN
                        vlans.append(VLAN(id=vlan_id, name=vlan_name))
                    except ValueError:
                        pass

        # Handle SpanningTreeMode enum
        spanning_tree_mode = SpanningTreeMode.RAPID_PVST  # Default
        if hasattr(form, "spanning_tree_mode_combo"):
            try:
                spanning_tree_mode = SpanningTreeMode(form.spanning_tree_mode_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        # Handle VTPMode enum
        vtp_mode = VTPMode.OFF  # Default
        if hasattr(form, "vtp_mode_combo"):
            try:
                vtp_mode = VTPMode(form.vtp_mode_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        return SwitchTemplate(
            hostname=form.hostname_input.text() or "Switch",
            # Use 'vlans' list with proper VLAN objects
            vlans=vlans,
            spanning_tree_mode=spanning_tree_mode,
            manager_vlan_id=int(form.manager_vlan_id_combo.currentText()),
            manager_ip=form.manager_ip_input.text().strip(),
            default_gateway=form.default_gateway_input.text().strip(),
            vtp_mode=vtp_mode,
            vtp_domain=form.vtp_domain_input.text() if hasattr(form, "vtp_domain_input") else None,
        )

    # --------------------------- SWITCH --------------------------- #
    if hasattr(form, "hostname_input") and hasattr(form, "manager_vlan_id_combo"):
        # Extract VLAN IDs from the VLAN table if it exists
        vlans = []
        if hasattr(form, "vlan_table"):
            for row in range(form.vlan_table.rowCount()):
                vlan_id_item = form.vlan_table.item(row, 0)
                vlan_name_item = form.vlan_table.item(row, 1)

                if vlan_id_item:
                    try:
                        vlan_id = int(vlan_id_item.text())
                        vlan_name = vlan_name_item.text() if vlan_name_item else f"VLAN{vlan_id}"
                        vlans.append({"id": vlan_id, "name": vlan_name})
                    except ValueError:
                        pass

        # Handle SpanningTreeMode enum
        spanning_tree_mode = SpanningTreeMode.RAPID_PVST  # Default
        if hasattr(form, "spanning_tree_mode_combo"):
            try:
                spanning_tree_mode = SpanningTreeMode(form.spanning_tree_mode_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        # Handle VTPMode enum
        vtp_mode = VTPMode.OFF  # Default
        if hasattr(form, "vtp_mode_combo"):
            try:
                vtp_mode = VTPMode(form.vtp_mode_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        return SwitchTemplate(
            hostname=form.hostname_input.text() or "Switch",
            # Use 'vlans' list with proper format
            vlans=vlans,
            spanning_tree_mode=spanning_tree_mode,
            manager_vlan_id=int(form.manager_vlan_id_combo.currentText()),
            manager_ip=form.manager_ip_input.text().strip(),
            default_gateway=form.default_gateway_input.text().strip(),
            vtp_mode=vtp_mode,
            vtp_domain=form.vtp_domain_input.text() if hasattr(form, "vtp_domain_input") else None,
        )

    return None