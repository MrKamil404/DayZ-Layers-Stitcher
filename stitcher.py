import os
from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox

class ImageStitcherLogic:
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

    def update_status(self, message):
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()
        print(message)
