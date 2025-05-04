# 'src/forms/AccessTemplateForm.py'
"""PySide6 widget that edits an *access-port template* in three tabs
(Basic | Security | Advanced).

The tab set is **always visible**, even in "New Template" mode
(*editable_interfaces=True*).  All widget attributes keep the historical
names expected by *FormProcessor*, so no downstream changes are required.

Added in 2025-05:
* Color picker for visual identification in the UI
"""
from PySide6 import QtWidgets, QtGui

from src.ui.color_picker import ColorPicker


class AccessTemplateForm(QtWidgets.QWidget):
    """GUI helper to create / edit *AccessTemplate* instances."""

    # ------------------------------------------------------------------ #
    def __init__(self, parent=None, instance=None, *, editable_interfaces: bool = False):
        super().__init__(parent)
        self._editable_interfaces = editable_interfaces
        self._build_ui()
        if instance is not None:
            self.load_from_instance(instance)

    # ================================================================== #
    #                           UI construction                          #
    # ================================================================== #
    def _build_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        root.addWidget(self.tabs)

        # ------------------------------ BASIC -------------------------- #
        basic = QtWidgets.QWidget()
        b = QtWidgets.QFormLayout(basic)

        self.interfaces_input = QtWidgets.QLineEdit()
        self.interfaces_input.setReadOnly(not self._editable_interfaces)

        self.vlan_id_input = QtWidgets.QSpinBox()
        self.vlan_id_input.setRange(1, 4094)

        self.description_input = QtWidgets.QLineEdit()

        # Add color picker
        self.color_picker = ColorPicker()

        self.voice_vlan_input = QtWidgets.QSpinBox()
        self.voice_vlan_input.setRange(0, 4094)

        self.poe_inline_input = QtWidgets.QLineEdit()
        self.speed_combo = QtWidgets.QComboBox()
        self.speed_combo.addItems(["auto", "10", "100", "1000"])
        self.duplex_combo = QtWidgets.QComboBox()
        self.duplex_combo.addItems(["auto", "half", "full"])
        self.auto_mdix_checkbox = QtWidgets.QCheckBox("Auto-MDIX")

        self.portfast_checkbox = QtWidgets.QCheckBox("STP PortFast")

        b.addRow("Interfaces:", self.interfaces_input)
        b.addRow("VLAN ID:", self.vlan_id_input)
        b.addRow("Description:", self.description_input)
        b.addRow("Template Color:", self.color_picker)
        b.addRow("Voice VLAN (0 = off):", self.voice_vlan_input)
        b.addRow("PoE inline:", self.poe_inline_input)
        b.addRow("Speed:", self.speed_combo)
        b.addRow("Duplex:", self.duplex_combo)
        b.addRow(self.auto_mdix_checkbox)
        b.addRow(self.portfast_checkbox)
        self.tabs.addTab(basic, "Podstawowe")

        # ----------------------------- SECURITY ------------------------ #
        sec = QtWidgets.QWidget()
        s = QtWidgets.QFormLayout(sec)

        self.port_security_checkbox = QtWidgets.QCheckBox("Port-Security")
        self.max_mac_input = QtWidgets.QSpinBox()
        self.max_mac_input.setRange(1, 64)
        self.violation_action_combo = QtWidgets.QComboBox()
        self.violation_action_combo.addItems(["shutdown", "restrict", "protect"])
        self.sticky_mac_checkbox = QtWidgets.QCheckBox("Sticky MAC")

        self.bpdu_guard_checkbox = QtWidgets.QCheckBox("BPDU Guard")
        self.bpdu_filter_checkbox = QtWidgets.QCheckBox("BPDU Filter")
        self.loop_guard_checkbox = QtWidgets.QCheckBox("Loop Guard")
        self.root_guard_checkbox = QtWidgets.QCheckBox("Root Guard")

        self.private_vlan_host_checkbox = QtWidgets.QCheckBox("Private-VLAN host")
        self.protected_port_checkbox = QtWidgets.QCheckBox("Protected port")

        self.qos_trust_combo = QtWidgets.QComboBox()
        self.qos_trust_combo.addItems(["--", "cos", "dscp"])
        self.service_policy_input = QtWidgets.QLineEdit()

        self.dot1x_checkbox = QtWidgets.QCheckBox("802.1X")
        self.mab_checkbox = QtWidgets.QCheckBox("MAB")

        s.addRow(self.port_security_checkbox)
        s.addRow("Max MACs:", self.max_mac_input)
        s.addRow("Violation:", self.violation_action_combo)
        s.addRow(self.sticky_mac_checkbox)
        s.addRow(self.bpdu_guard_checkbox, self.bpdu_filter_checkbox)
        s.addRow(self.loop_guard_checkbox, self.root_guard_checkbox)
        s.addRow(self.private_vlan_host_checkbox, self.protected_port_checkbox)
        s.addRow("QoS trust:", self.qos_trust_combo)
        s.addRow("Service-policy in:", self.service_policy_input)
        s.addRow(self.dot1x_checkbox, self.mab_checkbox)
        self.tabs.addTab(sec, "Security")

        # ---------------------------- ADVANCED ------------------------- #
        adv = QtWidgets.QWidget()
        a = QtWidgets.QFormLayout(adv)

        self.storm_control_checkbox = QtWidgets.QCheckBox("Storm-Control")
        self.storm_unit_pps = QtWidgets.QCheckBox("Use PPS unit")

        self.broadcast_min_input = QtWidgets.QDoubleSpinBox()
        self.broadcast_max_input = QtWidgets.QDoubleSpinBox()
        self.multicast_min_input = QtWidgets.QDoubleSpinBox()
        self.multicast_max_input = QtWidgets.QDoubleSpinBox()
        self.unknown_unicast_min_input = QtWidgets.QDoubleSpinBox()
        self.unknown_unicast_max_input = QtWidgets.QDoubleSpinBox()

        self.errdisable_timeout_input = QtWidgets.QSpinBox()
        self.errdisable_timeout_input.setRange(0, 600)

        self.dhcp_rate_input = QtWidgets.QSpinBox()
        self.dhcp_rate_input.setRange(0, 4096)
        self.arp_rate_input = QtWidgets.QSpinBox()
        self.arp_rate_input.setRange(0, 4096)

        a.addRow(self.storm_control_checkbox, self.storm_unit_pps)
        a.addRow("Bcast min %", self.broadcast_min_input)
        a.addRow("Bcast max %", self.broadcast_max_input)
        a.addRow("Mcast min %", self.multicast_min_input)
        a.addRow("Mcast max %", self.multicast_max_input)
        a.addRow("U-Ucast min %", self.unknown_unicast_min_input)
        a.addRow("U-Ucast max %", self.unknown_unicast_max_input)
        a.addRow("Errdisable timeout [s]:", self.errdisable_timeout_input)
        a.addRow("DHCP snoop rate [pps]:", self.dhcp_rate_input)
        a.addRow("ARP inspect rate [pps]:", self.arp_rate_input)
        self.tabs.addTab(adv, "Zaawansowane")

        # -------------------- dynamic enables -------------------------- #
        self.port_security_checkbox.toggled.connect(self._upd_ps_fields)
        self.storm_control_checkbox.toggled.connect(self._upd_storm_fields)
        self._upd_ps_fields()
        self._upd_storm_fields()

        # legacy alias (only one needed for retro-compat)
        self.voice_vlan_spin = self.voice_vlan_input

    # ------------------------------------------------------------------ #
    #                         helper slots                               #
    # ------------------------------------------------------------------ #
    def _upd_ps_fields(self) -> None:
        enabled = self.port_security_checkbox.isChecked()
        for w in (self.max_mac_input, self.violation_action_combo,
                  self.sticky_mac_checkbox):
            w.setEnabled(enabled)

    def _upd_storm_fields(self) -> None:
        enabled = self.storm_control_checkbox.isChecked()
        for w in (self.storm_unit_pps,
                  self.broadcast_min_input, self.broadcast_max_input,
                  self.multicast_min_input, self.multicast_max_input,
                  self.unknown_unicast_min_input, self.unknown_unicast_max_input):
            w.setEnabled(enabled)

    # ================================================================== #
    #                        data synchronisation                        #
    # ================================================================== #
    def load_from_instance(self, inst) -> None:
        """Populate widgets from an *AccessTemplate* instance."""
        self.interfaces_input.setText(",".join(inst.interfaces))
        self.vlan_id_input.setValue(inst.vlan_id)
        self.description_input.setText(inst.description or "")
        self.voice_vlan_input.setValue(inst.voice_vlan or 0)

        # Set color if available
        if hasattr(inst, 'color'):
            # Set text to color hex value
            self.color_picker.current_color = QtGui.QColor(inst.color)
            self.color_picker.color_button.setText(inst.color.upper())
            # Apply color to button
            self.color_picker.update_color_ui()

        # basic
        self.poe_inline_input.setText(inst.poe_inline or "")
        self.speed_combo.setCurrentText(inst.speed)
        self.duplex_combo.setCurrentText(inst.duplex)
        self.auto_mdix_checkbox.setChecked(inst.auto_mdix)
        self.portfast_checkbox.setChecked(inst.spanning_tree_portfast)

        # security
        self.port_security_checkbox.setChecked(inst.port_security_enabled)
        self.max_mac_input.setValue(inst.max_mac_addresses)
        self.violation_action_combo.setCurrentText(inst.violation_action)
        self.sticky_mac_checkbox.setChecked(inst.sticky_mac)

        self.bpdu_guard_checkbox.setChecked(inst.bpdu_guard)
        self.bpdu_filter_checkbox.setChecked(inst.bpdu_filter)
        self.loop_guard_checkbox.setChecked(inst.loop_guard)
        self.root_guard_checkbox.setChecked(inst.root_guard)

        self.private_vlan_host_checkbox.setChecked(inst.private_vlan_host)
        self.protected_port_checkbox.setChecked(inst.protected_port)

        self.qos_trust_combo.setCurrentText(inst.qos_trust or "--")
        self.service_policy_input.setText(inst.service_policy or "")
        self.dot1x_checkbox.setChecked(inst.dot1x)
        self.mab_checkbox.setChecked(inst.mab)

        # advanced / storm-control
        storm_any = any([
            inst.storm_control_broadcast_min, inst.storm_control_broadcast_max,
            inst.storm_control_multicast_min, inst.storm_control_multicast_max,
            inst.storm_control_unknown_unicast_min, inst.storm_control_unknown_unicast_max,
        ])
        self.storm_control_checkbox.setChecked(storm_any)
        self.storm_unit_pps.setChecked(inst.storm_control_unit_pps)

        self.broadcast_min_input.setValue(inst.storm_control_broadcast_min or 0.0)
        self.broadcast_max_input.setValue(inst.storm_control_broadcast_max or 0.0)
        self.multicast_min_input.setValue(inst.storm_control_multicast_min or 0.0)
        self.multicast_max_input.setValue(inst.storm_control_multicast_max or 0.0)
        self.unknown_unicast_min_input.setValue(inst.storm_control_unknown_unicast_min or 0.0)
        self.unknown_unicast_max_input.setValue(inst.storm_control_unknown_unicast_max or 0.0)

        self.errdisable_timeout_input.setValue(inst.errdisable_timeout or 0)
        self.dhcp_rate_input.setValue(inst.dhcp_snoop_rate or 0)
        self.arp_rate_input.setValue(inst.arp_inspection_rate or 0)