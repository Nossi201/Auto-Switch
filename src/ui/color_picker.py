# 'src/ui/color_picker.py'
"""
Color picker component for the user interface.
Provides a simple color selection dropdown for templates.
"""

from PySide6 import QtWidgets, QtCore, QtGui


class ColorPicker(QtWidgets.QWidget):
    """
    Color picker component with dropdown color selection interface.
    """

    def __init__(self, parent=None):
        """
        Initialize the color picker component.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.current_color = QtGui.QColor("#4287f5")  # Default blue color
        self.mouse_down = False
        self._dropdown_visible = False  # Track dropdown state
        self.color_mode = "RGB"  # Initialize color mode

        # Create layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create main color button
        self.color_button = QtWidgets.QPushButton(self.current_color.name().upper())
        self.color_button.setFixedHeight(30)
        self.color_button.setMinimumWidth(200)
        self.color_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.color_button.clicked.connect(self.toggle_dropdown)
        self.layout.addWidget(self.color_button)

        # Create dropdown color picker
        self.dropdown = QtWidgets.QFrame()
        self.dropdown.setWindowFlags(QtCore.Qt.Popup)
        self.dropdown.closeEvent = self.on_dropdown_close

        dropdown_layout = QtWidgets.QVBoxLayout(self.dropdown)
        dropdown_layout.setContentsMargins(10, 10, 10, 10)
        dropdown_layout.setSpacing(10)

        # RGB / HEX inputs
        rgb_layout = QtWidgets.QHBoxLayout()
        rgb_layout.setSpacing(10)

        # Mode toggle button
        self.mode_button = QtWidgets.QPushButton()
        self.mode_button.setFixedSize(26, 26)
        self.mode_button.setIcon(QtGui.QIcon())
        self.mode_button.setIconSize(QtCore.QSize(16, 16))
        self.mode_button.clicked.connect(self.toggle_color_mode)
        rgb_layout.addWidget(self.mode_button)

        # RGB input container
        self.rgb_container = QtWidgets.QWidget()
        rgb_inputs_layout = QtWidgets.QHBoxLayout(self.rgb_container)
        rgb_inputs_layout.setContentsMargins(0, 0, 0, 0)
        rgb_inputs_layout.setSpacing(5)

        # R input
        r_layout = QtWidgets.QHBoxLayout()
        self.r_label = QtWidgets.QLabel("R:")
        self.r_input = QtWidgets.QSpinBox()
        self.r_input.setRange(0, 255)
        self.r_input.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.r_input.setFixedWidth(45)
        self.r_input.valueChanged.connect(self.update_from_rgb)
        r_layout.addWidget(self.r_label)
        r_layout.addWidget(self.r_input)
        rgb_inputs_layout.addLayout(r_layout)

        # G input
        g_layout = QtWidgets.QHBoxLayout()
        self.g_label = QtWidgets.QLabel("G:")
        self.g_input = QtWidgets.QSpinBox()
        self.g_input.setRange(0, 255)
        self.g_input.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.g_input.setFixedWidth(45)
        self.g_input.valueChanged.connect(self.update_from_rgb)
        g_layout.addWidget(self.g_label)
        g_layout.addWidget(self.g_input)
        rgb_inputs_layout.addLayout(g_layout)

        # B input
        b_layout = QtWidgets.QHBoxLayout()
        self.b_label = QtWidgets.QLabel("B:")
        self.b_input = QtWidgets.QSpinBox()
        self.b_input.setRange(0, 255)
        self.b_input.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.b_input.setFixedWidth(45)
        self.b_input.valueChanged.connect(self.update_from_rgb)
        b_layout.addWidget(self.b_label)
        b_layout.addWidget(self.b_input)
        rgb_inputs_layout.addLayout(b_layout)

        rgb_layout.addWidget(self.rgb_container)

        # HEX input
        hex_container = QtWidgets.QWidget()
        hex_layout = QtWidgets.QHBoxLayout(hex_container)
        hex_layout.setContentsMargins(0, 0, 0, 0)
        hex_layout.setSpacing(5)

        self.hex_label = QtWidgets.QLabel("HEX:")
        hex_layout.addWidget(self.hex_label)

        self.hex_input = QtWidgets.QLineEdit()
        self.hex_input.setFixedHeight(26)
        self.hex_input.setFixedWidth(80)
        self.hex_input.textChanged.connect(self.update_from_hex)
        hex_layout.addWidget(self.hex_input)

        # Initially hidden
        hex_container.setVisible(False)

        rgb_layout.addWidget(hex_container)
        self.hex_container = hex_container

        rgb_layout.addStretch(1)
        dropdown_layout.addLayout(rgb_layout)

        # Hue slider with color wheel
        hue_layout = QtWidgets.QHBoxLayout()

        # Current color indicator
        self.color_circle = QtWidgets.QLabel()
        self.color_circle.setFixedSize(30, 30)
        hue_layout.addWidget(self.color_circle)

        # Hue slider
        self.hue_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.hue_slider.setRange(0, 359)
        self.hue_slider.setFixedHeight(20)
        self.hue_slider.valueChanged.connect(self.queue_update)
        hue_layout.addWidget(self.hue_slider, 1)
        dropdown_layout.addLayout(hue_layout)

        # Color canvas
        self.color_canvas = QtWidgets.QLabel()
        self.color_canvas.setMinimumSize(200, 150)
        self.color_canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.color_canvas.setMouseTracking(True)
        self.color_canvas.setCursor(QtCore.Qt.CrossCursor)
        self.color_canvas.mousePressEvent = self.handle_canvas_click
        self.color_canvas.mouseMoveEvent = self.handle_canvas_move
        self.color_canvas.mouseReleaseEvent = self.handle_canvas_release
        dropdown_layout.addWidget(self.color_canvas, stretch=1)

        # Canvas cache for performance
        self.canvas_cache = {}

        # Delayed update timer
        self.update_timer = QtCore.QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.delayed_update_canvas)

        # Initialize color values and UI
        self.set_rgb_inputs_from_color(self.current_color)
        self.update_color_ui()

    def on_dropdown_close(self, event):
        """Handle dropdown close event"""
        self._dropdown_visible = False
        event.accept()

    def toggle_color_mode(self):
        """Toggle between RGB and HEX input modes"""
        if self.color_mode == "RGB":
            # Switch to HEX mode
            self.color_mode = "HEX"
            self.rgb_container.setVisible(False)
            self.hex_container.setVisible(True)
            self.hex_input.setText(self.current_color.name().upper())
        else:
            # Switch to RGB mode
            self.color_mode = "RGB"
            self.rgb_container.setVisible(True)
            self.hex_container.setVisible(False)

    def toggle_dropdown(self):
        """Toggle the color picker dropdown visibility"""
        if self._dropdown_visible:
            self.dropdown.hide()
            self._dropdown_visible = False
            return

        # Position the dropdown below the button
        pos = self.color_button.mapToGlobal(QtCore.QPoint(0, self.color_button.height()))
        self.dropdown.setFixedWidth(max(350, self.width()))
        self.dropdown.move(pos)
        self.dropdown.show()
        self._dropdown_visible = True
        self.delayed_update_canvas()

    def set_rgb_inputs_from_color(self, color):
        """
        Set RGB input values from a color object

        Args:
            color: QColor object
        """
        self.r_input.blockSignals(True)
        self.g_input.blockSignals(True)
        self.b_input.blockSignals(True)
        self.hex_input.blockSignals(True)

        self.r_input.setValue(color.red())
        self.g_input.setValue(color.green())
        self.b_input.setValue(color.blue())
        self.hex_input.setText(color.name().upper())

        self.r_input.blockSignals(False)
        self.g_input.blockSignals(False)
        self.b_input.blockSignals(False)
        self.hex_input.blockSignals(False)

    def update_from_rgb(self):
        """Update color from RGB input values"""
        r = self.r_input.value()
        g = self.g_input.value()
        b = self.b_input.value()
        self.current_color = QtGui.QColor(r, g, b)

        # Update HEX field without triggering signals
        self.hex_input.blockSignals(True)
        self.hex_input.setText(self.current_color.name().upper())
        self.hex_input.blockSignals(False)

        self.update_color_ui()
        self.queue_update()

    def update_from_hex(self):
        """Update color from HEX input value"""
        hex_value = self.hex_input.text()
        color = QtGui.QColor(hex_value)
        if color.isValid():
            self.current_color = color

            # Update RGB fields without triggering signals
            self.r_input.blockSignals(True)
            self.g_input.blockSignals(True)
            self.b_input.blockSignals(True)

            self.r_input.setValue(self.current_color.red())
            self.g_input.setValue(self.current_color.green())
            self.b_input.setValue(self.current_color.blue())

            self.r_input.blockSignals(False)
            self.g_input.blockSignals(False)
            self.b_input.blockSignals(False)

            self.update_color_ui()
            self.queue_update()

    def update_color_ui(self):
        """Update UI elements with current color"""
        hex_value = self.current_color.name()
        self.color_button.setText(hex_value.upper())

        # Set background color of button
        self.color_button.setStyleSheet(f"background-color: {hex_value};")

        # Update color indicator
        self.color_circle.setStyleSheet(f"""
            background-color: {hex_value};
            border: 1px solid #AAAAAA;
            border-radius: 15px;
        """)

    def queue_update(self):
        """Schedule a delayed canvas update"""
        self.update_timer.stop()
        self.update_timer.start(50)  # 50ms delay

    def delayed_update_canvas(self):
        """Update canvas after delay"""
        hue = self.hue_slider.value()

        # Limit cache size
        if len(self.canvas_cache) > 60:
            # Remove oldest entries
            keys_to_remove = list(self.canvas_cache.keys())[:-50]  # Keep 50 most recent
            for key in keys_to_remove:
                del self.canvas_cache[key]

        # Check cache before generating new image
        canvas_size = (self.color_canvas.width(), self.color_canvas.height())
        cache_key = (hue, canvas_size)

        if cache_key in self.canvas_cache:
            self.color_canvas.setPixmap(self.canvas_cache[cache_key])
            return

        # Generate new image and store in cache
        pixmap = self.generate_color_canvas(hue)
        self.canvas_cache[cache_key] = pixmap
        self.color_canvas.setPixmap(pixmap)

    def generate_color_canvas(self, hue):
        """
        Generate color selection canvas for the given hue

        Args:
            hue: Hue value (0-359)

        Returns:
            QPixmap: Generated color canvas
        """
        canvas_width = self.color_canvas.width()
        canvas_height = self.color_canvas.height()
        pixmap = QtGui.QPixmap(canvas_width, canvas_height)

        # Use gradients for better performance
        painter = QtGui.QPainter(pixmap)

        # Saturation gradient (horizontal)
        sat_gradient = QtGui.QLinearGradient(0, 0, canvas_width, 0)
        sat_gradient.setColorAt(0, QtGui.QColor.fromHsvF(hue / 360.0, 0, 1))
        sat_gradient.setColorAt(1, QtGui.QColor.fromHsvF(hue / 360.0, 1, 1))

        # Fill background with saturation gradient
        painter.fillRect(0, 0, canvas_width, canvas_height, sat_gradient)

        # Value gradient (vertical)
        val_gradient = QtGui.QLinearGradient(0, 0, 0, canvas_height)
        val_gradient.setColorAt(0, QtGui.QColor(255, 255, 255, 0))  # Transparent white
        val_gradient.setColorAt(1, QtGui.QColor(0, 0, 0, 255))  # Opaque black

        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Multiply)
        painter.fillRect(0, 0, canvas_width, canvas_height, val_gradient)

        painter.end()
        return pixmap

    def handle_canvas_click(self, event):
        """Handle mouse click on color canvas"""
        self.mouse_down = True
        self.pick_color_from_canvas(event.pos())

    def handle_canvas_release(self, event):
        """Handle mouse release on color canvas"""
        self.mouse_down = False

    def handle_canvas_move(self, event):
        """Handle mouse move on color canvas"""
        if self.mouse_down:
            self.pick_color_from_canvas(event.pos())

    def pick_color_from_canvas(self, pos):
        """
        Pick color from position on canvas

        Args:
            pos: Position to pick color from
        """
        x = pos.x()
        y = pos.y()
        width = self.color_canvas.width()
        height = self.color_canvas.height()

        # Constrain to canvas bounds
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))

        # Calculate HSV values
        s = x / (width - 1)
        v = 1 - y / (height - 1)
        h = self.hue_slider.value() / 360.0

        # Create color from HSV
        color = QtGui.QColor()
        color.setHsvF(h, s, v)
        self.current_color = color

        # Update inputs and UI
        self.set_rgb_inputs_from_color(color)
        self.update_color_ui()

    def get_value(self):
        """
        Get the current color as HEX value

        Returns:
            str: HEX color value
        """
        return self.current_color.name()