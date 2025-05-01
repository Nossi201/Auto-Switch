"""SwitchTemplate form for user input."""

from PySide6 import QtWidgets


class SwitchTemplateForm(QtWidgets.QWidget):
    """Form for filling SwitchTemplate data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    # ---------------------------------------------------------------- #

    def _init_ui(self):
        """Create form fields for SwitchTemplate."""
        layout = QtWidgets.QFormLayout(self)

        self.hostname_input = QtWidgets.QLineEdit()

        # VLAN list – read-only: user modyfikuje poprzez AccessTemplate
        self.vlan_list_input = QtWidgets.QLineEdit()
        self.vlan_list_input.setReadOnly(True)

        self.spanning_tree_mode_combo = QtWidgets.QComboBox()
        self.spanning_tree_mode_combo.addItems(["pvst", "rapid-pvst", "mst"])

        # --- manager SVI ---
        self.manager_vlan_id_combo = QtWidgets.QComboBox()     # filled in load_from_instance()
        self.manager_ip_input = QtWidgets.QLineEdit()

        self.default_gateway_input = QtWidgets.QLineEdit()

        layout.addRow("Hostname:", self.hostname_input)
        layout.addRow("VLAN List (read-only):", self.vlan_list_input)
        layout.addRow("Spanning-tree Mode:", self.spanning_tree_mode_combo)
        layout.addRow("Manager VLAN ID:", self.manager_vlan_id_combo)
        layout.addRow("Manager IP:", self.manager_ip_input)
        layout.addRow("Default Gateway:", self.default_gateway_input)

        self.setLayout(layout)

    # ---------------------------------------------------------------- #

    def load_from_instance(self, instance):
        """Fill form fields from SwitchTemplate instance."""
        # Hostname & STP
        self.hostname_input.setText(instance.hostname)
        self.spanning_tree_mode_combo.setCurrentText(instance.spanning_tree_mode)

        # VLAN list (read-only text) + populate combo
        self.vlan_list_input.setText(", ".join(str(v) for v in instance.vlan_list))
        self.manager_vlan_id_combo.clear()
        for vid in instance.vlan_list:
            self.manager_vlan_id_combo.addItem(str(vid))
        # select current manager VLAN
        idx = self.manager_vlan_id_combo.findText(str(instance.manager_vlan_id))
        if idx != -1:
            self.manager_vlan_id_combo.setCurrentIndex(idx)

        # Manager IP & gateway
        self.manager_ip_input.setText(instance.manager_ip)
        self.default_gateway_input.setText(instance.default_gateway)
