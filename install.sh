#!/bin/bash

# AI Meeting Notes Generator - Installation Script
# This script automates the setup process for Linux and macOS

set -e  # Exit on any error

echo "🚀 AI Meeting Notes Generator - Installation Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt; then
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv ffmpeg curl git
        elif command_exists yum; then
            sudo yum install -y python3 python3-pip ffmpeg curl git
        elif command_exists pacman; then
            sudo pacman -S python python-pip ffmpeg curl git
        else
            log_error "Unsupported Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install python ffmpeg
        else
            log_error "Homebrew is required on macOS. Install from https://brew.sh/"
            exit 1
        fi
    else
        log_error "Unsupported operating system"
        exit 1
    fi

    log_success "System dependencies installed"
}

# Install Ollama
install_ollama() {
    log_info "Installing Ollama..."

    if command_exists ollama; then
        log_success "Ollama is already installed"
    else
        curl -fsSL https://ollama.com/install.sh | sh
        log_success "Ollama installed"
    fi

    # Start Ollama service
    log_info "Starting Ollama service..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        systemctl --user start ollama || ollama serve &
    else
        ollama serve &
    fi

    # Wait for Ollama to start
    sleep 5

    # Pull the model
    log_info "Downloading Llama 3.1 model (this may take a while)..."
    ollama pull llama3.1:8b
    log_success "Llama model downloaded"
}

# Setup Python environment
setup_python_env() {
    log_info "Setting up Python virtual environment..."

    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip

    # Install Python dependencies
    log_info "Installing Python packages..."
    pip install -r requirements.txt

    log_success "Python environment set up"
}

# Initialize database
init_database() {
    log_info "Initializing database..."

    source venv/bin/activate
    python -c "
from models.meeting import Meeting
from models.action_item import ActionItem
Meeting.init_db()
ActionItem.init_db()
print('Database initialized successfully')
    "

    log_success "Database initialized"
}

# Create configuration
create_config() {
    log_info "Creating configuration..."

    if [ ! -f ".env" ]; then
        cp .env.template .env
        log_success "Environment file created (.env)"
        log_warning "Please edit .env file to customize your configuration"
    else
        log_info "Environment file already exists"
    fi
}

# Main installation process
main() {
    echo
    log_info "Starting installation process..."
    echo

    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt not found. Please run this script from the project directory."
        exit 1
    fi

    # Install system dependencies
    install_system_deps
    echo

    # Install Ollama
    install_ollama
    echo

    # Setup Python environment
    setup_python_env
    echo

    # Initialize database
    init_database
    echo

    # Create configuration
    create_config
    echo

    log_success "Installation completed successfully!"
    echo
    echo "🎉 Setup Complete! 🎉"
    echo "==================="
    echo
    echo "To start the application:"
    echo "1. source venv/bin/activate"
    echo "2. python run.py"
    echo
    echo "Then visit: http://localhost:5000"
    echo
    echo "For Google Calendar integration:"
    echo "1. Download credentials.json from Google Cloud Console"
    echo "2. Place it in the project directory"
    echo
    log_warning "Note: Make sure Ollama is running before starting the app"
    echo "      You can start it with: ollama serve"
}

# Run main function
main "$@"