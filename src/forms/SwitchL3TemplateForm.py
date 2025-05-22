# src/forms/SwitchL3TemplateForm.py
"""Rozszerzony formularz PySide6 dla SwitchL3Template z kompleksowymi opcjami konfiguracji L3.

Formularz zawiera dodatkowe zakładki dla funkcji routingu warstwy 3:
- Interfejsy SVI: Konfiguracja interfejsów wirtualnych do komunikacji między VLAN-ami
- Routing: Konfiguracja protokołów routingu (OSPF, EIGRP, BGP) i tras statycznych
- Bezpieczeństwo L3: ACL, NAT, oraz zaawansowane funkcje filtrowania
- Usługi: Serwer DHCP, HSRP/VRRP, VRF
"""
from typing import List, Dict

from PySide6 import QtWidgets, QtCore, QtGui

from src.forms.SwitchL2TemplateForm import \
    SwitchL2TemplateForm  # Zmiana: importuj SwitchL2TemplateForm zamiast SwitchTemplateForm
from src.models.templates.SwitchL3Template import SwitchL3Template, SwitchVirtualInterface, StaticRoute, ACLEntry, \
    RoutingProtocol


class SwitchL3TemplateForm(SwitchL2TemplateForm):  # Zmiana: dziedzicz po SwitchL2TemplateForm
    """Kompleksowy formularz do konfiguracji przełącznika warstwy 3."""

    def __init__(self, parent=None, instance=None):
        # Inicjalizacja podstawowego formularza przełącznika
        super().__init__(parent, instance)

        # Debugowanie - sprawdź, czy atrybut 'tabs' istnieje
        if not hasattr(self, 'tabs'):
            print("[DEBUG] Atrybut 'tabs' nie istnieje w klasie bazowej! Tworzenie...")

            # Jeśli tabs nie istnieje, tworzymy nowy układ z zakładkami
            self.tabs = QtWidgets.QTabWidget()

            # Usuwamy istniejący układ i tworzymy nowy
            # UWAGA: To może usunąć wszystkie istniejące widgety!
            # Lepszym rozwiązaniem jest naprawienie klasy bazowej
            QtWidgets.QWidget().setLayout(self.layout())

            root = QtWidgets.QVBoxLayout(self)
            root.addWidget(self.tabs)

            # Utwórz podstawowe zakładki, które powinny być w SwitchL2TemplateForm
            self._create_base_tabs()

        # Dodaj dodatkowe zakładki dla funkcji L3
        self._create_l3_widgets()
        self._build_l3_layout()
        self._connect_l3_signals()

        # Załaduj dane z instancji, jeśli podana
        if instance is not None and isinstance(instance, SwitchL3Template):
            self.load_l3_from_instance(instance)

    def _create_base_tabs(self):
        """Utwórz podstawowe zakładki przełącznika L2, jeśli nie zostały utworzone przez klasę bazową."""
        # Ta metoda jest wywoływana tylko jeśli wykryto brak atrybutu 'tabs'

        # Zakładka Basic Settings
        basic_tab = QtWidgets.QWidget()
        basic_layout = QtWidgets.QFormLayout(basic_tab)

        self.hostname_input = QtWidgets.QLineEdit()
        self.manager_vlan_id_combo = QtWidgets.QComboBox()
        self.manager_vlan_id_combo.addItem("1")
        self.manager_ip_input = QtWidgets.QLineEdit()
        self.default_gateway_input = QtWidgets.QLineEdit()

        basic_layout.addRow("Hostname:", self.hostname_input)
        basic_layout.addRow("Management VLAN:", self.manager_vlan_id_combo)
        basic_layout.addRow("Management IP:", self.manager_ip_input)
        basic_layout.addRow("Default Gateway:", self.default_gateway_input)

        self.tabs.addTab(basic_tab, "Basic Settings")

        # Zakładka VLANs
        vlans_tab = QtWidgets.QWidget()
        vlans_layout = QtWidgets.QVBoxLayout(vlans_tab)

        self.vlan_table = QtWidgets.QTableWidget()
        self.vlan_table.setColumnCount(3)
        self.vlan_table.setHorizontalHeaderLabels(["VLAN ID", "Name", "Status"])

        vlans_layout.addWidget(self.vlan_table)

        self.tabs.addTab(vlans_tab, "VLANs")

    # --------------------------- L3 widgets ----------------------------- #
    def _create_l3_widgets(self) -> None:
        """Tworzenie wszystkich widgetów związanych z funkcjami L3."""
        # ---------------------------------------------------------------- #
        # Zakładka Interfejsy SVI
        # ---------------------------------------------------------------- #

        # Tabela interfejsów SVI
        self.svi_table = QtWidgets.QTableWidget()
        self.svi_table.setColumnCount(5)
        self.svi_table.setHorizontalHeaderLabels(["VLAN ID", "IP Address", "Subnet Mask", "Description", ""])
        self.svi_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.svi_table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

        self.add_svi_button = QtWidgets.QPushButton("Dodaj SVI")
        self.add_svi_button.clicked.connect(self._add_svi_row)

        # ---------------------------------------------------------------- #
        # Zakładka Routing
        # ---------------------------------------------------------------- #

        # Włączenie routingu
        self.routing_enabled_checkbox = QtWidgets.QCheckBox("Włącz routing IP")
        self.ipv6_routing_checkbox = QtWidgets.QCheckBox("Włącz routing IPv6")

        # Trasy statyczne
        self.static_routes_table = QtWidgets.QTableWidget()
        self.static_routes_table.setColumnCount(5)
        self.static_routes_table.setHorizontalHeaderLabels(["Prefix", "Mask", "Next Hop", "Distance", ""])
        self.static_routes_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.static_routes_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.add_static_route_button = QtWidgets.QPushButton("Dodaj trasę statyczną")
        self.add_static_route_button.clicked.connect(self._add_static_route_row)

        # OSPF
        self.ospf_enabled_checkbox = QtWidgets.QCheckBox("Włącz OSPF")
        self.ospf_process_id_input = QtWidgets.QSpinBox()
        self.ospf_process_id_input.setRange(1, 65535)
        self.ospf_router_id_input = QtWidgets.QLineEdit()

        self.ospf_networks_table = QtWidgets.QTableWidget()
        self.ospf_networks_table.setColumnCount(4)
        self.ospf_networks_table.setHorizontalHeaderLabels(["Network", "Wildcard", "Area", ""])
        self.ospf_networks_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        self.add_ospf_network_button = QtWidgets.QPushButton("Dodaj sieć OSPF")
        self.add_ospf_network_button.clicked.connect(self._add_ospf_network_row)

        # EIGRP
        self.eigrp_enabled_checkbox = QtWidgets.QCheckBox("Włącz EIGRP")
        self.eigrp_as_input = QtWidgets.QSpinBox()
        self.eigrp_as_input.setRange(1, 65535)

        self.eigrp_networks_table = QtWidgets.QTableWidget()
        self.eigrp_networks_table.setColumnCount(3)
        self.eigrp_networks_table.setHorizontalHeaderLabels(["Network", "Wildcard", ""])
        self.eigrp_networks_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        self.add_eigrp_network_button = QtWidgets.QPushButton("Dodaj sieć EIGRP")
        self.add_eigrp_network_button.clicked.connect(self._add_eigrp_network_row)

        # ---------------------------------------------------------------- #
        # Zakładka Bezpieczeństwo L3
        # ---------------------------------------------------------------- #

        # ACL
        self.acl_table = QtWidgets.QTableWidget()
        self.acl_table.setColumnCount(8)
        self.acl_table.setHorizontalHeaderLabels([
            "Nazwa ACL", "Seq", "Akcja", "Protokół",
            "Źródło", "Cel", "Port Oper", ""
        ])
        self.acl_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.acl_table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.acl_table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)

        self.add_acl_button = QtWidgets.QPushButton("Dodaj regułę ACL")
        self.add_acl_button.clicked.connect(self._add_acl_row)

        # NAT
        self.nat_inside_interfaces_input = QtWidgets.QLineEdit()
        self.nat_outside_interfaces_input = QtWidgets.QLineEdit()

        self.nat_pool_table = QtWidgets.QTableWidget()
        self.nat_pool_table.setColumnCount(5)
        self.nat_pool_table.setHorizontalHeaderLabels([
            "Nazwa puli", "Start IP", "End IP", "Prefix-length", ""
        ])
        self.nat_pool_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        self.add_nat_pool_button = QtWidgets.QPushButton("Dodaj pulę NAT")
        self.add_nat_pool_button.clicked.connect(self._add_nat_pool_row)

        self.nat_acl_pool_table = QtWidgets.QTableWidget()
        self.nat_acl_pool_table.setColumnCount(3)
        self.nat_acl_pool_table.setHorizontalHeaderLabels([
            "ACL", "Pool", ""
        ])
        self.nat_acl_pool_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.nat_acl_pool_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self.add_nat_acl_pool_button = QtWidgets.QPushButton("Dodaj mapowanie ACL -> Pool")
        self.add_nat_acl_pool_button.clicked.connect(self._add_nat_acl_pool_row)

        # ---------------------------------------------------------------- #
        # Zakładka Usługi
        # ---------------------------------------------------------------- #

        # DHCP Server
        self.dhcp_excluded_input = QtWidgets.QLineEdit()

        self.dhcp_pool_table = QtWidgets.QTableWidget()
        self.dhcp_pool_table.setColumnCount(5)
        self.dhcp_pool_table.setHorizontalHeaderLabels([
            "Nazwa puli", "Network", "Default Router", "DNS", ""
        ])
        self.dhcp_pool_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.dhcp_pool_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self.add_dhcp_pool_button = QtWidgets.QPushButton("Dodaj pulę DHCP")
        self.add_dhcp_pool_button.clicked.connect(self._add_dhcp_pool_row)

        # HSRP/VRRP
        self.hsrp_table = QtWidgets.QTableWidget()
        self.hsrp_table.setColumnCount(5)
        self.hsrp_table.setHorizontalHeaderLabels([
            "Interfejs", "Grupa", "IP", "Priorytet", ""
        ])
        self.hsrp_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.hsrp_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.add_hsrp_button = QtWidgets.QPushButton("Dodaj grupę HSRP")
        self.add_hsrp_button.clicked.connect(self._add_hsrp_row)

        # VRF
        self.vrf_table = QtWidgets.QTableWidget()
        self.vrf_table.setColumnCount(3)
        self.vrf_table.setHorizontalHeaderLabels([
            "Nazwa VRF", "Route Distinguisher", ""
        ])
        self.vrf_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.vrf_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self.add_vrf_button = QtWidgets.QPushButton("Dodaj VRF")
        self.add_vrf_button.clicked.connect(self._add_vrf_row)

    # --------------------------- L3 layout ----------------------------- #
    def _build_l3_layout(self) -> None:
        """Tworzenie układu formularza z dodatkowymi zakładkami L3."""
        # Sprawdź, czy mamy obiekt tabs
        if not hasattr(self, 'tabs'):
            print("[ERROR] Brak atrybutu 'tabs' w SwitchL3TemplateForm!")
            return

        # 9. Zakładka Interfejsy SVI
        svi_tab = QtWidgets.QWidget()
        svi_layout = QtWidgets.QVBoxLayout(svi_tab)
        svi_layout.addWidget(self.svi_table)
        svi_layout.addWidget(self.add_svi_button)
        self.tabs.addTab(svi_tab, "Interfejsy SVI")

        # 10. Zakładka Routing
        routing_tab = QtWidgets.QWidget()
        routing_layout = QtWidgets.QVBoxLayout(routing_tab)

        # General routing
        routing_group = QtWidgets.QGroupBox("Ogólne ustawienia routingu")
        routing_form = QtWidgets.QFormLayout(routing_group)
        routing_form.addRow(self.routing_enabled_checkbox)
        routing_form.addRow(self.ipv6_routing_checkbox)
        routing_layout.addWidget(routing_group)

        # Static routes
        static_group = QtWidgets.QGroupBox("Trasy statyczne")
        static_layout = QtWidgets.QVBoxLayout(static_group)
        static_layout.addWidget(self.static_routes_table)
        static_layout.addWidget(self.add_static_route_button)
        routing_layout.addWidget(static_group)

        # OSPF
        ospf_group = QtWidgets.QGroupBox("OSPF")
        ospf_layout = QtWidgets.QVBoxLayout(ospf_group)
        ospf_form = QtWidgets.QFormLayout()
        ospf_form.addRow(self.ospf_enabled_checkbox)
        ospf_form.addRow("Process ID:", self.ospf_process_id_input)
        ospf_form.addRow("Router ID:", self.ospf_router_id_input)
        ospf_layout.addLayout(ospf_form)
        ospf_layout.addWidget(self.ospf_networks_table)
        ospf_layout.addWidget(self.add_ospf_network_button)
        routing_layout.addWidget(ospf_group)

        # EIGRP
        eigrp_group = QtWidgets.QGroupBox("EIGRP")
        eigrp_layout = QtWidgets.QVBoxLayout(eigrp_group)
        eigrp_form = QtWidgets.QFormLayout()
        eigrp_form.addRow(self.eigrp_enabled_checkbox)
        eigrp_form.addRow("AS:", self.eigrp_as_input)
        eigrp_layout.addLayout(eigrp_form)
        eigrp_layout.addWidget(self.eigrp_networks_table)
        eigrp_layout.addWidget(self.add_eigrp_network_button)
        routing_layout.addWidget(eigrp_group)

        self.tabs.addTab(routing_tab, "Routing")

        # 11. Zakładka Bezpieczeństwo L3
        security_tab = QtWidgets.QWidget()
        security_layout = QtWidgets.QVBoxLayout(security_tab)

        # ACL
        acl_group = QtWidgets.QGroupBox("Access Control Lists")
        acl_layout = QtWidgets.QVBoxLayout(acl_group)
        acl_layout.addWidget(self.acl_table)
        acl_layout.addWidget(self.add_acl_button)
        security_layout.addWidget(acl_group)

        # NAT
        nat_group = QtWidgets.QGroupBox("Network Address Translation")
        nat_layout = QtWidgets.QVBoxLayout(nat_group)
        nat_form = QtWidgets.QFormLayout()
        nat_form.addRow("Inside Interfaces:", self.nat_inside_interfaces_input)
        nat_form.addRow("Outside Interfaces:", self.nat_outside_interfaces_input)
        nat_layout.addLayout(nat_form)

        nat_pool_label = QtWidgets.QLabel("NAT Pools:")
        nat_layout.addWidget(nat_pool_label)
        nat_layout.addWidget(self.nat_pool_table)
        nat_layout.addWidget(self.add_nat_pool_button)

        nat_acl_label = QtWidgets.QLabel("NAT ACL Mappings:")
        nat_layout.addWidget(nat_acl_label)
        nat_layout.addWidget(self.nat_acl_pool_table)
        nat_layout.addWidget(self.add_nat_acl_pool_button)

        security_layout.addWidget(nat_group)

        self.tabs.addTab(security_tab, "Bezpieczeństwo L3")

        # 12. Zakładka Usługi
        services_tab = QtWidgets.QWidget()
        services_layout = QtWidgets.QVBoxLayout(services_tab)

        # DHCP Server
        dhcp_group = QtWidgets.QGroupBox("DHCP Server")
        dhcp_layout = QtWidgets.QVBoxLayout(dhcp_group)
        dhcp_form = QtWidgets.QFormLayout()
        dhcp_form.addRow("Excluded Addresses:", self.dhcp_excluded_input)
        dhcp_layout.addLayout(dhcp_form)

        dhcp_layout.addWidget(self.dhcp_pool_table)
        dhcp_layout.addWidget(self.add_dhcp_pool_button)
        services_layout.addWidget(dhcp_group)

        # HSRP/VRRP
        hsrp_group = QtWidgets.QGroupBox("HSRP/VRRP")
        hsrp_layout = QtWidgets.QVBoxLayout(hsrp_group)
        hsrp_layout.addWidget(self.hsrp_table)
        hsrp_layout.addWidget(self.add_hsrp_button)
        services_layout.addWidget(hsrp_group)

        # VRF
        vrf_group = QtWidgets.QGroupBox("VRF")
        vrf_layout = QtWidgets.QVBoxLayout(vrf_group)
        vrf_layout.addWidget(self.vrf_table)
        vrf_layout.addWidget(self.add_vrf_button)
        services_layout.addWidget(vrf_group)

        self.tabs.addTab(services_tab, "Usługi")

    # ------------------------- Signals Connection ----------------------------- #
    def _connect_l3_signals(self) -> None:
        """Podłączenie sygnałów dla widgetów L3."""
        # Włączanie/wyłączanie sekcji w zależności od checkboxów
        self.ospf_enabled_checkbox.toggled.connect(self._update_ospf_fields)
        self.eigrp_enabled_checkbox.toggled.connect(self._update_eigrp_fields)

        # Wywołaj funkcje aktualizacji od razu po inicjalizacji
        self._update_ospf_fields()
        self._update_eigrp_fields()

    def _update_ospf_fields(self) -> None:
        """Włącz/wyłącz pola OSPF w zależności od stanu checkboxa."""
        enabled = self.ospf_enabled_checkbox.isChecked()
        self.ospf_process_id_input.setEnabled(enabled)
        self.ospf_router_id_input.setEnabled(enabled)
        self.ospf_networks_table.setEnabled(enabled)
        self.add_ospf_network_button.setEnabled(enabled)

    def _update_eigrp_fields(self) -> None:
        """Włącz/wyłącz pola EIGRP w zależności od stanu checkboxa."""
        enabled = self.eigrp_enabled_checkbox.isChecked()
        self.eigrp_as_input.setEnabled(enabled)
        self.eigrp_networks_table.setEnabled(enabled)
        self.add_eigrp_network_button.setEnabled(enabled)

    # ------------------------ Dynamic rows ---------------------------- #
    def _add_svi_row(self) -> None:
        """Dodaj nowy wiersz do tabeli interfejsów SVI."""
        row = self.svi_table.rowCount()
        self.svi_table.insertRow(row)

        vlan_id = QtWidgets.QSpinBox()
        vlan_id.setRange(1, 4094)

        ip_address = QtWidgets.QLineEdit()
        ip_address.setPlaceholderText("192.168.1.1")

        subnet_mask = QtWidgets.QLineEdit()
        subnet_mask.setPlaceholderText("255.255.255.0")

        description = QtWidgets.QLineEdit()

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.svi_table.removeRow(
            self.svi_table.indexAt(delete_button.pos()).row()))

        self.svi_table.setCellWidget(row, 0, vlan_id)
        self.svi_table.setCellWidget(row, 1, ip_address)
        self.svi_table.setCellWidget(row, 2, subnet_mask)
        self.svi_table.setCellWidget(row, 3, description)
        self.svi_table.setCellWidget(row, 4, delete_button)

    def _add_static_route_row(self) -> None:
        """Dodaj nowy wiersz do tabeli tras statycznych."""
        row = self.static_routes_table.rowCount()
        self.static_routes_table.insertRow(row)

        prefix = QtWidgets.QLineEdit()
        prefix.setPlaceholderText("192.168.0.0")

        mask = QtWidgets.QLineEdit()
        mask.setPlaceholderText("255.255.255.0")

        next_hop = QtWidgets.QLineEdit()
        next_hop.setPlaceholderText("10.0.0.1")

        distance = QtWidgets.QSpinBox()
        distance.setRange(1, 255)
        distance.setValue(1)

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.static_routes_table.removeRow(
            self.static_routes_table.indexAt(delete_button.pos()).row()))

        self.static_routes_table.setCellWidget(row, 0, prefix)
        self.static_routes_table.setCellWidget(row, 1, mask)
        self.static_routes_table.setCellWidget(row, 2, next_hop)
        self.static_routes_table.setCellWidget(row, 3, distance)
        self.static_routes_table.setCellWidget(row, 4, delete_button)

    def _add_ospf_network_row(self) -> None:
        """Dodaj nowy wiersz do tabeli sieci OSPF."""
        row = self.ospf_networks_table.rowCount()
        self.ospf_networks_table.insertRow(row)

        network = QtWidgets.QLineEdit()
        network.setPlaceholderText("192.168.1.0")

        wildcard = QtWidgets.QLineEdit()
        wildcard.setPlaceholderText("0.0.0.255")

        area = QtWidgets.QLineEdit()
        area.setPlaceholderText("0")

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.ospf_networks_table.removeRow(
            self.ospf_networks_table.indexAt(delete_button.pos()).row()))

        self.ospf_networks_table.setCellWidget(row, 0, network)
        self.ospf_networks_table.setCellWidget(row, 1, wildcard)
        self.ospf_networks_table.setCellWidget(row, 2, area)
        self.ospf_networks_table.setCellWidget(row, 3, delete_button)

    def _add_eigrp_network_row(self) -> None:
        """Dodaj nowy wiersz do tabeli sieci EIGRP."""
        row = self.eigrp_networks_table.rowCount()
        self.eigrp_networks_table.insertRow(row)

        network = QtWidgets.QLineEdit()
        network.setPlaceholderText("192.168.1.0")

        wildcard = QtWidgets.QLineEdit()
        wildcard.setPlaceholderText("0.0.0.255")

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.eigrp_networks_table.removeRow(
            self.eigrp_networks_table.indexAt(delete_button.pos()).row()))

        self.eigrp_networks_table.setCellWidget(row, 0, network)
        self.eigrp_networks_table.setCellWidget(row, 1, wildcard)
        self.eigrp_networks_table.setCellWidget(row, 2, delete_button)

    def _add_acl_row(self) -> None:
        """Dodaj nowy wiersz do tabeli ACL."""
        row = self.acl_table.rowCount()
        self.acl_table.insertRow(row)

        acl_name = QtWidgets.QLineEdit()
        acl_name.setPlaceholderText("ACL_NAME")

        sequence = QtWidgets.QSpinBox()
        sequence.setRange(1, 9999)
        sequence.setValue(10)

        action = QtWidgets.QComboBox()
        action.addItems(["permit", "deny"])

        protocol = QtWidgets.QComboBox()
        protocol.addItems(["ip", "tcp", "udp", "icmp"])
        protocol.setEditable(True)

        source = QtWidgets.QLineEdit()
        source.setPlaceholderText("any / host 1.1.1.1 / 1.1.1.0 0.0.0.255")

        destination = QtWidgets.QLineEdit()
        destination.setPlaceholderText("any")

        port_operator = QtWidgets.QComboBox()
        port_operator.addItems(["", "eq", "neq", "gt", "lt", "range"])

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.acl_table.removeRow(
            self.acl_table.indexAt(delete_button.pos()).row()))

        self.acl_table.setCellWidget(row, 0, acl_name)
        self.acl_table.setCellWidget(row, 1, sequence)
        self.acl_table.setCellWidget(row, 2, action)
        self.acl_table.setCellWidget(row, 3, protocol)
        self.acl_table.setCellWidget(row, 4, source)
        self.acl_table.setCellWidget(row, 5, destination)
        self.acl_table.setCellWidget(row, 6, port_operator)
        self.acl_table.setCellWidget(row, 7, delete_button)

    def _add_nat_pool_row(self) -> None:
        """Dodaj nowy wiersz do tabeli puli NAT."""
        row = self.nat_pool_table.rowCount()
        self.nat_pool_table.insertRow(row)

        pool_name = QtWidgets.QLineEdit()
        pool_name.setPlaceholderText("POOL_NAME")

        start_ip = QtWidgets.QLineEdit()
        start_ip.setPlaceholderText("10.0.0.1")

        end_ip = QtWidgets.QLineEdit()
        end_ip.setPlaceholderText("10.0.0.254")

        prefix = QtWidgets.QSpinBox()
        prefix.setRange(1, 32)
        prefix.setValue(24)

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.nat_pool_table.removeRow(
            self.nat_pool_table.indexAt(delete_button.pos()).row()))

        self.nat_pool_table.setCellWidget(row, 0, pool_name)
        self.nat_pool_table.setCellWidget(row, 1, start_ip)
        self.nat_pool_table.setCellWidget(row, 2, end_ip)
        self.nat_pool_table.setCellWidget(row, 3, prefix)
        self.nat_pool_table.setCellWidget(row, 4, delete_button)

    def _add_nat_acl_pool_row(self) -> None:
        """Dodaj nowy wiersz do tabeli mapowań ACL do puli NAT."""
        row = self.nat_acl_pool_table.rowCount()
        self.nat_acl_pool_table.insertRow(row)

        acl_name = QtWidgets.QLineEdit()
        acl_name.setPlaceholderText("ACL_NAME")

        pool_name = QtWidgets.QLineEdit()
        pool_name.setPlaceholderText("POOL_NAME")

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.nat_acl_pool_table.removeRow(
            self.nat_acl_pool_table.indexAt(delete_button.pos()).row()))

        self.nat_acl_pool_table.setCellWidget(row, 0, acl_name)
        self.nat_acl_pool_table.setCellWidget(row, 1, pool_name)
        self.nat_acl_pool_table.setCellWidget(row, 2, delete_button)

    def _add_dhcp_pool_row(self) -> None:
        """Dodaj nowy wiersz do tabeli puli DHCP."""
        row = self.dhcp_pool_table.rowCount()
        self.dhcp_pool_table.insertRow(row)

        pool_name = QtWidgets.QLineEdit()
        pool_name.setPlaceholderText("DHCP_POOL")

        network = QtWidgets.QLineEdit()
        network.setPlaceholderText("192.168.1.0 255.255.255.0")

        default_router = QtWidgets.QLineEdit()
        default_router.setPlaceholderText("192.168.1.1")

        dns = QtWidgets.QLineEdit()
        dns.setPlaceholderText("8.8.8.8 8.8.4.4")

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.dhcp_pool_table.removeRow(
            self.dhcp_pool_table.indexAt(delete_button.pos()).row()))

        self.dhcp_pool_table.setCellWidget(row, 0, pool_name)
        self.dhcp_pool_table.setCellWidget(row, 1, network)
        self.dhcp_pool_table.setCellWidget(row, 2, default_router)
        self.dhcp_pool_table.setCellWidget(row, 3, dns)
        self.dhcp_pool_table.setCellWidget(row, 4, delete_button)

    def _add_hsrp_row(self) -> None:
        """Dodaj nowy wiersz do tabeli grup HSRP."""
        row = self.hsrp_table.rowCount()
        self.hsrp_table.insertRow(row)

        interface = QtWidgets.QLineEdit()
        interface.setPlaceholderText("Vlan1")

        group = QtWidgets.QSpinBox()
        group.setRange(0, 255)

        ip = QtWidgets.QLineEdit()
        ip.setPlaceholderText("192.168.1.254")

        priority = QtWidgets.QSpinBox()
        priority.setRange(1, 255)
        priority.setValue(100)

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.hsrp_table.removeRow(
            self.hsrp_table.indexAt(delete_button.pos()).row()))

        self.hsrp_table.setCellWidget(row, 0, interface)
        self.hsrp_table.setCellWidget(row, 1, group)
        self.hsrp_table.setCellWidget(row, 2, ip)
        self.hsrp_table.setCellWidget(row, 3, priority)
        self.hsrp_table.setCellWidget(row, 4, delete_button)

    def _add_vrf_row(self) -> None:
        """Dodaj nowy wiersz do tabeli VRF."""
        row = self.vrf_table.rowCount()
        self.vrf_table.insertRow(row)

        vrf_name = QtWidgets.QLineEdit()
        vrf_name.setPlaceholderText("VRF_NAME")

        rd = QtWidgets.QLineEdit()
        rd.setPlaceholderText("65000:1")

        delete_button = QtWidgets.QPushButton("X")
        delete_button.setMaximumWidth(30)
        delete_button.clicked.connect(lambda: self.vrf_table.removeRow(
            self.vrf_table.indexAt(delete_button.pos()).row()))

        self.vrf_table.setCellWidget(row, 0, vrf_name)
        self.vrf_table.setCellWidget(row, 1, rd)
        self.vrf_table.setCellWidget(row, 2, delete_button)

    # ---------------------------- L3 Instance Data ----------------------------- #
    def load_from_instance(self, instance: SwitchL3Template) -> None:
        """Załaduj dane L3 z instancji SwitchL3Template."""
        # Ogólne ustawienia routingu
        self.routing_enabled_checkbox.setChecked(instance.ip_routing)
        self.ipv6_routing_checkbox.setChecked(instance.ipv6_routing)

        # Interfejsy SVI
        self.svi_table.setRowCount(0)
        for svi in instance.svi_interfaces:
            self._add_svi_row()
            row = self.svi_table.rowCount() - 1

            vlan_id_widget = self.svi_table.cellWidget(row, 0)
            ip_address_widget = self.svi_table.cellWidget(row, 1)
            subnet_mask_widget = self.svi_table.cellWidget(row, 2)
            description_widget = self.svi_table.cellWidget(row, 3)

            vlan_id_widget.setValue(svi.vlan_id)
            ip_address_widget.setText(svi.ip_address)
            subnet_mask_widget.setText(svi.subnet_mask)
            if svi.description:
                description_widget.setText(svi.description)

        # Trasy statyczne
        self.static_routes_table.setRowCount(0)
        for route in instance.static_routes:
            self._add_static_route_row()
            row = self.static_routes_table.rowCount() - 1

            prefix_widget = self.static_routes_table.cellWidget(row, 0)
            mask_widget = self.static_routes_table.cellWidget(row, 1)
            next_hop_widget = self.static_routes_table.cellWidget(row, 2)
            distance_widget = self.static_routes_table.cellWidget(row, 3)

            prefix_widget.setText(route.prefix)
            mask_widget.setText(route.mask)
            next_hop_widget.setText(route.next_hop)
            if route.distance:
                distance_widget.setValue(route.distance)

        # OSPF
        has_ospf = bool(instance.ospf_networks)
        self.ospf_enabled_checkbox.setChecked(has_ospf)
        self.ospf_process_id_input.setValue(instance.ospf_process_id)
        if instance.ospf_router_id:
            self.ospf_router_id_input.setText(instance.ospf_router_id)

        self.ospf_networks_table.setRowCount(0)
        for net, wildcard, area in instance.ospf_networks:
            self._add_ospf_network_row()
            row = self.ospf_networks_table.rowCount() - 1

            network_widget = self.ospf_networks_table.cellWidget(row, 0)
            wildcard_widget = self.ospf_networks_table.cellWidget(row, 1)
            area_widget = self.ospf_networks_table.cellWidget(row, 2)

            network_widget.setText(net)
            wildcard_widget.setText(wildcard)
            area_widget.setText(area)

        # EIGRP
        has_eigrp = bool(instance.eigrp_networks)
        self.eigrp_enabled_checkbox.setChecked(has_eigrp)
        if instance.eigrp_as:
            self.eigrp_as_input.setValue(instance.eigrp_as)

        self.eigrp_networks_table.setRowCount(0)
        for net, wildcard in instance.eigrp_networks:
            self._add_eigrp_network_row()
            row = self.eigrp_networks_table.rowCount() - 1

            network_widget = self.eigrp_networks_table.cellWidget(row, 0)
            wildcard_widget = self.eigrp_networks_table.cellWidget(row, 1)

            network_widget.setText(net)
            wildcard_widget.setText(wildcard)

        # ACL
        self.acl_table.setRowCount(0)
        for entry in instance.acl_entries:
            self._add_acl_row()
            row = self.acl_table.rowCount() - 1

            acl_name_widget = self.acl_table.cellWidget(row, 0)
            sequence_widget = self.acl_table.cellWidget(row, 1)
            action_widget = self.acl_table.cellWidget(row, 2)
            protocol_widget = self.acl_table.cellWidget(row, 3)
            source_widget = self.acl_table.cellWidget(row, 4)
            destination_widget = self.acl_table.cellWidget(row, 5)
            port_operator_widget = self.acl_table.cellWidget(row, 6)

            acl_name_widget.setText(entry.name)
            sequence_widget.setValue(entry.sequence)
            action_widget.setCurrentText(entry.action)
            protocol_widget.setCurrentText(entry.protocol)
            source_widget.setText(entry.source)
            destination_widget.setText(entry.destination)
            if entry.port_operator:
                port_operator_widget.setCurrentText(entry.port_operator)

        # NAT
        self.nat_inside_interfaces_input.setText(", ".join(instance.nat_inside_interfaces))
        self.nat_outside_interfaces_input.setText(", ".join(instance.nat_outside_interfaces))

        # NAT Pools
        self.nat_pool_table.setRowCount(0)
        if instance.nat_pool:
            for pool_name, pool_config in instance.nat_pool.items():
                # Parsowanie konfiguracji puli (przykład: "10.0.0.1 10.0.0.254 prefix-length 24")
                parts = pool_config.split()
                if len(parts) >= 4:
                    start_ip = parts[0]
                    end_ip = parts[1]
                    prefix_length = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 24

                    self._add_nat_pool_row()
                    row = self.nat_pool_table.rowCount() - 1

                    pool_name_widget = self.nat_pool_table.cellWidget(row, 0)
                    start_ip_widget = self.nat_pool_table.cellWidget(row, 1)
                    end_ip_widget = self.nat_pool_table.cellWidget(row, 2)
                    prefix_widget = self.nat_pool_table.cellWidget(row, 3)

                    pool_name_widget.setText(pool_name)
                    start_ip_widget.setText(start_ip)
                    end_ip_widget.setText(end_ip)
                    prefix_widget.setValue(prefix_length)

        # NAT ACL to Pool Mappings
        self.nat_acl_pool_table.setRowCount(0)
        if instance.nat_acl_to_pool:
            for acl_name, pool_name in instance.nat_acl_to_pool.items():
                self._add_nat_acl_pool_row()
                row = self.nat_acl_pool_table.rowCount() - 1

                acl_name_widget = self.nat_acl_pool_table.cellWidget(row, 0)
                pool_name_widget = self.nat_acl_pool_table.cellWidget(row, 1)

                acl_name_widget.setText(acl_name)
                pool_name_widget.setText(pool_name)

        # DHCP
        self.dhcp_excluded_input.setText(" ".join(instance.dhcp_excluded_addresses))

        # DHCP Pools
        self.dhcp_pool_table.setRowCount(0)
        for pool_name, pool_config in instance.dhcp_pools.items():
            self._add_dhcp_pool_row()
            row = self.dhcp_pool_table.rowCount() - 1

            pool_name_widget = self.dhcp_pool_table.cellWidget(row, 0)
            network_widget = self.dhcp_pool_table.cellWidget(row, 1)
            default_router_widget = self.dhcp_pool_table.cellWidget(row, 2)
            dns_widget = self.dhcp_pool_table.cellWidget(row, 3)

            pool_name_widget.setText(pool_name)

            if "network" in pool_config:
                network_widget.setText(pool_config["network"])
            if "default-router" in pool_config:
                default_router_widget.setText(pool_config["default-router"])
            if "dns-server" in pool_config:
                dns_widget.setText(pool_config["dns-server"])

        # HSRP
        self.hsrp_table.setRowCount(0)
        for intf, group_config in instance.hsrp_groups.items():
            for group_id, config in group_config.items():
                self._add_hsrp_row()
                row = self.hsrp_table.rowCount() - 1

                interface_widget = self.hsrp_table.cellWidget(row, 0)
                group_widget = self.hsrp_table.cellWidget(row, 1)
                ip_widget = self.hsrp_table.cellWidget(row, 2)
                priority_widget = self.hsrp_table.cellWidget(row, 3)

                interface_widget.setText(intf)
                group_widget.setValue(int(group_id))
                if "ip" in config:
                    ip_widget.setText(config["ip"])
                if "priority" in config:
                    priority_widget.setValue(int(config["priority"]))

        # VRF
        self.vrf_table.setRowCount(0)
        for vrf_name, vrf_config in instance.vrf_definitions.items():
            self._add_vrf_row()
            row = self.vrf_table.rowCount() - 1

            vrf_name_widget = self.vrf_table.cellWidget(row, 0)
            rd_widget = self.vrf_table.cellWidget(row, 1)

            vrf_name_widget.setText(vrf_name)
            if "rd" in vrf_config:
                rd_widget.setText(vrf_config["rd"])

    def _get_svi_list(self) -> List[SwitchVirtualInterface]:
        """Pobierz listę interfejsów SVI z tabeli."""
        svi_list = []
        for row in range(self.svi_table.rowCount()):
            vlan_id = self.svi_table.cellWidget(row, 0).value()
            ip_address = self.svi_table.cellWidget(row, 1).text()
            subnet_mask = self.svi_table.cellWidget(row, 2).text()
            description = self.svi_table.cellWidget(row, 3).text()

            if vlan_id and ip_address and subnet_mask:
                svi = SwitchVirtualInterface(
                    vlan_id=vlan_id,
                    ip_address=ip_address,
                    subnet_mask=subnet_mask,
                    description=description or None
                )
                svi_list.append(svi)

        return svi_list

    def _get_static_routes(self) -> List[StaticRoute]:
        """Pobierz listę tras statycznych z tabeli."""
        routes = []
        for row in range(self.static_routes_table.rowCount()):
            prefix = self.static_routes_table.cellWidget(row, 0).text()
            mask = self.static_routes_table.cellWidget(row, 1).text()
            next_hop = self.static_routes_table.cellWidget(row, 2).text()
            distance = self.static_routes_table.cellWidget(row, 3).value()

            if prefix and mask and next_hop:
                route = StaticRoute(
                    prefix=prefix,
                    mask=mask,
                    next_hop=next_hop,
                    distance=distance
                )
                routes.append(route)

        return routes

    def _get_ospf_networks(self) -> List[tuple]:
        """Pobierz listę sieci OSPF z tabeli."""
        networks = []
        for row in range(self.ospf_networks_table.rowCount()):
            network = self.ospf_networks_table.cellWidget(row, 0).text()
            wildcard = self.ospf_networks_table.cellWidget(row, 1).text()
            area = self.ospf_networks_table.cellWidget(row, 2).text()

            if network and wildcard and area:
                networks.append((network, wildcard, area))

        return networks

    def _get_eigrp_networks(self) -> List[tuple]:
        """Pobierz listę sieci EIGRP z tabeli."""
        networks = []
        for row in range(self.eigrp_networks_table.rowCount()):
            network = self.eigrp_networks_table.cellWidget(row, 0).text()
            wildcard = self.eigrp_networks_table.cellWidget(row, 1).text()

            if network and wildcard:
                networks.append((network, wildcard))

        return networks

    def _get_acl_entries(self) -> List[ACLEntry]:
        """Pobierz listę wpisów ACL z tabeli."""
        entries = []
        for row in range(self.acl_table.rowCount()):
            name = self.acl_table.cellWidget(row, 0).text()
            sequence = self.acl_table.cellWidget(row, 1).value()
            action = self.acl_table.cellWidget(row, 2).currentText()
            protocol = self.acl_table.cellWidget(row, 3).currentText()
            source = self.acl_table.cellWidget(row, 4).text()
            destination = self.acl_table.cellWidget(row, 5).text()
            port_operator = self.acl_table.cellWidget(row, 6).currentText()

            if name and action and protocol and source:
                entry = ACLEntry(
                    name=name,
                    sequence=sequence,
                    action=action,
                    protocol=protocol,
                    source=source,
                    destination=destination,
                    port_operator=port_operator or None
                )
                entries.append(entry)

        return entries

    def _get_nat_pools(self) -> Dict[str, str]:
        """Pobierz słownik pul NAT z tabeli."""
        pools = {}
        for row in range(self.nat_pool_table.rowCount()):
            name = self.nat_pool_table.cellWidget(row, 0).text()
            start_ip = self.nat_pool_table.cellWidget(row, 1).text()
            end_ip = self.nat_pool_table.cellWidget(row, 2).text()
            prefix = self.nat_pool_table.cellWidget(row, 3).value()

            if name and start_ip and end_ip:
                # Format: "start_ip end_ip prefix-length prefix"
                config = f"{start_ip} {end_ip} prefix-length {prefix}"
                pools[name] = config

        return pools

    def _get_nat_acl_mappings(self) -> Dict[str, str]:
        """Pobierz słownik mapowań ACL do pul NAT z tabeli."""
        mappings = {}
        for row in range(self.nat_acl_pool_table.rowCount()):
            acl_name = self.nat_acl_pool_table.cellWidget(row, 0).text()
            pool_name = self.nat_acl_pool_table.cellWidget(row, 1).text()

            if acl_name and pool_name:
                mappings[acl_name] = pool_name

        return mappings

    def _get_dhcp_pools(self) -> Dict[str, Dict[str, str]]:
        """Pobierz słownik pul DHCP z tabeli."""
        pools = {}
        for row in range(self.dhcp_pool_table.rowCount()):
            name = self.dhcp_pool_table.cellWidget(row, 0).text()
            network = self.dhcp_pool_table.cellWidget(row, 1).text()
            default_router = self.dhcp_pool_table.cellWidget(row, 2).text()
            dns = self.dhcp_pool_table.cellWidget(row, 3).text()

            if name and network:
                config = {}
                if network:
                    config["network"] = network
                if default_router:
                    config["default-router"] = default_router
                if dns:
                    config["dns-server"] = dns

                pools[name] = config

        return pools

    def _get_hsrp_groups(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Pobierz słownik grup HSRP z tabeli."""
        groups = {}
        for row in range(self.hsrp_table.rowCount()):
            interface = self.hsrp_table.cellWidget(row, 0).text()
            group_id = str(self.hsrp_table.cellWidget(row, 1).value())
            ip = self.hsrp_table.cellWidget(row, 2).text()
            priority = self.hsrp_table.cellWidget(row, 3).value()

            if interface and group_id and ip:
                if interface not in groups:
                    groups[interface] = {}

                groups[interface][group_id] = {
                    "ip": ip,
                    "priority": str(priority)
                }

        return groups

    def _get_vrf_definitions(self) -> Dict[str, Dict[str, str]]:
        """Pobierz słownik definicji VRF z tabeli."""
        vrf_defs = {}
        for row in range(self.vrf_table.rowCount()):
            name = self.vrf_table.cellWidget(row, 0).text()
            rd = self.vrf_table.cellWidget(row, 1).text()

            if name:
                config = {}
                if rd:
                    config["rd"] = rd
                    config["address-family ipv4"] = ""  # Domyślnie włączona

                vrf_defs[name] = config

        return vrf_defs

    def create_switch_l3_template(self) -> SwitchL3Template:
        """Utwórz i zwróć instancję SwitchL3Template z danych formularza."""
        # Najpierw pobierz dane podstawowego formularza przełącznika
        instance = SwitchL3Template(
            hostname=self.hostname_input.text() or "Switch",
            vlans=self._get_vlans_from_table(),
            manager_vlan_id=int(self.manager_vlan_id_combo.currentText() or 1),
            manager_ip=self.manager_ip_input.text().strip(),
            default_gateway=self.default_gateway_input.text().strip(),

            # Dodatkowe dane specyficzne dla L3
            ip_routing=self.routing_enabled_checkbox.isChecked(),
            ipv6_routing=self.ipv6_routing_checkbox.isChecked(),

            svi_interfaces=self._get_svi_list(),
            static_routes=self._get_static_routes(),

            ospf_process_id=self.ospf_process_id_input.value(),
            ospf_router_id=self.ospf_router_id_input.text() or None,
            ospf_networks=self._get_ospf_networks(),

            eigrp_as=self.eigrp_as_input.value() if self.eigrp_enabled_checkbox.isChecked() else None,
            eigrp_networks=self._get_eigrp_networks(),

            acl_entries=self._get_acl_entries(),

            nat_inside_interfaces=[s.strip() for s in self.nat_inside_interfaces_input.text().split(",") if s.strip()],
            nat_outside_interfaces=[s.strip() for s in self.nat_outside_interfaces_input.text().split(",") if
                                    s.strip()],
            nat_pool=self._get_nat_pools(),
            nat_acl_to_pool=self._get_nat_acl_mappings(),

            dhcp_excluded_addresses=[s.strip() for s in self.dhcp_excluded_input.text().split() if s.strip()],
            dhcp_pools=self._get_dhcp_pools(),

            hsrp_groups=self._get_hsrp_groups(),
            vrf_definitions=self._get_vrf_definitions()
        )

        return instance

    def _get_vlans_from_table(self):
        """Pobierz listę obiektów VLAN z tabeli."""
        from src.models.templates.SwitchL2Template import VLAN
        vlans = []

        # Pobierz wiersze z tabeli VLAN
        for row in range(self.vlan_table.rowCount()):
            vlan_id_item = self.vlan_table.item(row, 0)
            vlan_name_item = self.vlan_table.item(row, 1)
            vlan_state_item = self.vlan_table.item(row, 2)

            if vlan_id_item:
                try:
                    vlan_id = int(vlan_id_item.text())
                    vlan_name = vlan_name_item.text() if vlan_name_item else f"VLAN{vlan_id}"
                    vlan_state = vlan_state_item.text() if vlan_state_item else "active"

                    vlans.append(VLAN(id=vlan_id, name=vlan_name, state=vlan_state))
                except ValueError:
                    pass

        # Dodaj VLAN-y z SVI, które nie są jeszcze na liście
        vlan_ids = {vlan.id for vlan in vlans}
        for row in range(self.svi_table.rowCount()):
            vlan_id = self.svi_table.cellWidget(row, 0).value()
            if vlan_id and vlan_id not in vlan_ids:
                description = self.svi_table.cellWidget(row, 3).text() or f"VLAN{vlan_id}"
                vlans.append(VLAN(id=vlan_id, name=description))
                vlan_ids.add(vlan_id)

        return vlans