@echo off
echo ============================================
echo Installing Essential Applications
echo ============================================

:: Check if winget is installed
winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Winget is not installed. Please install the Windows Package Manager first.
    pause
    exit /b 1
)

:: Install essential applications
winget install -e --id Microsoft.VisualStudioCode
winget install -e --id Python.Python.3.12
winget install -e --id VLC.VLC
winget install -e --id Notepad++.Notepad++
winget install -e --id 7zip.7zip

:: Install additional applications
winget install -e --id Qt.QtCreator
winget install -e --id PuTTY.PuTTY
winget install -e --id Docker.DockerDesktop
winget install -e --id KiCad.KiCad

:: Check if Bambu Studio is available
echo Installing Bambu Studio (if available)...
winget search "Bambu Studio" | findstr "Available" >nul
if %errorlevel%==0 (
    winget install -e --id BambuLab.BambuStudio
) else (
    echo Bambu Studio not found in winget. Please install it manually.
)

echo ============================================
echo All apps have been installed!
echo ============================================
pause
