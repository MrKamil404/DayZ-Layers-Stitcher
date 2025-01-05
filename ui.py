import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QColorDialog, QGraphicsView, QGraphicsScene
from stitcher import ImageStitcherLogic
from helpers import select_color, validate_inputs

class ImageStitcher(QtWidgets.QWidget, ImageStitcherLogic):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("DayZ Layers Stitcher")
        self.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        layout.addWidget(QtWidgets.QLabel("Grid Size:"), 0, 0)
        self.grid_size_entry = QtWidgets.QLineEdit()
        self.grid_size_entry.setValidator(QtGui.QIntValidator(1, 43))
        self.grid_size_entry.setToolTip("Enter the grid size (1-43)")
        layout.addWidget(self.grid_size_entry, 0, 1)

        layout.addWidget(QtWidgets.QLabel("Trim Pixels:"), 1, 0)
        self.trim_pixels_entry = QtWidgets.QLineEdit()
        self.trim_pixels_entry.setValidator(QtGui.QIntValidator(0, 32))
        self.trim_pixels_entry.setToolTip("Enter the number of pixels to trim (0-32)")
        layout.addWidget(self.trim_pixels_entry, 1, 1)

        layout.addWidget(QtWidgets.QLabel("Prefix:"), 2, 0)
        self.prefix_var = QtWidgets.QComboBox()
        self.prefix_var.addItems(["s", "m", "n"])
        self.prefix_var.setToolTip("Select the prefix for the images")
        layout.addWidget(self.prefix_var, 2, 1)

        layout.addWidget(QtWidgets.QLabel("Background Color:"), 3, 0)
        self.color_var = QtWidgets.QLineEdit("#000000")
        self.color_button = QtWidgets.QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        self.color_button.setToolTip("Select the background color")
        layout.addWidget(self.color_button, 3, 1)
        layout.addWidget(self.color_var, 3, 2)

        layout.addWidget(QtWidgets.QLabel("Image Directory:"), 4, 0)
        self.image_directory_entry = QtWidgets.QLineEdit()
        self.browse_image_dir_button = QtWidgets.QPushButton("Browse")
        self.browse_image_dir_button.clicked.connect(self.select_image_directory)
        self.browse_image_dir_button.setToolTip("Select the directory containing the images")
        layout.addWidget(self.image_directory_entry, 4, 1)
        layout.addWidget(self.browse_image_dir_button, 4, 2)

        layout.addWidget(QtWidgets.QLabel("Output Path:"), 5, 0)
        self.output_path_entry = QtWidgets.QLineEdit()
        self.browse_output_button = QtWidgets.QPushButton("Browse")
        self.browse_output_button.clicked.connect(self.select_output_path)
        self.browse_output_button.setToolTip("Select the output path for the stitched image")
        layout.addWidget(self.output_path_entry, 5, 1)
        layout.addWidget(self.browse_output_button, 5, 2)

        layout.addWidget(QtWidgets.QLabel("Preview Tile Quality (px):"), 6, 0)
        self.preview_quality_entry = QtWidgets.QLineEdit("128")
        self.preview_quality_entry.setValidator(QtGui.QIntValidator(1, 4096))
        self.preview_quality_entry.setToolTip("Enter the preview quality in pixels (1-4096)")
        layout.addWidget(self.preview_quality_entry, 6, 1)

        self.preview_progress_bar = QtWidgets.QProgressBar()
        layout.addWidget(self.preview_progress_bar, 7, 0, 1, 3)

        self.stitching_progress_bar = QtWidgets.QProgressBar()
        layout.addWidget(self.stitching_progress_bar, 8, 0, 1, 3)

        self.console = QtWidgets.QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console, 9, 0, 1, 3)

        self.merge_button = QtWidgets.QPushButton("Merge")
        self.merge_button.clicked.connect(self.run_stitching)
        self.merge_button.setToolTip("Click to start stitching the images")
        layout.addWidget(self.merge_button, 10, 0, 1, 3)

        self.info_label = QtWidgets.QLabel("Use mouse wheel to zoom and click-drag to pan the preview.")
        self.info_label.setStyleSheet("color: blue;")
        layout.addWidget(self.info_label, 0, 3)

        self.reload_preview_button = QtWidgets.QPushButton("Reload preview")
        self.reload_preview_button.clicked.connect(self.reload_preview)
        self.reload_preview_button.setToolTip("Click to reload the preview")
        layout.addWidget(self.reload_preview_button, 1, 3)

        self.graphics_view = QGraphicsView()
        self.graphics_view.setFixedSize(512, 512)
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.graphics_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphics_view.viewport().installEventFilter(self)
        layout.addWidget(self.graphics_view, 2, 3, 12, 1)

        self.preview_info_label = QtWidgets.QLabel("Preview Image Size: N/A\nFull Image Size: N/A")
        layout.addWidget(self.preview_info_label, 11, 0, 1, 3)

        self.buy_me_coffee_button = QtWidgets.QPushButton("Buy Me A Coffee")
        self.buy_me_coffee_button.clicked.connect(self.open_buy_me_coffee)
        layout.addWidget(self.buy_me_coffee_button, 12, 0, 1, 1, alignment=QtCore.Qt.AlignLeft)

        self.help_button = QtWidgets.QPushButton("How to Use")
        self.help_button.clicked.connect(self.show_help)
        layout.addWidget(self.help_button, 12, 1, 1, 2, alignment=QtCore.Qt.AlignLeft)

        self.setLayout(layout)

    def open_buy_me_coffee(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://buymeacoffee.com/mrkamil404"))

    def show_help(self):
        help_message = (
            "How to Use DayZ Layers Stitcher:\n\n"
            "1. Prepare the PNG layer files. The file names should look like this: S/M/N_x_x_lco.\n"
            "2. Set Grid Size and Trim Pixels: Enter the grid size and the number of pixels to trim from each image.\n"
            "3. Select Prefix: Choose the prefix for the images to be stitched.\n"
            "4. Choose Background Color: Select a background color for the stitched image.\n"
            "5. Select Image Directory: Browse and select the directory containing the images to be stitched.\n"
            "6. Specify Output Path: Browse and specify the output path for the final stitched image.\n"
            "7. Set Preview Quality: Enter the desired quality for the preview image.\n"
            "8. Generate Preview: Click 'Reload preview' to generate and view a preview of the stitched image.\n"
            "9. Stitch Images: Click 'Merge' to start the stitching process and save the final image to the specified output path."
        )
        QMessageBox.information(self, "Help", help_message)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Wheel and source is self.graphics_view.viewport():
            if event.angleDelta().y() > 0:
                self.graphics_view.scale(1.25, 1.25)
            else:
                self.graphics_view.scale(0.8, 0.8)
            return True
        return super().eventFilter(source, event)

    def render_preview(self, image):
        self.graphics_scene.clear()
        qimage = QtGui.QImage(image.tobytes(), image.width, image.height, image.width * 3, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        self.graphics_scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.graphics_scene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)

    def update_preview_info(self, preview_image, full_image_size):
        preview_size = preview_image.size
        self.preview_info_label.setText(
            f"Preview Image Size: {preview_size[0]}x{preview_size[1]}\n"
            f"Full Image Size: {full_image_size[0]}x{full_image_size[1]}"
        )

    def select_image_directory(self):
        try:
            if not validate_inputs(self.grid_size_entry, self.trim_pixels_entry):
                raise ValueError("Fill in 'Grid Size' and 'Trim Pixels. Grid size cannot be greater than 43 and Trim pixels cannot be greater than 32")
            path = QFileDialog.getExistingDirectory(self, "Select Image Directory")
            if path:
                self.image_directory_entry.setText(path)
                self.reload_preview()
        except ValueError as ve:
            QMessageBox.critical(self, "Input Error", str(ve))
            self.update_console(f"Input Error: {ve}")

    def select_output_path(self):
        if not validate_inputs(self.grid_size_entry, self.trim_pixels_entry):
            QMessageBox.critical(self, "Input Error", "Fill in 'Grid Size' and 'Trim Pixels' before selecting an output path. Grid size cannot be greater than 43 and Trim pixels cannot be greater than 32.")
            self.update_console("Input Error: Fill in 'Grid Size' and 'Trim Pixels' before selecting an output path. Grid size cannot be greater than 43 and Trim pixels cannot be greater than 32.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Stitched Image As", "", "PNG files (*.png);;JPEG files (*.jpg);;All files (*.*)")
        if path:
            self.output_path_entry.setText(path)

    def select_color(self):
        select_color(self.color_var)

    def reload_preview(self):
        try:
            grid_size = int(self.grid_size_entry.text())
            trim_pixels = int(self.trim_pixels_entry.text())
            if grid_size > 43:
                raise ValueError("Grid size cannot be greater than 43.")
            if trim_pixels > 32:
                raise ValueError("Trim pixels cannot be greater than 32.")
            image_directory = self.image_directory_entry.text()
            prefix = self.prefix_var.currentText()
            background_color = self.color_var.text()
            if not image_directory:
                raise ValueError("Image directory not selected.")
            self.preview_images(image_directory, grid_size, trim_pixels, prefix, background_color)
        except ValueError as ve:
            QMessageBox.critical(self, "Input Error", str(ve))
            self.update_console(f"Input Error: {ve}")

    def update_console(self, message):
        self.console.append(message)
