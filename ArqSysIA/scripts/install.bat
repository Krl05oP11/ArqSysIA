@echo off
REM ArqSysIA Installation Script for Windows
REM Author: Carlos
REM Description: Automated installation script for ArqSysIA

setlocal enabledelayedexpansion

echo ========================================
echo   ArqSysIA Installation Script
echo ========================================
echo.

REM Check Python version
echo [INFO] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.11 or higher.
    exit /b 1
)

python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.11+ is required.
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Create virtual environment
echo.
echo [INFO] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    exit /b 1
)
echo [OK] Virtual environment created

REM Activate virtual environment
echo.
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    exit /b 1
)
echo [OK] Virtual environment activated

REM Upgrade pip
echo.
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip
    exit /b 1
)

REM Install dependencies
echo.
echo [INFO] Installing ArqSysIA...
pip install -e .
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)
echo [OK] Dependencies installed

REM Verify installation
echo.
echo [INFO] Verifying installation...
arqsysia --version
if errorlevel 1 (
    echo [ERROR] Installation verification failed
    exit /b 1
)
echo [OK] ArqSysIA installed successfully!

REM Ask about tests
echo.
set /p RUN_TESTS="Do you want to run tests? (y/n): "
if /i "%RUN_TESTS%"=="y" (
    echo.
    echo [INFO] Running tests...
    pytest tests\ -v
    if errorlevel 1 (
        echo [WARNING] Some tests failed
    ) else (
        echo [OK] All tests passed!
    )
)

REM Completion message
echo.
echo ========================================
echo [OK] Installation complete!
echo ========================================
echo.
echo To use ArqSysIA:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run: arqsysia MyProject
echo.
echo For more information, visit:
echo   https://github.com/Krl05oP11/ArqSysIA
echo.

pause
