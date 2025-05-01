#src/views/ConfigPageAdd/ConfigMainArea.py
"""Main work area on the configuration page (interfaces, info pane, dynamic form).

Synchronizes AccessTemplate VLANs with SwitchTemplate and logs active instance
state to console whenever the radio‑button selection changes.
"""

from __future__ import annotations

from typing import Any, Dict, List
from dataclasses import asdict

from PySide6 import QtWidgets

from src.models.InterfaceAssignmentManager import InterfaceAssignmentManager

from src.forms.AccessTemplateForm import AccessTemplateForm
from src.forms.RouterTemplateForm import RouterTemplateForm
from src.forms.SwitchTemplateForm import SwitchTemplateForm
from src.forms.TrunkTemplateForm import TrunkTemplateForm

from src.models.templates.AccessTemplate import AccessTemplate
from src.models.templates.RouterTemplate import RouterTemplate
from src.models.templates.SwitchTemplate import SwitchTemplate
from src.models.templates.TrunkTemplate import TrunkTemplate

from src.views.ConfigPageAdd.logic.FormProcessor import build_template_instance
from src.views.ConfigPageAdd.logic.InterfaceHandler import reassign_interface
from src.views.ConfigPageAdd.logic.TemplateManager import generate_template_name
from src.views.ConfigPageAdd.logic.Exporter import export_template

class ConfigMainArea(QtWidgets.QWidget):
    """Central configuration workspace."""

    def __init__(self, parent: QtWidgets.QWidget | None, device_info: Dict[str, Any] | None) -> None:
        super().__init__(parent)
        self._device_info: Dict[str, Any] = device_info or {}
        self.current_form: QtWidgets.QWidget | None = None
        self.current_template_type: str = "device"
        # cache of template instances keyed by radio value ("device", "vlan", custom‑name)
        self.custom_templates: Dict[str, object] = {}
        self.form_container: QtWidgets.QStackedWidget

        self.interface_manager = InterfaceAssignmentManager(
            device_info.get("interfaces", []),
            "vlan" if device_info.get("device_type", "router") == "switch" else "device",
        )

        self._init_ui()

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

        btn_layout = QtWidgets.QHBoxLayout()
        self.back_btn = QtWidgets.QPushButton("Wstecz")
        self.back_btn.clicked.connect(self._on_back_clicked)
        btn_layout.addWidget(self.back_btn)

        self.save_btn = QtWidgets.QPushButton("Zapisz")
        self.save_btn.clicked.connect(self._apply_form_changes)
        btn_layout.addWidget(self.save_btn)

        self.export_btn = QtWidgets.QPushButton("Exportuj")
        self.export_btn.clicked.connect(self._on_export_clicked)
        btn_layout.addWidget(self.export_btn)

        root.addLayout(btn_layout)
        root.addStretch(1)

        # start with device form
        self.load_form_by_radio_choice("device")

    # ------------------------- navigation -------------------------- #
    def _on_back_clicked(self):
        main = self.window()
        if hasattr(main, "goto_start"):
            main.goto_start()

    def _on_export_clicked(self):
        instance = build_template_instance(self.current_form)
        export_template(instance, self)

    # ------------------------- apply/save -------------------------- #
    def _apply_form_changes(self) -> None:
        if self.current_form is None:
            return

        instance = build_template_instance(self.current_form)
        if not instance:
            return

        # Jeśli AccessTemplate → dopisz VLAN do SwitchTemplate
        if isinstance(instance, AccessTemplate):
            switch: object | None = self.custom_templates.get("device")
            if isinstance(switch, SwitchTemplate):
                vlan_id: int = instance.vlan_id
                if vlan_id in switch.vlan_list:
                    QtWidgets.QMessageBox.warning(self, "Błąd", f"VLAN {vlan_id} już istnieje.")
                    return
                switch.vlan_list.append(vlan_id)
                print(f"[DEBUG] Dodano VLAN {vlan_id} do SwitchTemplate")

        # zapisz / nadpisz bieżącą instancję
        self.custom_templates[self.current_template_type] = instance
        print(f"[DEBUG] Saved instance: {instance}")

    # ---------------------- radio‑switch handler -------------------- #
    def load_form_by_radio_choice(self, template_type: str) -> None:
        print(f"[DEBUG] load_form_by_radio_choice({template_type})")
        self.current_template_type = template_type
        dev_type = self._device_info.get("device_type", "router").lower()

        # interfejsy przypisane do danego szablonu
        assigned_ifaces = [
            iface
            for iface, tpl in self.interface_manager.interface_map.items()
            if tpl == template_type
        ]

        # -------------------------- resolve instance ------------------------- #
        instance = None
        form_cls = None

        if template_type == "device":
            # Użyj istniejącego lub stwórz i ZAPISZ do custom_templates
            instance = self.custom_templates.get("device")
            if instance is None:
                instance = (
                    SwitchTemplate(hostname="Switch")
                    if dev_type == "switch"
                    else RouterTemplate(hostname="Router")
                )
                self.custom_templates["device"] = instance  # ważne → późniejsza synchronizacja VLAN
            form_cls = SwitchTemplateForm if dev_type == "switch" else RouterTemplateForm

        elif template_type == "vlan":
            instance = self.custom_templates.get("vlan")
            if instance is None:
                instance = AccessTemplate(interfaces=assigned_ifaces)
                self.custom_templates["vlan"] = instance
            else:
                if hasattr(instance, "interfaces"):
                    instance.interfaces = assigned_ifaces
            form_cls = AccessTemplateForm

        elif template_type in self.custom_templates:
            instance = self.custom_templates[template_type]
            if hasattr(instance, "interfaces"):
                instance.interfaces = assigned_ifaces

            form_cls = (
                AccessTemplateForm
                if isinstance(instance, AccessTemplate)
                else TrunkTemplateForm
            )

        # -------------------------- guard --------------------------- #
        if not instance or not form_cls:
            print(f"[ERROR] Cannot load form for template type: {template_type}")
            return

        # log instance data
        print("[DEBUG] Active instance data:")
        for k, v in asdict(instance).items():
            print(f"  {k}: {v}")

        # build form and load data
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

    def _reload_default_view(self) -> None:
        print("[DEBUG] Reload default view")
        self.load_form_by_radio_choice(self.current_template_type)

    def _on_accept_new_template(self) -> None:
        """Handle accepting a new Access/Trunk template from NewTemplateArea.
        Performs VLAN‑duplication validation for AccessTemplate before saving.
        """
        print("[DEBUG] Accepting new template")
        if not hasattr(self.current_form, "get_full_template_instance"):
            print("[ERROR] Creator missing get_full_template_instance")
            return

        instance = self.current_form.get_full_template_instance()
        if instance is None:
            print("[ERROR] Creator returned None")
            return

        # --- Validation for AccessTemplate VLAN duplication ---
        if isinstance(instance, AccessTemplate):
            switch = self.custom_templates.get("device")
            if isinstance(switch, SwitchTemplate):
                vlan_id = instance.vlan_id
                if vlan_id in switch.vlan_list:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Błąd",
                        f"Nie można utworzyć nowego AccessTemplate: VLAN {vlan_id} już istnieje.",
                    )
                    print(f"[DEBUG] Aborted – VLAN {vlan_id} already present in SwitchTemplate")
                    return  # przerwij – nie zapisuj duplikatu
                # jeśli unikalny, dopisz do listy VLAN‑ów
                switch.vlan_list.append(vlan_id)
                print(f"[DEBUG] Dodano VLAN {vlan_id} do SwitchTemplate")

        # --- Save template and add radio button ---
        name = generate_template_name(instance, list(self.custom_templates.keys()))
        self.custom_templates[name] = instance
        print(f"[DEBUG] Added custom template '{name}'")

        sidebar = getattr(self.parent(), "sidebar", None)
        if sidebar and hasattr(sidebar, "add_new_template_radio"):
            sidebar.add_new_template_radio(name)
            btn = sidebar._radio_buttons.get(name)
            if btn:
                btn.setChecked(True)

        self._reload_default_view()
