@echo off
REM AI Meeting Notes Generator - Windows Installation Script
REM This script automates the setup process for Windows

echo.
echo 🚀 AI Meeting Notes Generator - Windows Installation
echo ==================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found
    echo Please run this script from the project directory
    pause
    exit /b 1
)

echo [INFO] Creating Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo [INFO] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo [INFO] Creating configuration file...
if not exist ".env" (
    copy .env.template .env
    echo [SUCCESS] Environment file created (.env)
    echo [WARNING] Please edit .env file to customize your configuration
) else (
    echo [INFO] Environment file already exists
)

echo.
echo [SUCCESS] Installation completed!
echo.
echo 🎉 Setup Complete! 🎉
echo ==================
echo.
echo Before running the application:
echo 1. Download and install Ollama from https://ollama.com
echo 2. Run: ollama pull llama3.1:8b
echo 3. Start Ollama service: ollama serve
echo.
echo To start the application:
echo 1. venv\Scripts\activate.bat
echo 2. python run.py
echo.
echo Then visit: http://localhost:5000
echo.
echo For Google Calendar integration:
echo 1. Download credentials.json from Google Cloud Console
echo 2. Place it in the project directory
echo.
pause