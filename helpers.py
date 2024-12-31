from PyQt5.QtWidgets import QColorDialog

def select_color(color_var):
    color = QColorDialog.getColor()
    if color.isValid():
        color_var.setText(color.name())
        color_var.setStyleSheet(f"background-color: {color.name()};")

def validate_inputs(grid_size_entry, trim_pixels_entry):
    try:
        grid_size = int(grid_size_entry.text())
        trim_pixels = int(trim_pixels_entry.text())
        if grid_size > 42 or trim_pixels > 32:
            return False
        return True
    except ValueError:
        return False
