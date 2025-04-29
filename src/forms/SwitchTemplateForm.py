# src/forms/SwitchTemplateForm.py
"""SwitchTemplate form for user input."""

from PySide6 import QtWidgets

class SwitchTemplateForm(QtWidgets.QWidget):
    """Form for filling SwitchTemplate data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Create form fields for SwitchTemplate."""
        layout = QtWidgets.QFormLayout(self)

        self.hostname_input = QtWidgets.QLineEdit()

        self.vlan_list_input = QtWidgets.QLineEdit()
        self.spanning_tree_mode_combo = QtWidgets.QComboBox()
        self.spanning_tree_mode_combo.addItems(["pvst", "rapid-pvst", "mst"])

        layout.addRow("Hostname:", self.hostname_input)
        layout.addRow("VLAN List (id:name comma separated):", self.vlan_list_input)
        layout.addRow("Spanning-tree Mode:", self.spanning_tree_mode_combo)
