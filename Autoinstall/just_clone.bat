@echo off
echo.
echo ======================================================
echo   Step 3: Clone all Repos into C:\_GitHub
echo ======================================================
echo.
echo We'll now clone every repository owned by "DvidMakesThings" 
echo into C:\_GitHub. Make sure C:\ is available.
echo.
echo Press any key to begin cloning...
pause > nul

:: Switch to C:\_GitHub (create it if needed)
if not exist "C:\_GitHub" mkdir "C:\_GitHub"
cd /d "C:\_GitHub"

:: Use GitHub CLI to list and clone all repos (limit = 1000)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "gh repo list DvidMakesThings --limit 1000 --json nameWithOwner -q '.[] | .nameWithOwner' | ForEach-Object { gh repo clone $_ }"

echo.
echo All repositories have been cloned (or updated if they already existed).
echo Press any key to exit...
pause > nul
