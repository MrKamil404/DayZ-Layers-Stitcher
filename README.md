# DayZ Layers Stitcher

DayZ Layers Stitcher is a graphical user interface (GUI) application designed for stitching images together, specifically for DayZ map layers. It is built using PyQt5 for the GUI components and the Python Imaging Library (PIL) for image processing.

## Features

- **Grid Size and Trim Pixels**: Allows the user to specify the grid size and the number of pixels to trim from each image.
- **Prefix Selection**: Users can select a prefix for the images to be stitched.
- **Background Color**: Users can choose a background color for the stitched image.
- **Image Directory and Output Path**: Users can select the directory containing the images to be stitched and specify the output path for the final stitched image.
- **Preview Quality**: Users can set the quality of the preview image.
- **Progress Bars**: Displays progress bars for both preview generation and the stitching process.
- **Status and Information Labels**: Provides status updates and information about the preview and full image sizes.
- **Image Preview**: Displays a preview of the stitched image, allowing users to zoom and pan.
- **Merge Button**: Initiates the stitching process.
- **Reload Preview**: Reloads the preview image based on the current settings.

## Key Libraries

The program uses the following key libraries:

1. **os**: For interacting with the operating system, such as listing files in a directory.
2. **PIL (Python Imaging Library)**: Specifically, the `Image` module from the `Pillow` package, which is used for image processing tasks like opening, cropping, resizing, and saving images.
3. **PyQt5**: A set of Python bindings for the Qt application framework, used for creating the graphical user interface (GUI). The specific modules and classes used include:
   - `QtWidgets`: For various GUI components like `QWidget`, `QLabel`, `QLineEdit`, `QPushButton`, `QFileDialog`, `QMessageBox`, `QColorDialog`, `QGraphicsView`, `QGraphicsScene`, and `QGraphicsPixmapItem`.
   - `QtGui`: For handling images and rendering, including `QImage`, `QPixmap`, and `QPainter`.
   - `QtCore`: For core non-GUI functionality, such as event handling with `QEvent`.

## How to Use

1. **Prepare the PNG layer files**. The file names should look like this: S/M/N_x_x_lco.
2. **Set Grid Size and Trim Pixels**: Enter the grid size and the number of pixels to trim from each image.
3. **Select Prefix**: Choose the prefix for the images to be stitched.
4. **Choose Background Color**: Select a background color for the stitched image.
5. **Select Image Directory**: Browse and select the directory containing the images to be stitched.
6. **Specify Output Path**: Browse and specify the output path for the final stitched image.
7. **Set Preview Quality**: Enter the desired quality for the preview image.
8. **Generate Preview**: Click "Reload preview" to generate and view a preview of the stitched image.
9. **Stitch Images**: Click "Merge" to start the stitching process and save the final image to the specified output path.

## Support

If you find this project useful, consider buying me a coffee!

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/mrkamil404)

