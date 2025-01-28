@echo off

REM Check if a parameter is provided
if "%~1"=="" (
    REM Prompt the user for the project name
    set /p PROJECT_NAME="Enter the project name: "
) else (
    set PROJECT_NAME=%~1
)

REM Set the template folder to a relative path
set TEMPLATE_FOLDER=%~dp0..\Templates

REM Ask for the destination folder
set /p DEST_FOLDER="Enter the destination folder: "

REM Copy the content of the template folder to the destination folder
xcopy "%TEMPLATE_FOLDER%" "%DEST_FOLDER%" /E /I /Y

echo Files copied from %TEMPLATE_FOLDER% to %DEST_FOLDER%

echo Creating project folder structure for %PROJECT_NAME%...

REM Create the project folder and subfolders
call :CreateDir "%DEST_FOLDER%\src\HardwareDesign"
call :CreateDir "%DEST_FOLDER%\src\PDF"
call :CreateDir "%DEST_FOLDER%\src\Libraries"
call :CreateDir "%DEST_FOLDER%\src\Software"
call :CreateDir "%DEST_FOLDER%\docs\Datasheets"
call :CreateDir "%DEST_FOLDER%\docs"
call :CreateDir "%DEST_FOLDER%\docs\Manuals"
call :CreateDir "%DEST_FOLDER%\docs\Reports"
call :CreateDir "%DEST_FOLDER%\images"
call :CreateDir "%DEST_FOLDER%\tests"
call :CreateDir "%DEST_FOLDER%\tests\UnitTests"
call :CreateDir "%DEST_FOLDER%\tests\IntegrationTests"
call :CreateDir "%DEST_FOLDER%\misc"

echo Creating and updating Readme.md files...

REM Copy and update Readme.md files
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%" "%DEST_FOLDER%"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\src" "%DEST_FOLDER%\src"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\src\HardwareDesign" "%DEST_FOLDER%\src\HardwareDesign"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\src\PDF" "%DEST_FOLDER%\src\PDF"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\src\Libraries" "%DEST_FOLDER%\src\Libraries"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\src\Software" "%DEST_FOLDER%\src\Software"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\docs\Datasheets" "%DEST_FOLDER%\docs\Datasheets"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\docs" "%DEST_FOLDER%\docs"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\docs\Manuals" "%DEST_FOLDER%\docs\Manuals"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\docs\Reports" "%DEST_FOLDER%\docs\Reports"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\images" "%DEST_FOLDER%\images"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\tests" "%DEST_FOLDER%\tests"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\tests\UnitTests" "%DEST_FOLDER%\tests\UnitTests"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\tests\IntegrationTests" "%DEST_FOLDER%\tests\IntegrationTests"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\misc" "%DEST_FOLDER%\misc"

echo Checking for existing schematic file...
if exist "%DEST_FOLDER%\src\HardwareDesign\%PROJECT_NAME%.sch" (
    set /p OVERWRITE_SCH="Schematic file already exists. Do you want to overwrite it? (y/n): "
    if /i "%OVERWRITE_SCH%"=="y" (
        echo Creating schematic file with project name...
        copy /Y "%TEMPLATE_FOLDER%\src\HardwareDesign\template.sch" "%DEST_FOLDER%\src\HardwareDesign\%PROJECT_NAME%.sch"
        if %errorlevel% neq 0 (
            echo Failed to create template.sch file.
        ) else (
            echo template.sch file created successfully.
            del "%DEST_FOLDER%\src\HardwareDesign\template.sch"
            powershell -Command "(Get-Content -path '%DEST_FOLDER%\src\HardwareDesign\%PROJECT_NAME%.sch') -replace '%%PROJECT_NAME%%', '%PROJECT_NAME%' | Set-Content -path '%DEST_FOLDER%\src\HardwareDesign\%PROJECT_NAME%.sch'"
            if %errorlevel% neq 0 (
                echo Failed to update schematic file with project name.
            ) else (
                echo Schematic file updated with project name successfully.
            )
        )
    ) else (
        echo Skipping schematic file creation.
    )
) else (
    echo Creating schematic file with project name...
    copy /Y "%TEMPLATE_FOLDER%\src\HardwareDesign\template.sch" "%DEST_FOLDER%\src\HardwareDesign\%PROJECT_NAME%.sch"
    if %errorlevel% neq 0 (
        echo Failed to create template.sch file.
    ) else (
        echo template.sch file created successfully.
        del "%DEST_FOLDER%\src\HardwareDesign\template.sch"
        powershell -Command "(Get-Content -path '%DEST_FOLDER%\src\HardwareDesign\%PROJECT_NAME%.sch') -replace '%%PROJECT_NAME%%', '%PROJECT_NAME%' | Set-Content -path '%DEST_FOLDER%\src\HardwareDesign\%PROJECT_NAME%.sch'"
        if %errorlevel% neq 0 (
            echo Failed to update schematic file with project name.
        ) else (
            echo Schematic file updated with project name successfully.
        )
    )
)

echo Folder structure and Readme.md files created for project: %PROJECT_NAME%
echo Eagle Project and schematics file created
pause
goto :eof

REM Function to create a directory if it doesn't exist
:CreateDir
if not exist "%~1" (
    echo Creating directory %~1...
    mkdir "%~1"
    if %errorlevel% neq 0 (
        echo Failed to create directory %~1.
    ) else (
        echo Directory %~1 created successfully.
    )
) else (
    echo Directory %~1 already exists, skipping creation.
)
goto :eof

REM Function to copy and replace %PROJECT_NAME% in Readme.md files
:CopyAndReplaceReadme
if exist "%~1\Readme.md" (
    echo Creating and updating Readme.md in %~2...
    copy "%~1\Readme.md" "%~2\Readme.md"
    if %errorlevel% neq 0 (
        echo Failed to create Readme.md in %~2.
    ) else (
        echo Readme.md created in %~2 successfully.
        powershell -Command "(Get-Content -path '%~2\Readme.md') -replace '%%PROJECT_NAME%%', '%PROJECT_NAME%' | Set-Content -path '%~2\Readme.md'"
        if %errorlevel% neq 0 (
            echo Failed to update Readme.md with project name in %~2.
        ) else (
            echo Readme.md updated with project name in %~2 successfully.
        )
    )
) else (
    echo Readme.md already exists in %~2, skipping creation.
)
goto :eof