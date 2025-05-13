# src/forms/SwitchTemplateForm.py
"""Enhanced PySide6 form for SwitchTemplate with comprehensive configuration options.

The form now includes eight tabs for organizing switch configuration options:
- Basic Settings: Core device information and basic settings
- VLANs: VLAN configuration including creation and management
- Spanning Tree: Detailed STP settings including mode, priorities, and guards
- Port Security: Security features including MAC limits, violation actions
- QoS: Quality of Service settings and class maps
- Monitoring: Logging, SNMP, and monitoring protocols
- Advanced Layer2: Additional layer 2 features like UDLD, IGMP snooping
- System Settings: Power management, administrative settings
"""
from PySide6 import QtWidgets


class SwitchTemplateForm(QtWidgets.QWidget):
    """Comprehensive form for configuring all aspects of a Cisco switch."""

    def __init__(self, parent=None, instance=None):
        super().__init__(parent)
        self._create_widgets()
        self._build_layout()
        if instance:
            self.load_from_instance(instance)

    # --------------------------- widgets ----------------------------- #
    def _create_widgets(self) -> None:
        # 1. Basic Settings Tab ------------------------------------------
        self.hostname_input = QtWidgets.QLineEdit()
        self.domain_name_input = QtWidgets.QLineEdit()
        
        self.manager_vlan_id_combo = QtWidgets.QComboBox()
        self.manager_ip_input = QtWidgets.QLineEdit()
        self.default_gateway_input = QtWidgets.QLineEdit()
        
        self.enable_cdp_checkbox = QtWidgets.QCheckBox("Enable CDP")
        self.enable_lldp_checkbox = QtWidgets.QCheckBox("Enable LLDP")
        
        # 2. VLANs Tab ---------------------------------------------------
        self.vlan_table = QtWidgets.QTableWidget()
        self.vlan_table.setColumnCount(3)
        self.vlan_table.setHorizontalHeaderLabels(["VLAN ID", "Name", "Status"])
        
        self.add_vlan_button = QtWidgets.QPushButton("Add VLAN")
        self.remove_vlan_button = QtWidgets.QPushButton("Remove VLAN")
        
        self.vtp_mode_combo = QtWidgets.QComboBox()
        self.vtp_mode_combo.addItems(["off", "server", "client", "transparent"])
        self.vtp_domain_input = QtWidgets.QLineEdit()
        
        # 3. Spanning Tree Tab -------------------------------------------
        self.spanning_tree_mode_combo = QtWidgets.QComboBox()
        self.spanning_tree_mode_combo.addItems(["pvst", "rapid-pvst", "mst"])
        
        self.stp_priority_input = QtWidgets.QSpinBox()
        self.stp_priority_input.setRange(0, 61440)
        self.stp_priority_input.setSingleStep(4096)
        
        self.bpduguard_checkbox = QtWidgets.QCheckBox("BPDU Guard Default")
        self.loopguard_checkbox = QtWidgets.QCheckBox("Loop Guard Default")
        self.rootguard_checkbox = QtWidgets.QCheckBox("Root Guard Default")
        
        self.forward_time_input = QtWidgets.QSpinBox()
        self.forward_time_input.setRange(4, 30)
        self.hello_time_input = QtWidgets.QSpinBox()
        self.hello_time_input.setRange(1, 10)
        self.max_age_input = QtWidgets.QSpinBox()
        self.max_age_input.setRange(6, 40)
        
        # 4. Port Security Tab -------------------------------------------
        self.dhcp_snooping_checkbox = QtWidgets.QCheckBox("Enable DHCP Snooping")
        self.dhcp_snooping_vlan_input = QtWidgets.QLineEdit()
        
        self.arp_inspection_checkbox = QtWidgets.QCheckBox("Enable ARP Inspection")
        self.arp_inspection_vlan_input = QtWidgets.QLineEdit()
        
        self.ip_source_guard_checkbox = QtWidgets.QCheckBox("Enable IP Source Guard Default")
        
        self.port_security_violation_combo = QtWidgets.QComboBox()
        self.port_security_violation_combo.addItems(["shutdown", "restrict", "protect"])
        
        self.storm_control_default_checkbox = QtWidgets.QCheckBox("Enable Storm Control Default")
        self.storm_control_threshold_input = QtWidgets.QDoubleSpinBox()
        self.storm_control_threshold_input.setRange(0, 100)
        
        # 5. QoS Tab -----------------------------------------------------
        self.mls_qos_checkbox = QtWidgets.QCheckBox("Enable MLS QoS")
        
        self.trust_state_combo = QtWidgets.QComboBox()
        self.trust_state_combo.addItems(["--", "cos", "dscp"])
        
        self.auto_qos_checkbox = QtWidgets.QCheckBox("Enable Auto QoS")
        
        self.qos_queue_table = QtWidgets.QTableWidget()
        self.qos_queue_table.setColumnCount(3)
        self.qos_queue_table.setHorizontalHeaderLabels(["Queue", "Priority", "Bandwidth"])
        
        # 6. Monitoring Tab ----------------------------------------------
        self.logging_host_input = QtWidgets.QLineEdit()
        self.logging_level_combo = QtWidgets.QComboBox()
        self.logging_level_combo.addItems(["emergencies", "alerts", "critical", 
                                          "errors", "warnings", "notifications", 
                                          "informational", "debugging"])
        
        self.snmp_checkbox = QtWidgets.QCheckBox("Enable SNMP")
        self.snmp_community_input = QtWidgets.QLineEdit()
        self.snmp_location_input = QtWidgets.QLineEdit()
        self.snmp_contact_input = QtWidgets.QLineEdit()
        
        self.span_checkbox = QtWidgets.QCheckBox("Enable SPAN")
        self.span_source_input = QtWidgets.QLineEdit()
        self.span_destination_input = QtWidgets.QLineEdit()
        
        # 7. Advanced Layer2 Tab -----------------------------------------
        self.udld_mode_combo = QtWidgets.QComboBox()
        self.udld_mode_combo.addItems(["disabled", "normal", "aggressive"])
        
        self.igmp_snooping_checkbox = QtWidgets.QCheckBox("Enable IGMP Snooping")
        self.mld_snooping_checkbox = QtWidgets.QCheckBox("Enable MLD Snooping")
        
        self.mac_aging_time_input = QtWidgets.QSpinBox()
        self.mac_aging_time_input.setRange(0, 1000000)
        self.mac_aging_time_input.setSingleStep(10)
        
        self.jumbo_frames_checkbox = QtWidgets.QCheckBox("Enable Jumbo Frames")
        self.mtu_size_input = QtWidgets.QSpinBox()
        self.mtu_size_input.setRange(1500, 9198)
        
        # 8. System Settings Tab -----------------------------------------
        self.enable_ssh_checkbox = QtWidgets.QCheckBox("Enable SSH & AAA")
        self.enable_secret_checkbox = QtWidgets.QCheckBox("Enable Secret Password")
        
        self.aaa_authentication_checkbox = QtWidgets.QCheckBox("AAA Authentication")
        self.aaa_authorization_checkbox = QtWidgets.QCheckBox("AAA Authorization")
        self.aaa_accounting_checkbox = QtWidgets.QCheckBox("AAA Accounting")
        
        self.radius_server_input = QtWidgets.QLineEdit()
        self.radius_key_input = QtWidgets.QLineEdit()
        self.radius_key_input.setEchoMode(QtWidgets.QLineEdit.Password)
        
        self.tacacs_server_input = QtWidgets.QLineEdit()
        self.tacacs_key_input = QtWidgets.QLineEdit()
        self.tacacs_key_input.setEchoMode(QtWidgets.QLineEdit.Password)
        
        self.poe_power_budget_input = QtWidgets.QSpinBox()
        self.poe_power_budget_input.setRange(0, 1000)
        
        self.energy_efficient_ethernet_checkbox = QtWidgets.QCheckBox("Energy Efficient Ethernet")

    # --------------------------- layout ------------------------------ #
    def _build_layout(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        tabs = QtWidgets.QTabWidget()

        # 1. Basic Settings Tab Layout
        basic_tab = QtWidgets.QWidget()
        basic_layout = QtWidgets.QFormLayout(basic_tab)
        basic_layout.addRow("Hostname:", self.hostname_input)
        basic_layout.addRow("Domain Name:", self.domain_name_input)
        basic_layout.addRow("Management VLAN:", self.manager_vlan_id_combo)
        basic_layout.addRow("Management IP:", self.manager_ip_input)
        basic_layout.addRow("Default Gateway:", self.default_gateway_input)
        basic_layout.addRow(self.enable_cdp_checkbox)
        basic_layout.addRow(self.enable_lldp_checkbox)
        tabs.addTab(basic_tab, "Basic Settings")
        
        # 2. VLANs Tab Layout
        vlans_tab = QtWidgets.QWidget()
        vlans_layout = QtWidgets.QVBoxLayout(vlans_tab)
        vlans_layout.addWidget(self.vlan_table)
        
        vlan_buttons = QtWidgets.QHBoxLayout()
        vlan_buttons.addWidget(self.add_vlan_button)
        vlan_buttons.addWidget(self.remove_vlan_button)
        vlans_layout.addLayout(vlan_buttons)
        
        vtp_group = QtWidgets.QGroupBox("VTP Configuration")
        vtp_form = QtWidgets.QFormLayout(vtp_group)
        vtp_form.addRow("VTP Mode:", self.vtp_mode_combo)
        vtp_form.addRow("VTP Domain:", self.vtp_domain_input)
        vlans_layout.addWidget(vtp_group)
        
        tabs.addTab(vlans_tab, "VLANs")
        
        # 3. Spanning Tree Tab Layout
        stp_tab = QtWidgets.QWidget()
        stp_layout = QtWidgets.QFormLayout(stp_tab)
        stp_layout.addRow("Mode:", self.spanning_tree_mode_combo)
        stp_layout.addRow("Bridge Priority:", self.stp_priority_input)
        stp_layout.addRow(self.bpduguard_checkbox)
        stp_layout.addRow(self.loopguard_checkbox)
        stp_layout.addRow(self.rootguard_checkbox)
        
        timers_group = QtWidgets.QGroupBox("STP Timers")
        timers_form = QtWidgets.QFormLayout(timers_group)
        timers_form.addRow("Forward Time:", self.forward_time_input)
        timers_form.addRow("Hello Time:", self.hello_time_input)
        timers_form.addRow("Max Age:", self.max_age_input)
        stp_layout.addRow(timers_group)
        
        tabs.addTab(stp_tab, "Spanning Tree")
        
        # 4. Port Security Tab Layout
        security_tab = QtWidgets.QWidget()
        security_layout = QtWidgets.QFormLayout(security_tab)
        security_layout.addRow(self.dhcp_snooping_checkbox)
        security_layout.addRow("DHCP Snooping VLANs:", self.dhcp_snooping_vlan_input)
        security_layout.addRow(self.arp_inspection_checkbox)
        security_layout.addRow("ARP Inspection VLANs:", self.arp_inspection_vlan_input)
        security_layout.addRow(self.ip_source_guard_checkbox)
        security_layout.addRow("Default Violation:", self.port_security_violation_combo)
        security_layout.addRow(self.storm_control_default_checkbox)
        security_layout.addRow("Default Threshold (%):", self.storm_control_threshold_input)
        
        tabs.addTab(security_tab, "Port Security")
        
        # 5. QoS Tab Layout
        qos_tab = QtWidgets.QWidget()
        qos_layout = QtWidgets.QVBoxLayout(qos_tab)
        
        qos_settings = QtWidgets.QFormLayout()
        qos_settings.addRow(self.mls_qos_checkbox)
        qos_settings.addRow("Default Trust:", self.trust_state_combo)
        qos_settings.addRow(self.auto_qos_checkbox)
        qos_layout.addLayout(qos_settings)
        
        qos_layout.addWidget(QtWidgets.QLabel("Queue Configuration:"))
        qos_layout.addWidget(self.qos_queue_table)
        
        tabs.addTab(qos_tab, "QoS")
        
        # 6. Monitoring Tab Layout
        monitoring_tab = QtWidgets.QWidget()
        monitoring_layout = QtWidgets.QVBoxLayout(monitoring_tab)
        
        logging_group = QtWidgets.QGroupBox("Logging")
        logging_form = QtWidgets.QFormLayout(logging_group)
        logging_form.addRow("Logging Host:", self.logging_host_input)
        logging_form.addRow("Logging Level:", self.logging_level_combo)
        monitoring_layout.addWidget(logging_group)
        
        snmp_group = QtWidgets.QGroupBox("SNMP")
        snmp_form = QtWidgets.QFormLayout(snmp_group)
        snmp_form.addRow(self.snmp_checkbox)
        snmp_form.addRow("Community:", self.snmp_community_input)
        snmp_form.addRow("Location:", self.snmp_location_input)
        snmp_form.addRow("Contact:", self.snmp_contact_input)
        monitoring_layout.addWidget(snmp_group)
        
        span_group = QtWidgets.QGroupBox("SPAN/Port Mirroring")
        span_form = QtWidgets.QFormLayout(span_group)
        span_form.addRow(self.span_checkbox)
        span_form.addRow("Source Ports:", self.span_source_input)
        span_form.addRow("Destination Port:", self.span_destination_input)
        monitoring_layout.addWidget(span_group)
        
        tabs.addTab(monitoring_tab, "Monitoring")
        
        # 7. Advanced Layer2 Tab Layout
        adv_layer2_tab = QtWidgets.QWidget()
        adv_layer2_layout = QtWidgets.QFormLayout(adv_layer2_tab)
        adv_layer2_layout.addRow("UDLD Mode:", self.udld_mode_combo)
        adv_layer2_layout.addRow(self.igmp_snooping_checkbox)
        adv_layer2_layout.addRow(self.mld_snooping_checkbox)
        adv_layer2_layout.addRow("MAC Aging Time (sec):", self.mac_aging_time_input)
        adv_layer2_layout.addRow(self.jumbo_frames_checkbox)
        adv_layer2_layout.addRow("MTU Size:", self.mtu_size_input)
        
        tabs.addTab(adv_layer2_tab, "Advanced Layer2")
        
        # 8. System Settings Tab Layout
        system_tab = QtWidgets.QWidget()
        system_layout = QtWidgets.QVBoxLayout(system_tab)
        
        auth_group = QtWidgets.QGroupBox("Authentication")
        auth_form = QtWidgets.QFormLayout(auth_group)
        auth_form.addRow(self.enable_ssh_checkbox)
        auth_form.addRow(self.enable_secret_checkbox)
        auth_form.addRow(self.aaa_authentication_checkbox)
        auth_form.addRow(self.aaa_authorization_checkbox)
        auth_form.addRow(self.aaa_accounting_checkbox)
        system_layout.addWidget(auth_group)
        
        radius_group = QtWidgets.QGroupBox("RADIUS")
        radius_form = QtWidgets.QFormLayout(radius_group)
        radius_form.addRow("Server:", self.radius_server_input)
        radius_form.addRow("Key:", self.radius_key_input)
        system_layout.addWidget(radius_group)
        
        tacacs_group = QtWidgets.QGroupBox("TACACS+")
        tacacs_form = QtWidgets.QFormLayout(tacacs_group)
        tacacs_form.addRow("Server:", self.tacacs_server_input)
        tacacs_form.addRow("Key:", self.tacacs_key_input)
        system_layout.addWidget(tacacs_group)
        
        power_group = QtWidgets.QGroupBox("Power Management")
        power_form = QtWidgets.QFormLayout(power_group)
        power_form.addRow("PoE Power Budget (W):", self.poe_power_budget_input)
        power_form.addRow(self.energy_efficient_ethernet_checkbox)
        system_layout.addWidget(power_group)
        
        tabs.addTab(system_tab, "System")

        root.addWidget(tabs)

    # --------------------------- loader ------------------------------ #
    def load_from_instance(self, instance):
        """Fill form fields from SwitchTemplate instance."""
        # This method would need to be updated to handle the new fields
        self.hostname_input.setText(instance.hostname)
        self.spanning_tree_mode_combo.setCurrentText(instance.spanning_tree_mode)

        # VLAN list + Manager VLAN combo
        # Update VLAN table here
        self.populate_vlan_table(instance.vlan_list)
        
        self.manager_vlan_id_combo.clear()
        for vid in instance.vlan_list:
            self.manager_vlan_id_combo.addItem(str(vid))
        idx = self.manager_vlan_id_combo.findText(str(instance.manager_vlan_id))
        if idx != -1:
            self.manager_vlan_id_combo.setCurrentIndex(idx)

        self.manager_ip_input.setText(instance.manager_ip)
        self.default_gateway_input.setText(instance.default_gateway)
        
        # Load other fields based on expanded SwitchTemplate class
        # This would be expanded significantly for all the new fields
        
    def populate_vlan_table(self, vlan_list):
        """Populate the VLAN table with the given VLAN IDs."""
        self.vlan_table.setRowCount(len(vlan_list))
        for row, vlan_id in enumerate(vlan_list):
            self.vlan_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(vlan_id)))
            self.vlan_table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"VLAN{vlan_id}"))
            self.vlan_table.setItem(row, 2, QtWidgets.QTableWidgetItem("active"))