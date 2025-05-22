# 'src/views/StartPage.py'
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

        self._router_models, self._switch_l2_models, self._switch_l3_models = self._load_device_models()

        self.device_type: str = "router"
        self.selected_model: Dict[str, Any] | None = None

        self._init_ui()

    # ------------------------------ helpers --------------------------- #

    def _init_ui(self) -> None:
        """Create all widgets for the start page."""
        root = QtWidgets.QVBoxLayout(self)

        # Radio buttons for device type
        type_box = QtWidgets.QHBoxLayout()
        self.radio_router = QtWidgets.QRadioButton("Router")
        self.radio_switch_l2 = QtWidgets.QRadioButton("Switch L2")
        self.radio_switch_l3 = QtWidgets.QRadioButton("Switch L3")
        self.radio_router.setChecked(True)
        type_box.addWidget(self.radio_router)
        type_box.addWidget(self.radio_switch_l2)
        type_box.addWidget(self.radio_switch_l3)
        root.addLayout(type_box)

        # Connect signals for radio buttons
        self.radio_router.toggled.connect(lambda c: self._on_type_changed("router") if c else None)
        self.radio_switch_l2.toggled.connect(lambda c: self._on_type_changed("switch_l2") if c else None)
        self.radio_switch_l3.toggled.connect(lambda c: self._on_type_changed("switch_l3") if c else None)

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

    def _load_device_models(self) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Parse *cisco_devices.json* and return separated router/switch lists for L2 and L3."""
        try:
            data_path = (
                Path(ResourceManager.get_data_path("cisco_devices.json"))
                if ResourceManager and hasattr(ResourceManager, "get_data_path")
                else Path(__file__).parent / ".." / "data" / "cisco_devices.json"
            ).resolve()

            with data_path.open("r", encoding="utf-8") as fh:
                raw = json.load(fh)

            routers = [dict(name=n, **d) for n, d in raw.get("routers", {}).items()]

            # Segregate switches by type (L2 or L3)
            switches_l2 = []
            switches_l3 = []

            for name, data in raw.get("switches", {}).items():
                switch_data = dict(name=name, **data)
                if data.get("type") == "L3":
                    switches_l3.append(switch_data)
                else:
                    # Default to L2 if type is not specified or is L2
                    switches_l2.append(switch_data)

            return routers, switches_l2, switches_l3

        except FileNotFoundError:
            QtWidgets.QMessageBox.critical(self, "Error", "File 'cisco_devices.json' not found!")
            return [], [], []
        except json.JSONDecodeError:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid JSON in 'cisco_devices.json'!")
            return [], [], []

    # ---------------------- dynamic UI manipulation ------------------ #

    def _populate_model_buttons(self) -> None:
        """Refresh the list of models based on the selected device type."""
        # Remove previous buttons
        while (item := self._list_layout.takeAt(0)) and item.widget():
            item.widget().setParent(None)

        # Select correct models list based on device type
        if self.device_type == "router":
            models = self._router_models
        elif self.device_type == "switch_l2":
            models = self._switch_l2_models
        elif self.device_type == "switch_l3":
            models = self._switch_l3_models
        else:
            models = []

        # Create new button group
        self._model_button_group = QtWidgets.QButtonGroup(self)
        self._model_button_group.setExclusive(True)
        self._model_button_group.buttonClicked.connect(self._on_model_selected)

        # Add a radio button for each model
        for model in models:
            btn = QtWidgets.QRadioButton(model["name"])
            btn.setToolTip(f'{model["description"]}\nInterfaces: {", ".join(model["interfaces"])}')
            self._model_button_group.addButton(btn)
            self._list_layout.addWidget(btn)

        self.next_btn.setEnabled(False)

    # ---------------------------- handlers --------------------------- #

    def _on_type_changed(self, new_type: str) -> None:
        """Switch between router, switch L2, and switch L3 model lists."""
        if new_type != self.device_type:
            self.device_type = new_type
            self.selected_model = None
            self._populate_model_buttons()

    def _on_model_selected(self, btn: QtWidgets.QAbstractButton) -> None:  # noqa: D401
        """Store selection and enable the Next button."""
        # Select appropriate model list based on device type
        if self.device_type == "router":
            models = self._router_models
        elif self.device_type == "switch_l2":
            models = self._switch_l2_models
        elif self.device_type == "switch_l3":
            models = self._switch_l3_models
        else:
            models = []

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

        # Map internal device_type to the format expected by the rest of the application
        if self.device_type in ["switch_l2", "switch_l3"]:
            device_info["device_type"] = "switch"
            # Preserve the L2/L3 information
            device_info["switch_layer"] = "L2" if self.device_type == "switch_l2" else "L3"
        else:
            device_info["device_type"] = self.device_type

        setattr(main, "selected_device", device_info)

        # Navigate forward
        if hasattr(main, "goto_sc"):
            main.goto_sc()