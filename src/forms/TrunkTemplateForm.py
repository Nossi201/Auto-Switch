"""TrunkTemplate form for user input (no interface selection – handled via button click)"""

from PySide6 import QtWidgets

class TrunkTemplateForm(QtWidgets.QWidget):
    """Form for filling TrunkTemplate data."""

    def __init__(self, parent=None, instance=None):
        super().__init__(parent)
        self._init_ui()
        if instance:
            self.load_from_instance(instance)

    def _init_ui(self):
        """Create form fields for TrunkTemplate."""
        layout = QtWidgets.QFormLayout(self)

        self.allowed_vlans_input = QtWidgets.QLineEdit()
        self.native_vlan_input = QtWidgets.QSpinBox()
        self.native_vlan_input.setRange(1, 4094)

        self.description_input = QtWidgets.QLineEdit()

        self.pruning_checkbox = QtWidgets.QCheckBox("Enable VLAN Pruning")
        self.stp_guard_checkbox = QtWidgets.QCheckBox("Enable STP Root Guard")

        self.encapsulation_combo = QtWidgets.QComboBox()
        self.encapsulation_combo.addItems(["dot1q", "isl"])

        layout.addRow("Allowed VLANs (comma separated):", self.allowed_vlans_input)
        layout.addRow("Native VLAN:", self.native_vlan_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow(self.pruning_checkbox)
        layout.addRow(self.stp_guard_checkbox)
        layout.addRow("Encapsulation:", self.encapsulation_combo)

        self.setLayout(layout)

    def load_from_instance(self, instance):
        """Fill form fields from TrunkTemplate instance."""
        self.allowed_vlans_input.setText(",".join(str(v) for v in instance.allowed_vlans))
        self.native_vlan_input.setValue(instance.native_vlan)
        self.description_input.setText(instance.description or "")
        self.pruning_checkbox.setChecked(instance.pruning_enabled)
        self.stp_guard_checkbox.setChecked(instance.spanning_tree_guard_root)
        idx = self.encapsulation_combo.findText(instance.encapsulation)
        if idx != -1:
            self.encapsulation_combo.setCurrentIndex(idx)
