"""PySide6 form for SwitchTemplate with Basic / Security / Advanced tabs.

The form always displays all tabs because the chassis template is created
implicitly on first entry and not via the new-template wizard.
"""
from PySide6 import QtWidgets


class SwitchTemplateForm(QtWidgets.QWidget):
    """Form for filling SwitchTemplate (device-level) data."""

    # ------------------------------------------------------------------ #
    def __init__(self, parent=None, instance=None):
        super().__init__(parent)
        self._create_widgets()
        self._build_layout()
        if instance:
            self.load_from_instance(instance)

    # --------------------------- widgets ----------------------------- #
    def _create_widgets(self) -> None:
        # Basic ----------------------------------------------------------
        self.hostname_input = QtWidgets.QLineEdit()
        self.vlan_list_input = QtWidgets.QLineEdit()
        self.vlan_list_input.setReadOnly(True)

        self.spanning_tree_mode_combo = QtWidgets.QComboBox()
        self.spanning_tree_mode_combo.addItems(["pvst", "rapid-pvst", "mst"])

        self.manager_vlan_id_combo = QtWidgets.QComboBox()
        self.manager_ip_input = QtWidgets.QLineEdit()
        self.default_gateway_input = QtWidgets.QLineEdit()

        # Security (place-holders – future expansion) -------------------
        self.enable_ssh_checkbox = QtWidgets.QCheckBox("Enable SSH & AAA")
        self.enable_secret_checkbox = QtWidgets.QCheckBox("Enable secret password")
        self.snmp_checkbox = QtWidgets.QCheckBox("Configure SNMP")
        self.logging_host_input = QtWidgets.QLineEdit()

        # Advanced (place-holders) --------------------------------------
        self.bpduguard_checkbox = QtWidgets.QCheckBox("bpduguard default / loopguard")
        self.dhcp_snoop_checkbox = QtWidgets.QCheckBox("Enable DHCP Snooping / DAI")
        self.qos_global_checkbox = QtWidgets.QCheckBox("Enable global QoS (mls qos)")
        self.monitoring_checkbox = QtWidgets.QCheckBox("Enable errdisable recovery / EEM")

    # --------------------------- layout ------------------------------ #
    def _build_layout(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        tabs = QtWidgets.QTabWidget()

        # ---- Podstawowe ------------------------------------------------ #
        basic_w = QtWidgets.QWidget()
        basic_form = QtWidgets.QFormLayout(basic_w)
        basic_form.addRow("Hostname:", self.hostname_input)
        basic_form.addRow("VLAN List (read-only):", self.vlan_list_input)
        basic_form.addRow("Spanning-tree Mode:", self.spanning_tree_mode_combo)
        basic_form.addRow("Manager VLAN ID:", self.manager_vlan_id_combo)
        basic_form.addRow("Manager IP:", self.manager_ip_input)
        basic_form.addRow("Default Gateway:", self.default_gateway_input)
        tabs.addTab(basic_w, "Podstawowe")

        # ---- Security --------------------------------------------------- #
        sec_w = QtWidgets.QWidget()
        sec_form = QtWidgets.QFormLayout(sec_w)
        sec_form.addRow(self.enable_ssh_checkbox)
        sec_form.addRow(self.enable_secret_checkbox)
        sec_form.addRow(self.snmp_checkbox)
        sec_form.addRow("Logging host IP:", self.logging_host_input)
        tabs.addTab(sec_w, "Security")

        # ---- Zaawansowane ---------------------------------------------- #
        adv_w = QtWidgets.QWidget()
        adv_form = QtWidgets.QFormLayout(adv_w)
        adv_form.addRow(self.bpduguard_checkbox)
        adv_form.addRow(self.dhcp_snoop_checkbox)
        adv_form.addRow(self.qos_global_checkbox)
        adv_form.addRow(self.monitoring_checkbox)
        tabs.addTab(adv_w, "Zaawansowane")

        root.addWidget(tabs)

    # --------------------------- loader ------------------------------ #
    def load_from_instance(self, instance):
        """Fill form fields from SwitchTemplate instance."""
        self.hostname_input.setText(instance.hostname)
        self.spanning_tree_mode_combo.setCurrentText(instance.spanning_tree_mode)

        # VLAN list + Manager VLAN combo
        self.vlan_list_input.setText(", ".join(str(v) for v in instance.vlan_list))
        self.manager_vlan_id_combo.clear()
        for vid in instance.vlan_list:
            self.manager_vlan_id_combo.addItem(str(vid))
        idx = self.manager_vlan_id_combo.findText(str(instance.manager_vlan_id))
        if idx != -1:
            self.manager_vlan_id_combo.setCurrentIndex(idx)

        self.manager_ip_input.setText(instance.manager_ip)
        self.default_gateway_input.setText(instance.default_gateway)
