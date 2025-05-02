#src/forms/TrunkTemplateForm.py
"""PySide6 form for TrunkTemplate.

Key points
----------

* **editable_interfaces** (bool, default *False*) – constructor flag that
  toggles whether the *Interfaces* field is user-editable.
  * NewTemplateArea *passes* `editable_interfaces=True` so a fresh template can
  be seeded by typing/pasting ports.
  * In normal edit mode the field remains read-only – it updates only when the
    operator clicks an interface button.

* **Native-VLAN auto-append** – whenever the *Native VLAN* spin-box changes,
  the value is ensured at the end of the *Allowed VLANs* CSV.

All runtime strings stay Polish (labels), while comments remain English.
"""

from PySide6 import QtWidgets


class TrunkTemplateForm(QtWidgets.QWidget):
    """Form for filling TrunkTemplate data."""

    def __init__(self,
                 parent=None,
                 instance=None,
                 *,
                 editable_interfaces: bool = False):
        """
        Parameters
        ----------
        editable_interfaces : bool, default False
            If *True* the user may freely edit the ‘Interfaces’ line-edit
            (used by *NewTemplateArea*).  If *False* the line-edit is
            read-only and driven solely by interface-selection buttons.
        """
        super().__init__(parent)
        self._editable_interfaces = editable_interfaces
        self._init_ui()
        if instance:
            self.load_from_instance(instance)

    # ------------------------------------------------------------------ #
    def _init_ui(self):
        """Create widgets and layout for TrunkTemplate."""
        form = QtWidgets.QFormLayout(self)

        # Interfaces
        self.interfaces_input = QtWidgets.QLineEdit()
        self.interfaces_input.setReadOnly(not self._editable_interfaces)

        # VLAN widgets
        self.allowed_vlans_input = QtWidgets.QLineEdit()
        self.native_vlan_input = QtWidgets.QSpinBox()
        self.native_vlan_input.setRange(1, 4094)
        self.native_vlan_input.valueChanged.connect(self._ensure_native_in_allowed)

        # Common check-boxes
        self.description_input = QtWidgets.QLineEdit()
        self.pruning_checkbox = QtWidgets.QCheckBox("Enable VLAN Pruning")
        self.stp_guard_checkbox = QtWidgets.QCheckBox("Enable STP Root Guard")

        # Encapsulation & DTP
        self.encapsulation_combo = QtWidgets.QComboBox()
        self.encapsulation_combo.addItems(["dot1q", "isl"])
        self.dtp_mode_combo = QtWidgets.QComboBox()
        self.dtp_mode_combo.addItems(["--", "auto", "desirable"])
        self.nonegotiate_checkbox = QtWidgets.QCheckBox("Disable DTP (nonegotiate)")

        # STP PortFast
        self.portfast_checkbox = QtWidgets.QCheckBox("Enable STP PortFast (trunk)")

        # ---- layout ----
        form.addRow("Interfaces:", self.interfaces_input)
        form.addRow("Allowed VLANs:", self.allowed_vlans_input)
        form.addRow("Native VLAN:", self.native_vlan_input)
        form.addRow("Description:", self.description_input)
        form.addRow(self.pruning_checkbox)
        form.addRow(self.stp_guard_checkbox)
        form.addRow("Encapsulation:", self.encapsulation_combo)
        form.addRow("Dynamic DTP:", self.dtp_mode_combo)
        form.addRow(self.nonegotiate_checkbox)
        form.addRow(self.portfast_checkbox)

        self.setLayout(form)

    # ------------------------------------------------------------------ #
    def _ensure_native_in_allowed(self):
        """Guarantee native VLAN is present at the end of the CSV list."""
        native = str(self.native_vlan_input.value())
        tokens = [t.strip() for t in self.allowed_vlans_input.text().split(",") if t.strip()]
        if native not in tokens:
            tokens.append(native)
            self.allowed_vlans_input.setText(",".join(tokens))

    # ------------------------------------------------------------------ #
    def load_from_instance(self, instance):
        """Populate widgets from an existing TrunkTemplate instance."""
        self.interfaces_input.setText(",".join(instance.interfaces))
        self.allowed_vlans_input.setText(",".join(str(v) for v in instance.allowed_vlans))
        self.native_vlan_input.setValue(instance.native_vlan)
        self.description_input.setText(instance.description or "")
        self.pruning_checkbox.setChecked(instance.pruning_enabled)
        self.stp_guard_checkbox.setChecked(instance.spanning_tree_guard_root)
        self.encapsulation_combo.setCurrentText(instance.encapsulation)
        self.dtp_mode_combo.setCurrentText(instance.dtp_mode or "--")
        self.nonegotiate_checkbox.setChecked(instance.nonegotiate)
        self.portfast_checkbox.setChecked(instance.spanning_tree_portfast)
