#src/forms/AccessTemplateForm.py
"""PySide6 form for AccessTemplate.

The Interfaces field can now be either editable (typing allowed) or read-only
(button-only) – controlled by *editable_interfaces* argument in the ctor.
"""

from PySide6 import QtWidgets


class AccessTemplateForm(QtWidgets.QWidget):
    """Form for filling AccessTemplate data."""

    def __init__(self, parent=None, instance=None, *, editable_interfaces=False):
        """
        *editable_interfaces* – if True, user may type interface names directly
        (used in *NewTemplateArea*); otherwise the field is read-only and updated
        exclusively by interface-grid buttons.
        """
        super().__init__(parent)
        self._editable_interfaces = editable_interfaces
        self._init_ui()
        if instance:
            self.load_from_instance(instance)

    # ------------------------------------------------------------------ #
    def _init_ui(self):
        """Create widgets and layout."""
        layout = QtWidgets.QFormLayout(self)

        # Interfaces
        self.interfaces_input = QtWidgets.QLineEdit()
        self.interfaces_input.setReadOnly(not self._editable_interfaces)

        # VLAN
        self.vlan_id_input = QtWidgets.QSpinBox()
        self.vlan_id_input.setRange(1, 4094)

        # Description
        self.description_input = QtWidgets.QLineEdit()

        # Port-Security
        self.port_security_checkbox = QtWidgets.QCheckBox("Enable Port-Security")
        self.max_mac_input = QtWidgets.QSpinBox()
        self.max_mac_input.setRange(1, 64)
        self.violation_action_combo = QtWidgets.QComboBox()
        self.violation_action_combo.addItems(["shutdown", "restrict", "protect"])
        self.sticky_mac_checkbox = QtWidgets.QCheckBox("Sticky MAC")

        # Storm-Control
        self.storm_control_checkbox = QtWidgets.QCheckBox("Enable Storm-Control")
        self.broadcast_min_input = QtWidgets.QDoubleSpinBox()
        self.broadcast_max_input = QtWidgets.QDoubleSpinBox()
        self.multicast_min_input = QtWidgets.QDoubleSpinBox()
        self.multicast_max_input = QtWidgets.QDoubleSpinBox()

        # PortFast
        self.portfast_checkbox = QtWidgets.QCheckBox("Enable Spanning-tree PortFast")

        # Voice-VLAN
        self.voice_vlan_input = QtWidgets.QSpinBox()
        self.voice_vlan_input.setRange(0, 4094)

        # ------- layout -------
        layout.addRow("Interfaces:", self.interfaces_input)
        layout.addRow("VLAN ID:", self.vlan_id_input)
        layout.addRow("Description:", self.description_input)

        layout.addRow(self.port_security_checkbox)
        layout.addRow("Max MACs:", self.max_mac_input)
        layout.addRow("Violation:", self.violation_action_combo)
        layout.addRow(self.sticky_mac_checkbox)
        layout.addRow("Voice VLAN (0 = off):", self.voice_vlan_input)

        layout.addRow(self.storm_control_checkbox)
        layout.addRow("Broadcast Min %", self.broadcast_min_input)
        layout.addRow("Broadcast Max %", self.broadcast_max_input)
        layout.addRow("Multicast Min %", self.multicast_min_input)
        layout.addRow("Multicast Max %", self.multicast_max_input)

        layout.addRow(self.portfast_checkbox)

        self.setLayout(layout)

        # Enable/disable nested fields
        self.port_security_checkbox.toggled.connect(self._toggle_port_security_fields)
        self.storm_control_checkbox.toggled.connect(self._toggle_storm_control_fields)
        self._toggle_port_security_fields()
        self._toggle_storm_control_fields()

    # ------------------------------------------------------------------ #
    def _toggle_port_security_fields(self):
        state = self.port_security_checkbox.isChecked()
        for w in (self.max_mac_input, self.violation_action_combo, self.sticky_mac_checkbox):
            w.setEnabled(state)

    # ------------------------------------------------------------------ #
    def _toggle_storm_control_fields(self):
        state = self.storm_control_checkbox.isChecked()
        for w in (
            self.broadcast_min_input,
            self.broadcast_max_input,
            self.multicast_min_input,
            self.multicast_max_input,
        ):
            w.setEnabled(state)

    # ------------------------------------------------------------------ #
    def load_from_instance(self, instance):
        """Populate widgets from AccessTemplate instance."""
        self.interfaces_input.setText(",".join(instance.interfaces))
        self.vlan_id_input.setValue(instance.vlan_id)
        self.description_input.setText(instance.description or "")
        self.port_security_checkbox.setChecked(instance.port_security_enabled)
        self.max_mac_input.setValue(instance.max_mac_addresses)
        self.violation_action_combo.setCurrentText(instance.violation_action)
        self.sticky_mac_checkbox.setChecked(instance.sticky_mac)
        self.voice_vlan_input.setValue(instance.voice_vlan or 0)

        self.storm_control_checkbox.setChecked(
            any(
                [
                    instance.storm_control_broadcast_min,
                    instance.storm_control_broadcast_max,
                    instance.storm_control_multicast_min,
                    instance.storm_control_multicast_max,
                ]
            )
        )
        self.broadcast_min_input.setValue(instance.storm_control_broadcast_min or 0.0)
        self.broadcast_max_input.setValue(instance.storm_control_broadcast_max or 0.0)
        self.multicast_min_input.setValue(instance.storm_control_multicast_min or 0.0)
        self.multicast_max_input.setValue(instance.storm_control_multicast_max or 0.0)
        self.portfast_checkbox.setChecked(instance.spanning_tree_portfast)
