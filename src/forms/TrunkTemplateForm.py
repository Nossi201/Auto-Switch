# 'src/forms/TrunkTemplateForm.py'
"""PySide6 GUI for TrunkTemplate – three categories (Basic | Security | Advanced).

Keeps legacy attribute names so *FormProcessor* continues to work.

Added in 2025-05:
* Color picker for visual identification in the UI
"""
from PySide6 import QtWidgets, QtGui

from src.ui.color_picker import ColorPicker


class TrunkTemplateForm(QtWidgets.QWidget):
    """Editor for TrunkTemplate."""

    def __init__(self, parent=None, instance=None, *, editable_interfaces=False):
        super().__init__(parent)
        self._editable_interfaces = editable_interfaces
        self._build_ui()
        if instance:
            self.load_from_instance(instance)

    # --------------------------- UI ---------------------------------- #
    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        root.addWidget(self.tabs)

        # --------------- BASIC --------------- #
        basic = QtWidgets.QWidget()
        b = QtWidgets.QFormLayout(basic)

        self.interfaces_input = QtWidgets.QLineEdit()
        self.interfaces_input.setReadOnly(not self._editable_interfaces)

        self.allowed_vlans_input = QtWidgets.QLineEdit()
        self.native_vlan_input = QtWidgets.QSpinBox()
        self.native_vlan_input.setRange(1, 4094)
        self.native_vlan_input.valueChanged.connect(self._ensure_native)

        self.description_input = QtWidgets.QLineEdit()

        # Add color picker
        self.color_picker = ColorPicker()

        self.encapsulation_combo = QtWidgets.QComboBox()
        self.encapsulation_combo.addItems(["dot1q", "isl"])
        self.dtp_mode_combo = QtWidgets.QComboBox()
        self.dtp_mode_combo.addItems(["--", "auto", "desirable"])
        self.nonegotiate_checkbox = QtWidgets.QCheckBox("Disable DTP (nonegotiate)")

        self.portfast_checkbox = QtWidgets.QCheckBox("STP PortFast (trunk)")

        b.addRow("Interfaces:", self.interfaces_input)
        b.addRow("Allowed VLANs:", self.allowed_vlans_input)
        b.addRow("Native VLAN:", self.native_vlan_input)
        b.addRow("Description:", self.description_input)
        b.addRow("Template Color:", self.color_picker)
        b.addRow("Encapsulation:", self.encapsulation_combo)
        b.addRow("DTP mode:", self.dtp_mode_combo)
        b.addRow(self.nonegotiate_checkbox)
        b.addRow(self.portfast_checkbox)
        self.tabs.addTab(basic, "Podstawowe")

        # -------------- SECURITY ------------- #
        sec = QtWidgets.QWidget()
        s = QtWidgets.QFormLayout(sec)

        self.pruning_checkbox = QtWidgets.QCheckBox("Enable VLAN Pruning")
        self.stp_guard_checkbox = QtWidgets.QCheckBox("Root Guard")
        self.dhcp_trust_checkbox = QtWidgets.QCheckBox("DHCP-snooping trust")
        self.qos_trust_combo = QtWidgets.QComboBox()
        self.qos_trust_combo.addItems(["--", "cos", "dscp"])

        s.addRow(self.pruning_checkbox)
        s.addRow(self.stp_guard_checkbox)
        s.addRow(self.dhcp_trust_checkbox)
        s.addRow("QoS trust:", self.qos_trust_combo)
        self.tabs.addTab(sec, "Security")

        # ------------- ADVANCED ------------- #
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

        self.speed_combo = QtWidgets.QComboBox()
        self.speed_combo.addItems(["auto", "10", "100", "1000"])
        self.duplex_combo = QtWidgets.QComboBox()
        self.duplex_combo.addItems(["auto", "half", "full"])
        self.auto_mdix_checkbox = QtWidgets.QCheckBox("Auto-MDIX")

        self.errdisable_timeout_input = QtWidgets.QSpinBox()
        self.errdisable_timeout_input.setRange(0, 600)

        self.channel_group_input = QtWidgets.QSpinBox()
        self.channel_group_input.setRange(0, 128)
        self.channel_mode_combo = QtWidgets.QComboBox()
        self.channel_mode_combo.addItems(["--", "on", "active", "passive"])

        a.addRow(self.storm_control_checkbox, self.storm_unit_pps)
        a.addRow("Bcast min", self.broadcast_min_input)
        a.addRow("Bcast max", self.broadcast_max_input)
        a.addRow("Mcast min", self.multicast_min_input)
        a.addRow("Mcast max", self.multicast_max_input)
        a.addRow("U-Ucast min", self.unknown_unicast_min_input)
        a.addRow("U-Ucast max", self.unknown_unicast_max_input)

        a.addRow("Speed:", self.speed_combo)
        a.addRow("Duplex:", self.duplex_combo)
        a.addRow(self.auto_mdix_checkbox)
        a.addRow("Errdisable timeout [s]:", self.errdisable_timeout_input)
        a.addRow("Channel-group:", self.channel_group_input)
        a.addRow("Channel mode:", self.channel_mode_combo)
        self.tabs.addTab(adv, "Zaawansowane")

        # toggles
        self.storm_control_checkbox.toggled.connect(self._upd_storm_fields)
        self._upd_storm_fields()

    # --------------------- helpers ------------------------------ #
    def _ensure_native(self):
        native = str(self.native_vlan_input.value())
        csv = [v.strip() for v in self.allowed_vlans_input.text().split(",") if v.strip()]
        if native not in csv:
            csv.append(native)
            self.allowed_vlans_input.setText(",".join(csv))

    def _upd_storm_fields(self):
        st = self.storm_control_checkbox.isChecked()
        for w in (self.storm_unit_pps,
                  self.broadcast_min_input, self.broadcast_max_input,
                  self.multicast_min_input, self.multicast_max_input,
                  self.unknown_unicast_min_input, self.unknown_unicast_max_input):
            w.setEnabled(st)

    # ------------------- load / save ---------------------------- #
    def load_from_instance(self, inst):
        self.interfaces_input.setText(",".join(inst.interfaces))
        self.allowed_vlans_input.setText(",".join(str(v) for v in inst.allowed_vlans))
        self.native_vlan_input.setValue(inst.native_vlan)
        self.description_input.setText(inst.description or "")

        # Set color if available
        if hasattr(inst, 'color'):
            # Set text to color hex value
            self.color_picker.current_color = QtGui.QColor(inst.color)
            self.color_picker.color_button.setText(inst.color.upper())
            # Apply color to button
            self.color_picker.update_color_ui()

        self.pruning_checkbox.setChecked(inst.pruning_enabled)
        self.stp_guard_checkbox.setChecked(inst.spanning_tree_guard_root)

        self.encapsulation_combo.setCurrentText(inst.encapsulation)
        self.dtp_mode_combo.setCurrentText(inst.dtp_mode or "--")
        self.nonegotiate_checkbox.setChecked(inst.nonegotiate)

        self.portfast_checkbox.setChecked(inst.spanning_tree_portfast)

        self.dhcp_trust_checkbox.setChecked(inst.dhcp_snooping_trust)
        self.qos_trust_combo.setCurrentText(inst.qos_trust or "--")

        # storm
        enabled = any([
            inst.storm_control_broadcast_min, inst.storm_control_broadcast_max,
            inst.storm_control_multicast_min, inst.storm_control_multicast_max,
            inst.storm_control_unknown_unicast_min, inst.storm_control_unknown_unicast_max,
        ])
        self.storm_control_checkbox.setChecked(enabled)
        self.storm_unit_pps.setChecked(inst.storm_control_unit_pps)

        self.broadcast_min_input.setValue(inst.storm_control_broadcast_min or 0.0)
        self.broadcast_max_input.setValue(inst.storm_control_broadcast_max or 0.0)
        self.multicast_min_input.setValue(inst.storm_control_multicast_min or 0.0)
        self.multicast_max_input.setValue(inst.storm_control_multicast_max or 0.0)
        self.unknown_unicast_min_input.setValue(inst.storm_control_unknown_unicast_min or 0.0)
        self.unknown_unicast_max_input.setValue(inst.storm_control_unknown_unicast_max or 0.0)

        self.speed_combo.setCurrentText(inst.speed)
        self.duplex_combo.setCurrentText(inst.duplex)
        self.auto_mdix_checkbox.setChecked(inst.auto_mdix)
        self.errdisable_timeout_input.setValue(inst.errdisable_timeout or 0)

        self.channel_group_input.setValue(inst.channel_group or 0)
        self.channel_mode_combo.setCurrentText(inst.channel_group_mode or "--")