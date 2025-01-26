@echo off

REM Check if a parameter is provided
if "%~1"=="" (
    REM Prompt the user for the project name
    set /p PROJECT_NAME="Enter the project name: "
) else (
    set PROJECT_NAME=%~1
)

REM Path to the template folder
set TEMPLATE_FOLDER=G:\My Drive\Git\Templates

echo Creating project folder structure for %PROJECT_NAME%...

REM Create the project folder and subfolders
call :CreateDir "%PROJECT_NAME%\src\HardwareDesign"
call :CreateDir "%PROJECT_NAME%\src\PDF"
call :CreateDir "%PROJECT_NAME%\src\Libraries"
call :CreateDir "%PROJECT_NAME%\src\Software"
call :CreateDir "%PROJECT_NAME%\docs\Datasheets"
call :CreateDir "%PROJECT_NAME%\docs"
call :CreateDir "%PROJECT_NAME%\docs\Manuals"
call :CreateDir "%PROJECT_NAME%\docs\Reports"
call :CreateDir "%PROJECT_NAME%\images"
call :CreateDir "%PROJECT_NAME%\tests"
call :CreateDir "%PROJECT_NAME%\tests\UnitTests"
call :CreateDir "%PROJECT_NAME%\tests\IntegrationTests"
call :CreateDir "%PROJECT_NAME%\misc"

echo Creating and updating Readme.md files...

REM Copy and update Readme.md files
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%" "%PROJECT_NAME%"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\src" "%PROJECT_NAME%\src"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\src\HardwareDesign" "%PROJECT_NAME%\src\HardwareDesign"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\src\PDF" "%PROJECT_NAME%\src\PDF"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\src\Libraries" "%PROJECT_NAME%\src\Libraries"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\src\Software" "%PROJECT_NAME%\src\Software"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\docs\Datasheets" "%PROJECT_NAME%\docs\Datasheets"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\docs" "%PROJECT_NAME%\docs"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\docs\Manuals" "%PROJECT_NAME%\docs\Manuals"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\docs\Reports" "%PROJECT_NAME%\docs\Reports"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\images" "%PROJECT_NAME%\images"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\tests" "%PROJECT_NAME%\tests"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\tests\UnitTests" "%PROJECT_NAME%\tests\UnitTests"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\tests\IntegrationTests" "%PROJECT_NAME%\tests\IntegrationTests"
call :CopyAndReplaceReadme "%TEMPLATE_FOLDER%\misc" "%PROJECT_NAME%\misc"

echo Checking for existing eagle.epf file...
if exist "%PROJECT_NAME%\src\HardwareDesign\eagle.epf" (
    set /p OVERWRITE_EPF="Eagle Project file already exists. Do you want to overwrite it? (y/n): "
    if /i "%OVERWRITE_EPF%"=="y" (
        echo Creating Eagle Project file...
        copy /Y "%TEMPLATE_FOLDER%\src\HardwareDesign\eagle.epf" "%PROJECT_NAME%\src\HardwareDesign\eagle.epf"
        if %errorlevel% neq 0 (
            echo Failed to create eagle.epf file.
        ) else (
            echo Eagle Project file created successfully.
        )
    ) else (
        echo Skipping Eagle Project file creation.
    )
) else (
    echo Creating Eagle Proect file...
    copy /Y "%TEMPLATE_FOLDER%\src\HardwareDesign\eagle.epf" "%PROJECT_NAME%\src\HardwareDesign\eagle.epf"
    if %errorlevel% neq 0 (
        echo Failed to create Eagle Project file.
    ) else (
        echo Eagle Project file created successfully.
    )
)

echo Checking for existing schematic file...
if exist "%PROJECT_NAME%\src\HardwareDesign\%PROJECT_NAME%.sch" (
    set /p OVERWRITE_SCH="Schematic file already exists. Do you want to overwrite it? (y/n): "
    if /i "%OVERWRITE_SCH%"=="y" (
        echo Creating schematic file with project name...
        copy /Y "%TEMPLATE_FOLDER%\src\HardwareDesign\template.sch" "%PROJECT_NAME%\src\HardwareDesign\%PROJECT_NAME%.sch"
        if %errorlevel% neq 0 (
            echo Failed to created template.sch file.
        ) else (
            echo template.sch file created successfully.
            powershell -Command "(Get-Content -path '%PROJECT_NAME%\src\HardwareDesign\%PROJECT_NAME%.sch') -replace '%%PROJECT_NAME%%', '%PROJECT_NAME%' | Set-Content -path '%PROJECT_NAME%\src\HardwareDesign\%PROJECT_NAME%.sch'"
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
    copy /Y "%TEMPLATE_FOLDER%\src\HardwareDesign\template.sch" "%PROJECT_NAME%\src\HardwareDesign\%PROJECT_NAME%.sch"
    if %errorlevel% neq 0 (
        echo Failed to create template.sch file.
    ) else (
        echo template.sch file created successfully.
        powershell -Command "(Get-Content -path '%PROJECT_NAME%\src\HardwareDesign\%PROJECT_NAME%.sch') -replace '%%PROJECT_NAME%%', '%PROJECT_NAME%' | Set-Content -path '%PROJECT_NAME%\src\HardwareDesign\%PROJECT_NAME%.sch'"
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
if not exist "%~2\Readme.md" (
    echo Creating and updating Readme.md in %~2...
    copy "%~1\Readme.md" "%~2\Readme.md"
    if %errorlevel% neq 0 (
        echo Failed to create Readme.md to %~2.
    ) else (
        echo Readme.md created to %~2 successfully.
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