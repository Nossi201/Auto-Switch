# src/forms/RouterTemplateForm.py
"""RouterTemplate form for user input."""

from PySide6 import QtWidgets

class RouterTemplateForm(QtWidgets.QWidget):
    """Form for filling RouterTemplate data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Create form fields for RouterTemplate."""
        layout = QtWidgets.QFormLayout(self)

        self.hostname_input = QtWidgets.QLineEdit()

        self.interface_name_input = QtWidgets.QLineEdit()
        self.interface_ip_input = QtWidgets.QLineEdit()
        self.interface_mask_input = QtWidgets.QLineEdit()

        self.routing_protocols_input = QtWidgets.QLineEdit()
        self.static_routes_input = QtWidgets.QLineEdit()

        layout.addRow("Hostname:", self.hostname_input)
        layout.addRow("Interface Name:", self.interface_name_input)
        layout.addRow("Interface IP Address:", self.interface_ip_input)
        layout.addRow("Interface Subnet Mask:", self.interface_mask_input)
        layout.addRow("Routing Protocols (comma separated):", self.routing_protocols_input)
        layout.addRow("Static Routes (destination/next-hop pairs comma separated):", self.static_routes_input)
