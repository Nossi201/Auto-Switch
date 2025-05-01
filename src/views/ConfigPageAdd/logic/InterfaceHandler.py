#src/views/ConfigPageAdd/logic/InterfaceHandler.py
"""Handles interface assignment logic."""

from PySide6.QtWidgets import QMessageBox

def reassign_interface(interface_manager, iface: str, current_template_type: str, parent_widget):
    """Reassign interface to the selected template if necessary."""
    previous_template = interface_manager.get_template(iface)

    if current_template_type == previous_template:
        QMessageBox.information(parent_widget, "Info", f"Interface {iface} is already assigned to {current_template_type}.")
        return

    interface_manager.assign(iface, current_template_type)
    QMessageBox.information(parent_widget, "Updated", f"Interface {iface} reassigned from {previous_template} to {current_template_type}.")
    print(f"[DEBUG] Interface {iface} reassigned from {previous_template} to {current_template_type}")
