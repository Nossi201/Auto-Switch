# src/forms/AccessTemplateForm.py
"""AccessTemplate form for user input."""

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
        self.port_security_checkbox = QtWidgets.QCheckBox("Enable Port Security")
        self.max_mac_input = QtWidgets.QSpinBox()
        self.max_mac_input.setRange(1, 100)

        self.violation_action_combo = QtWidgets.QComboBox()
        self.violation_action_combo.addItems(["shutdown", "restrict", "protect"])

        self.voice_vlan_input = QtWidgets.QSpinBox()
        self.voice_vlan_input.setRange(0, 4094)

        self.storm_control_input = QtWidgets.QDoubleSpinBox()
        self.storm_control_input.setRange(0.0, 100.0)
        self.storm_control_input.setSuffix(" %")

        self.portfast_checkbox = QtWidgets.QCheckBox("Enable Spanning-tree Portfast")

        layout.addRow("Interfaces (comma separated):", self.interfaces_input)
        layout.addRow("VLAN ID:", self.vlan_id_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow(self.port_security_checkbox)
        layout.addRow("Max MAC Addresses:", self.max_mac_input)
        layout.addRow("Violation Action:", self.violation_action_combo)
        layout.addRow("Voice VLAN:", self.voice_vlan_input)
        layout.addRow("Storm Control (%):", self.storm_control_input)
        layout.addRow(self.portfast_checkbox)

        self.setLayout(layout)

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
        if instance.voice_vlan:
            self.voice_vlan_input.setValue(instance.voice_vlan)
        if instance.storm_control_broadcast:
            self.storm_control_input.setValue(instance.storm_control_broadcast)
        self.portfast_checkbox.setChecked(instance.spanning_tree_portfast)
