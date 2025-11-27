@echo off

if "%~1"=="" (
    set /p base_version=Please, provide base documentation version: 
) else (
    set base_version=%~1
)
if "%~2"=="" (
    set /p version=Please, provide new documentation version: 
) else (
    set version=%~2
)

echo.
echo WARNING! If exists, source/%version% directory will be erased and reset to %base_version% version. 
echo If this is what you want, press any key. Otherwise, close the terminal.
pause

python scripts/set_up_version.py %base_version% %version%

echo.
echo Successfully set up a directory for %version% version.
pause