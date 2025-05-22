# 'src/views/ConfigPageAdd/ConfigMainArea.py'
"""Main workspace on the configuration page.

*FIX 2025-05-01*
After accepting a brand-new template, every interface contained in the instance
is now pushed into InterfaceAssignmentManager so that subsequent radio-button
selections keep the interface list intact.

*UPDATE 2025-05-04*
Added color support for interface buttons and templates. Interface buttons
are now colored according to the template they belong to.

*UPDATE 2025-05-05*
Interface buttons now show correct colors immediately upon application start.
"""

from __future__ import annotations

from typing import Any, Dict, List
from dataclasses import asdict

from PySide6 import QtWidgets, QtGui

from src.models.InterfaceAssignmentManager import InterfaceAssignmentManager

from src.forms.AccessTemplateForm import AccessTemplateForm
from src.forms.RouterTemplateForm import RouterTemplateForm
from src.forms.SwitchL2TemplateForm import SwitchL2TemplateForm
from src.forms.TrunkTemplateForm import TrunkTemplateForm

from src.models.templates.AccessTemplate import AccessTemplate
from src.models.templates.RouterTemplate import RouterTemplate
from src.models.templates.SwitchL2Template import SwitchL2Template
from src.models.templates.SwitchL3Template import SwitchL3Template
from src.models.templates.TrunkTemplate import TrunkTemplate

from src.utils.color_utils import get_contrasting_text_color

from src.views.ConfigPageAdd.logic.FormProcessor import build_template_instance
from src.views.ConfigPageAdd.logic.InterfaceHandler import reassign_interface
from src.views.ConfigPageAdd.logic.TemplateManager import generate_template_name
from src.views.ConfigPageAdd.logic.Exporter import export_template


class ConfigMainArea(QtWidgets.QWidget):
    """Central configuration workspace."""

    def __init__(self,
                 parent: QtWidgets.QWidget | None,
                 device_info: Dict[str, Any] | None) -> None:
        super().__init__(parent)
        self._device_info: Dict[str, Any] = device_info or {}
        self.current_form: QtWidgets.QWidget | None = None
        self.current_template_type: str = "device"
        # cache of template instances keyed by radio value ("device", "vlan", custom-name)
        self.custom_templates: Dict[str, object] = {}
        self.form_container: QtWidgets.QStackedWidget

        # Dictionary to store interface buttons for easy access when updating colors
        self.interface_buttons: Dict[str, QtWidgets.QPushButton] = {}

        self.interface_manager = InterfaceAssignmentManager(
            device_info.get("interfaces", []),
            "vlan" if device_info.get("device_type", "router") == "switch" else "device",
        )

        # Initialize default templates before UI to have them ready for coloring
        self._init_default_templates()
        self._init_ui()

    # --------------------------- INIT --------------------------- #
    def _init_default_templates(self) -> None:
        """Initialize default templates if needed."""
        dev_type = self._device_info.get("device_type", "router").lower()
        switch_layer = self._device_info.get("switch_layer", "L2")  # Nowa linia

        # Initialize device template
        if "device" not in self.custom_templates:
            # Sprawdź typ przełącznika (L2 vs L3)
            if dev_type == "switch":
                if switch_layer == "L3":
                    # Utworzenie instancji SwitchL3Template dla przełączników L3
                    from src.models.templates.SwitchL3Template import SwitchL3Template
                    self.custom_templates["device"] = SwitchL3Template(hostname="Switch")
                else:
                    # Standardowa instancja SwitchTemplate dla przełączników L2
                    self.custom_templates["device"] = SwitchL2Template(hostname="Switch")
            else:
                self.custom_templates["device"] = RouterTemplate(hostname="Router")

        # Initialize VLAN 1 template for switches with default color
        if dev_type == "switch" and "vlan" not in self.custom_templates:
            vlan_interfaces = self.interface_manager.get_interfaces_for_template("vlan")
            self.custom_templates["vlan"] = AccessTemplate(
                interfaces=vlan_interfaces,
                vlan_id=1,
                color="#4287f5"  # Default blue color
            )

    # --------------------------- UI INIT --------------------------- #
    def _init_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        # row of interface buttons (if any)
        ifaces: List[str] = self._device_info.get("interfaces", [])
        if ifaces:
            grid = QtWidgets.QGridLayout()
            cols = 4
            for idx, iface in enumerate(ifaces):
                btn = QtWidgets.QPushButton(iface)
                btn.clicked.connect(
                    lambda _, n=iface: reassign_interface(
                        self.interface_manager, n, self.current_template_type, self
                    )
                )
                grid.addWidget(btn, idx // cols, idx % cols)
                # Store the button reference for color updates
                self.interface_buttons[iface] = btn
            root.addLayout(grid)

        # form area
        row = QtWidgets.QHBoxLayout()
        self.form_container = QtWidgets.QStackedWidget()
        row.addWidget(self.form_container, 1)
        root.addLayout(row)

        # action buttons
        self.apply_btn = QtWidgets.QPushButton("Zastosuj zmiany")
        self.apply_btn.clicked.connect(self._apply_form_changes)
        root.addWidget(self.apply_btn)

        btn_box = QtWidgets.QHBoxLayout()
        self.back_btn = QtWidgets.QPushButton("Wstecz")
        self.back_btn.clicked.connect(self._on_back_clicked)
        btn_box.addWidget(self.back_btn)

        self.save_btn = QtWidgets.QPushButton("Zapisz")
        self.save_btn.clicked.connect(self._apply_form_changes)
        btn_box.addWidget(self.save_btn)

        self.export_btn = QtWidgets.QPushButton("Exportuj")
        self.export_btn.clicked.connect(self._on_export_clicked)
        btn_box.addWidget(self.export_btn)

        root.addLayout(btn_box)
        root.addStretch(1)

        # start with Device form
        self.load_form_by_radio_choice("device")

        # Update interface button colors immediately
        self._update_interface_button_colors()

        # Make sure sidebar radio colors are initialized
        self._update_sidebar_radio_colors()

    # ------------------------- navigation -------------------------- #
    def _on_back_clicked(self):
        main = self.window()
        if hasattr(main, "goto_start"):
            main.goto_start()

    def _on_export_clicked(self):
        instance = build_template_instance(self.current_form)
        export_template(instance, self)

    # ------------------------- Color management --------------------- #
    def _update_interface_button_colors(self) -> None:
        """Update colors of all interface buttons based on their template assignments."""
        for iface, btn in self.interface_buttons.items():
            template_name = self.interface_manager.get_template(iface)
            template_instance = self.custom_templates.get(template_name)

            if template_instance and hasattr(template_instance, 'color'):
                # Set button background color based on template color
                color = template_instance.color
                text_color = get_contrasting_text_color(color)

                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: {text_color};
                        border: 1px solid #555555;
                        border-radius: 3px;
                        padding: 4px;
                    }}
                    QPushButton:hover {{
                        border: 1px solid #999999;
                    }}
                """)
            else:
                # Default style if no template or color
                btn.setStyleSheet("")

    def _update_sidebar_radio_colors(self) -> None:
        """Update colors of all radio buttons in the sidebar."""
        sidebar = getattr(self.parent(), "sidebar", None)
        if sidebar and hasattr(sidebar, "_radio_buttons"):
            for template_name, radio_btn in sidebar._radio_buttons.items():
                if template_name in self.custom_templates:
                    template = self.custom_templates[template_name]
                    if hasattr(template, 'color'):
                        sidebar._apply_color_to_radio(radio_btn, template.color)

    # ------------------------- apply/save -------------------------- #
    def _apply_form_changes(self) -> None:
        """
        Persist the currently displayed form, then:

        1. Store/overwrite the template instance in self.custom_templates.
        2. If the instance exposes generate_config(), build the CLI:
              • When saving the SwitchTemplate (device radio) we pass all
                AccessTemplates first and TrunkTemplates second as nested
                configs so they appear inside configure terminal.
              • Otherwise we just call instance.generate_config().
        3. Dump the CLI to stdout (for logs).
        4. Copy the CLI block to the system clipboard.
        5. Show an information dialog.
        6. Update interface button colors and sidebar radio colors
        """
        # --- build instance from the active form ------------------- #
        if self.current_form is None:
            return

        instance = build_template_instance(self.current_form)
        if not instance:
            return

        # --- keep VLAN list coherent on the device template -------- #
        if isinstance(instance, AccessTemplate):
            switch = self.custom_templates.get("device")
            if isinstance(switch, SwitchL2Template):
                # add the VLAN only if it is not yet on the list
                if instance.vlan_id not in switch.vlan_list:
                    switch.vlan_list.append(instance.vlan_id)

        # --- store / overwrite current template -------------------- #
        self.custom_templates[self.current_template_type] = instance
        print(f"[DEBUG] Saved template '{self.current_template_type}'")

        # --- update interface button colors ------------------------ #
        self._update_interface_button_colors()

        # --- update sidebar radio colors --------------------------- #
        self._update_sidebar_radio_colors()

        # --- generate CLI if supported ----------------------------- #
        if hasattr(instance, "generate_config"):
            # collect child templates when saving the switch
            if isinstance(instance, SwitchL2Template):
                access_templates = [
                    t for k, t in self.custom_templates.items()
                    if k != "device" and isinstance(t, AccessTemplate)
                ]
                trunk_templates = [
                    t for k, t in self.custom_templates.items()
                    if k != "device" and isinstance(t, TrunkTemplate)
                ]
                nested = access_templates + trunk_templates
                cli_lines = instance.generate_config(nested)
            else:
                cli_lines = instance.generate_config()

            cli_text = "\n".join(cli_lines)

            # stdout dump
            print("\n=== Generated CLI for template "
                  f"'{self.current_template_type}' ===\n{cli_text}\n"
                  "=== end CLI =====================================\n")

            # clipboard copy
            QtWidgets.QApplication.clipboard().setText(cli_text)

            # UI feedback
            QtWidgets.QMessageBox.information(
                self, "Skopiowano",
                "Konfiguracja została wygenerowana, skopiowana do schowka "
                "i wyświetlona w konsoli."
            )

    # --------------------- new template creator -------------------- #
    def show_new_template_area(self) -> None:
        from src.views.ConfigPageAdd.NewTemplateArea import NewTemplateArea

        print("[DEBUG] Opening NewTemplateArea")
        creator = NewTemplateArea(self)
        self.form_container.addWidget(creator)
        self.form_container.setCurrentWidget(creator)
        self.current_form = creator

        creator.cancel_btn.clicked.connect(self._reload_default_view)
        creator.accept_btn.clicked.connect(self._on_accept_new_template)

    # ---------------------------------------------------------------- #
    def _reload_default_view(self) -> None:
        print("[DEBUG] Reload default view")
        self.load_form_by_radio_choice(self.current_template_type)

    # ---------------------------------------------------------------- #
    def _on_accept_new_template(self) -> None:
        """Store new template instance and update interface map."""
        print("[DEBUG] Accepting new template")

        if not hasattr(self.current_form, "get_full_template_instance"):
            print("[ERROR] Creator missing get_full_template_instance")
            return

        instance = self.current_form.get_full_template_instance()
        if instance is None:
            print("[ERROR] Creator returned None")
            return

        # --- AccessTemplate VLAN duplication check ------------------ #
        if isinstance(instance, AccessTemplate):
            switch = self.custom_templates.get("device")
            if isinstance(switch, SwitchL2Template):
                vlan_id = instance.vlan_id
                # Używamy property vlan_list, które zwraca listę int'ów
                vlan_list = switch.vlan_list
                if vlan_id in vlan_list:
                    QtWidgets.QMessageBox.warning(
                        self, "Błąd",
                        f"Nie można utworzyć AccessTemplate: VLAN {vlan_id} już istnieje."
                    )
                    return
                # Dodajemy nowy VLAN do SwitchTemplate
                from src.models.templates.SwitchL2Template import VLAN
                switch.vlans.append(VLAN(id=vlan_id, name=instance.description or f"VLAN{vlan_id}"))
                print(f"[DEBUG] Added VLAN {vlan_id} to SwitchTemplate")

        # --- Save template ----------------------------------------- #
        name = generate_template_name(instance, list(self.custom_templates.keys()))
        self.custom_templates[name] = instance
        print(f"[DEBUG] Added custom template '{name}' with interfaces {instance.interfaces}")

        # --- NEW → register every interface in InterfaceAssignmentManager
        for iface in getattr(instance, "interfaces", []):
            if self.interface_manager.assign(iface, name):
                print(f"[DEBUG] Interface {iface} mapped to template '{name}'")

        # --- add radio button & auto-select ------------------------- #
        sidebar = getattr(self.parent(), "sidebar", None)
        if sidebar and hasattr(sidebar, "add_new_template_radio"):
            sidebar.add_new_template_radio(name, instance.color if hasattr(instance, 'color') else None)
            btn = sidebar._radio_buttons.get(name)
            if btn:
                btn.setChecked(True)

        # Update interface button colors
        self._update_interface_button_colors()

        # finally return to normal view
        self._reload_default_view()

    # ---------------------- radio-switch handler -------------------- #
    def load_form_by_radio_choice(self, template_type: str) -> None:
        print(f"[DEBUG] load_form_by_radio_choice({template_type})")
        self.current_template_type = template_type
        dev_type = self._device_info.get("device_type", "router").lower()
        switch_layer = self._device_info.get("switch_layer", "L2")  # Nowa linia

        # interfaces assigned to this template
        assigned_ifaces = self.interface_manager.get_interfaces_for_template(template_type)

        # ---------- resolve instance + form class ------------------- #
        instance = None
        form_cls = None

        if template_type == "device":
            instance = self.custom_templates.get("device")
            if instance is None:
                # Wybierz odpowiednią klasę w zależności od typu urządzenia i warstwy
                if dev_type == "switch":
                    if switch_layer == "L3":
                        from src.models.templates.SwitchL3Template import SwitchL3Template
                        instance = SwitchL3Template(hostname="Switch")
                    else:
                        instance = SwitchL2Template(hostname="Switch")
                else:
                    instance = RouterTemplate(hostname="Router")
                self.custom_templates["device"] = instance

            # Wybierz odpowiednią klasę formularza
            if dev_type == "switch":
                if switch_layer == "L3" and hasattr(instance, "ip_routing"):
                    # Użyj formularza L3 jeśli typ urządzenia to przełącznik L3
                    from src.forms.SwitchL3TemplateForm import SwitchL3TemplateForm
                    form_cls = SwitchL3TemplateForm
                else:
                    form_cls = SwitchL2TemplateForm
            else:
                form_cls = RouterTemplateForm

        elif template_type == "vlan":
            instance = self.custom_templates.get("vlan")
            if instance is None:
                instance = AccessTemplate(interfaces=assigned_ifaces)
                self.custom_templates["vlan"] = instance
            else:
                instance.interfaces = assigned_ifaces
            form_cls = AccessTemplateForm

        elif template_type in self.custom_templates:
            instance = self.custom_templates[template_type]
            if hasattr(instance, "interfaces"):
                instance.interfaces = assigned_ifaces
            form_cls = AccessTemplateForm if isinstance(instance, AccessTemplate) else TrunkTemplateForm

        # guard
        if not instance or not form_cls:
            print(f"[ERROR] Cannot load form for template type: {template_type}")
            return

        # build and load form
        form_widget = form_cls()
        if hasattr(form_widget, "load_from_instance"):
            form_widget.load_from_instance(instance)

        # replace widget
        if current := self.form_container.currentWidget():
            self.form_container.removeWidget(current)
            current.deleteLater()
        self.form_container.addWidget(form_widget)
        self.form_container.setCurrentWidget(form_widget)
        self.current_form = form_widget

        # Update interface button colors
        self._update_interface_button_colors()

        # debug dump
        print("[DEBUG] Active instance data:")
        for k, v in asdict(instance).items():
            print(f"  {k}: {v}")