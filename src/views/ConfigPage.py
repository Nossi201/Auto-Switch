"""Composite configuration page (ConfigSidebar + ConfigMainArea).
Acts as the second screen in the application flow.
"""

from PySide6 import QtWidgets

from src.views.ConfigPageAdd.ConfigSidebar import ConfigSidebar
from src.views.ConfigPageAdd.ConfigMainArea import ConfigMainArea

class ConfigPage(QtWidgets.QWidget):
    """High‑level container that combines sidebar and main area."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._parent_main = parent
        self._init_ui()

    def _init_ui(self) -> None:
        """Lay out sidebar and workspace."""
        root = QtWidgets.QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = ConfigSidebar(self)
        root.addWidget(self.sidebar)

        selected = getattr(self._parent_main, "selected_device", None)
        self.main_area = ConfigMainArea(self, selected)
        root.addWidget(self.main_area, 1)

        self.sidebar.template_changed.connect(self.main_area.load_form_by_radio_choice)

        # Load default form based on initially selected radio button
        self.main_area.load_form_by_radio_choice("device")

    def _reload_default_view(self) -> None:
        """Handle accepting a new template."""
        if not hasattr(self, "new_template_area"):
            return

        form_data = self.new_template_area.get_template_data()
        print("Accepted new template:", form_data)
        self._reload_default_view()