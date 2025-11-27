@echo off

if "%~1"=="" (
    set /p version=Please provide version: 
) else (
    set version=%~1
)

echo.
echo Generating XMLs with Doxygen...
doxygen source/%version%/api-doc/Doxyfile
echo XMLs have been generated!

echo.
echo Building Sphinx project...
python scripts/build_api.py %version%
echo The project has been built.
pause
