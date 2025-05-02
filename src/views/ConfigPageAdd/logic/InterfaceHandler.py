#src/views/ConfigPageAdd/logic/InterfaceHandler.py
"""Handles interface-button clicks.

If the current view is *NewTemplateArea* we just append the clicked interface
to the inner form’s *Interfaces* field.  Otherwise we perform the normal
re-assignment via InterfaceAssignmentManager and refresh the active form.
"""

from PySide6.QtWidgets import QMessageBox

_NEW_TEMPLATE_CLASSNAME = "NewTemplateArea"   # sentinel to detect new-template mode


def _append_to_new_template(parent_widget, iface: str) -> bool:
    """Return *True* if running inside NewTemplateArea and iface appended."""
    creator = getattr(parent_widget, "current_form", None)
    if creator is None or creator.__class__.__name__ != _NEW_TEMPLATE_CLASSNAME:
        return False
    inner = getattr(creator, "current_form", None)
    if inner is None or not hasattr(inner, "interfaces_input"):
        return False

    tokens = [t.strip() for t in inner.interfaces_input.text().split(",") if t.strip()]
    if iface not in tokens:
        tokens.append(iface)
        inner.interfaces_input.setText(",".join(tokens))
        QMessageBox.information(parent_widget, "Dodano", f"Interfejs {iface} dodany do nowego szablonu.")
    return True


def reassign_interface(interface_manager,
                       iface: str,
                       current_template_type: str,
                       parent_widget):
    """Main dispatcher for interface button clicks."""
    # branch – NewTemplateArea
    if _append_to_new_template(parent_widget, iface):
        return

    # normal branch – update InterfaceAssignmentManager
    previous_template = interface_manager.get_template(iface)
    if current_template_type == previous_template:
        QMessageBox.information(
            parent_widget, "Info",
            f"Interface {iface} already belongs to template '{current_template_type}'."
        )
        return

    interface_manager.assign(iface, current_template_type)
    QMessageBox.information(
        parent_widget, "Zmieniono",
        f"Interface {iface}: {previous_template} ➜ {current_template_type}"
    )

    # force form refresh so the read-only Interfaces field updates
    if hasattr(parent_widget, "load_form_by_radio_choice"):
        parent_widget.load_form_by_radio_choice(current_template_type)
