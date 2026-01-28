# Build script to create a one-file executable using PyInstaller
# Run this from the project root in PowerShell: .\build_exe.ps1

$ErrorActionPreference = 'Stop'

Write-Host "Installing PyInstaller (if not present)..."
python -m pip install --upgrade pip
python -m pip install pyinstaller==5.13.0

Write-Host "Building one-file executable for gui_launcher.py..."
pyinstaller --onefile --name job_automation_gui --add-data "config;config" --add-data "resumes;resumes" --add-data "logs;logs" gui_launcher.py

Write-Host "Build complete. Executable located in the 'dist' directory."
