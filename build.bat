@echo off
echo ========================================
echo    DayZ_Layers_Siticher - Builder Script
echo ========================================
echo.

echo ...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo.
echo Building app...
py -m PyInstaller --onefile --windowed --name "DayZ_Layers_Siticher" --icon=NONE main.py

echo.
if exist "dist\PAA_Resize_Tool.exe" (
    echo ========================================
    echo    SUCCESS
    echo ========================================
    echo.
    echo Localization: dist\DayZ_Layers_Siticher.exe
    echo Size:
    dir dist\PAA_Resize_Tool.exe | find ".exe"
    echo.
    echo Run app? (T/N)
    set /p choice=
    if /i "%choice%"=="T" (
        echo Running app...
        start "" "dist\DayZ_Layers_Siticher.exe"
    )
) else (
    echo ========================================
    echo    ERROR
    echo ========================================
)

echo.
pause
