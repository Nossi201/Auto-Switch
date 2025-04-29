#src/views/ConfigPageAdd/ConfigMainArea.py
"""Main work area on the configuration page (interfaces, info pane, dynamic form).

This **fixed** version solves mismatched form ↔ model handling that caused an
AttributeError when the active form did not expose the expected widgets.
The code now:
* Chooses the correct form in `load_form_by_radio_choice()`.
* Builds the right dataclass instance in `_apply_form_changes()` using
  `isinstance()` checks instead of relying on `current_template_type`.
* Supports router & switch device templates, default VLAN-1 (Access), Trunk and
  any user-defined template stored in `custom_templates`.
"""

from __future__ import annotations

from dataclasses import fields
from typing import Any, Dict, List, Type

from PySide6 import QtWidgets

from src.forms.AccessTemplateForm import AccessTemplateForm
from src.forms.RouterTemplateForm import RouterTemplateForm
from src.forms.SwitchTemplateForm import SwitchTemplateForm
from src.forms.TrunkTemplateForm import TrunkTemplateForm
from src.models.templates.AccessTemplate import AccessTemplate
from src.models.templates.RouterTemplate import RouterTemplate
from src.models.templates.SwitchTemplate import SwitchTemplate
from src.models.templates.TrunkTemplate import TrunkTemplate


class ConfigMainArea(QtWidgets.QWidget):
    """Central configuration workspace."""

    # ------------------------------------------------------------------ #
    # Construction & static UI
    # ------------------------------------------------------------------ #

    def __init__(
            self,
            parent: QtWidgets.QWidget | None,
            device_info: Dict[str, Any] | None,
    ) -> None:
        super().__init__(parent)

        self._device_info: Dict[str, Any] = device_info or {}

        # Runtime state
        self.current_form: QtWidgets.QWidget | None = None
        self.current_template_type: str = "device"
        self.custom_templates: Dict[str, object] = {}

        # Handles set in _init_ui()
        self.device_info_label: QtWidgets.QLabel
        self.form_container: QtWidgets.QStackedWidget

        self._init_ui()
        print("[DEBUG] ConfigMainArea initialised")

    # ------------------------------------------------------------------ #

    def _init_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        # ---------- Interfaces grid ----------
        interfaces: List[str] = self._device_info.get("interfaces", [])
        if interfaces:
            grid = QtWidgets.QGridLayout()
            cols = 4
            for idx, iface in enumerate(interfaces):
                btn = QtWidgets.QPushButton(iface)
                btn.clicked.connect(lambda _, n=iface: self._on_interface_button_clicked(n))
                grid.addWidget(btn, idx // cols, idx % cols)
            root.addLayout(grid)

        # ---------- Info pane + form ----------
        row = QtWidgets.QHBoxLayout()

        self.device_info_label = QtWidgets.QLabel()
        self.device_info_label.setStyleSheet("font-weight: bold;")
        self.device_info_label.setMinimumWidth(260)
        self.device_info_label.setWordWrap(True)
        row.addWidget(self.device_info_label)

        self.form_container = QtWidgets.QStackedWidget()
        row.addWidget(self.form_container, 1)
        root.addLayout(row)

        # ---------- Apply ----------
        self.apply_btn = QtWidgets.QPushButton("Zastosuj zmiany")
        self.apply_btn.clicked.connect(self._apply_form_changes)
        root.addWidget(self.apply_btn)

        root.addStretch(1)

        # default
        self.load_form_by_radio_choice("device")

    # ------------------------------------------------------------------ #
    # Helper utilities
    # ------------------------------------------------------------------ #

    def _on_interface_button_clicked(self, name: str) -> None:
        print(f"[DEBUG] Interface button clicked: {name}")

    def _update_label_for_instance(self, instance: object) -> None:
        self.device_info_label.setText(
            "\n".join(f"{f.name}: {getattr(instance, f.name)}" for f in fields(instance))
        )

    def _set_new_form(self, widget: QtWidgets.QWidget) -> None:
        if current := self.form_container.currentWidget():
            self.form_container.removeWidget(current)
            current.deleteLater()
        self.form_container.addWidget(widget)
        self.form_container.setCurrentWidget(widget)
        self.current_form = widget

    # ------------------------------------------------------------------ #
    # Sidebar callback
    # ------------------------------------------------------------------ #

    def load_form_by_radio_choice(self, template_type: str) -> None:
        print(f"[DEBUG] load_form_by_radio_choice({template_type})")
        self.current_template_type = template_type
        dev_type = self._device_info.get("device_type", "router").lower()

        if template_type == "device":
            if dev_type == "router":
                self._push_form(RouterTemplateForm, RouterTemplate(hostname="Router"))
            else:
                self._push_form(SwitchTemplateForm, SwitchTemplate(hostname="Switch"))

        elif template_type == "vlan":
            self._push_form(AccessTemplateForm, AccessTemplate())

        elif template_type in self.custom_templates:
            inst = self.custom_templates[template_type]
            if isinstance(inst, AccessTemplate):
                self._push_form(AccessTemplateForm, inst)
            elif isinstance(inst, TrunkTemplate):
                self._push_form(TrunkTemplateForm, inst)
            else:
                print(f"[ERROR] Unknown custom template type: {type(inst)}")
        else:
            print(f"[ERROR] Unknown key: {template_type}")

    # ------------------------------------------------------------------ #

    def _push_form(self, form_cls: Type[QtWidgets.QWidget], instance: object | None) -> None:
        form: QtWidgets.QWidget = form_cls()
        if instance and hasattr(form, "load_from_instance"):
            form.load_from_instance(instance)
        self._set_new_form(form)

        if instance:
            self._update_label_for_instance(instance)
        else:
            self.device_info_label.clear()

        print(f"[DEBUG] Switched form → {form_cls.__name__}")

    # ------------------------------------------------------------------ #
    # New-template creator
    # ------------------------------------------------------------------ #

    def show_new_template_area(self) -> None:
        from src.views.ConfigPageAdd.NewTemplateArea import NewTemplateArea

        print("[DEBUG] Opening NewTemplateArea")
        self.device_info_label.hide()
        creator = NewTemplateArea(self)
        self._set_new_form(creator)

        creator.cancel_btn.clicked.connect(self._reload_default_view)
        creator.accept_btn.clicked.connect(self._on_accept_new_template)

    def _reload_default_view(self) -> None:
        print("[DEBUG] Reload default view")
        self.device_info_label.show()
        self.load_form_by_radio_choice(self.current_template_type)

    def _on_accept_new_template(self) -> None:
        print("[DEBUG] Accepting new template")
        if not hasattr(self.current_form, "get_full_template_instance"):
            print("[ERROR] Creator missing get_full_template_instance")
            return

        instance = self.current_form.get_full_template_instance()
        if instance is None:
            print("[ERROR] Creator returned None")
            return

        # ---------- radio-button label logic ----------
        if isinstance(instance, TrunkTemplate):
            # Prefer native-VLAN id, fall back to first allowed-VLAN
            vid = instance.native_vlan or (instance.allowed_vlans[0] if instance.allowed_vlans else 0)
            base_name = f"TRUNK {vid}" if vid else "TRUNK"
        else:  # AccessTemplate
            vid = getattr(instance, "vlan_id", None)
            base_name = f"VLAN {vid}" if vid else "Custom template"

        name = base_name
        idx = 1
        while name in self.custom_templates:
            idx += 1
            name = f"{base_name} ({idx})"

        self.custom_templates[name] = instance
        print(f"[DEBUG] Added custom template '{name}'")

        sidebar = getattr(self.parent(), "sidebar", None)
        if sidebar and hasattr(sidebar, "add_new_template_radio"):
            sidebar.add_new_template_radio(name)
            btn = sidebar._radio_buttons.get(name)
            if btn:
                btn.setChecked(True)

        self._reload_default_view()

    # ------------------------------------------------------------------ #
    # Apply button logic
    # ------------------------------------------------------------------ #

    def _apply_form_changes(self) -> None:
        if self.current_form is None:
            return

        form = self.current_form
        instance: object

        # -------- Access --------
        if isinstance(form, AccessTemplateForm):
            instance = AccessTemplate(
                interfaces=[s.strip() for s in form.interfaces_input.text().split(",") if s.strip()],
                vlan_id=form.vlan_id_input.value(),
                description=form.description_input.text() or None,
                port_security_enabled=form.port_security_checkbox.isChecked(),
                max_mac_addresses=form.max_mac_input.value(),
                violation_action=form.violation_action_combo.currentText(),
                voice_vlan=form.voice_vlan_input.value() or None,
                storm_control_broadcast=form.storm_control_input.value() or None,
                spanning_tree_portfast=form.portfast_checkbox.isChecked(),
            )

        # -------- Trunk --------
        elif isinstance(form, TrunkTemplateForm):
            instance = TrunkTemplate(
                interfaces=[s.strip() for s in form.interfaces_input.text().split(",") if s.strip()],
                allowed_vlans=[int(v) for v in form.allowed_vlans_input.text().split(",") if v.strip().isdigit()],
                native_vlan=form.native_vlan_input.value(),
                description=form.description_input.text() or None,
                pruning_enabled=form.pruning_checkbox.isChecked(),
                spanning_tree_guard_root=form.stp_guard_checkbox.isChecked(),
                encapsulation=form.encapsulation_combo.currentText(),
            )

        # -------- Router --------
        elif isinstance(form, RouterTemplateForm):
            iface_name = form.interface_name_input.text().strip()
            iface_ip = form.interface_ip_input.text().strip()
            iface_mask = form.interface_mask_input.text().strip()
            interfaces = (
                {iface_name: {"ip": iface_ip, "mask": iface_mask}}
                if iface_name and iface_ip and iface_mask
                else {}
            )
            instance = RouterTemplate(
                hostname=form.hostname_input.text() or "Router",
                interfaces=interfaces,
                routing_protocols=[p.strip() for p in form.routing_protocols_input.text().split(",") if p.strip()],
                static_routes=[],
            )

        # -------- Switch --------
        elif isinstance(form, SwitchTemplateForm):
            vlan_entries = [
                {"id": p.split(":")[0].strip(), "name": p.split(":")[1].strip()}
                for p in form.vlan_list_input.text().split(",")
                if ":" in p
            ] if form.vlan_list_input.text().strip() else []

            instance = SwitchTemplate(
                hostname=form.hostname_input.text() or "Switch",
                vlan_list=vlan_entries,
                spanning_tree_mode=form.spanning_tree_mode_combo.currentText(),
            )

        else:
            print(f"[ERROR] Unsupported form class: {type(form)}")
            return

        self._update_label_for_instance(instance)
        print(f"[DEBUG] Saved instance: {instance}")
