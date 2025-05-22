# 'src/views/MainWindow.py'
"""
Main window – swaps pages by replacing the central widget
"""
from PySide6.QtWidgets import QMainWindow, QSizePolicy

from src.views.StartPage import StartPage
from src.views.ConfigPage import ConfigPage


class MainWindow(QMainWindow):
    """Main window that can switch pages by resetting centralWidget()."""

    # ------------------------------------------------------------------ #

    def __init__(self) -> None:  # noqa: D401
        super().__init__()

        # Meta‑settings
        self.setWindowTitle("Network Device Configuration Tool")
        self.resize(800, 600)
        self.setMinimumSize(480, 600)

        # Selected device information – filled by StartPage → Next
        self.selected_device = None  # will hold a dict with model data
        self.previous_device_type = None  # Track previous device type to detect changes

        # Cache of page instances to avoid recreation cost
        self._pages: dict[type, object] = {}

        # Show first page
        self.page = self._get_or_create(StartPage)
        self.setCentralWidget(self.page)

    # -------------------------- navigation API ------------------------ #

    def goto_start(self) -> None:
        """Switch UI to the landing StartPage."""
        self._switch_to(StartPage)

    def goto_sc(self) -> None:
        """Switch UI to the configuration page (ConfigPage)."""
        if ConfigPage is not None:
            # Check if device type changed since last configuration
            current_device_type = self._get_current_device_type()
            if self.previous_device_type != current_device_type:
                # Remove cached ConfigPage if device type changed
                if ConfigPage in self._pages:
                    del self._pages[ConfigPage]
                # Store new device type
                self.previous_device_type = current_device_type

            self._switch_to(ConfigPage)

    # ---------------------------- internals --------------------------- #

    def _get_current_device_type(self) -> str:
        """Get the current device type + layer combination as a unique identifier."""
        if not self.selected_device:
            return "unknown"

        device_type = self.selected_device.get("device_type", "unknown")
        if device_type == "switch":
            # Include the switch layer in the type for differentiation
            switch_layer = self.selected_device.get("switch_layer", "L2")
            return f"{device_type}_{switch_layer}"
        return device_type

    def _get_or_create(self, page_cls):
        """Return existing instance of *page_cls* or construct it."""
        if page_cls not in self._pages:
            widget = page_cls(self)  # parent is MainWindow
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self._pages[page_cls] = widget
        return self._pages[page_cls]

    def _switch_to(self, page_cls):
        """Detach the current central widget and replace it with *page_cls*."""
        new_page = self._get_or_create(page_cls)

        # Only detach if different widget; keep instance alive for caching
        old_page = self.centralWidget()
        if old_page is not None and old_page is not new_page:
            old_page.setParent(None)

        self.page = new_page
        self.setCentralWidget(new_page)