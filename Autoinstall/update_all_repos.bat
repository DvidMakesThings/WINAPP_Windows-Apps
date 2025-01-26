@echo off
:: -------------------------------------------------------------------
:: update_all_repos.bat
:: Pulls the latest commits in every Git repo under G:\_GitHub
:: (one repo per folder, no nested repos).
:: -------------------------------------------------------------------

echo.
echo ==========================================================
echo   Updating all repos in G:\_GitHub
echo ==========================================================
echo.

:: Switch to G:\_GitHub (the /d parameter allows changing drives in CMD)
cd /d "G:\_GitHub"

:: Loop over every folder in this directory
for /D %%d in (*) do (
    :: Check if the folder is a Git repo by looking for ".git" subfolder
    if exist "%%d\.git" (
        echo Updating %%d ...
        git -C "%%d" pull
        echo.
    )
)

echo All repositories have been updated!
pause
