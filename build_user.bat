@echo off

if "%~1"=="" (
    set /p version=Please provide version: 
) else (
    set version=%~1
)

echo.
echo Building Sphinx project...
python scripts/build_user.py %version%
echo The project has been built.
pause
