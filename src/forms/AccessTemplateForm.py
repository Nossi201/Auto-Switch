# src/forms/AccessTemplateForm.py
"""AccessTemplate form for user input with dynamic field enabling."""

from PySide6 import QtWidgets

class AccessTemplateForm(QtWidgets.QWidget):
    """Form for filling AccessTemplate data."""

    def __init__(self, parent=None, instance=None):
        super().__init__(parent)
        self._init_ui()
        if instance:
            self.load_from_instance(instance)

    def _init_ui(self):
        """Create form fields for AccessTemplate."""
        layout = QtWidgets.QFormLayout(self)

        self.interfaces_input = QtWidgets.QLineEdit()
        self.vlan_id_input = QtWidgets.QSpinBox()
        self.vlan_id_input.setRange(1, 4094)

        self.description_input = QtWidgets.QLineEdit()

        # --- Port Security ---
        self.port_security_checkbox = QtWidgets.QCheckBox("Enable Port Security")
        self.port_security_checkbox.toggled.connect(self._toggle_port_security_fields)

        self.max_mac_input = QtWidgets.QSpinBox()
        self.max_mac_input.setRange(1, 100)

        self.violation_action_combo = QtWidgets.QComboBox()
        self.violation_action_combo.addItems(["shutdown", "restrict", "protect"])

        self.voice_vlan_input = QtWidgets.QSpinBox()
        self.voice_vlan_input.setRange(0, 4094)

        self.sticky_mac_checkbox = QtWidgets.QCheckBox("Use Sticky MACs")

        # --- Storm Control ---
        self.storm_control_checkbox = QtWidgets.QCheckBox("Enable Storm Control")
        self.storm_control_checkbox.toggled.connect(self._toggle_storm_control_fields)

        self.broadcast_min_input = QtWidgets.QDoubleSpinBox()
        self.broadcast_min_input.setRange(0.0, 100.0)
        self.broadcast_min_input.setSuffix(" %")

        self.broadcast_max_input = QtWidgets.QDoubleSpinBox()
        self.broadcast_max_input.setRange(0.0, 100.0)
        self.broadcast_max_input.setSuffix(" %")

        self.multicast_min_input = QtWidgets.QDoubleSpinBox()
        self.multicast_min_input.setRange(0.0, 100.0)
        self.multicast_min_input.setSuffix(" %")

        self.multicast_max_input = QtWidgets.QDoubleSpinBox()
        self.multicast_max_input.setRange(0.0, 100.0)
        self.multicast_max_input.setSuffix(" %")

        # --- Portfast ---
        self.portfast_checkbox = QtWidgets.QCheckBox("Enable Spanning-tree Portfast")

        layout.addRow("Interfaces (comma separated):", self.interfaces_input)
        layout.addRow("VLAN ID:", self.vlan_id_input)
        layout.addRow("Description:", self.description_input)

        layout.addRow(self.port_security_checkbox)
        layout.addRow("Max MAC Addresses:", self.max_mac_input)
        layout.addRow("Violation Action:", self.violation_action_combo)
        layout.addRow("Voice VLAN:", self.voice_vlan_input)
        layout.addRow(self.sticky_mac_checkbox)

        layout.addRow(self.storm_control_checkbox)
        layout.addRow("Broadcast Min:", self.broadcast_min_input)
        layout.addRow("Broadcast Max:", self.broadcast_max_input)
        layout.addRow("Multicast Min:", self.multicast_min_input)
        layout.addRow("Multicast Max:", self.multicast_max_input)

        layout.addRow(self.portfast_checkbox)

        self.setLayout(layout)

        self._toggle_port_security_fields()
        self._toggle_storm_control_fields()

    def _toggle_port_security_fields(self):
        enabled = self.port_security_checkbox.isChecked()
        self.max_mac_input.setEnabled(enabled)
        self.violation_action_combo.setEnabled(enabled)
        self.voice_vlan_input.setEnabled(enabled)
        self.sticky_mac_checkbox.setEnabled(enabled)

    def _toggle_storm_control_fields(self):
        enabled = self.storm_control_checkbox.isChecked()
        self.broadcast_min_input.setEnabled(enabled)
        self.broadcast_max_input.setEnabled(enabled)
        self.multicast_min_input.setEnabled(enabled)
        self.multicast_max_input.setEnabled(enabled)

    def load_from_instance(self, instance):
        """Fill form fields from AccessTemplate instance."""
        self.interfaces_input.setText(",".join(instance.interfaces))
        self.vlan_id_input.setValue(instance.vlan_id)
        self.description_input.setText(instance.description or "")

        self.port_security_checkbox.setChecked(instance.port_security_enabled)
        self.max_mac_input.setValue(instance.max_mac_addresses)
        idx = self.violation_action_combo.findText(instance.violation_action)
        if idx != -1:
            self.violation_action_combo.setCurrentIndex(idx)
        self.voice_vlan_input.setValue(instance.voice_vlan or 0)
        self.sticky_mac_checkbox.setChecked(getattr(instance, "sticky_mac", False))

        self.storm_control_checkbox.setChecked(
            any([
                instance.storm_control_broadcast_min,
                instance.storm_control_broadcast_max,
                instance.storm_control_multicast_min,
                instance.storm_control_multicast_max,
            ])
        )
        self.broadcast_min_input.setValue(instance.storm_control_broadcast_min or 0.0)
        self.broadcast_max_input.setValue(instance.storm_control_broadcast_max or 0.0)
        self.multicast_min_input.setValue(instance.storm_control_multicast_min or 0.0)
        self.multicast_max_input.setValue(instance.storm_control_multicast_max or 0.0)

        self.portfast_checkbox.setChecked(instance.spanning_tree_portfast)
        self._toggle_port_security_fields()
        self._toggle_storm_control_fields()