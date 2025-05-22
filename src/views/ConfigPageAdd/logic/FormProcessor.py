# 'src/views/ConfigPageAdd/logic/FormProcessor.py'
"""Builds template instances from PySide6 forms.

Access-Template branch extended with every new checkbox / field so that
no *unexpected-keyword* errors appear.

Updated in 2025-05 to handle new color field for templates and proper enum handling.
"""
from src.models.templates.AccessTemplate import AccessTemplate, PowerInlineMode, ViolationAction, QoSTrustState
from src.models.templates.TrunkTemplate import TrunkTemplate, EncapsulationType, DTPMode
from src.models.templates.RouterTemplate import RouterTemplate
from src.models.templates.SwitchL2Template import   SwitchL2Template, SpanningTreeMode, VTPMode


def _bool(form, attr):
    """Return *form.<attr>.isChecked()* safely."""
    return getattr(form, attr).isChecked() if hasattr(form, attr) else False


def build_template_instance(form):
    """Return filled template instance or *None* when form is not recognised."""
    if form is None:
        return None

    # --------------------------- ACCESS --------------------------- #
    if hasattr(form, "interfaces_input") and hasattr(form, "vlan_id_input"):
        # Get color value if the color picker exists
        color_value = form.color_picker.get_value() if hasattr(form, "color_picker") else "#4287f5"

        # Handle PowerInlineMode enum
        poe_inline_mode = PowerInlineMode.AUTO  # Default
        if hasattr(form, "poe_inline_combo"):
            try:
                poe_inline_mode = PowerInlineMode(form.poe_inline_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        # Handle ViolationAction enum
        violation_action = ViolationAction.SHUTDOWN  # Default
        if hasattr(form, "violation_action_combo"):
            try:
                violation_action = ViolationAction(form.violation_action_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        # Handle QoSTrustState enum
        qos_trust = None
        if hasattr(form, "qos_trust_combo") and form.qos_trust_combo.currentText() != "--":
            try:
                qos_trust = QoSTrustState(form.qos_trust_combo.currentText())
            except ValueError:
                pass  # Keep None if invalid

        return AccessTemplate(
            # base
            interfaces=[s.strip() for s in form.interfaces_input.text().split(",") if s.strip()],
            vlan_id=form.vlan_id_input.value(),
            description=form.description_input.text() or None,
            color=color_value,  # Add color field
            voice_vlan=form.voice_vlan_input.value() or None,

            # security
            port_security_enabled=_bool(form, "port_security_checkbox"),
            max_mac_addresses=form.max_mac_input.value(),
            violation_action=violation_action,
            sticky_mac=_bool(form, "sticky_mac_checkbox"),

            # STP
            spanning_tree_portfast=_bool(form, "spanning_tree_portfast_checkbox"),
            bpdu_guard=_bool(form, "bpdu_guard_checkbox"),
            bpdu_filter=_bool(form, "bpdu_filter_checkbox"),
            loop_guard=_bool(form, "loop_guard_checkbox"),
            root_guard=_bool(form, "root_guard_checkbox"),

            # private-VLAN / protected-port
            private_vlan_host=_bool(form, "private_vlan_host_checkbox"),
            protected_port=_bool(form, "protected_port_checkbox"),

            # QoS / NAC
            qos_trust=qos_trust,
            service_policy_input=form.service_policy_input.text() or None,
            mab=_bool(form, "mab_checkbox"),
            dot1x=_bool(form, "dot1x_checkbox"),

            # PoE
            poe_inline=poe_inline_mode,
            poe_enabled=_bool(form, "poe_enabled_checkbox") if hasattr(form, "poe_enabled_checkbox") else True,

            # storm-control
            storm_control_broadcast_min=form.broadcast_min_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_broadcast_max=form.broadcast_max_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_multicast_min=form.multicast_min_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_multicast_max=form.multicast_max_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_unknown_unicast_min=form.unknown_unicast_min_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_unknown_unicast_max=form.unknown_unicast_max_input.value()
            if _bool(form, "storm_control_checkbox") else None,
            storm_control_unit_pps=_bool(form, "storm_unit_pps"),

            # physical
            speed=form.speed_combo.currentText(),
            duplex=form.duplex_combo.currentText(),
            auto_mdix=_bool(form, "auto_mdix_checkbox"),

            # errdisable / limits
            errdisable_timeout=form.errdisable_timeout_input.value() if hasattr(form,
                                                                                "errdisable_timeout_input") else None,
            dhcp_snoop_rate=form.dhcp_snoop_rate_input.value() if hasattr(form, "dhcp_snoop_rate_input") else None,
            arp_inspection_rate=form.arp_inspection_rate_input.value() if hasattr(form,
                                                                                  "arp_inspection_rate_input") else None,
        )

        # Fragment metody build_template_instance dla obsługi TrunkTemplate

        # ---------------- TRUNK ----------------- #
    if hasattr(form, "native_vlan_input"):
        storm_on = _bool(form, "storm_control_checkbox")
        # Get color value if the color picker exists
        color_value = form.color_picker.get_value() if hasattr(form, "color_picker") else "#8A2BE2"

        # Handle EncapsulationType enum
        encapsulation = EncapsulationType.DOT1Q  # Default
        if hasattr(form, "encapsulation_combo"):
            try:
                encapsulation = EncapsulationType(form.encapsulation_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        # Handle DTPMode enum
        dtp_mode = None
        if hasattr(form, "dtp_mode_combo") and form.dtp_mode_combo.currentText() != "--":
            try:
                dtp_mode = DTPMode(form.dtp_mode_combo.currentText())
            except ValueError:
                pass  # Keep None if invalid

        # Tworzymy instancję TrunkTemplate bez parametru color
        trunk_template = TrunkTemplate(
            interfaces=[s.strip() for s in form.interfaces_input.text().split(",") if s.strip()],
            allowed_vlans=[int(v.strip()) for v in form.allowed_vlans_input.text().split(",") if
                           v.strip().isdigit()],
            native_vlan=form.native_vlan_input.value(),
            description=form.description_input.text() or None,

            # basic flags
            pruning_enabled=_bool(form, "pruning_checkbox"),
            spanning_tree_guard_root=_bool(form, "stp_guard_checkbox"),
            encapsulation=encapsulation,
            dtp_mode=dtp_mode,
            nonegotiate=_bool(form, "nonegotiate_checkbox"),
            spanning_tree_portfast=_bool(form, "portfast_checkbox"),

            # security
            dhcp_snooping_trust=_bool(form, "dhcp_trust_checkbox"),
            qos_trust=(None if form.qos_trust_combo.currentText() == "--" else form.qos_trust_combo.currentText()),

            # storm-control
            storm_control_broadcast_min=form.broadcast_min_input.value() if storm_on else None,
            storm_control_broadcast_max=form.broadcast_max_input.value() if storm_on else None,
            storm_control_multicast_min=form.multicast_min_input.value() if storm_on else None,
            storm_control_multicast_max=form.multicast_max_input.value() if storm_on else None,
            storm_control_unknown_unicast_min=form.unknown_unicast_min_input.value() if storm_on else None,
            storm_control_unknown_unicast_max=form.unknown_unicast_max_input.value() if storm_on else None,
            storm_control_unit_pps=_bool(form, "storm_unit_pps"),

            # L1 / timers
            speed=form.speed_combo.currentText(),
            duplex=form.duplex_combo.currentText(),
            auto_mdix=_bool(form, "auto_mdix_checkbox"),
            errdisable_timeout=form.errdisable_timeout_input.value() or None,

            # etherchannel
            channel_group=(form.channel_group_input.value() or None),
            channel_group_mode=(None if form.channel_mode_combo.currentText() == "--"
                                else form.channel_mode_combo.currentText()),
        )

        # Ustawiamy atrybut color po utworzeniu instancji
        if hasattr(trunk_template, 'color'):
            setattr(trunk_template, 'color', color_value)

        return trunk_template

    # --------------------------- ROUTER --------------------------- #
    if hasattr(form, "hostname_input") and hasattr(form, "manager_vlan_id_combo"):
        # Extract VLAN IDs from the VLAN table if it exists
        vlans = []
        if hasattr(form, "vlan_table"):
            for row in range(form.vlan_table.rowCount()):
                vlan_id_item = form.vlan_table.item(row, 0)
                vlan_name_item = form.vlan_table.item(row, 1)

                if vlan_id_item:
                    try:
                        vlan_id = int(vlan_id_item.text())
                        vlan_name = vlan_name_item.text() if vlan_name_item else f"VLAN{vlan_id}"
                        # Tworzymy obiekt VLAN zamiast słownika
                        from src.models.templates.SwitchL2Template import VLAN
                        vlans.append(VLAN(id=vlan_id, name=vlan_name))
                    except ValueError:
                        pass

        # Handle SpanningTreeMode enum
        spanning_tree_mode = SpanningTreeMode.RAPID_PVST  # Default
        if hasattr(form, "spanning_tree_mode_combo"):
            try:
                spanning_tree_mode = SpanningTreeMode(form.spanning_tree_mode_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        # Handle VTPMode enum
        vtp_mode = VTPMode.OFF  # Default
        if hasattr(form, "vtp_mode_combo"):
            try:
                vtp_mode = VTPMode(form.vtp_mode_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        return SwitchL2Template(
            hostname=form.hostname_input.text() or "Switch",
            # Use 'vlans' list with proper VLAN objects
            vlans=vlans,
            spanning_tree_mode=spanning_tree_mode,
            manager_vlan_id=int(form.manager_vlan_id_combo.currentText()),
            manager_ip=form.manager_ip_input.text().strip(),
            default_gateway=form.default_gateway_input.text().strip(),
            vtp_mode=vtp_mode,
            vtp_domain=form.vtp_domain_input.text() if hasattr(form, "vtp_domain_input") else None,
        )

    # --------------------------- SWITCH L2 --------------------------- #
    if hasattr(form, "hostname_input") and hasattr(form, "manager_vlan_id_combo"):
        # Extract VLAN IDs from the VLAN table if it exists
        vlans = []
        if hasattr(form, "vlan_table"):
            for row in range(form.vlan_table.rowCount()):
                vlan_id_item = form.vlan_table.item(row, 0)
                vlan_name_item = form.vlan_table.item(row, 1)

                if vlan_id_item:
                    try:
                        vlan_id = int(vlan_id_item.text())
                        vlan_name = vlan_name_item.text() if vlan_name_item else f"VLAN{vlan_id}"
                        vlans.append({"id": vlan_id, "name": vlan_name})
                    except ValueError:
                        pass

        # Handle SpanningTreeMode enum
        spanning_tree_mode = SpanningTreeMode.RAPID_PVST  # Default
        if hasattr(form, "spanning_tree_mode_combo"):
            try:
                spanning_tree_mode = SpanningTreeMode(form.spanning_tree_mode_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        # Handle VTPMode enum
        vtp_mode = VTPMode.OFF  # Default
        if hasattr(form, "vtp_mode_combo"):
            try:
                vtp_mode = VTPMode(form.vtp_mode_combo.currentText())
            except ValueError:
                pass  # Stick with default if invalid

        return SwitchL2Template(
            hostname=form.hostname_input.text() or "Switch",
            # Use 'vlans' list with proper format
            vlans=vlans,
            spanning_tree_mode=spanning_tree_mode,
            manager_vlan_id=int(form.manager_vlan_id_combo.currentText()),
            manager_ip=form.manager_ip_input.text().strip(),
            default_gateway=form.default_gateway_input.text().strip(),
            vtp_mode=vtp_mode,
            vtp_domain=form.vtp_domain_input.text() if hasattr(form, "vtp_domain_input") else None,
        )
    # --------------------------- SWITCH L3 --------------------------- #
    if hasattr(form, "hostname_input") and hasattr(form, "routing_enabled_checkbox"):
        # Sprawdź, czy mamy do czynienia z formularzem SwitchL3TemplateForm
        if hasattr(form, "svi_table") and hasattr(form, "create_switch_l3_template"):
            # Użyj metody pomocniczej z formularza, która zbiera wszystkie dane
            return form.create_switch_l3_template()

        # Alternatywnie, możemy sami zbudować instancję z danych formularza
        from src.models.templates.SwitchL3Template import SwitchL3Template, SwitchVirtualInterface, StaticRoute, \
            ACLEntry

        # Pobieranie danych z formularza
        hostname = form.hostname_input.text() or "Switch"

        # Pobieranie VLAN-ów z tabeli VLAN
        vlans = []
        if hasattr(form, "vlan_table"):
            from src.models.templates.SwitchL3Template  import VLAN
            for row in range(form.vlan_table.rowCount()):
                vlan_id_item = form.vlan_table.item(row, 0)
                vlan_name_item = form.vlan_table.item(row, 1)

                if vlan_id_item:
                    try:
                        vlan_id = int(vlan_id_item.text())
                        vlan_name = vlan_name_item.text() if vlan_name_item else f"VLAN{vlan_id}"
                        vlans.append(VLAN(id=vlan_id, name=vlan_name))
                    except ValueError:
                        pass

        # Pobieranie interfejsów SVI z tabeli
        svi_interfaces = []
        if hasattr(form, "svi_table"):
            for row in range(form.svi_table.rowCount()):
                vlan_id = form.svi_table.cellWidget(row, 0).value()
                ip_address = form.svi_table.cellWidget(row, 1).text()
                subnet_mask = form.svi_table.cellWidget(row, 2).text()
                description = form.svi_table.cellWidget(row, 3).text()

                if vlan_id and ip_address and subnet_mask:
                    svi = SwitchVirtualInterface(
                        vlan_id=vlan_id,
                        ip_address=ip_address,
                        subnet_mask=subnet_mask,
                        description=description or None
                    )
                    svi_interfaces.append(svi)

        # Pobieranie tras statycznych z tabeli
        static_routes = []
        if hasattr(form, "static_routes_table"):
            for row in range(form.static_routes_table.rowCount()):
                prefix = form.static_routes_table.cellWidget(row, 0).text()
                mask = form.static_routes_table.cellWidget(row, 1).text()
                next_hop = form.static_routes_table.cellWidget(row, 2).text()
                distance = form.static_routes_table.cellWidget(row, 3).value()

                if prefix and mask and next_hop:
                    route = StaticRoute(
                        prefix=prefix,
                        mask=mask,
                        next_hop=next_hop,
                        distance=distance
                    )
                    static_routes.append(route)

        # Pobieranie sieci OSPF z tabeli
        ospf_networks = []
        if hasattr(form, "ospf_networks_table") and hasattr(form,
                                                            "ospf_enabled_checkbox") and form.ospf_enabled_checkbox.isChecked():
            for row in range(form.ospf_networks_table.rowCount()):
                network = form.ospf_networks_table.cellWidget(row, 0).text()
                wildcard = form.ospf_networks_table.cellWidget(row, 1).text()
                area = form.ospf_networks_table.cellWidget(row, 2).text()

                if network and wildcard and area:
                    ospf_networks.append((network, wildcard, area))

        # Pobieranie sieci EIGRP z tabeli
        eigrp_networks = []
        eigrp_as = None
        if hasattr(form, "eigrp_networks_table") and hasattr(form,
                                                             "eigrp_enabled_checkbox") and form.eigrp_enabled_checkbox.isChecked():
            eigrp_as = form.eigrp_as_input.value() if hasattr(form, "eigrp_as_input") else None

            for row in range(form.eigrp_networks_table.rowCount()):
                network = form.eigrp_networks_table.cellWidget(row, 0).text()
                wildcard = form.eigrp_networks_table.cellWidget(row, 1).text()

                if network and wildcard:
                    eigrp_networks.append((network, wildcard))

        # Pobieranie wpisów ACL z tabeli
        acl_entries = []
        if hasattr(form, "acl_table"):
            for row in range(form.acl_table.rowCount()):
                name = form.acl_table.cellWidget(row, 0).text()
                sequence = form.acl_table.cellWidget(row, 1).value()
                action = form.acl_table.cellWidget(row, 2).currentText()
                protocol = form.acl_table.cellWidget(row, 3).currentText()
                source = form.acl_table.cellWidget(row, 4).text()
                destination = form.acl_table.cellWidget(row, 5).text()
                port_operator = form.acl_table.cellWidget(row, 6).currentText()

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
                    acl_entries.append(entry)

        # Pobieranie konfiguracji NAT
        nat_inside_interfaces = []
        nat_outside_interfaces = []
        nat_pool = {}
        nat_acl_to_pool = {}

        if hasattr(form, "nat_inside_interfaces_input"):
            nat_inside_interfaces = [s.strip() for s in form.nat_inside_interfaces_input.text().split(",") if s.strip()]

        if hasattr(form, "nat_outside_interfaces_input"):
            nat_outside_interfaces = [s.strip() for s in form.nat_outside_interfaces_input.text().split(",") if
                                      s.strip()]

        if hasattr(form, "nat_pool_table"):
            for row in range(form.nat_pool_table.rowCount()):
                name = form.nat_pool_table.cellWidget(row, 0).text()
                start_ip = form.nat_pool_table.cellWidget(row, 1).text()
                end_ip = form.nat_pool_table.cellWidget(row, 2).text()
                prefix = form.nat_pool_table.cellWidget(row, 3).value()

                if name and start_ip and end_ip:
                    # Format: "start_ip end_ip prefix-length prefix"
                    config = f"{start_ip} {end_ip} prefix-length {prefix}"
                    nat_pool[name] = config

        if hasattr(form, "nat_acl_pool_table"):
            for row in range(form.nat_acl_pool_table.rowCount()):
                acl_name = form.nat_acl_pool_table.cellWidget(row, 0).text()
                pool_name = form.nat_acl_pool_table.cellWidget(row, 1).text()

                if acl_name and pool_name:
                    nat_acl_to_pool[acl_name] = pool_name

        # Pobieranie konfiguracji DHCP
        dhcp_excluded_addresses = []
        dhcp_pools = {}

        if hasattr(form, "dhcp_excluded_input"):
            dhcp_excluded_addresses = [s.strip() for s in form.dhcp_excluded_input.text().split() if s.strip()]

        if hasattr(form, "dhcp_pool_table"):
            for row in range(form.dhcp_pool_table.rowCount()):
                name = form.dhcp_pool_table.cellWidget(row, 0).text()
                network = form.dhcp_pool_table.cellWidget(row, 1).text()
                default_router = form.dhcp_pool_table.cellWidget(row, 2).text()
                dns = form.dhcp_pool_table.cellWidget(row, 3).text()

                if name and network:
                    config = {}
                    if network:
                        config["network"] = network
                    if default_router:
                        config["default-router"] = default_router
                    if dns:
                        config["dns-server"] = dns

                    dhcp_pools[name] = config

        # Pobieranie konfiguracji HSRP
        hsrp_groups = {}

        if hasattr(form, "hsrp_table"):
            for row in range(form.hsrp_table.rowCount()):
                interface = form.hsrp_table.cellWidget(row, 0).text()
                group_id = str(form.hsrp_table.cellWidget(row, 1).value())
                ip = form.hsrp_table.cellWidget(row, 2).text()
                priority = form.hsrp_table.cellWidget(row, 3).value()

                if interface and group_id and ip:
                    if interface not in hsrp_groups:
                        hsrp_groups[interface] = {}

                    hsrp_groups[interface][group_id] = {
                        "ip": ip,
                        "priority": str(priority)
                    }

        # Pobieranie konfiguracji VRF
        vrf_definitions = {}

        if hasattr(form, "vrf_table"):
            for row in range(form.vrf_table.rowCount()):
                name = form.vrf_table.cellWidget(row, 0).text()
                rd = form.vrf_table.cellWidget(row, 1).text()

                if name:
                    config = {}
                    if rd:
                        config["rd"] = rd
                        config["address-family ipv4"] = ""  # Domyślnie włączona

                    vrf_definitions[name] = config

        # Odczytanie pozostałych ustawień z formularza przełącznika L2
        manager_vlan_id = int(form.manager_vlan_id_combo.currentText()) if hasattr(form, "manager_vlan_id_combo") else 1
        manager_ip = form.manager_ip_input.text().strip() if hasattr(form,
                                                                     "manager_ip_input") else "192.168.1.1 255.255.255.0"
        default_gateway = form.default_gateway_input.text().strip() if hasattr(form,
                                                                               "default_gateway_input") else "192.168.1.254"

        # Tworzenie instancji SwitchL3Template
        return SwitchL3Template(
            hostname=hostname,
            vlans=vlans,
            manager_vlan_id=manager_vlan_id,
            manager_ip=manager_ip,
            default_gateway=default_gateway,

            # Funkcje routingu L3
            ip_routing=form.routing_enabled_checkbox.isChecked() if hasattr(form, "routing_enabled_checkbox") else True,
            ipv6_routing=form.ipv6_routing_checkbox.isChecked() if hasattr(form, "ipv6_routing_checkbox") else False,
            svi_interfaces=svi_interfaces,
            static_routes=static_routes,

            # OSPF
            ospf_process_id=form.ospf_process_id_input.value() if hasattr(form, "ospf_process_id_input") else 1,
            ospf_router_id=form.ospf_router_id_input.text() if hasattr(form, "ospf_router_id_input") else None,
            ospf_networks=ospf_networks,

            # EIGRP
            eigrp_as=eigrp_as,
            eigrp_networks=eigrp_networks,

            # ACL
            acl_entries=acl_entries,

            # NAT
            nat_inside_interfaces=nat_inside_interfaces,
            nat_outside_interfaces=nat_outside_interfaces,
            nat_pool=nat_pool,
            nat_acl_to_pool=nat_acl_to_pool,

            # DHCP
            dhcp_excluded_addresses=dhcp_excluded_addresses,
            dhcp_pools=dhcp_pools,

            # HSRP
            hsrp_groups=hsrp_groups,

            # VRF
            vrf_definitions=vrf_definitions
        )
    return None