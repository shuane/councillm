@echo off
setlocal enabledelayedexpansion

:: Default values
set N_MODELS=6
set NO_LOGGING=false
set EXTRA_ARGS=

:: Parse command line arguments
:parse_args
if "%~1"=="" goto end_parse_args
if "%~1"=="-n" (
    set N_MODELS=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--no-logging" (
    set NO_LOGGING=true
    shift
    goto parse_args
) else (
    :: Collect any other arguments to pass to the Python script
    set EXTRA_ARGS=!EXTRA_ARGS! %~1
    shift
    goto parse_args
)
:end_parse_args

:: Pass arguments to the Python script
if "%NO_LOGGING%"=="true" (
    uv run --isolated --no-project --with-requirements councillm/cl_requirements.txt councillm/app.py -n %N_MODELS% --no-logging %EXTRA_ARGS%
) else (
    uv run --isolated --no-project --with-requirements councillm/cl_requirements.txt councillm/app.py -n %N_MODELS% %EXTRA_ARGS%
)
