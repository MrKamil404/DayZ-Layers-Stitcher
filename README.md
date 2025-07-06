# DayZ Layers Stitcher

![preview](https://raw.githubusercontent.com/MrKamil404/DayZ-Layers-Stitcher/refs/heads/master/images/DayZ%20Layers%20Stitcher%201.0.1.png?token=GHSAT0AAAAAAC2KGDBPKBKU5EMPOZEIUZKOZ3UKP4Q)

## Description
DayZ Layers Stitcher is a tool for stitching image layers together.

## Features

- **Grid Size and Trim Pixels**: Allows the user to specify the grid size and the number of pixels to trim from each image.
- **Prefix Selection**: Users can select a prefix for the images to be stitched.
- **Background Color**: Users can choose a background color for the stitched image.
- **PAA File Support**: Automatic conversion of .paa files to .png using ImageToPAA from DayZTools with intelligent caching.
- **Multi-threading**: Faster processing using multiple CPU cores for file conversion and image loading.
- **Intelligent Caching**: Converted .paa files are cached to avoid re-conversion on subsequent operations.
- **Cache Management**: Manual cache clearing option for when source files are updated.
- **Image Directory and Output Path**: Users can select the directory containing the images to be stitched and specify the output path for the final stitched image.
- **Preview Quality**: Users can set the quality of the preview image.
- **Progress Bars**: Displays progress bars for both preview generation and the stitching process.
- **Status and Information Labels**: Provides status updates and information about the preview and full image sizes.
- **Image Preview**: Displays a preview of the stitched image, allowing users to zoom and pan.
- **Merge Button**: Initiates the stitching process.
- **Reload Preview**: Reloads the preview image based on the current settings.
- **Temporary File Management**: Automatically manages temporary files during PAA conversion.

## Key Libraries

The program uses the following key libraries:

1. **os**: For interacting with the operating system, such as listing files in a directory.
2. **subprocess**: For running external programs like ImageToPAA.exe.
3. **shutil**: For file operations such as removing temporary directories.
4. **hashlib**: For file integrity checking and caching.
5. **json**: For storing cache metadata.
6. **concurrent.futures**: For multi-threading support to improve performance.
7. **PIL (Python Imaging Library)**: Specifically, the `Image` module from the `Pillow` package, which is used for image processing tasks like opening, cropping, resizing, and saving images.
3. **PyQt5**: A set of Python bindings for the Qt application framework, used for creating the graphical user interface (GUI). The specific modules and classes used include:
   - `QtWidgets`: For various GUI components like `QWidget`, `QLabel`, `QLineEdit`, `QPushButton`, `QFileDialog`, `QMessageBox`, `QColorDialog`, `QGraphicsView`, `QGraphicsScene`, and `QGraphicsPixmapItem`.
   - `QtGui`: For handling images and rendering, including `QImage`, `QPixmap`, and `QPainter`.
   - `QtCore`: For core non-GUI functionality, such as event handling with `QEvent`.

## How to Use

1. **Prepare the PNG or PAA layer files**. The file names should look like this: S/M/N_x_x_lco.
2. **Set Grid Size and Trim Pixels**: Enter the grid size and the number of pixels to trim from each image.
3. **Select Prefix**: Choose the prefix for the images to be stitched.
4. **Choose Background Color**: Select a background color for the stitched image.
5. **(Optional) Set ImageToPAA Path**: If you have .paa files, browse and select the path to ImageToPAA.exe from DayZTools.
6. **Select Image Directory**: Browse and select the directory containing the images to be stitched.
7. **Specify Output Path**: Browse and specify the output path for the final stitched image.
8. **Set Preview Quality**: Enter the desired quality for the preview image.
9. **Generate Preview**: Click "Reload preview" to generate and view a preview of the stitched image.
10. **Stitch Images**: Click "Merge" to start the stitching process and save the final image to the specified output path.

### PAA File Support

The application now supports .paa files from DayZ with intelligent caching and multi-threading:

**Smart Conversion Process:**
1. When you select a directory containing .paa files, they are automatically converted to .png format using ImageToPAA.exe
2. Converted files are cached in a `temp` folder to avoid re-conversion
3. The application checks file hashes to detect changes and only re-converts modified files
4. Subsequent operations (preview reload, merge) use cached .png files for faster performance

**Multi-threading Benefits:**
- File conversion uses up to 4 concurrent threads for faster processing
- Image loading also utilizes multi-threading for improved performance
- Progress is shown in real-time during operations

**Cache Management:**
- Use the "Clear Cache" button to manually remove all cached files
- Cache is automatically managed - only changed .paa files are re-converted
- Cache information is stored in `temp/cache_info.json`

**Note**: To use .paa file support, you need to have DayZTools installed and specify the path to ImageToPAA.exe in the application settings.

## Support

If you find this project useful, consider buying me a coffee!

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/mrkamil404)

