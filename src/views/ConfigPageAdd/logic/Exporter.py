#src/views/ConfigPageAdd/logic/Exporter.py
"""Handles export of current form data to external file formats."""

from PySide6.QtWidgets import QMessageBox

def export_template(instance, parent_widget):
    """Placeholder for export functionality."""
    QMessageBox.information(parent_widget, "Eksport", "Funkcja eksportu nie została jeszcze zaimplementowana.")
    print("[DEBUG] Export requested for instance:")
    print(instance)
