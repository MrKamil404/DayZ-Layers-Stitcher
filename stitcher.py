import os
import subprocess
import shutil
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
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

            available_png_files = self.get_available_png_files(image_directory, prefix)
            
            if not available_png_files:
                raise ValueError("No images found matching the specified prefix and extension in the directory.")

            self.load_images_multithreaded(available_png_files, trim_pixels, images)

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

            if grid_size > 128:
                raise ValueError("Grid size cannot be greater than 128.")
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

    def load_single_image(self, args):
        """Loads a single image (for multithreading)"""
        filename, image_directory, trim_pixels = args
        
        try:
            _, x_str, y_str, _ = filename.split('_')
            x = int(x_str)
            y = int(y_str)

            image_path = os.path.join(image_directory, filename)
            img = Image.open(image_path)
            width, height = img.size
            cropped_img = img.crop((trim_pixels, trim_pixels, width - trim_pixels, height - trim_pixels))
            
            return (x, y), cropped_img, None
        except Exception as e:
            return None, None, f"Error loading {filename}: {e}"
    
    def load_images_multithreaded(self, available_png_files, trim_pixels, images):
        """Loads images using multithreading"""
        load_args = []
        for filename, image_directory in available_png_files:
            load_args.append((filename, image_directory, trim_pixels))
        
        max_workers = min(4, len(load_args))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.load_single_image, args) for args in load_args]
            
            for i, future in enumerate(futures):
                self.update_status(f"Loading images... ({i + 1}/{len(futures)})")
                self.stitching_progress_bar.setValue(i + 1)
                QtWidgets.QApplication.processEvents()
                
                position, cropped_img, error = future.result()
                
                if error:
                    print(error)
                    self.update_status(error)
                elif position and cropped_img:
                    images[position] = cropped_img

    def preview_images(self, image_directory, grid_size, trim_pixels, prefix, background_color):
        try:
            if grid_size > 128:
                raise ValueError("Grid size cannot be greater than 128.")
            if trim_pixels > 32:
                raise ValueError("Trim pixels cannot be greater than 32.")

            preview_quality = int(self.preview_quality_entry.text())
            images = {}
            self.preview_progress_bar.setValue(0)
            QtWidgets.QApplication.processEvents()

            available_png_files = self.get_available_png_files(image_directory, prefix)
            
            if not available_png_files:
                raise ValueError("No images found matching the specified prefix.")

            self.preview_progress_bar.setMaximum(len(available_png_files))

            self.load_preview_images_multithreaded(available_png_files, trim_pixels, preview_quality, images)

            preview_image = Image.new('RGB', (preview_quality * grid_size, preview_quality * grid_size), background_color)
            for x in range(grid_size):
                for y in range(grid_size):
                    if (x, y) in images:
                        preview_image.paste(images[(x, y)], (x * preview_quality, y * preview_quality))

            if available_png_files:
                first_filename, first_directory = available_png_files[0]
                first_path = os.path.join(first_directory, first_filename)
                temp_img = Image.open(first_path)
                width, height = temp_img.size
                temp_img.close()
            else:
                width, height = 512, 512

            self.render_preview(preview_image)
            self.update_preview_info(preview_image, (width * grid_size, height * grid_size))
            self.update_status("Preview loaded.")
                
        except ValueError as ve:
            QMessageBox.critical(self, "Input Error", str(ve))
            print(f"Input Error: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading preview: {e}")
            print(f"Error: Error loading preview: {e}")

    def load_single_preview_image(self, args):
        """Loads a single image for preview (for multithreading)"""
        filename, image_directory, trim_pixels, preview_quality = args
        
        try:
            _, x_str, y_str, _ = filename.split('_')
            x = int(x_str)
            y = int(y_str)

            image_path = os.path.join(image_directory, filename)
            img = Image.open(image_path)
            width, height = img.size
            cropped_img = img.crop((trim_pixels, trim_pixels, width - trim_pixels, height - trim_pixels))
            scaled_img = cropped_img.resize((preview_quality, preview_quality))
            
            return (x, y), scaled_img, None
        except Exception as e:
            return None, None, f"Error loading preview {filename}: {e}"
    
    def load_preview_images_multithreaded(self, available_png_files, trim_pixels, preview_quality, images):
        """Loads images for preview using multithreading"""
        load_args = []
        for filename, image_directory in available_png_files:
            load_args.append((filename, image_directory, trim_pixels, preview_quality))
        
        max_workers = min(4, len(load_args))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.load_single_preview_image, args) for args in load_args]
            
            for i, future in enumerate(futures):
                self.update_status(f"Loading preview images... ({i + 1}/{len(futures)})")
                self.preview_progress_bar.setValue(i + 1)
                QtWidgets.QApplication.processEvents()
                
                position, scaled_img, error = future.result()
                
                if error:
                    print(error)
                    self.update_status(error)
                elif position and scaled_img:
                    images[position] = scaled_img

    def update_status(self, message):
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()
        print(message)
