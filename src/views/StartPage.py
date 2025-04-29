'src/views/StartPage.py'
"""Landing page – lets the user select a device and proceed to configuration."""

import json
from pathlib import Path
from typing import List, Dict, Any

from PySide6 import QtWidgets

from src.utils import ResourceManager

class StartPage(QtWidgets.QWidget):
    """First page of the app – choose router/switch model, then go next."""

    # ------------------------------------------------------------------ #

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:  # noqa: D401
        super().__init__(parent)

        self._router_models, self._switch_models = self._load_device_models()

        self.device_type: str = "router"
        self.selected_model: Dict[str, Any] | None = None

        self._init_ui()

    # ------------------------------ helpers --------------------------- #

    def _init_ui(self) -> None:
        """Create all widgets for the start page."""
        root = QtWidgets.QVBoxLayout(self)

        # Radio buttons
        type_box = QtWidgets.QHBoxLayout()
        self.radio_router = QtWidgets.QRadioButton("Router")
        self.radio_switch = QtWidgets.QRadioButton("Switch")
        self.radio_router.setChecked(True)
        type_box.addWidget(self.radio_router)
        type_box.addWidget(self.radio_switch)
        root.addLayout(type_box)

        self.radio_router.toggled.connect(lambda c: self._on_type_changed("router") if c else None)
        self.radio_switch.toggled.connect(lambda c: self._on_type_changed("switch") if c else None)

        # List of device models
        list_container = QtWidgets.QWidget()
        self._list_layout = QtWidgets.QVBoxLayout(list_container)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(list_container)
        root.addWidget(scroll, 1)

        self._model_button_group = QtWidgets.QButtonGroup(self)
        self._model_button_group.buttonClicked.connect(self._on_model_selected)

        # Next button
        self.next_btn = QtWidgets.QPushButton("Dalej →")
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self._on_next_clicked)
        root.addWidget(self.next_btn)

        # Populate model buttons (MUST be AFTER creating next_btn)
        self._populate_model_buttons()

    # -------------------------- data loading -------------------------- #

    def _load_device_models(self) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Parse *cisco_devices.json* and return separated router/switch lists."""
        try:
            data_path = (
                Path(ResourceManager.get_data_path("cisco_devices.json"))
                if ResourceManager and hasattr(ResourceManager, "get_data_path")
                else Path(__file__).parent / ".." / "data" / "cisco_devices.json"
            ).resolve()

            with data_path.open("r", encoding="utf-8") as fh:
                raw = json.load(fh)

            routers = [dict(name=n, **d) for n, d in raw.get("routers", {}).items()]
            switches = [dict(name=n, **d) for n, d in raw.get("switches", {}).items()]
            return routers, switches

        except FileNotFoundError:
            QtWidgets.QMessageBox.critical(self, "Error", "File 'cisco_devices.json' not found!")
            return [], []
        except json.JSONDecodeError:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid JSON in 'cisco_devices.json'!")
            return [], []

    # ---------------------- dynamic UI manipulation ------------------ #

    def _populate_model_buttons(self) -> None:
        """Refresh the list of models based on the selected device type."""
        # Remove previous buttons
        while (item := self._list_layout.takeAt(0)) and item.widget():
            item.widget().setParent(None)

        models = self._router_models if self.device_type == "router" else self._switch_models
        self._model_button_group = QtWidgets.QButtonGroup(self)
        self._model_button_group.setExclusive(True)
        self._model_button_group.buttonClicked.connect(self._on_model_selected)  # <-- DODAJ TO

        for model in models:
            btn = QtWidgets.QRadioButton(model["name"])
            btn.setToolTip(f'{model["description"]}\nInterfaces: {", ".join(model["interfaces"])}')
            self._model_button_group.addButton(btn)
            self._list_layout.addWidget(btn)

        self.next_btn.setEnabled(False)

    # ---------------------------- handlers --------------------------- #

    def _on_type_changed(self, new_type: str) -> None:
        """Switch between router and switch model lists."""
        if new_type != self.device_type:
            self.device_type = new_type
            self.selected_model = None
            self._populate_model_buttons()

    def _on_model_selected(self, btn: QtWidgets.QAbstractButton) -> None:  # noqa: D401
        """Store selection and enable the Next button."""
        models = self._router_models if self.device_type == "router" else self._switch_models
        self.selected_model = next((m for m in models if m["name"] == btn.text()), None)
        self.next_btn.setEnabled(self.selected_model is not None)

    def _on_next_clicked(self) -> None:
        """Persist the selection on MainWindow and go to the config page."""
        if self.selected_model is None:
            QtWidgets.QMessageBox.warning(self, "Brak wyboru", "Najpierw wybierz model urządzenia!")
            return

        # Store selection on the MainWindow instance
        main = self.window()
        device_info = dict(self.selected_model)
        device_info["device_type"] = self.device_type
        setattr(main, "selected_device", device_info)
        # Navigate forward
        if hasattr(main, "goto_sc"):
            main.goto_sc()