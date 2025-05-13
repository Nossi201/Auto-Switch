# src/views/ConfigPageAdd/NewTemplateArea.py
"""Widget for creating a brand-new Access or Trunk template.

Passes *editable_interfaces=True* to underlying forms so the user can type or
paste interface names when adding a fresh template. The widget supports
the enhanced forms with all advanced configuration options.
"""

from PySide6 import QtWidgets
from src.forms.AccessTemplateForm import AccessTemplateForm
from src.forms.TrunkTemplateForm import TrunkTemplateForm
from src.models.templates.AccessTemplate import AccessTemplate
from src.models.templates.TrunkTemplate import TrunkTemplate


class NewTemplateArea(QtWidgets.QWidget):
    """Area to create a new Access or Trunk template."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_form = None
        self._init_ui()

    # ------------------------------------------------------------------ #
    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)

        # selector
        self.template_selector = QtWidgets.QComboBox()
        self.template_selector.addItems(["Access", "Trunk"])
        self.template_selector.currentTextChanged.connect(self._on_template_type_changed)
        layout.addWidget(self.template_selector)

        # dynamic form container
        self.dynamic_form_area = QtWidgets.QVBoxLayout()
        layout.addLayout(self.dynamic_form_area)

        # buttons
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.accept_btn = QtWidgets.QPushButton("Accept")
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addWidget(self.cancel_btn)
        btn_box.addWidget(self.accept_btn)
        layout.addLayout(btn_box)

        # initial form
        self._load_template_form("Access")

    # ------------------------------------------------------------------ #
    def _load_template_form(self, template_type: str):
        if self.current_form:
            self.dynamic_form_area.removeWidget(self.current_form)
            self.current_form.deleteLater()
            self.current_form = None

        if template_type == "Access":
            self.current_form = AccessTemplateForm(editable_interfaces=True)
        else:
            self.current_form = TrunkTemplateForm(editable_interfaces=True)

        self.dynamic_form_area.addWidget(self.current_form)

    # ------------------------------------------------------------------ #
    def _on_template_type_changed(self, template_type: str):
        self._load_template_form(template_type)

    # ------------------------------------------------------------------ #
    def get_full_template_instance(self):
        """Return a fully populated template object (AccessTemplate/TrunkTemplate).

        This method handles both the original and enhanced forms, checking for
        the presence of the create_access_template() method to determine which approach to use.
        """
        # For enhanced AccessTemplateForm with create_access_template() method
        if isinstance(self.current_form, AccessTemplateForm) and hasattr(self.current_form, 'create_access_template'):
            return self.current_form.create_access_template()

        # For enhanced TrunkTemplateForm with similar method (if implemented)
        if isinstance(self.current_form, TrunkTemplateForm) and hasattr(self.current_form, 'create_trunk_template'):
            return self.current_form.create_trunk_template()

        # Legacy fallback for original forms
        if isinstance(self.current_form, AccessTemplateForm):
            return AccessTemplate(
                interfaces=[
                    s.strip() for s in self.current_form.interfaces_input.text().split(",") if s.strip()
                ],
                vlan_id=self.current_form.vlan_id_input.value(),
                description=self.current_form.description_input.text() or None,
                color=self.current_form.color_picker.get_value() if hasattr(self.current_form,
                                                                            'color_picker') else None,
                port_security_enabled=self.current_form.port_security_checkbox.isChecked(),
                max_mac_addresses=self.current_form.max_mac_input.value(),
                violation_action=self.current_form.violation_action_combo.currentText(),
                voice_vlan=self.current_form.voice_vlan_input.value()
                if self.current_form.voice_vlan_input.value() > 0
                else None,
                sticky_mac=self.current_form.sticky_mac_checkbox.isChecked(),
                storm_control_broadcast_min=self.current_form.broadcast_min_input.value()
                if self.current_form.storm_control_checkbox.isChecked()
                else None,
                storm_control_broadcast_max=self.current_form.broadcast_max_input.value()
                if self.current_form.storm_control_checkbox.isChecked()
                else None,
                storm_control_multicast_min=self.current_form.multicast_min_input.value()
                if self.current_form.storm_control_checkbox.isChecked()
                else None,
                storm_control_multicast_max=self.current_form.multicast_max_input.value()
                if self.current_form.storm_control_checkbox.isChecked()
                else None,
                spanning_tree_portfast=self.current_form.spanning_tree_portfast_checkbox.isChecked()
                if hasattr(self.current_form, "spanning_tree_portfast_checkbox")
                else False,
            )

        if isinstance(self.current_form, TrunkTemplateForm):
            # Tworzymy instancję TrunkTemplate bez parametru color
            trunk_template = TrunkTemplate(
                interfaces=[
                    s.strip() for s in self.current_form.interfaces_input.text().split(",") if s.strip()
                ],
                allowed_vlans=[
                    int(v.strip())
                    for v in self.current_form.allowed_vlans_input.text().split(",")
                    if v.strip().isdigit()
                ],
                native_vlan=self.current_form.native_vlan_input.value(),
                description=self.current_form.description_input.text() or None,
                pruning_enabled=self.current_form.pruning_checkbox.isChecked(),
                spanning_tree_guard_root=self.current_form.stp_guard_checkbox.isChecked(),
                encapsulation=self.current_form.encapsulation_combo.currentText(),
                dtp_mode=(
                    None if self.current_form.dtp_mode_combo.currentText() == "--" else
                    self.current_form.dtp_mode_combo.currentText()
                ),
                nonegotiate=self.current_form.nonegotiate_checkbox.isChecked(),
                spanning_tree_portfast=self.current_form.portfast_checkbox.isChecked(),
            )

            # Jeśli TrunkTemplate ma atrybut color, ustawiamy go po utworzeniu instancji
            if hasattr(trunk_template, 'color') and hasattr(self.current_form, 'color_picker'):
                setattr(trunk_template, 'color', self.current_form.color_picker.get_value())

            return trunk_template

        return None