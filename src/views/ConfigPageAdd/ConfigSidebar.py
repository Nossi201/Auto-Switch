# src/views/ConfigPageAdd/ConfigSidebar.py
"""Sidebar panel for the configuration page.
Displays 'New Template' button and dynamically created radio buttons.
"""

from PySide6 import QtWidgets
from PySide6.QtCore import Signal

class ConfigSidebar(QtWidgets.QFrame):
    """Vertical toolbar docked on the left side of the Config page."""

    template_changed = Signal(str)  # Signal emitted when radio selection changes

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFixedWidth(120)
        self._parent_main = self._find_main_window()
        self._device_info = getattr(self._parent_main, "selected_device", {}) if self._parent_main else {}

        self._radio_buttons = {}  # Dictionary to keep track of radio buttons

        self._init_ui()

    def _find_main_window(self):
        """Traverse up to find the MainWindow."""
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, "goto_start"):
                return parent
            parent = parent.parent()
        return None

    def _init_ui(self) -> None:
        """Build widgets for the sidebar."""
        self.root = QtWidgets.QVBoxLayout(self)
        self.root.setContentsMargins(8, 8, 8, 8)
        self.root.setSpacing(10)

        self.new_template_btn = QtWidgets.QPushButton("New Template")
        self.new_template_btn.clicked.connect(self._on_new_template_clicked)
        self.root.addWidget(self.new_template_btn)

        device_type = self._device_info.get("device_type", "router").lower()

        self.radio_device = QtWidgets.QRadioButton("Device")
        self.radio_device.setChecked(True)
        self.radio_device.toggled.connect(lambda checked: self._on_radio_changed("device") if checked else None)
        self.root.addWidget(self.radio_device)
        self._radio_buttons = {"device": self.radio_device}

        if device_type == "switch":
            self.radio_vlan1 = QtWidgets.QRadioButton("VLAN 1")
            self.radio_vlan1.toggled.connect(lambda checked: self._on_radio_changed("vlan") if checked else None)
            self.root.addWidget(self.radio_vlan1)
            self._radio_buttons["vlan"] = self.radio_vlan1

        self.root.addStretch(1)

    def _on_radio_changed(self, selection: str):
        """Emit template_changed signal when radio button selection changes."""
        self.template_changed.emit(selection)

    def _on_new_template_clicked(self):
        """Handle 'New Template' button click."""
        if hasattr(self._parent_main.page.main_area, "show_new_template_area"):
            self._parent_main.page.main_area.show_new_template_area()

    def add_new_template_radio(self, name: str):
        """Add a new radio button for the newly created template."""
        radio = QtWidgets.QRadioButton(name)
        radio.toggled.connect(lambda checked, n=name: self._on_radio_changed(n) if checked else None)
        self.root.insertWidget(self.root.count() - 1, radio)  # Insert before the stretch
        self._radio_buttons[name] = radio

