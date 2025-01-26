@echo off
:: --------------------------------------------------
:: clone_all_repos.bat
:: --------------------------------------------------
:: This batch file helps:
::  1. Download & install GitHub CLI (manually)
::  2. Authenticate GitHub CLI
::  3. Clone all repos for "DvidMakesThings" into G:\_GitHub
:: --------------------------------------------------

echo.
echo ==================================================================
echo   Step 1: Download & Install GitHub CLI (if not already installed)
echo ==================================================================
echo.
echo This script will open the GitHub CLI releases page in your browser.
echo Choose the "windows amd64 installer" (.msi) for 64-bit Windows 
echo (common) or the "windows 386 installer" if you're on 32-bit Windows.
echo.
echo Press any key to open the download page, or press Ctrl+C to cancel.
pause > nul

start https://github.com/cli/cli/releases

echo.
echo When you have finished installing GitHub CLI, press any key to continue.
pause > nul

echo.
echo ======================================================
echo   Step 2: Authenticate with GitHub CLI
echo ======================================================
echo.
echo The next command runs "gh auth login" in PowerShell.
echo Follow the prompts to sign into your GitHub account.
echo.
echo Press any key to proceed...
pause > nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "gh auth login"

echo.
echo ======================================================
echo   Step 3: Clone all Repos into G:\_GitHub
echo ======================================================
echo.
echo We'll now clone every repository owned by "DvidMakesThings" 
echo into G:\_GitHub. Make sure G:\ is available.
echo.
echo Press any key to begin cloning...
pause > nul

:: Switch to G:\_GitHub (create it if needed)
if not exist "G:\_GitHub" mkdir "G:\_GitHub"
cd /d "G:\_GitHub"

:: Use GitHub CLI to list and clone all repos (limit = 1000)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "gh repo list DvidMakesThings --limit 1000 --json nameWithOwner -q '.[] | .nameWithOwner' | ForEach-Object { gh repo clone $_ }"

echo.
echo All repositories have been cloned (or updated if they already existed).
echo Press any key to exit...
pause > nul
