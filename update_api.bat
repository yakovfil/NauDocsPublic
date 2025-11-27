@echo off

if "%~1"=="-h" (
    goto :help
)
if "%~1"=="--help" (
    goto :help
)
if "%~1"=="" (
    set /p doc_version=Please, provide documentation version: 
) else (
    set doc_version=%~1
)

echo.
echo Parsing header files...
python scripts/parse_headers.py %doc_version%


echo.
echo Add or modify necessary sections and topics in the [extracted_info] folder.
echo Press Enter to continue the proccess...
pause >nul

REM Call the second Python script
python scripts/set_up_structure.py %doc_version%
echo.
echo Header files have been successfully parsed and built .rsts are put into the [generated_content] folder.
pause

goto :eof

:help
echo.
echo Usage: update [cpp_source] [doc_version] [topic_name]
echo.
echo Options:
echo   -h, --help    Show this help message
echo.
goto :eof