import os
from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QColorDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

class ImageStitcher(QtWidgets.QWidget):
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
        self.grid_size_entry.setValidator(QtGui.QIntValidator(1, 42))
        layout.addWidget(self.grid_size_entry, 0, 1)

        layout.addWidget(QtWidgets.QLabel("Trim Pixels:"), 1, 0)
        self.trim_pixels_entry = QtWidgets.QLineEdit()
        self.trim_pixels_entry.setValidator(QtGui.QIntValidator(0, 32))
        layout.addWidget(self.trim_pixels_entry, 1, 1)

        layout.addWidget(QtWidgets.QLabel("Prefix:"), 2, 0)
        self.prefix_var = QtWidgets.QComboBox()
        self.prefix_var.addItems(["S", "M", "N"])
        layout.addWidget(self.prefix_var, 2, 1)

        layout.addWidget(QtWidgets.QLabel("Background Color:"), 3, 0)
        self.color_var = QtWidgets.QLineEdit("#000000")
        self.color_button = QtWidgets.QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        layout.addWidget(self.color_button, 3, 1)
        layout.addWidget(self.color_var, 3, 2)

        layout.addWidget(QtWidgets.QLabel("Image Directory:"), 4, 0)
        self.image_directory_entry = QtWidgets.QLineEdit()
        self.browse_image_dir_button = QtWidgets.QPushButton("Browse")
        self.browse_image_dir_button.clicked.connect(self.select_image_directory)
        layout.addWidget(self.image_directory_entry, 4, 1)
        layout.addWidget(self.browse_image_dir_button, 4, 2)

        layout.addWidget(QtWidgets.QLabel("Output Path:"), 5, 0)
        self.output_path_entry = QtWidgets.QLineEdit()
        self.browse_output_button = QtWidgets.QPushButton("Browse")
        self.browse_output_button.clicked.connect(self.select_output_path)
        layout.addWidget(self.output_path_entry, 5, 1)
        layout.addWidget(self.browse_output_button, 5, 2)

        layout.addWidget(QtWidgets.QLabel("Preview Quality (px):"), 6, 0)
        self.preview_quality_entry = QtWidgets.QLineEdit("128")
        self.preview_quality_entry.setValidator(QtGui.QIntValidator(1, 4096))
        layout.addWidget(self.preview_quality_entry, 6, 1)

        self.preview_progress_bar = QtWidgets.QProgressBar()
        layout.addWidget(self.preview_progress_bar, 7, 0, 1, 3)

        self.stitching_progress_bar = QtWidgets.QProgressBar()
        layout.addWidget(self.stitching_progress_bar, 8, 0, 1, 3)

        self.status_label = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status_label, 9, 0, 1, 3)

        self.merge_button = QtWidgets.QPushButton("Merge")
        self.merge_button.clicked.connect(self.run_stitching)
        layout.addWidget(self.merge_button, 10, 0, 1, 3)

        self.info_label = QtWidgets.QLabel("Use mouse wheel to zoom and click-drag to pan the preview.")
        self.info_label.setStyleSheet("color: blue;")
        layout.addWidget(self.info_label, 0, 3)

        self.reload_preview_button = QtWidgets.QPushButton("Reload preview")
        self.reload_preview_button.clicked.connect(self.reload_preview)
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

        self.preview_info_label = QtWidgets.QLabel("Preview Image Size: N/A\nFull Image Size: N/A\nEstimated File Size: N/A")
        layout.addWidget(self.preview_info_label, 11, 0, 1, 3)

        self.setLayout(layout)

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
        estimated_file_size = ((full_image_size[0] * full_image_size[1] * 3) / (1024 * 1024)) / 10  # in MB
        self.preview_info_label.setText(
            f"Preview Image Size: {preview_size[0]}x{preview_size[1]}\n"
            f"Full Image Size: {full_image_size[0]}x{full_image_size[1]}\n"
            f"Estimated File Size: {estimated_file_size:.2f} MB"
        )

    def main(self, grid_size, trim_pixels, image_directory, output_path, prefix, background_color):
        try:
            images = {}
            self.update_status("Loading image list...")
            self.stitching_progress_bar.setValue(0)
            self.stitching_progress_bar.setMaximum(grid_size * grid_size)
            QtWidgets.QApplication.processEvents()

            file_list = [f for f in os.listdir(image_directory) if f.startswith(prefix) and f.endswith(".png")]
            if not file_list:
                raise ValueError("No images found matching the specified prefix and extension in the directory.")

            for idx, filename in enumerate(file_list):
                self.update_status(f"Loading image {filename}...")
                self.stitching_progress_bar.setValue(idx + 1)
                QtWidgets.QApplication.processEvents()

                _, x_str, y_str, _ = filename.split('_')
                x = int(x_str)
                y = int(y_str)

                image_path = os.path.join(image_directory, filename)
                img = Image.open(image_path)
                width, height = img.size
                cropped_img = img.crop((trim_pixels, trim_pixels, width - trim_pixels, height - trim_pixels))
                images[(x, y)] = cropped_img

            sample_image = next(iter(images.values()))
            image_width, image_height = sample_image.size
            stitched_image = Image.new('RGB', (image_width * grid_size, image_height * grid_size), background_color)

            for x in range(grid_size):
                for y in range(grid_size):
                    if (x, y) in images:
                        self.update_status(f"Stitching image at position ({x}, {y})...")
                        stitched_image.paste(images[(x, y)], (x * image_width, y * image_height))
                    else:
                        self.update_status(f"Generating blank image at position ({x}, {y})...")

                    self.stitching_progress_bar.setValue(self.stitching_progress_bar.value() + 1)
                    QtWidgets.QApplication.processEvents()

            self.update_status("Process completed. Saving image...")

            stitched_image.save(output_path)
            self.update_status("Process completed. Image saved!")
            QMessageBox.information(self, "Success", f"Image saved as {output_path}!")
            print(f"Success: Image saved as {output_path}!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            print(f"Error: An error occurred: {e}")

    def run_stitching(self):
        try:
            grid_size = int(self.grid_size_entry.text())
            trim_pixels = int(self.trim_pixels_entry.text())

            if grid_size > 42:
                raise ValueError("Grid size cannot be greater than 42.")
            if trim_pixels > 32:
                raise ValueError("Trim pixels cannot be greater than 32.")

            image_directory = self.image_directory_entry.text()
            output_path = self.output_path_entry.text()
            prefix = self.prefix_var.currentText()
            background_color = self.color_var.text()

            if not image_directory or not output_path:
                raise ValueError("Image directory or output path is not specified.")
            
            self.main(grid_size, trim_pixels, image_directory, output_path, prefix, background_color)
        except ValueError as ve:
            QMessageBox.critical(self, "Input Error", str(ve))
            print(f"Input Error: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            print(f"Error: {e}")

    def select_output_path(self):
        if not self.validate_inputs():
            QMessageBox.critical(self, "Input Error", "Fill in 'Grid Size' and 'Trim Pixels' before selecting an output path. Grid size cannot be greater than 42 and Trim pixels cannot be greater than 32.")
            print("Input Error: Fill in 'Grid Size' and 'Trim Pixels' before selecting an output path. Grid size cannot be greater than 42 and Trim pixels cannot be greater than 32.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Stitched Image As", "", "PNG files (*.png);;JPEG files (*.jpg);;All files (*.*)")
        if path:
            self.output_path_entry.setText(path)

    def preview_images(self, image_directory, grid_size, trim_pixels, prefix, background_color):
        try:
            if grid_size > 42:
                raise ValueError("Grid size cannot be greater than 42.")
            if trim_pixels > 32:
                raise ValueError("Trim pixels cannot be greater than 32.")

            preview_quality = int(self.preview_quality_entry.text())
            images = {}
            self.preview_progress_bar.setValue(0)
            self.preview_progress_bar.setMaximum(len(os.listdir(image_directory)))
            QtWidgets.QApplication.processEvents()

            file_list = [f for f in os.listdir(image_directory) if f.startswith(prefix) and f.endswith(".png")]
            if not file_list:
                raise ValueError("No images found matching the specified prefix.")

            for idx, filename in enumerate(file_list):
                self.update_status(f"Loading preview for image {filename}...")
                self.preview_progress_bar.setValue(idx + 1)
                QtWidgets.QApplication.processEvents()

                _, x_str, y_str, _ = filename.split('_')
                x = int(x_str)
                y = int(y_str)

                image_path = os.path.join(image_directory, filename)
                img = Image.open(image_path)
                width, height = img.size
                cropped_img = img.crop((trim_pixels, trim_pixels, width - trim_pixels, height - trim_pixels))
                scaled_img = cropped_img.resize((preview_quality, preview_quality)) 
                images[(x, y)] = scaled_img

            preview_image = Image.new('RGB', (preview_quality * grid_size, preview_quality * grid_size), background_color)
            for x in range(grid_size):
                for y in range(grid_size):
                    if (x, y) in images:
                        preview_image.paste(images[(x, y)], (x * preview_quality, y * preview_quality))

            self.render_preview(preview_image)
            self.update_preview_info(preview_image, (width * grid_size, height * grid_size))
            self.update_status("Preview loaded.")
        except ValueError as ve:
            QMessageBox.critical(self, "Input Error", str(ve))
            print(f"Input Error: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading preview: {e}")
            print(f"Error: Error loading preview: {e}")

    def select_image_directory(self):
        try:
            if not self.validate_inputs():
                raise ValueError("Fill in 'Grid Size' and 'Trim Pixels. Grid size cannot be greater than 42 and Trim pixels cannot be greater than 32")
            path = QFileDialog.getExistingDirectory(self, "Select Image Directory")
            if path:
                self.image_directory_entry.setText(path)
                self.reload_preview()
        except ValueError as ve:
            QMessageBox.critical(self, "Input Error", str(ve))
            print(f"Input Error: {ve}")

    def reload_preview(self):
        try:
            grid_size = int(self.grid_size_entry.text())
            trim_pixels = int(self.trim_pixels_entry.text())
            if grid_size > 42:
                raise ValueError("Grid size cannot be greater than 42.")
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
            print(f"Input Error: {ve}")

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_var.setText(color.name())
            self.color_var.setStyleSheet(f"background-color: {color.name()};")

    def validate_inputs(self):
        try:
            grid_size = int(self.grid_size_entry.text())
            trim_pixels = int(self.trim_pixels_entry.text())
            if grid_size > 42 or trim_pixels > 32:
                return False
            return True
        except ValueError:
            return False

    def update_status(self, message):
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()
        print(message)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ex = ImageStitcher()
    ex.show()
    sys.exit(app.exec_())

