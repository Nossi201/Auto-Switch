"""Widget for creating a new Access or Trunk template."""

from PySide6 import QtWidgets
from src.forms.AccessTemplateForm import AccessTemplateForm
from src.forms.TrunkTemplateForm import TrunkTemplateForm

class NewTemplateArea(QtWidgets.QWidget):
    """Area to create a new Access or Trunk template."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_form = None
        self._init_ui()

    def _init_ui(self):
        """Initialize template selection and form area."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)

        self.template_selector = QtWidgets.QComboBox()
        self.template_selector.addItems(["Access", "Trunk"])
        self.template_selector.currentTextChanged.connect(self._on_template_type_changed)
        layout.addWidget(self.template_selector)

        self.dynamic_form_area = QtWidgets.QVBoxLayout()
        layout.addLayout(self.dynamic_form_area)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.accept_btn = QtWidgets.QPushButton("Accept")
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.accept_btn)
        layout.addLayout(button_layout)

        self._load_template_form("Access")

    def _load_template_form(self, template_type: str):
        """Load AccessTemplateForm or TrunkTemplateForm dynamically."""
        if self.current_form:
            self.dynamic_form_area.removeWidget(self.current_form)
            self.current_form.deleteLater()
            self.current_form = None

        if template_type == "Access":
            self.current_form = AccessTemplateForm()
        else:
            self.current_form = TrunkTemplateForm()

        self.dynamic_form_area.addWidget(self.current_form)

    def _on_template_type_changed(self, template_type: str):
        """Handle user switching template type."""
        self._load_template_form(template_type)

    def get_template_data(self):
        """Collect full template info from form."""
        vlan_id = None

        if hasattr(self.current_form, "vlan_id_input"):
            vlan_id = self.current_form.vlan_id_input.value()
        elif hasattr(self.current_form, "native_vlan_input"):
            vlan_id = self.current_form.native_vlan_input.value()

        return {
            "vlan_id": vlan_id,
            "template_type": self.template_selector.currentText()
        }

    def get_full_template_instance(self):
        """Return a filled AccessTemplate or TrunkTemplate instance."""
        from src.models.templates.AccessTemplate import AccessTemplate
        from src.models.templates.TrunkTemplate import TrunkTemplate

        if isinstance(self.current_form, AccessTemplateForm):
            return AccessTemplate(
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

        elif isinstance(self.current_form, TrunkTemplateForm):
            return TrunkTemplate(
                interfaces=[s.strip() for s in self.current_form.interfaces_input.text().split(",") if s.strip()],
                allowed_vlans=[int(v.strip()) for v in self.current_form.allowed_vlans_input.text().split(",") if
                               v.strip().isdigit()],
                native_vlan=self.current_form.native_vlan_input.value(),
                description=self.current_form.description_input.text() or None,
                pruning_enabled=self.current_form.pruning_checkbox.isChecked(),
                spanning_tree_guard_root=self.current_form.stp_guard_checkbox.isChecked(),
                encapsulation=self.current_form.encapsulation_combo.currentText()
            )

        return None

