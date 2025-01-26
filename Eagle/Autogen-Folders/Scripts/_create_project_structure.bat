@echo off

REM Check if a parameter is provided
if "%~1"=="" (
    REM Prompt the user for the project name
    set /p PROJECT_NAME="Enter the project name: "
) else (
    set PROJECT_NAME=%~1
)

REM Create the project folder and subfolders
call :CreateDir "%PROJECT_NAME%\src\HardwareDesign"
call :CreateDir "%PROJECT_NAME%\src\PDF"
call :CreateDir "%PROJECT_NAME%\src\Libraries"
call :CreateDir "%PROJECT_NAME%\src\Software"
call :CreateDir "%PROJECT_NAME%\docs\Datasheets"
call :CreateDir "%PROJECT_NAME%\docs\Manuals"
call :CreateDir "%PROJECT_NAME%\docs\Reports"
call :CreateDir "%PROJECT_NAME%\images"
call :CreateDir "%PROJECT_NAME%\tests\UnitTests"
call :CreateDir "%PROJECT_NAME%\tests\IntegrationTests"
call :CreateDir "%PROJECT_NAME%\misc"

REM Create empty Readme.md files in all folders
call :CreateReadme "%PROJECT_NAME%"
call :CreateReadme "%PROJECT_NAME%\src"
call :CreateReadme "%PROJECT_NAME%\src\HardwareDesign"
call :CreateReadme "%PROJECT_NAME%\src\PDF"
call :CreateReadme "%PROJECT_NAME%\src\Libraries"
call :CreateReadme "%PROJECT_NAME%\src\Software"
call :CreateReadme "%PROJECT_NAME%\docs\Datasheets"
call :CreateReadme "%PROJECT_NAME%\docs"
call :CreateReadme "%PROJECT_NAME%\docs\Manuals"
call :CreateReadme "%PROJECT_NAME%\docs\Reports"
call :CreateReadme "%PROJECT_NAME%\images"
call :CreateReadme "%PROJECT_NAME%\tests"
call :CreateReadme "%PROJECT_NAME%\tests\UnitTests"
call :CreateReadme "%PROJECT_NAME%\tests\IntegrationTests"
call :CreateReadme "%PROJECT_NAME%\misc"

echo Folder structure and Readme.md files created for project: %PROJECT_NAME%
pause
goto :eof

REM Function to create a directory if it doesn't exist
:CreateDir
if not exist "%~1" (
    mkdir "%~1"
)
goto :eof

REM Function to create an empty Readme.md file if it doesn't exist
:CreateReadme
if not exist "%~1\Readme.md" (
    type nul > "%~1\Readme.md"
)
goto :eof