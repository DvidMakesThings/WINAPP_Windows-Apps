@echo off

echo ============================================
echo Checking SSH Agent
echo ============================================
sc query ssh-agent | find "RUNNING" >nul
if %errorlevel%==0 (
    echo SSH Agent is already running.
) else (
    echo SSH Agent is not running. Attempting to enable and start it...
    sc config ssh-agent start= auto
    net start ssh-agent
    if %errorlevel%==0 (
        echo SSH Agent started successfully.
    ) else (
        echo Failed to start SSH Agent. Please check your system configuration.
        pause
        exit /b 1
    )
)

echo ============================================
echo Checking for an existing SSH key
echo ============================================
if exist "%USERPROFILE%\.ssh\id_ed25519" (
    echo SSH key already exists. Skipping key generation.
) else (
    echo No SSH key found. Generating a new SSH key...
    ssh-keygen -t ed25519 -C "s.dvid@hotmail.com" -f "%USERPROFILE%\.ssh\id_ed25519" -q -N ""
    echo SSH key generated successfully.
)

echo ============================================
echo Adding the SSH key to the SSH Agent
echo ============================================
ssh-add "%USERPROFILE%\.ssh\id_ed25519"

echo ============================================
echo Displaying the public key (copy this to GitHub)
echo ============================================
type "%USERPROFILE%\.ssh\id_ed25519.pub"

echo ============================================
echo Open this URL to add the key to your GitHub account:
echo https://github.com/settings/keys
echo ============================================
pause

echo ============================================
echo Testing the SSH connection to GitHub
echo ============================================
ssh -T git@github.com

pause
