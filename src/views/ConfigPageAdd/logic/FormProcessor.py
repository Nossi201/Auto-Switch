#src/views/ConfigPageAdd/logic/FormProcessor.py
"""Builds template dataclass instances from PySide6 forms.

Extended in the *Trunk Template* branch to persist additional fields introduced
in the new UI (nonegotiate, dynamic DTP mode, STP PortFast trunk).
"""

from src.models.templates.AccessTemplate import AccessTemplate
from src.models.templates.TrunkTemplate import TrunkTemplate
from src.models.templates.RouterTemplate import RouterTemplate
from src.models.templates.SwitchTemplate import SwitchTemplate


def build_template_instance(form):
    """Return a filled template instance based on the supplied form widget."""
    if form is None:
        return None

    # ----------------------------- Access ----------------------------- #
    if hasattr(form, "interfaces_input") and hasattr(form, "vlan_id_input"):
        return AccessTemplate(
            interfaces=[s.strip() for s in form.interfaces_input.text().split(",") if s.strip()],
            vlan_id=form.vlan_id_input.value(),
            description=form.description_input.text() or None,
            port_security_enabled=form.port_security_checkbox.isChecked(),
            max_mac_addresses=form.max_mac_input.value(),
            violation_action=form.violation_action_combo.currentText(),
            voice_vlan=form.voice_vlan_input.value() if form.voice_vlan_input.value() > 0 else None,
            sticky_mac=form.sticky_mac_checkbox.isChecked(),
            storm_control_broadcast_min=form.broadcast_min_input.value() if form.storm_control_checkbox.isChecked() else None,
            storm_control_broadcast_max=form.broadcast_max_input.value() if form.storm_control_checkbox.isChecked() else None,
            storm_control_multicast_min=form.multicast_min_input.value() if form.storm_control_checkbox.isChecked() else None,
            storm_control_multicast_max=form.multicast_max_input.value() if form.storm_control_checkbox.isChecked() else None,
            spanning_tree_portfast=form.portfast_checkbox.isChecked(),
        )

    # ------------------------------ Trunk ----------------------------- #
    if hasattr(form, "allowed_vlans_input") and hasattr(form, "native_vlan_input"):
        return TrunkTemplate(
            interfaces=[s.strip() for s in form.interfaces_input.text().split(",") if s.strip()],
            allowed_vlans=[int(v.strip()) for v in form.allowed_vlans_input.text().split(",") if v.strip().isdigit()],
            native_vlan=form.native_vlan_input.value(),
            description=form.description_input.text() or None,
            pruning_enabled=form.pruning_checkbox.isChecked(),
            spanning_tree_guard_root=form.stp_guard_checkbox.isChecked(),
            encapsulation=form.encapsulation_combo.currentText(),
            # --- new fields ---
            nonegotiate=form.nonegotiate_checkbox.isChecked() if hasattr(form, "nonegotiate_checkbox") else False,
            dtp_mode=form.dtp_mode_combo.currentText()
            if hasattr(form, "dtp_mode_combo") and form.dtp_mode_combo.currentText() != "--"
            else None,
            spanning_tree_portfast=form.portfast_checkbox.isChecked() if hasattr(form, "portfast_checkbox") else False,
        )

    # ------------------------------ Router ---------------------------- #
    if hasattr(form, "interface_name_input") and hasattr(form, "interface_ip_input"):
        iface_name = form.interface_name_input.text().strip()
        iface_ip = form.interface_ip_input.text().strip()
        iface_mask = form.interface_mask_input.text().strip()
        interfaces = (
            {iface_name: {"ip": iface_ip, "mask": iface_mask}}
            if iface_name and iface_ip and iface_mask
            else {}
        )
        return RouterTemplate(
            hostname=form.hostname_input.text() or "Router",
            interfaces=interfaces,
            routing_protocols=[p.strip() for p in form.routing_protocols_input.text().split(",") if p.strip()],
            static_routes=[],
        )

    # ------------------------------ Switch ---------------------------- #
    if hasattr(form, "vlan_list_input") and hasattr(form, "spanning_tree_mode_combo"):
        return SwitchTemplate(
            hostname=form.hostname_input.text() or "Switch",
            vlan_list=[int(v.strip()) for v in form.vlan_list_input.text().split(",") if v.strip().isdigit()],
            spanning_tree_mode=form.spanning_tree_mode_combo.currentText(),
            manager_vlan_id=int(form.manager_vlan_id_combo.currentText()),
            manager_ip=form.manager_ip_input.text().strip(),
            default_gateway=form.default_gateway_input.text().strip(),
        )

    return None
