"""Builds template instances from PySide6 forms.

Access-Template branch extended with every new checkbox / field so that
no *unexpected-keyword* errors appear.
"""
from src.models.templates.AccessTemplate import AccessTemplate
from src.models.templates.TrunkTemplate import TrunkTemplate
from src.models.templates.RouterTemplate import RouterTemplate
from src.models.templates.SwitchTemplate import SwitchTemplate


def _bool(form, attr):
    """Return *form.<attr>.isChecked()* safely."""
    return getattr(form, attr).isChecked() if hasattr(form, attr) else False


def build_template_instance(form):
    """Return filled template instance or *None* when form is not recognised."""
    if form is None:
        return None

    # --------------------------- ACCESS --------------------------- #
    if hasattr(form, "interfaces_input") and hasattr(form, "vlan_id_input"):
        return AccessTemplate(
            # base
            interfaces=[s.strip() for s in form.interfaces_input.text().split(",") if s.strip()],
            vlan_id=form.vlan_id_input.value(),
            description=form.description_input.text() or None,
            voice_vlan=form.voice_vlan_input.value() or None,

            # security
            port_security_enabled=_bool(form, "port_security_checkbox"),
            max_mac_addresses=form.max_mac_input.value(),
            violation_action=form.violation_action_combo.currentText(),
            sticky_mac=_bool(form, "sticky_mac_checkbox"),

            # STP
            spanning_tree_portfast=_bool(form, "portfast_checkbox"),
            bpdu_guard=_bool(form, "bpdu_guard_checkbox"),
            bpdu_filter=_bool(form, "bpdu_filter_checkbox"),
            loop_guard=_bool(form, "loop_guard_checkbox"),
            root_guard=_bool(form, "root_guard_checkbox"),

            # private-VLAN / protected-port
            private_vlan_host=_bool(form, "private_vlan_host_checkbox"),
            protected_port=_bool(form, "protected_port_checkbox"),

            # QoS / NAC
            qos_trust=(None if form.qos_trust_combo.currentText() == "--"
                       else form.qos_trust_combo.currentText()),
            service_policy=form.service_policy_input.text() or None,
            mab=_bool(form, "mab_checkbox"),
            dot1x=_bool(form, "dot1x_checkbox"),

            # PoE
            poe_inline=form.poe_inline_input.text().strip() or None,

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
            errdisable_timeout=form.errdisable_timeout_input.value() or None,
            dhcp_snoop_rate=form.dhcp_rate_input.value() or None,
            arp_inspection_rate=form.arp_rate_input.value() or None,
        )

        # ---------------- TRUNK ----------------- #
    if hasattr(form, "native_vlan_input"):
        storm_on = _bool(form, "storm_control_checkbox")
        return TrunkTemplate(
            interfaces=[s.strip() for s in form.interfaces_input.text().split(",") if s.strip()],
            allowed_vlans=[int(v.strip()) for v in form.allowed_vlans_input.text().split(",") if
                           v.strip().isdigit()],
            native_vlan=form.native_vlan_input.value(),
            description=form.description_input.text() or None,

            # basic flags
            pruning_enabled=_bool(form, "pruning_checkbox"),
            spanning_tree_guard_root=_bool(form, "stp_guard_checkbox"),
            encapsulation=form.encapsulation_combo.currentText(),
            dtp_mode=(None if form.dtp_mode_combo.currentText() == "--" else form.dtp_mode_combo.currentText()),
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

    # --------------------------- ROUTER --------------------------- #
    if hasattr(form, "interface_name_input"):
        iface = form.interface_name_input.text().strip()
        ip   = form.interface_ip_input.text().strip()
        mask = form.interface_mask_input.text().strip()
        interfaces = {iface: {"ip": ip, "mask": mask}} if iface and ip and mask else {}
        return RouterTemplate(
            hostname=form.hostname_input.text() or "Router",
            interfaces=interfaces,
            routing_protocols=[p.strip() for p in form.routing_protocols_input.text().split(",") if p.strip()],
            static_routes=[],
        )

    # --------------------------- SWITCH --------------------------- #
    if hasattr(form, "vlan_list_input"):
        return SwitchTemplate(
            hostname=form.hostname_input.text() or "Switch",
            vlan_list=[int(v.strip()) for v in form.vlan_list_input.text().split(",") if v.strip().isdigit()],
            spanning_tree_mode=form.spanning_tree_mode_combo.currentText(),
            manager_vlan_id=int(form.manager_vlan_id_combo.currentText()),
            manager_ip=form.manager_ip_input.text().strip(),
            default_gateway=form.default_gateway_input.text().strip(),
        )

    return None
