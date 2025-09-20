@echo off
echo ================================================
echo Transmission Dashboard - Executable Builder
echo ================================================
echo.

echo Installing build requirements...
python -m pip install pyinstaller pystray pillow flask openpyxl

echo.
echo Building executable...
python build_exe.py

echo.
echo Build process completed!
echo Check the 'deployment' folder for the executable.
pause
