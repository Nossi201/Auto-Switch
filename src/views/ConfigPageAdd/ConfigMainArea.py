#src/views/ConfigPageAdd/ConfigMainArea.py
"""Central area of the configuration page.
Displays interface buttons at the top, template information on the left, form on the right, and Apply Changes button below.
"""

from typing import Any, Dict, List
from PySide6 import QtWidgets
from dataclasses import fields

from src.forms.AccessTemplateForm import AccessTemplateForm
from src.forms.RouterTemplateForm import RouterTemplateForm
from src.forms.TrunkTemplateForm import TrunkTemplateForm

from src.models.templates.AccessTemplate import AccessTemplate
from src.models.templates.RouterTemplate import RouterTemplate
from src.models.templates.TrunkTemplate import TrunkTemplate

class ConfigMainArea(QtWidgets.QWidget):
    """Main configuration workspace (interfaces top, info left, form right, apply button below)."""

    def __init__(self, parent: QtWidgets.QWidget | None, device_info: Dict[str, Any] | None) -> None:
        super().__init__(parent)
        self._device_info = device_info or {}
        self.custom_templates = {}
        self.current_form = None
        self.device_info_label = None
        self.new_template_area = None
        self.current_template_type = "device"
        self._init_ui()

    def _init_ui(self) -> None:
        """Build the layout: interface buttons on top, info and form side by side, apply button below."""
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        interfaces: List[str] = self._device_info.get("interfaces", [])
        if interfaces:
            self.grid = QtWidgets.QGridLayout()
            self.grid.setHorizontalSpacing(6)
            self.grid.setVerticalSpacing(6)
            cols = 4
            for idx, iface in enumerate(interfaces):
                btn = QtWidgets.QPushButton(iface)
                btn.clicked.connect(lambda _, name=iface: self._on_interface_button_clicked(name))
                row = idx // cols
                col = idx % cols
                self.grid.addWidget(btn, row, col)
            root.addLayout(self.grid)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setSpacing(20)

        self.device_info_label = QtWidgets.QLabel()
        self.device_info_label.setStyleSheet("font-weight: bold;")
        self.device_info_label.setMinimumWidth(250)
        self.device_info_label.setWordWrap(True)
        top_layout.addWidget(self.device_info_label)

        self.form_container = QtWidgets.QStackedWidget()
        top_layout.addWidget(self.form_container, 1)

        root.addLayout(top_layout)

        self.apply_changes_btn = QtWidgets.QPushButton("Zastosuj zmiany")
        self.apply_changes_btn.clicked.connect(self._apply_form_changes)
        root.addWidget(self.apply_changes_btn)

        root.addStretch(1)

        self.load_form_by_radio_choice(self.current_template_type)

    def _on_interface_button_clicked(self, iface_name: str) -> None:
        """Handle interface button click (currently does nothing)."""
        print(f"Interface button clicked: {iface_name}")

    def _update_label_for_instance(self, instance) -> None:
        """Update label text to show instance attribute values."""
        field_lines = []
        for f in fields(instance):
            value = getattr(instance, f.name)
            line = f"{f.name}: {value}"
            field_lines.append(line)
        self.device_info_label.setText("\n".join(field_lines))

    def load_form_by_radio_choice(self, template_type: str) -> None:
        """Load form depending on selected radio button."""
        self.current_template_type = template_type

        device_type = self._device_info.get("device_type", "router").lower()

        if template_type == "device":
            if device_type == "router":
                from src.models.templates.RouterTemplate import RouterTemplate
                from src.forms.RouterTemplateForm import RouterTemplateForm
                new_form = RouterTemplateForm()
                instance = RouterTemplate(hostname="Router")
                self._update_label_for_instance(instance)
                print(f"[DEBUG] Router Device Template Selected: {instance}")
            else:  # switch
                from src.models.templates.SwitchTemplate import SwitchTemplate
                from src.forms.SwitchTemplateForm import SwitchTemplateForm
                new_form = SwitchTemplateForm()
                instance = SwitchTemplate(hostname="Switch")
                self._update_label_for_instance(instance)
                print(f"[DEBUG] Switch Device Template Selected: {instance}")

        elif template_type == "vlan":
            if device_type == "switch":
                from src.models.templates.AccessTemplate import AccessTemplate
                from src.forms.AccessTemplateForm import AccessTemplateForm
                new_form = AccessTemplateForm()
                instance = AccessTemplate()
                self._update_label_for_instance(instance)
                print(f"[DEBUG] Switch VLAN 1 (Access Port) Template Selected: {instance}")
            else:
                print("[ERROR] Routers do not have VLANs!")
                return

        else:
            print(f"[ERROR] Unknown template type: {template_type}")
            return

        self.set_new_form(new_form)

    def _apply_form_changes(self) -> None:
        """Apply changes from form and update the label."""
        if self.current_form is None:
            return

        if self.current_template_type == "device":
            instance = AccessTemplate(
                interfaces=[s.strip() for s in self.current_form.interfaces_input.text().split(",") if s.strip()],
                vlan_id=self.current_form.vlan_id_input.value(),
                description=self.current_form.description_input.text() or None,
                port_security_enabled=self.current_form.port_security_checkbox.isChecked(),
                max_mac_addresses=self.current_form.max_mac_input.value(),
                violation_action=self.current_form.violation_action_combo.currentText(),
                voice_vlan=self.current_form.voice_vlan_input.value() if self.current_form.voice_vlan_input.value() > 0 else None,
                storm_control_broadcast=self.current_form.storm_control_input.value() if self.current_form.storm_control_input.value() > 0 else None,
                spanning_tree_portfast=self.current_form.portfast_checkbox.isChecked()
            )
            self._update_label_for_instance(instance)

        elif self.current_template_type == "vlan":
            instance = TrunkTemplate(
                interfaces=[s.strip() for s in self.current_form.interfaces_input.text().split(",") if s.strip()],
                allowed_vlans=[int(s) for s in self.current_form.allowed_vlans_input.text().split(",") if s.strip().isdigit()],
                native_vlan=self.current_form.native_vlan_input.value(),
                description=self.current_form.description_input.text() or None,
                pruning_enabled=self.current_form.pruning_checkbox.isChecked(),
                spanning_tree_guard_root=self.current_form.stp_guard_checkbox.isChecked(),
                encapsulation=self.current_form.encapsulation_combo.currentText()
            )
            self._update_label_for_instance(instance)

    def set_new_form(self, widget: QtWidgets.QWidget) -> None:
        """Replace current form with new widget."""
        if self.form_container.currentWidget():
            old_widget = self.form_container.currentWidget()
            self.form_container.removeWidget(old_widget)
            old_widget.deleteLater()

        self.form_container.addWidget(widget)
        self.form_container.setCurrentWidget(widget)
        self.current_form = widget

    def show_new_template_area(self) -> None:
        """Clear form and label, and show New Template creator."""
        from src.views.ConfigPageAdd.NewTemplateArea import NewTemplateArea

        self.device_info_label.hide()
        new_template_area = NewTemplateArea(self)
        self.set_new_form(new_template_area)

        new_template_area.cancel_btn.clicked.connect(self._reload_default_view)
        new_template_area.accept_btn.clicked.connect(self._on_accept_new_template)

    def _reload_default_view(self) -> None:
        """Reload the default device info and form after cancel."""
        self.device_info_label.show()
        self.load_form_by_radio_choice(self.current_template_type)

    def _on_accept_new_template(self) -> None:
        """Handle accepting a new template."""
        if not isinstance(self.current_form, QtWidgets.QWidget):
            return

        if hasattr(self.current_form, 'get_template_data') and hasattr(self.current_form, 'get_full_template_instance'):
            form_data = self.current_form.get_template_data()
            instance = self.current_form.get_full_template_instance()

            if instance is None:
                print("[ERROR] Failed to create template instance!")
                return

            print(f"[DEBUG] Accepted new template instance: {instance}")

            vlan_id = getattr(instance, "native_vlan", None) or getattr(instance, "vlan_id", None)

            if vlan_id is not None:
                name = f"VLAN {vlan_id}"
            else:
                name = "New VLAN"

            self.custom_templates[name] = instance  # <--- tutaj zapisujemy pełny obiekt!

            # Add radio button
            if hasattr(self.parent(), "sidebar"):
                sidebar = getattr(self.parent(), "sidebar", None)
                if sidebar and hasattr(sidebar, "add_new_template_radio"):
                    sidebar.add_new_template_radio(name)
                    btn = sidebar._radio_buttons.get(name)
                    if btn:
                        btn.setChecked(True)

        self._reload_default_view()





