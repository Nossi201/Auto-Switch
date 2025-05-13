# src/forms/AccessTemplateForm.py
"""Enhanced PySide6 widget for editing access-port templates with comprehensive options.

The form implements eight tab categories with feature groups organized in each tab.
All possible Cisco IOS/IOS-XE access port configuration options are available through
the intuitive GUI. The design follows a consistent pattern across all forms for
easy maintenance and extensibility.
"""
from PySide6 import QtWidgets, QtCore, QtGui
from typing import List, Dict, Any, Optional

from src.views.ConfigPageAdd.MainTabStructure import TabCategory, FeatureGroup, get_tab_structure
from src.models.templates.AccessTemplate import AccessTemplate, ViolationAction, PowerInlineMode, QoSTrustState
from src.widgets.ColorPicker import ColorPicker  # Import the existing ColorPicker


class AccessTemplateForm(QtWidgets.QWidget):
    """Comprehensive GUI for creating and editing AccessTemplate instances."""

    def __init__(self, parent=None, instance=None, *, editable_interfaces: bool = False):
        super().__init__(parent)
        self._editable_interfaces = editable_interfaces

        # Get tab structure specific for access ports
        self._tab_structure = get_tab_structure("access")

        # Create all widgets and build UI
        self._create_all_widgets()
        self._build_layout()

        # Set up dynamic widget connections
        self._connect_signals()

        # Load instance data if provided
        if instance is not None:
            self.load_from_instance(instance)

    def _create_all_widgets(self) -> None:
        """Create all form widgets organized by category and group."""
        # Dictionary to store all widgets by category and group
        self.widgets = {}

        # Initialize all widget categories
        for category in self._tab_structure:
            self.widgets[category] = {}

            # Initialize all widget groups within each category
            for group in self._tab_structure[category]:
                self.widgets[category][group] = {}

        # ---------------------------------------------------------------- #
        # Basic Settings Tab
        # ---------------------------------------------------------------- #

        # Identification group
        self.interfaces_input = QtWidgets.QLineEdit()
        self.interfaces_input.setReadOnly(not self._editable_interfaces)
        self.vlan_id_input = QtWidgets.QSpinBox()
        self.vlan_id_input.setRange(1, 4094)
        self.description_input = QtWidgets.QLineEdit()

        # Add color picker
        self.color_picker = ColorPicker()

        self.widgets[TabCategory.BASIC][FeatureGroup.IDENTIFICATION] = {
            "interfaces_label": QtWidgets.QLabel("Interfaces:"),
            "interfaces_input": self.interfaces_input,
            "vlan_id_label": QtWidgets.QLabel("VLAN ID:"),
            "vlan_id_input": self.vlan_id_input,
            "description_label": QtWidgets.QLabel("Description:"),
            "description_input": self.description_input,
            "color_picker": self.color_picker
        }

        # Physical layer group
        self.speed_combo = QtWidgets.QComboBox()
        self.speed_combo.addItems(["auto", "10", "100", "1000", "10000"])
        self.duplex_combo = QtWidgets.QComboBox()
        self.duplex_combo.addItems(["auto", "half", "full"])
        self.auto_mdix_checkbox = QtWidgets.QCheckBox("Auto-MDIX")
        self.energy_efficient_ethernet_checkbox = QtWidgets.QCheckBox("Energy Efficient Ethernet")
        self.flow_control_receive_checkbox = QtWidgets.QCheckBox("Flow Control Receive")
        self.flow_control_send_checkbox = QtWidgets.QCheckBox("Flow Control Send")

        self.widgets[TabCategory.BASIC][FeatureGroup.PHYSICAL] = {
            "speed_label": QtWidgets.QLabel("Speed:"),
            "speed_combo": self.speed_combo,
            "duplex_label": QtWidgets.QLabel("Duplex:"),
            "duplex_combo": self.duplex_combo,
            "auto_mdix_checkbox": self.auto_mdix_checkbox,
            "energy_efficient_ethernet_checkbox": self.energy_efficient_ethernet_checkbox,
            "flow_control_receive_checkbox": self.flow_control_receive_checkbox,
            "flow_control_send_checkbox": self.flow_control_send_checkbox,
        }

        # Discovery protocols group
        self.cdp_enabled_checkbox = QtWidgets.QCheckBox("Enable CDP")
        self.lldp_transmit_checkbox = QtWidgets.QCheckBox("LLDP Transmit")
        self.lldp_receive_checkbox = QtWidgets.QCheckBox("LLDP Receive")
        self.load_interval_input = QtWidgets.QSpinBox()
        self.load_interval_input.setRange(30, 600)
        self.load_interval_input.setSingleStep(30)
        self.load_interval_input.setValue(300)

        self.widgets[TabCategory.BASIC][FeatureGroup.DISCOVERY] = {
            "cdp_enabled_checkbox": self.cdp_enabled_checkbox,
            "lldp_transmit_checkbox": self.lldp_transmit_checkbox,
            "lldp_receive_checkbox": self.lldp_receive_checkbox,
            "load_interval_label": QtWidgets.QLabel("Load Interval (sec):"),
            "load_interval_input": self.load_interval_input
        }

        # ---------------------------------------------------------------- #
        # VLANs Tab
        # ---------------------------------------------------------------- #

        # VLAN Configuration group
        # Already created vlan_id_input in Basic tab

        # Voice VLAN group
        self.voice_vlan_input = QtWidgets.QSpinBox()
        self.voice_vlan_input.setRange(0, 4094)
        self.voice_vlan_dot1p_checkbox = QtWidgets.QCheckBox("802.1p Priority Tagging")
        self.voice_vlan_none_checkbox = QtWidgets.QCheckBox("Disable Voice VLAN")

        self.widgets[TabCategory.VLANS][FeatureGroup.VOICE_VLAN] = {
            "voice_vlan_label": QtWidgets.QLabel("Voice VLAN ID (0=off):"),
            "voice_vlan_input": self.voice_vlan_input,
            "voice_vlan_dot1p_checkbox": self.voice_vlan_dot1p_checkbox,
            "voice_vlan_none_checkbox": self.voice_vlan_none_checkbox
        }

        # ---------------------------------------------------------------- #
        # Spanning Tree Tab
        # ---------------------------------------------------------------- #

        # STP Protection features
        self.spanning_tree_portfast_checkbox = QtWidgets.QCheckBox("PortFast")
        self.spanning_tree_portfast_trunk_checkbox = QtWidgets.QCheckBox("PortFast Trunk")
        self.bpdu_guard_checkbox = QtWidgets.QCheckBox("BPDU Guard")
        self.bpdu_filter_checkbox = QtWidgets.QCheckBox("BPDU Filter")
        self.loop_guard_checkbox = QtWidgets.QCheckBox("Loop Guard")
        self.root_guard_checkbox = QtWidgets.QCheckBox("Root Guard")

        self.spanning_tree_link_type_combo = QtWidgets.QComboBox()
        self.spanning_tree_link_type_combo.addItems(["default", "point-to-point", "shared"])

        self.widgets[TabCategory.SPANNING_TREE][FeatureGroup.STP_PROTECTION] = {
            "spanning_tree_portfast_checkbox": self.spanning_tree_portfast_checkbox,
            "spanning_tree_portfast_trunk_checkbox": self.spanning_tree_portfast_trunk_checkbox,
            "bpdu_guard_checkbox": self.bpdu_guard_checkbox,
            "bpdu_filter_checkbox": self.bpdu_filter_checkbox,
            "loop_guard_checkbox": self.loop_guard_checkbox,
            "root_guard_checkbox": self.root_guard_checkbox,
            "spanning_tree_link_type_label": QtWidgets.QLabel("Link Type:"),
            "spanning_tree_link_type_combo": self.spanning_tree_link_type_combo
        }

        # ---------------------------------------------------------------- #
        # Security Tab
        # ---------------------------------------------------------------- #

        # Port Security group
        self.port_security_checkbox = QtWidgets.QCheckBox("Port-Security")
        self.max_mac_input = QtWidgets.QSpinBox()
        self.max_mac_input.setRange(1, 132)
        self.violation_action_combo = QtWidgets.QComboBox()
        self.violation_action_combo.addItems(["shutdown", "restrict", "protect"])
        self.sticky_mac_checkbox = QtWidgets.QCheckBox("Sticky MAC")
        self.mac_address_table = QtWidgets.QTableWidget(0, 2)
        self.mac_address_table.setHorizontalHeaderLabels(["MAC Address", ""])
        self.add_mac_button = QtWidgets.QPushButton("Add MAC")

        self.widgets[TabCategory.SECURITY][FeatureGroup.PORT_SECURITY] = {
            "port_security_checkbox": self.port_security_checkbox,
            "max_mac_label": QtWidgets.QLabel("Max MACs:"),
            "max_mac_input": self.max_mac_input,
            "violation_action_label": QtWidgets.QLabel("Violation:"),
            "violation_action_combo": self.violation_action_combo,
            "sticky_mac_checkbox": self.sticky_mac_checkbox,
            "mac_address_table": self.mac_address_table,
            "add_mac_button": self.add_mac_button
        }

        # Authentication Methods group
        self.dot1x_checkbox = QtWidgets.QCheckBox("802.1X")
        self.mab_checkbox = QtWidgets.QCheckBox("MAC Authentication Bypass (MAB)")
        self.webauth_checkbox = QtWidgets.QCheckBox("Web Authentication")
        self.webauth_local_checkbox = QtWidgets.QCheckBox("Use Local Database")

        self.authentication_host_mode_combo = QtWidgets.QComboBox()
        self.authentication_host_mode_combo.addItems([
            "single-host", "multi-auth", "multi-domain", "multi-host"
        ])

        self.authentication_open_checkbox = QtWidgets.QCheckBox("Open Authentication")
        self.authentication_periodic_checkbox = QtWidgets.QCheckBox("Periodic Re-Authentication")
        self.authentication_timer_input = QtWidgets.QSpinBox()
        self.authentication_timer_input.setRange(1, 65535)
        self.authentication_timer_input.setValue(3600)

        self.authentication_order_list = QtWidgets.QListWidget()
        self.authentication_order_list.addItems(["dot1x", "mab", "webauth"])
        self.authentication_order_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.widgets[TabCategory.SECURITY][FeatureGroup.AUTH_METHODS] = {
            "dot1x_checkbox": self.dot1x_checkbox,
            "mab_checkbox": self.mab_checkbox,
            "webauth_checkbox": self.webauth_checkbox,
            "webauth_local_checkbox": self.webauth_local_checkbox,
            "authentication_host_mode_label": QtWidgets.QLabel("Host Mode:"),
            "authentication_host_mode_combo": self.authentication_host_mode_combo,
            "authentication_open_checkbox": self.authentication_open_checkbox,
            "authentication_periodic_checkbox": self.authentication_periodic_checkbox,
            "authentication_timer_label": QtWidgets.QLabel("Re-Auth Timer (sec):"),
            "authentication_timer_input": self.authentication_timer_input,
            "authentication_order_label": QtWidgets.QLabel("Authentication Order:"),
            "authentication_order_list": self.authentication_order_list
        }

        # DHCP & ARP Security group
        self.dhcp_snoop_trust_checkbox = QtWidgets.QCheckBox("DHCP Snooping Trust")
        self.dhcp_snoop_rate_input = QtWidgets.QSpinBox()
        self.dhcp_snoop_rate_input.setRange(0, 4096)

        self.arp_inspection_trust_checkbox = QtWidgets.QCheckBox("ARP Inspection Trust")
        self.arp_inspection_rate_input = QtWidgets.QSpinBox()
        self.arp_inspection_rate_input.setRange(0, 4096)

        self.dhcp_relay_information_checkbox = QtWidgets.QCheckBox("DHCP Option 82")

        self.widgets[TabCategory.SECURITY][FeatureGroup.DHCP_ARP] = {
            "dhcp_snoop_trust_checkbox": self.dhcp_snoop_trust_checkbox,
            "dhcp_snoop_rate_label": QtWidgets.QLabel("DHCP Snooping Rate (pps):"),
            "dhcp_snoop_rate_input": self.dhcp_snoop_rate_input,
            "arp_inspection_trust_checkbox": self.arp_inspection_trust_checkbox,
            "arp_inspection_rate_label": QtWidgets.QLabel("ARP Inspection Rate (pps):"),
            "arp_inspection_rate_input": self.arp_inspection_rate_input,
            "dhcp_relay_information_checkbox": self.dhcp_relay_information_checkbox
        }

        # IP Source Guard group
        self.ip_source_guard_checkbox = QtWidgets.QCheckBox("IP Source Guard")

        self.widgets[TabCategory.SECURITY][FeatureGroup.IP_SOURCE] = {
            "ip_source_guard_checkbox": self.ip_source_guard_checkbox
        }

        # IPv6 Security
        self.ipv6_nd_inspection_checkbox = QtWidgets.QCheckBox("IPv6 ND Inspection")
        self.ipv6_ra_guard_checkbox = QtWidgets.QCheckBox("IPv6 RA Guard")
        self.device_tracking_checkbox = QtWidgets.QCheckBox("Device Tracking")

        self.widgets[TabCategory.SECURITY][FeatureGroup.IPV6_SECURITY] = {
            "ipv6_nd_inspection_checkbox": self.ipv6_nd_inspection_checkbox,
            "ipv6_ra_guard_checkbox": self.ipv6_ra_guard_checkbox,
            "device_tracking_checkbox": self.device_tracking_checkbox
        }

        # ---------------------------------------------------------------- #
        # QoS Tab
        # ---------------------------------------------------------------- #

        # QoS Trust Settings
        self.qos_trust_combo = QtWidgets.QComboBox()
        self.qos_trust_combo.addItems(["--", "cos", "dscp"])

        self.widgets[TabCategory.QOS][FeatureGroup.QOS_TRUST] = {
            "qos_trust_label": QtWidgets.QLabel("QoS Trust:"),
            "qos_trust_combo": self.qos_trust_combo
        }

        # QoS Marking group
        self.qos_cos_override_input = QtWidgets.QSpinBox()
        self.qos_cos_override_input.setRange(0, 7)

        self.qos_dscp_override_input = QtWidgets.QSpinBox()
        self.qos_dscp_override_input.setRange(0, 63)

        self.priority_queue_out_checkbox = QtWidgets.QCheckBox("Priority Queue Out")

        self.widgets[TabCategory.QOS][FeatureGroup.QOS_MARKING] = {
            "qos_cos_override_label": QtWidgets.QLabel("CoS Override Value:"),
            "qos_cos_override_input": self.qos_cos_override_input,
            "qos_dscp_override_label": QtWidgets.QLabel("DSCP Override Value:"),
            "qos_dscp_override_input": self.qos_dscp_override_input,
            "priority_queue_out_checkbox": self.priority_queue_out_checkbox
        }

        # QoS Policing group
        self.service_policy_input = QtWidgets.QLineEdit()
        self.service_policy_output_input = QtWidgets.QLineEdit()

        self.shape_average_input = QtWidgets.QSpinBox()
        self.shape_average_input.setRange(8000, 1000000000)
        self.shape_average_input.setSingleStep(8000)

        self.police_rate_input = QtWidgets.QSpinBox()
        self.police_rate_input.setRange(8000, 1000000000)
        self.police_rate_input.setSingleStep(8000)

        self.police_burst_input = QtWidgets.QSpinBox()
        self.police_burst_input.setRange(1000, 512000000)
        self.police_burst_input.setSingleStep(1000)

        self.widgets[TabCategory.QOS][FeatureGroup.QOS_POLICING] = {
            "service_policy_label": QtWidgets.QLabel("Service Policy Input:"),
            "service_policy_input": self.service_policy_input,
            "service_policy_output_label": QtWidgets.QLabel("Service Policy Output:"),
            "service_policy_output_input": self.service_policy_output_input,
            "shape_average_label": QtWidgets.QLabel("Shape Average (bps):"),
            "shape_average_input": self.shape_average_input,
            "police_rate_label": QtWidgets.QLabel("Police Rate (bps):"),
            "police_rate_input": self.police_rate_input,
            "police_burst_label": QtWidgets.QLabel("Police Burst (bytes):"),
            "police_burst_input": self.police_burst_input
        }

        # ---------------------------------------------------------------- #
        # Monitoring Tab
        # ---------------------------------------------------------------- #

        # Error Detection & Recovery
        self.errdisable_timeout_input = QtWidgets.QSpinBox()
        self.errdisable_timeout_input.setRange(0, 86400)

        self.errdisable_recovery_list = QtWidgets.QListWidget()
        recovery_causes = [
            "all", "arp-inspection", "bpduguard", "channel-misconfig",
            "dhcp-rate-limit", "dtp-flap", "l2ptguard", "link-flap",
            "pagp-flap", "psecure-violation", "security-violation",
            "storm-control", "udld"
        ]
        for cause in recovery_causes:
            item = QtWidgets.QListWidgetItem(cause)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.errdisable_recovery_list.addItem(item)

        self.widgets[TabCategory.MONITORING][FeatureGroup.ERRDISABLE] = {
            "errdisable_timeout_label": QtWidgets.QLabel("Errdisable Timeout (sec):"),
            "errdisable_timeout_input": self.errdisable_timeout_input,
            "errdisable_recovery_label": QtWidgets.QLabel("Recovery Causes:"),
            "errdisable_recovery_list": self.errdisable_recovery_list
        }

        # ---------------------------------------------------------------- #
        # Advanced Layer 2 Tab
        # ---------------------------------------------------------------- #

        # Storm Control group
        self.storm_control_checkbox = QtWidgets.QCheckBox("Storm-Control")
        self.storm_unit_pps = QtWidgets.QCheckBox("Use PPS unit")

        self.broadcast_min_input = QtWidgets.QDoubleSpinBox()
        self.broadcast_max_input = QtWidgets.QDoubleSpinBox()
        self.multicast_min_input = QtWidgets.QDoubleSpinBox()
        self.multicast_max_input = QtWidgets.QDoubleSpinBox()
        self.unknown_unicast_min_input = QtWidgets.QDoubleSpinBox()
        self.unknown_unicast_max_input = QtWidgets.QDoubleSpinBox()

        self.storm_control_action_combo = QtWidgets.QComboBox()
        self.storm_control_action_combo.addItems(["--", "shutdown", "trap"])

        self.widgets[TabCategory.ADVANCED_L2][FeatureGroup.STORM_CONTROL] = {
            "storm_control_checkbox": self.storm_control_checkbox,
            "storm_unit_pps": self.storm_unit_pps,
            "broadcast_min_label": QtWidgets.QLabel("Broadcast Min:"),
            "broadcast_min_input": self.broadcast_min_input,
            "broadcast_max_label": QtWidgets.QLabel("Broadcast Max:"),
            "broadcast_max_input": self.broadcast_max_input,
            "multicast_min_label": QtWidgets.QLabel("Multicast Min:"),
            "multicast_min_input": self.multicast_min_input,
            "multicast_max_label": QtWidgets.QLabel("Multicast Max:"),
            "multicast_max_input": self.multicast_max_input,
            "unknown_unicast_min_label": QtWidgets.QLabel("Unknown Unicast Min:"),
            "unknown_unicast_min_input": self.unknown_unicast_min_input,
            "unknown_unicast_max_label": QtWidgets.QLabel("Unknown Unicast Max:"),
            "unknown_unicast_max_input": self.unknown_unicast_max_input,
            "storm_control_action_label": QtWidgets.QLabel("Action:"),
            "storm_control_action_combo": self.storm_control_action_combo
        }

        # UDLD group
        self.udld_enable_checkbox = QtWidgets.QCheckBox("Enable UDLD")
        self.udld_aggressive_checkbox = QtWidgets.QCheckBox("Aggressive Mode")

        self.widgets[TabCategory.ADVANCED_L2][FeatureGroup.UDLD] = {
            "udld_enable_checkbox": self.udld_enable_checkbox,
            "udld_aggressive_checkbox": self.udld_aggressive_checkbox
        }

        # ---------------------------------------------------------------- #
        # System Tab
        # ---------------------------------------------------------------- #

        # Power Management
        self.poe_enabled_checkbox = QtWidgets.QCheckBox("Enable PoE")
        self.poe_inline_combo = QtWidgets.QComboBox()
        self.poe_inline_combo.addItems(["auto", "static", "never", "maximum", "perpetual-poe"])

        self.poe_priority_combo = QtWidgets.QComboBox()
        self.poe_priority_combo.addItems(["low", "medium", "high", "critical"])

        self.poe_limit_input = QtWidgets.QSpinBox()
        self.poe_limit_input.setRange(0, 60000)
        self.poe_limit_input.setSingleStep(1000)

        self.widgets[TabCategory.SYSTEM][FeatureGroup.POWER] = {
            "poe_enabled_checkbox": self.poe_enabled_checkbox,
            "poe_inline_label": QtWidgets.QLabel("PoE Mode:"),
            "poe_inline_combo": self.poe_inline_combo,
            "poe_priority_label": QtWidgets.QLabel("Priority:"),
            "poe_priority_combo": self.poe_priority_combo,
            "poe_limit_label": QtWidgets.QLabel("Power Limit (mW):"),
            "poe_limit_input": self.poe_limit_input
        }

        # Miscellaneous group
        self.private_vlan_host_checkbox = QtWidgets.QCheckBox("Private-VLAN Host")
        self.private_vlan_mapping_input = QtWidgets.QLineEdit()
        self.protected_port_checkbox = QtWidgets.QCheckBox("Protected Port")
        self.no_neighbor_checkbox = QtWidgets.QCheckBox("No Neighbor")

        self.widgets[TabCategory.SYSTEM][FeatureGroup.MISC] = {
            "private_vlan_host_checkbox": self.private_vlan_host_checkbox,
            "private_vlan_mapping_label": QtWidgets.QLabel("PVLAN Mapping:"),
            "private_vlan_mapping_input": self.private_vlan_mapping_input,
            "protected_port_checkbox": self.protected_port_checkbox,
            "no_neighbor_checkbox": self.no_neighbor_checkbox
        }

        # Legacy alias for retro-compatibility
        self.voice_vlan_spin = self.voice_vlan_input
        self.portfast_checkbox = self.spanning_tree_portfast_checkbox

    def _build_layout(self) -> None:
        """Create the complete form layout with tabs and groupboxes."""
        root = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        root.addWidget(self.tabs)

        # Create a tab for each category
        for category in self._tab_structure:
            tab = QtWidgets.QWidget()
            tab_layout = QtWidgets.QVBoxLayout(tab)

            # Create a group box for each feature group in this category
            for group in self._tab_structure[category]:
                group_box = QtWidgets.QGroupBox(group.value)
                group_layout = QtWidgets.QFormLayout(group_box)

                # Add all widgets for this group to the form layout
                for widget_name, widget in self.widgets[category][group].items():
                    if isinstance(widget, QtWidgets.QLabel):
                        # Skip labels as they'll be added with their field
                        continue

                    # Handle ColorPicker specially
                    if widget_name == "color_picker":
                        group_layout.addRow(widget)
                        continue

                    # Check if this widget has a corresponding label
                    label_name = widget_name.replace("_input", "_label").replace("_combo", "_label").replace("_checkbox", "_label")
                    label = self.widgets[category][group].get(label_name)

                    # Add the widget with its label if it has one, otherwise add it directly
                    if label:
                        group_layout.addRow(label, widget)
                    elif isinstance(widget, QtWidgets.QCheckBox):
                        group_layout.addRow(widget)
                    elif isinstance(widget, QtWidgets.QTableWidget) or isinstance(widget, QtWidgets.QListWidget):
                        # These widgets should span both columns
                        item_label = QtWidgets.QLabel(widget_name.replace("_table", "").replace("_list", "").replace("_", " ").title() + ":")
                        group_layout.addRow(item_label)
                        group_layout.addRow(widget)

                        # Add associated buttons if any
                        button_name = widget_name.replace("_table", "_button").replace("_list", "_button")
                        button = self.widgets[category][group].get(button_name)
                        if button:
                            group_layout.addRow(button)

                # Add the group box to the tab
                tab_layout.addWidget(group_box)

            # Add stretch to push groups to the top
            tab_layout.addStretch(1)

            # Add the tab to the tab widget
            self.tabs.addTab(tab, category.value)

        # Set the first tab as active
        self.tabs.setCurrentIndex(0)

    def _connect_signals(self) -> None:
        """Connect widget signals to slot functions."""
        # Connect port security toggling
        self.port_security_checkbox.toggled.connect(self._update_port_security_fields)

        # Connect storm control toggling
        self.storm_control_checkbox.toggled.connect(self._update_storm_control_fields)

        # Connect PoE toggling
        self.poe_enabled_checkbox.toggled.connect(self._update_poe_fields)

        # Connect authentication toggling
        self.dot1x_checkbox.toggled.connect(self._update_auth_fields)
        self.webauth_checkbox.toggled.connect(self._update_webauth_fields)

        # Connect UDLD toggling
        self.udld_enable_checkbox.toggled.connect(self._update_udld_fields)

        # Connect voice VLAN toggling
        self.voice_vlan_none_checkbox.toggled.connect(self._update_voice_vlan_fields)
        self.voice_vlan_dot1p_checkbox.toggled.connect(self._update_voice_vlan_fields)

        # Initialize all dependent fields
        self._update_port_security_fields()
        self._update_storm_control_fields()
        self._update_poe_fields()
        self._update_auth_fields()
        self._update_webauth_fields()
        self._update_udld_fields()
        self._update_voice_vlan_fields()

        # Add MAC button connection
        self.add_mac_button.clicked.connect(self._add_mac_address)

    # -------------------------- Slot functions --------------------------- #

    def _update_port_security_fields(self) -> None:
        """Enable/disable port security related fields."""
        enabled = self.port_security_checkbox.isChecked()
        for field in [self.max_mac_input, self.violation_action_combo,
                     self.sticky_mac_checkbox, self.mac_address_table,
                     self.add_mac_button]:
            field.setEnabled(enabled)

    def _update_storm_control_fields(self) -> None:
        """Enable/disable storm control related fields."""
        enabled = self.storm_control_checkbox.isChecked()
        for field in [self.storm_unit_pps, self.broadcast_min_input,
                     self.broadcast_max_input, self.multicast_min_input,
                     self.multicast_max_input, self.unknown_unicast_min_input,
                     self.unknown_unicast_max_input, self.storm_control_action_combo]:
            field.setEnabled(enabled)

    def _update_poe_fields(self) -> None:
        """Enable/disable PoE related fields."""
        enabled = self.poe_enabled_checkbox.isChecked()
        for field in [self.poe_inline_combo, self.poe_priority_combo,
                     self.poe_limit_input]:
            field.setEnabled(enabled)

    def _update_auth_fields(self) -> None:
        """Enable/disable authentication related fields."""
        enabled = self.dot1x_checkbox.isChecked() or self.mab_checkbox.isChecked()
        for field in [self.authentication_host_mode_combo, self.authentication_open_checkbox,
                     self.authentication_periodic_checkbox, self.authentication_timer_input,
                     self.authentication_order_list]:
            field.setEnabled(enabled)

    def _update_webauth_fields(self) -> None:
        """Enable/disable web authentication related fields."""
        enabled = self.webauth_checkbox.isChecked()
        self.webauth_local_checkbox.setEnabled(enabled)

    def _update_udld_fields(self) -> None:
        """Enable/disable UDLD related fields."""
        enabled = self.udld_enable_checkbox.isChecked()
        self.udld_aggressive_checkbox.setEnabled(enabled)

    def _update_voice_vlan_fields(self) -> None:
        """Handle voice VLAN option exclusivity."""
        if self.voice_vlan_none_checkbox.isChecked():
            self.voice_vlan_input.setEnabled(False)
            self.voice_vlan_dot1p_checkbox.setEnabled(False)
        elif self.voice_vlan_dot1p_checkbox.isChecked():
            self.voice_vlan_input.setEnabled(False)
            self.voice_vlan_none_checkbox.setEnabled(False)
        else:
            self.voice_vlan_input.setEnabled(True)
            self.voice_vlan_none_checkbox.setEnabled(True)
            self.voice_vlan_dot1p_checkbox.setEnabled(True)

    def _add_mac_address(self) -> None:
        """Add a new row to the MAC address table."""
        row = self.mac_address_table.rowCount()
        self.mac_address_table.insertRow(row)

        mac_edit = QtWidgets.QLineEdit()
        mac_edit.setPlaceholderText("00:11:22:33:44:55")

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)

        # Connect the delete button to remove this row
        delete_button.clicked.connect(lambda: self.mac_address_table.removeRow(
            self.mac_address_table.indexAt(delete_button.pos()).row()))

        self.mac_address_table.setCellWidget(row, 0, mac_edit)
        self.mac_address_table.setCellWidget(row, 1, delete_button)

    # -------------------------- Data sync functions ---------------------- #

    def load_from_instance(self, inst) -> None:
        """Populate widgets from an AccessTemplate instance."""
        # Basic identification
        self.interfaces_input.setText(",".join(inst.interfaces))
        self.vlan_id_input.setValue(inst.vlan_id)
        self.description_input.setText(inst.description or "")

        # Set color if provided - using current_color for ColorPicker
        if hasattr(inst, 'color') and inst.color:
            # Check if the color is a valid QColor
            color_value = inst.color
            if isinstance(color_value, str) and QtGui.QColor(color_value).isValid():
                # Use the toggle_dropdown() to initialize the color picker properly
                self.color_picker.toggle_dropdown()
                self.color_picker.dropdown.hide()

                # Set the current_color directly
                self.color_picker.current_color = QtGui.QColor(color_value)
                self.color_picker.update_color_ui()

        # Physical layer settings
        self.speed_combo.setCurrentText(inst.speed)
        self.duplex_combo.setCurrentText(inst.duplex)
        self.auto_mdix_checkbox.setChecked(inst.auto_mdix)
        self.energy_efficient_ethernet_checkbox.setChecked(inst.energy_efficient_ethernet)
        self.flow_control_receive_checkbox.setChecked(inst.flow_control_receive)
        self.flow_control_send_checkbox.setChecked(inst.flow_control_send)

        # Discovery protocols
        self.cdp_enabled_checkbox.setChecked(inst.cdp_enabled)
        self.lldp_transmit_checkbox.setChecked(inst.lldp_transmit)
        self.lldp_receive_checkbox.setChecked(inst.lldp_receive)
        self.load_interval_input.setValue(inst.load_interval)

        # Voice VLAN
        if inst.voice_vlan_none:
            self.voice_vlan_none_checkbox.setChecked(True)
        elif inst.voice_vlan_dot1p:
            self.voice_vlan_dot1p_checkbox.setChecked(True)
        elif inst.voice_vlan:
            self.voice_vlan_input.setValue(inst.voice_vlan)

        # Spanning Tree features
        self.spanning_tree_portfast_checkbox.setChecked(inst.spanning_tree_portfast)
        self.spanning_tree_portfast_trunk_checkbox.setChecked(inst.spanning_tree_portfast_trunk)
        self.bpdu_guard_checkbox.setChecked(inst.bpdu_guard)
        self.bpdu_filter_checkbox.setChecked(inst.bpdu_filter)
        self.loop_guard_checkbox.setChecked(inst.loop_guard)
        self.root_guard_checkbox.setChecked(inst.root_guard)

        if inst.spanning_tree_link_type:
            self.spanning_tree_link_type_combo.setCurrentText(inst.spanning_tree_link_type)

        # Port Security
        self.port_security_checkbox.setChecked(inst.port_security_enabled)
        self.max_mac_input.setValue(inst.max_mac_addresses)

        # Handle the ViolationAction enum
        if isinstance(inst.violation_action, ViolationAction):
            self.violation_action_combo.setCurrentText(inst.violation_action.value)
        else:
            # Fallback for string values for backward compatibility
            self.violation_action_combo.setCurrentText(str(inst.violation_action))

        self.sticky_mac_checkbox.setChecked(inst.sticky_mac)

        # Clear and populate MAC address table
        self.mac_address_table.setRowCount(0)
        for mac in inst.restricted_mac_addresses:
            self._add_mac_address()
            row = self.mac_address_table.rowCount() - 1
            mac_edit = self.mac_address_table.cellWidget(row, 0)
            mac_edit.setText(mac)

        # Authentication
        self.dot1x_checkbox.setChecked(inst.dot1x)
        self.mab_checkbox.setChecked(inst.mab)
        self.webauth_checkbox.setChecked(inst.webauth)
        self.webauth_local_checkbox.setChecked(inst.webauth_local)

        self.authentication_host_mode_combo.setCurrentText(inst.authentication_host_mode)
        self.authentication_open_checkbox.setChecked(inst.authentication_open)
        self.authentication_periodic_checkbox.setChecked(inst.authentication_periodic)
        self.authentication_timer_input.setValue(inst.authentication_timer_reauthenticate)

        # DHCP/ARP security
        self.dhcp_snoop_trust_checkbox.setChecked(inst.dhcp_snoop_trust)
        self.dhcp_snoop_rate_input.setValue(inst.dhcp_snoop_rate or 0)
        self.arp_inspection_trust_checkbox.setChecked(inst.arp_inspection_trust)
        self.arp_inspection_rate_input.setValue(inst.arp_inspection_rate or 0)
        self.dhcp_relay_information_checkbox.setChecked(inst.ip_dhcp_relay_information)

        # IP Source Guard
        self.ip_source_guard_checkbox.setChecked(inst.ip_source_guard)

        # IPv6 Security
        self.ipv6_nd_inspection_checkbox.setChecked(inst.ipv6_nd_inspection)
        self.ipv6_ra_guard_checkbox.setChecked(inst.ipv6_ra_guard)
        self.device_tracking_checkbox.setChecked(inst.device_tracking)

        # QoS Trust Settings
        if inst.qos_trust:
            if isinstance(inst.qos_trust, QoSTrustState):
                self.qos_trust_combo.setCurrentText(inst.qos_trust.value)
            else:
                # Fallback for string values
                self.qos_trust_combo.setCurrentText(str(inst.qos_trust))
        else:
            self.qos_trust_combo.setCurrentText("--")

        # QoS Marking
        if inst.qos_cos_override is not None:
            self.qos_cos_override_input.setValue(inst.qos_cos_override)
        if inst.qos_dscp_override is not None:
            self.qos_dscp_override_input.setValue(inst.qos_dscp_override)
        self.priority_queue_out_checkbox.setChecked(inst.priority_queue_out)

        # QoS Policing/Shaping
        self.service_policy_input.setText(inst.service_policy_input or "")
        self.service_policy_output_input.setText(inst.service_policy_output or "")
        if inst.shape_average:
            self.shape_average_input.setValue(inst.shape_average)
        if inst.police_rate:
            self.police_rate_input.setValue(inst.police_rate)
        if inst.police_burst:
            self.police_burst_input.setValue(inst.police_burst)

        # Error Recovery
        self.errdisable_timeout_input.setValue(inst.errdisable_timeout or 0)

        # Check errdisable recovery causes in the list
        for i in range(self.errdisable_recovery_list.count()):
            item = self.errdisable_recovery_list.item(i)
            cause = item.text()
            if cause in inst.errdisable_recovery_cause:
                item.setCheckState(QtCore.Qt.Checked)

        # Storm Control
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

        if inst.storm_control_action:
            self.storm_control_action_combo.setCurrentText(inst.storm_control_action)

        # UDLD
        self.udld_enable_checkbox.setChecked(inst.udld_enable)
        self.udld_aggressive_checkbox.setChecked(inst.udld_aggressive)

        # Power Management (PoE)
        self.poe_enabled_checkbox.setChecked(inst.poe_enabled)

        # Handle PowerInlineMode enum
        if isinstance(inst.poe_inline, PowerInlineMode):
            self.poe_inline_combo.setCurrentText(inst.poe_inline.value)
        else:
            # Fallback for string values
            self.poe_inline_combo.setCurrentText(str(inst.poe_inline))

        self.poe_priority_combo.setCurrentText(inst.poe_priority)
        if inst.poe_limit:
            self.poe_limit_input.setValue(inst.poe_limit)

        # Private VLAN and others
        self.private_vlan_host_checkbox.setChecked(inst.private_vlan_host)
        self.private_vlan_mapping_input.setText(inst.private_vlan_mapping or "")
        self.protected_port_checkbox.setChecked(inst.protected_port)
        self.no_neighbor_checkbox.setChecked(inst.no_neighbor)

        # Update dependent fields
        self._update_port_security_fields()
        self._update_storm_control_fields()
        self._update_poe_fields()
        self._update_auth_fields()
        self._update_webauth_fields()
        self._update_udld_fields()
        self._update_voice_vlan_fields()

    def get_mac_addresses(self) -> List[str]:
        """Extract MAC addresses from the table widget."""
        macs = []
        for row in range(self.mac_address_table.rowCount()):
            mac_edit = self.mac_address_table.cellWidget(row, 0)
            mac = mac_edit.text().strip()
            if mac:
                macs.append(mac)
        return macs

    def get_errdisable_recovery_causes(self) -> List[str]:
        """Extract checked errdisable recovery causes from the list widget."""
        causes = []
        for i in range(self.errdisable_recovery_list.count()):
            item = self.errdisable_recovery_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                causes.append(item.text())
        return causes

    def get_authentication_order(self) -> List[str]:
        """Extract authentication order from the list widget."""
        order = []
        for i in range(self.authentication_order_list.count()):
            item = self.authentication_order_list.item(i)
            order.append(item.text())
        return order

    def get_instance_data(self) -> Dict[str, Any]:
        """Collect all form data into a dictionary for creating AccessTemplate instance."""
        data = {
            # Basic identification
            "interfaces": [s.strip() for s in self.interfaces_input.text().split(",") if s.strip()],
            "vlan_id": self.vlan_id_input.value(),
            "description": self.description_input.text() or None,
            "color": self.color_picker.get_value(),  # Get color from picker using get_value()

            # Physical layer
            "speed": self.speed_combo.currentText(),
            "duplex": self.duplex_combo.currentText(),
            "auto_mdix": self.auto_mdix_checkbox.isChecked(),
            "energy_efficient_ethernet": self.energy_efficient_ethernet_checkbox.isChecked(),
            "flow_control_receive": self.flow_control_receive_checkbox.isChecked(),
            "flow_control_send": self.flow_control_send_checkbox.isChecked(),

            # Discovery protocols
            "cdp_enabled": self.cdp_enabled_checkbox.isChecked(),
            "lldp_transmit": self.lldp_transmit_checkbox.isChecked(),
            "lldp_receive": self.lldp_receive_checkbox.isChecked(),
            "load_interval": self.load_interval_input.value(),

            # Voice VLAN
            "voice_vlan": (None if self.voice_vlan_none_checkbox.isChecked() or 
                           self.voice_vlan_dot1p_checkbox.isChecked() else 
                           self.voice_vlan_input.value() or None),
            "voice_vlan_dot1p": self.voice_vlan_dot1p_checkbox.isChecked(),
            "voice_vlan_none": self.voice_vlan_none_checkbox.isChecked(),

            # Spanning Tree
            "spanning_tree_portfast": self.spanning_tree_portfast_checkbox.isChecked(),
            "spanning_tree_portfast_trunk": self.spanning_tree_portfast_trunk_checkbox.isChecked(),
            "bpdu_guard": self.bpdu_guard_checkbox.isChecked(),
            "bpdu_filter": self.bpdu_filter_checkbox.isChecked(),
            "loop_guard": self.loop_guard_checkbox.isChecked(),
            "root_guard": self.root_guard_checkbox.isChecked(),
            "spanning_tree_link_type": (None if self.spanning_tree_link_type_combo.currentText() == "default" else
                                       self.spanning_tree_link_type_combo.currentText()),

            # Port Security
            "port_security_enabled": self.port_security_checkbox.isChecked(),
            "max_mac_addresses": self.max_mac_input.value(),
            "violation_action": ViolationAction(self.violation_action_combo.currentText()),
            "sticky_mac": self.sticky_mac_checkbox.isChecked(),
            "restricted_mac_addresses": self.get_mac_addresses(),

            # Authentication
            "dot1x": self.dot1x_checkbox.isChecked(),
            "mab": self.mab_checkbox.isChecked(),
            "webauth": self.webauth_checkbox.isChecked(),
            "webauth_local": self.webauth_local_checkbox.isChecked(),
            "authentication_host_mode": self.authentication_host_mode_combo.currentText(),
            "authentication_open": self.authentication_open_checkbox.isChecked(),
            "authentication_periodic": self.authentication_periodic_checkbox.isChecked(),
            "authentication_timer_reauthenticate": self.authentication_timer_input.value(),
            "authentication_order": self.get_authentication_order(),
            "authentication_priority": self.get_authentication_order(),  # Same as order for now

            # DHCP/ARP Security
            "dhcp_snoop_trust": self.dhcp_snoop_trust_checkbox.isChecked(),
            "dhcp_snoop_rate": self.dhcp_snoop_rate_input.value() or None,
            "arp_inspection_trust": self.arp_inspection_trust_checkbox.isChecked(),
            "arp_inspection_rate": self.arp_inspection_rate_input.value() or None,
            "ip_dhcp_relay_information": self.dhcp_relay_information_checkbox.isChecked(),

            # IP Source Guard
            "ip_source_guard": self.ip_source_guard_checkbox.isChecked(),

            # IPv6 Security
            "ipv6_nd_inspection": self.ipv6_nd_inspection_checkbox.isChecked(),
            "ipv6_ra_guard": self.ipv6_ra_guard_checkbox.isChecked(),
            "device_tracking": self.device_tracking_checkbox.isChecked(),

            # QoS Trust
            "qos_trust": (None if self.qos_trust_combo.currentText() == "--" 
                         else QoSTrustState(self.qos_trust_combo.currentText())),

            # QoS Marking
            "qos_cos_override": self.qos_cos_override_input.value() if self.qos_cos_override_input.value() > 0 else None,
            "qos_dscp_override": self.qos_dscp_override_input.value() if self.qos_dscp_override_input.value() > 0 else None,
            "priority_queue_out": self.priority_queue_out_checkbox.isChecked(),

            # QoS Policing
            "service_policy_input": self.service_policy_input.text() or None,
            "service_policy_output": self.service_policy_output_input.text() or None,
            "shape_average": self.shape_average_input.value() if self.shape_average_input.value() > 0 else None,
            "police_rate": self.police_rate_input.value() if self.police_rate_input.value() > 0 else None,
            "police_burst": self.police_burst_input.value() if self.police_burst_input.value() > 0 else None,

            # Error Recovery
            "errdisable_timeout": self.errdisable_timeout_input.value() or None,
            "errdisable_recovery_cause": self.get_errdisable_recovery_causes(),

            # Storm Control
            "storm_control_broadcast_min": (self.broadcast_min_input.value() 
                                           if self.storm_control_checkbox.isChecked() else None),
            "storm_control_broadcast_max": (self.broadcast_max_input.value() 
                                           if self.storm_control_checkbox.isChecked() else None),
            "storm_control_multicast_min": (self.multicast_min_input.value() 
                                           if self.storm_control_checkbox.isChecked() else None),
            "storm_control_multicast_max": (self.multicast_max_input.value() 
                                           if self.storm_control_checkbox.isChecked() else None),
            "storm_control_unknown_unicast_min": (self.unknown_unicast_min_input.value() 
                                                 if self.storm_control_checkbox.isChecked() else None),
            "storm_control_unknown_unicast_max": (self.unknown_unicast_max_input.value() 
                                                 if self.storm_control_checkbox.isChecked() else None),
            "storm_control_unit_pps": self.storm_unit_pps.isChecked(),
            "storm_control_action": (None if self.storm_control_action_combo.currentText() == "--" 
                                    else self.storm_control_action_combo.currentText()),

            # UDLD
            "udld_enable": self.udld_enable_checkbox.isChecked(),
            "udld_aggressive": self.udld_aggressive_checkbox.isChecked(),

            # Power Management (PoE)
            "poe_enabled": self.poe_enabled_checkbox.isChecked(),
            "poe_inline": PowerInlineMode(self.poe_inline_combo.currentText()),
            "poe_priority": self.poe_priority_combo.currentText(),
            "poe_limit": self.poe_limit_input.value() or None,

            # Miscellaneous
            "private_vlan_host": self.private_vlan_host_checkbox.isChecked(),
            "private_vlan_mapping": self.private_vlan_mapping_input.text() or None,
            "protected_port": self.protected_port_checkbox.isChecked(),
            "no_neighbor": self.no_neighbor_checkbox.isChecked(),
        }

        return data

    def create_access_template(self) -> AccessTemplate:
        """Create and return an AccessTemplate instance from the form data."""
        data = self.get_instance_data()
        return AccessTemplate(**data)