import os
import subprocess
import shutil
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QColorDialog, QGraphicsView, QGraphicsScene
from stitcher import ImageStitcherLogic
from helpers import select_color, validate_inputs

class ImageStitcher(QtWidgets.QWidget, ImageStitcherLogic):
    def __init__(self):
        super().__init__()
        self.imagetopaa_path = ""
        self.temp_dir = os.path.join(os.getcwd(), "temp")
        self.cache_file = os.path.join(self.temp_dir, "cache_info.json")
        self.current_paa_cache = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("DayZ Layers Stitcher 1.1")
        self.setMinimumSize(1270, 870)
        self.resize(1270, 870)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(2)

        left_panel = QtWidgets.QVBoxLayout()
        left_widget = QtWidgets.QWidget()
        left_widget.setMaximumWidth(300)
        left_widget.setMinimumWidth(300)
        left_widget.setLayout(left_panel)

        basic_group = QtWidgets.QGroupBox("Basic Settings")
        basic_layout = QtWidgets.QGridLayout()
        basic_layout.setSpacing(2)

        basic_layout.addWidget(QtWidgets.QLabel("Grid Size:"), 0, 0)
        self.grid_size_entry = QtWidgets.QLineEdit()
        self.grid_size_entry.setValidator(QtGui.QIntValidator(1, 128))
        self.grid_size_entry.setToolTip("Enter the grid size (1-128)")
        basic_layout.addWidget(self.grid_size_entry, 0, 1)

        basic_layout.addWidget(QtWidgets.QLabel("Trim Pixels:"), 1, 0)
        self.trim_pixels_entry = QtWidgets.QLineEdit()
        self.trim_pixels_entry.setValidator(QtGui.QIntValidator(0, 32))
        self.trim_pixels_entry.setToolTip("Enter the number of pixels to trim (0-32)")
        basic_layout.addWidget(self.trim_pixels_entry, 1, 1)

        basic_layout.addWidget(QtWidgets.QLabel("Prefix:"), 2, 0)
        self.prefix_var = QtWidgets.QComboBox()
        self.prefix_var.addItems(["S", "s", "M", "m", "N", "n"])
        self.prefix_var.setToolTip("Select the prefix for the images")
        basic_layout.addWidget(self.prefix_var, 2, 1)

        basic_layout.addWidget(QtWidgets.QLabel("Background Color:"), 3, 0)
        color_layout = QtWidgets.QHBoxLayout()
        self.color_var = QtWidgets.QLineEdit("#000000")
        self.color_button = QtWidgets.QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        self.color_button.setToolTip("Select the background color")
        color_layout.addWidget(self.color_var)
        color_layout.addWidget(self.color_button)
        color_widget = QtWidgets.QWidget()
        color_widget.setLayout(color_layout)
        basic_layout.addWidget(color_widget, 3, 1)

        basic_group.setLayout(basic_layout)
        left_panel.addWidget(basic_group)

        workers_group = QtWidgets.QGroupBox("Processing Settings")
        workers_layout = QtWidgets.QGridLayout()
        workers_layout.setSpacing(2)

        workers_layout.addWidget(QtWidgets.QLabel("Workers:"), 0, 0)
        self.workers_entry = QtWidgets.QLineEdit("4")
        self.workers_entry.setValidator(QtGui.QIntValidator(1, 64))
        self.workers_entry.setToolTip("Enter the number of workers for parallel processing (1-64)")
        workers_layout.addWidget(self.workers_entry, 0, 1)

        workers_group.setLayout(workers_layout)
        left_panel.addWidget(workers_group)

        paths_group = QtWidgets.QGroupBox("File Paths")
        paths_layout = QtWidgets.QVBoxLayout()
        paths_layout.setSpacing(10)

        imagetopaa_layout = QtWidgets.QVBoxLayout()
        imagetopaa_layout.addWidget(QtWidgets.QLabel("ImageToPAA Path (optional):"))
        self.imagetopaa_path_entry = QtWidgets.QLineEdit()
        self.imagetopaa_path_entry.setPlaceholderText("Select ImageToPAA.exe from DayZTools...")
        imagetopaa_layout.addWidget(self.imagetopaa_path_entry)
        self.browse_imagetopaa_button = QtWidgets.QPushButton("Browse ImageToPAA.exe")
        self.browse_imagetopaa_button.clicked.connect(self.select_imagetopaa_path)
        self.browse_imagetopaa_button.setToolTip("Select the path to ImageToPAA.exe from DayZTools")
        imagetopaa_layout.addWidget(self.browse_imagetopaa_button)
        paths_layout.addLayout(imagetopaa_layout)

        image_dir_layout = QtWidgets.QVBoxLayout()
        image_dir_layout.addWidget(QtWidgets.QLabel("Image Directory:"))
        self.image_directory_entry = QtWidgets.QLineEdit()
        self.image_directory_entry.setPlaceholderText("Select directory with images...")
        image_dir_layout.addWidget(self.image_directory_entry)
        self.browse_image_dir_button = QtWidgets.QPushButton("Browse Image Directory")
        self.browse_image_dir_button.clicked.connect(self.select_image_directory)
        self.browse_image_dir_button.setToolTip("Select the directory containing the images")
        image_dir_layout.addWidget(self.browse_image_dir_button)
        paths_layout.addLayout(image_dir_layout)

        output_layout = QtWidgets.QVBoxLayout()
        output_layout.addWidget(QtWidgets.QLabel("Output Path:"))
        self.output_path_entry = QtWidgets.QLineEdit()
        self.output_path_entry.setPlaceholderText("Select output file location...")
        output_layout.addWidget(self.output_path_entry)
        self.browse_output_button = QtWidgets.QPushButton("Browse Output Location")
        self.browse_output_button.clicked.connect(self.select_output_path)
        self.browse_output_button.setToolTip("Select the output path for the stitched image")
        output_layout.addWidget(self.browse_output_button)
        paths_layout.addLayout(output_layout)

        paths_group.setLayout(paths_layout)
        left_panel.addWidget(paths_group)

        preview_group = QtWidgets.QGroupBox("Preview Settings")
        preview_layout = QtWidgets.QVBoxLayout()
        preview_layout.setSpacing(8)

        quality_layout = QtWidgets.QHBoxLayout()
        quality_layout.addWidget(QtWidgets.QLabel("Tile Quality (px):"))
        self.preview_quality_entry = QtWidgets.QLineEdit("128")
        self.preview_quality_entry.setValidator(QtGui.QIntValidator(1, 4096))
        self.preview_quality_entry.setToolTip("Enter the preview quality in pixels (1-4096)")
        quality_layout.addWidget(self.preview_quality_entry)
        preview_layout.addLayout(quality_layout)

        self.reload_preview_button = QtWidgets.QPushButton("Reload Preview")
        self.reload_preview_button.clicked.connect(self.reload_preview)
        self.reload_preview_button.setToolTip("Click to reload the preview")
        preview_layout.addWidget(self.reload_preview_button)

        preview_group.setLayout(preview_layout)
        left_panel.addWidget(preview_group)

        actions_group = QtWidgets.QGroupBox("Progress & Actions")
        actions_layout = QtWidgets.QVBoxLayout()
        actions_layout.setSpacing(8)

        actions_layout.addWidget(QtWidgets.QLabel("Preview Progress:"))
        self.preview_progress_bar = QtWidgets.QProgressBar()
        self.preview_progress_bar.setAlignment(QtCore.Qt.AlignCenter) 
        actions_layout.addWidget(self.preview_progress_bar)

        actions_layout.addWidget(QtWidgets.QLabel("Stitching Progress:"))
        self.stitching_progress_bar = QtWidgets.QProgressBar()
        self.stitching_progress_bar.setAlignment(QtCore.Qt.AlignCenter) 
        actions_layout.addWidget(self.stitching_progress_bar)

        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 3px;")
        actions_layout.addWidget(self.status_label)

        self.merge_button = QtWidgets.QPushButton("Merge Images")
        self.merge_button.clicked.connect(self.run_stitching)
        self.merge_button.setToolTip("Click to start stitching the images")
        actions_layout.addWidget(self.merge_button)

        actions_group.setLayout(actions_layout)
        left_panel.addWidget(actions_group)

        tools_group = QtWidgets.QGroupBox("Tools")
        tools_layout = QtWidgets.QHBoxLayout()

        self.clear_cache_button = QtWidgets.QPushButton("Clear Cache")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        self.clear_cache_button.setToolTip("Clear converted PAA files cache")
        tools_layout.addWidget(self.clear_cache_button)

        self.help_button = QtWidgets.QPushButton("How to Use")
        self.help_button.clicked.connect(self.show_help)
        tools_layout.addWidget(self.help_button)

        self.buy_me_coffee_button = QtWidgets.QPushButton("Buy Me A Coffee")
        self.buy_me_coffee_button.clicked.connect(self.open_buy_me_coffee)
        self.buy_me_coffee_button.setStyleSheet("QPushButton { background-color: #FF6B35; color: white; } QPushButton:hover { background-color: #E55A2B; }")
        tools_layout.addWidget(self.buy_me_coffee_button)

        tools_group.setLayout(tools_layout)
        left_panel.addWidget(tools_group)

        left_panel.addStretch()
        main_layout.addWidget(left_widget, 0)

        right_panel = QtWidgets.QVBoxLayout()
        right_widget = QtWidgets.QWidget()
        right_widget.setLayout(right_panel)

        preview_display_group = QtWidgets.QGroupBox("Image Preview")
        preview_display_layout = QtWidgets.QVBoxLayout()

        self.info_label = QtWidgets.QLabel("Use mouse wheel to zoom and click-drag to pan the preview.")
        self.info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        self.info_label.setFixedHeight(26)
        preview_display_layout.addWidget(self.info_label)

        self.graphics_view = QGraphicsView()
        self.graphics_view.setMinimumSize(400, 710)
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.graphics_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphics_view.viewport().installEventFilter(self)
        preview_display_layout.addWidget(self.graphics_view)

        self.preview_info_label = QtWidgets.QLabel("Preview Image Size: N/A\nFull Image Size: N/A")
        self.preview_info_label.setStyleSheet("background-color: #f9f9f9; padding: 8px; border: 1px solid #ddd; border-radius: 3px;")
        self.preview_info_label.setFixedHeight(48)
        preview_display_layout.addWidget(self.preview_info_label)

        preview_display_group.setLayout(preview_display_layout)
        right_panel.addWidget(preview_display_group)

        main_layout.addWidget(right_widget, 1)
        self.setLayout(main_layout)

    def open_buy_me_coffee(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://buymeacoffee.com/mrkamil404"))

    def show_help(self):
        help_message = (
            "How to Use DayZ Layers Stitcher:\n\n"
            "1. Prepare the PNG or PAA layer files. The file names should look like this: S/M/N_x_x_lco.\n"
            "2. Set Grid Size and Trim Pixels: Enter the grid size and the number of pixels to trim from each image.\n"
            "3. Select Prefix: Choose the prefix for the images to be stitched.\n"
            "4. Choose Background Color: Select a background color for the stitched image.\n"
            "5. Set Workers: Choose the number of workers (1-64) for parallel processing. More workers = faster conversion but more CPU usage.\n"
            "6. (Optional) Set ImageToPAA Path: If you have .paa files, select the path to ImageToPAA.exe from DayZTools.\n"
            "7. Select Image Directory: Browse and select the directory containing the images to be stitched.\n"
            "8. Specify Output Path: Browse and specify the output path for the final stitched image.\n"
            "9. Set Preview Quality: Enter the desired quality for the preview image.\n"
            "10. Generate Preview: Click 'Reload preview' to generate and view a preview of the stitched image.\n"
            "11. Stitch Images: Click 'Merge' to start the stitching process and save the final image to the specified output path.\n\n"
            "Note: PAA files will be automatically converted to PNG using ImageToPAA and stored in a temporary folder during processing."
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
        self.clear_cache() 
        try:
            if not validate_inputs(self.grid_size_entry, self.trim_pixels_entry):
                raise ValueError("Fill in 'Grid Size' and 'Trim Pixels. Grid size cannot be greater than 128 and Trim pixels cannot be greater than 32")
            path = QFileDialog.getExistingDirectory(self, "Select Image Directory")
            if path:
                previous_dir = self.image_directory_entry.text()
                self.image_directory_entry.setText(path)
                
                if path != previous_dir:
                    self.process_paa_files_if_needed(path)
                
                self.reload_preview()
        except ValueError as ve:
            QMessageBox.critical(self, "Input Error", str(ve))
            print(f"Input Error: {ve}")
    
    def process_paa_files_if_needed(self, image_directory):
        try:
            prefix = self.prefix_var.currentText()
            paa_files = [f for f in os.listdir(image_directory) if f.startswith(prefix) and f.endswith(".paa")]
            
            if paa_files:
                self.update_status(f"Found {len(paa_files)} .paa files. Checking cache...")
                QtWidgets.QApplication.processEvents()
                
                self.convert_paa_to_png(paa_files, image_directory)
                
                self.update_status(f"PAA files have been processed.")
                QtWidgets.QApplication.processEvents()
                
        except Exception as e:
            print(f"Error while processing PAA files: {e}")
            self.update_status(f"Error while processing PAA files: {e}")

    def select_output_path(self):
        if not validate_inputs(self.grid_size_entry, self.trim_pixels_entry):
            QMessageBox.critical(self, "Input Error", "Fill in 'Grid Size' and 'Trim Pixels' before selecting an output path. Grid size cannot be greater than 128 and Trim pixels cannot be greater than 32.")
            print("Input Error: Fill in 'Grid Size' and 'Trim Pixels' before selecting an output path. Grid size cannot be greater than 128 and Trim pixels cannot be greater than 32.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Stitched Image As", "", "PNG files (*.png);;JPEG files (*.jpg);;All files (*.*)")
        if path:
            self.output_path_entry.setText(path)

    def select_color(self):
        select_color(self.color_var)
    
    def select_imagetopaa_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select ImageToPAA.exe", "", "Executable files (*.exe);;All files (*.*)")
        if path:
            self.imagetopaa_path_entry.setText(path)
            self.imagetopaa_path = path
    
    def get_file_hash(self, file_path):
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def load_cache_info(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_cache_info(self, cache_data):
        os.makedirs(self.temp_dir, exist_ok=True)
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Error while saving cache: {e}")
    
    def check_paa_files_changed(self, paa_files, image_directory):
        cache_data = self.load_cache_info()
        changed_files = []
        
        for paa_file in paa_files:
            paa_path = os.path.join(image_directory, paa_file)
            current_hash = self.get_file_hash(paa_path)
            png_filename = paa_file.replace('.paa', '.png')
            png_path = os.path.join(self.temp_dir, png_filename)
            
            if (paa_file in cache_data and 
                cache_data[paa_file].get('hash') == current_hash and 
                os.path.exists(png_path)):
                self.current_paa_cache[paa_file] = png_filename
            else:
                changed_files.append(paa_file)
        
        return changed_files
    
    def convert_single_paa(self, args):
        paa_file, paa_path, png_path, imagetopaa_path = args
        
        try:
            cmd = [imagetopaa_path, paa_path, png_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(png_path):
                return paa_file, True, None
            else:
                return paa_file, False, f"Conversion error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return paa_file, False, "Timeout during conversion"
        except Exception as e:
            return paa_file, False, str(e)
    
    def convert_paa_to_png(self, paa_files, image_directory):
        if not self.imagetopaa_path:
            raise ValueError("ImageToPAA path is not set. Please select ImageToPAA.exe from DayZTools.")
        
        if not os.path.exists(self.imagetopaa_path):
            raise ValueError(f"ImageToPAA not found at: {self.imagetopaa_path}")
        
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.preview_progress_bar.setValue(0)
        self.preview_progress_bar.setMaximum(len(paa_files))
        
        files_to_convert = self.check_paa_files_changed(paa_files, image_directory)
        
        self.update_status(f"Cache checked. Files to convert: {len(files_to_convert)} of {len(paa_files)}")
        QtWidgets.QApplication.processEvents()
        
        if files_to_convert:
            conversion_args = []
            for paa_file in files_to_convert:
                paa_path = os.path.join(image_directory, paa_file)
                png_filename = paa_file.replace('.paa', '.png')
                png_path = os.path.join(self.temp_dir, png_filename)
                conversion_args.append((paa_file, paa_path, png_path, self.imagetopaa_path))
            
            converted_files = []
            cache_data = self.load_cache_info()
            
            try:
                max_workers = min(int(self.workers_entry.text()), len(files_to_convert))
            except (ValueError, AttributeError):
                max_workers = min(4, len(files_to_convert))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self.convert_single_paa, args) for args in conversion_args]
                
                for i, future in enumerate(futures):
                    self.update_status(f"Converting files... ({i + 1}/{len(futures)})")
                    progress_value = len(paa_files) - len(files_to_convert) + i + 1
                    self.preview_progress_bar.setValue(progress_value)
                    QtWidgets.QApplication.processEvents()
                    
                    paa_file, success, error = future.result()
                    
                    if success:
                        png_filename = paa_file.replace('.paa', '.png')
                        converted_files.append(png_filename)
                        self.current_paa_cache[paa_file] = png_filename
                        
                        paa_path = os.path.join(image_directory, paa_file)
                        file_hash = self.get_file_hash(paa_path)
                        cache_data[paa_file] = {
                            'hash': file_hash,
                            'png_file': png_filename
                        }
                    else:
                        print(f"Conversion error {paa_file}: {error}")
                        self.update_status(f"Conversion error {paa_file}")
            
            self.save_cache_info(cache_data)
            
            self.update_status(f"Converted {len(converted_files)} new files")
        else:
            self.update_status("All .paa files are already converted (using cache)")
            self.preview_progress_bar.setValue(len(paa_files))
        
        all_png_files = []
        for paa_file in paa_files:
            png_filename = paa_file.replace('.paa', '.png')
            png_path = os.path.join(self.temp_dir, png_filename)
            if os.path.exists(png_path):
                all_png_files.append(png_filename)
                self.current_paa_cache[paa_file] = png_filename
        
        self.preview_progress_bar.setValue(0)
        self.preview_progress_bar.setMaximum(100)
        
        return all_png_files
    
    def cleanup_temp_files(self, keep_cache=False):
        if os.path.exists(self.temp_dir):
            try:
                if keep_cache:
                    for file in os.listdir(self.temp_dir):
                        if file.endswith('.png'):
                            file_path = os.path.join(self.temp_dir, file)
                            os.remove(file_path)
                    self.current_paa_cache.clear()
                else:
                    shutil.rmtree(self.temp_dir)
                    os.makedirs(self.temp_dir, exist_ok=True)
                    self.current_paa_cache.clear()
            except Exception as e:
                print(f"Error while cleaning temp folder: {e}")
    
    def get_available_png_files(self, image_directory, prefix):
        direct_png = [f for f in os.listdir(image_directory) if f.startswith(prefix) and f.endswith(".png")]
        
        cached_png = []
        if os.path.exists(self.temp_dir):
            cached_png = [f for f in os.listdir(self.temp_dir) if f.startswith(prefix) and f.endswith(".png")]
        
        result = []
        for png_file in direct_png:
            result.append((png_file, image_directory))
        
        for png_file in cached_png:
            if png_file not in direct_png:
                result.append((png_file, self.temp_dir))
        
        return result
    
    def clear_cache(self):
        try:
            reply = QMessageBox.question(self, "Clear Cache", 
                "Are you sure you want to clear the cache of converted PAA files?\n"
                "This will cause all PAA files to be converted again on next use.",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.cleanup_temp_files(keep_cache=False)
                self.update_status("Cache has been cleared.")
                QMessageBox.information(self, "Cache Cleared", "Cache of converted PAA files has been cleared.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error while clearing cache: {e}")

    def reload_preview(self):
        try:
            grid_size = int(self.grid_size_entry.text())
            trim_pixels = int(self.trim_pixels_entry.text())
            if grid_size > 128:
                raise ValueError("Grid size cannot be greater than 128.")
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
