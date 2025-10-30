#!/bin/bash

# ArqSysIA Installation Script for Linux/Mac
# Author: Carlos
# Description: Automated installation script for ArqSysIA

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check Python version
check_python() {
    print_info "Checking Python version..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11 or higher."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    required_version="3.11"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
        print_error "Python $python_version found, but 3.11+ is required."
        exit 1
    fi
    
    print_success "Python $python_version found"
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -e .
    print_success "Dependencies installed"
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."
    if arqsysia --version &> /dev/null; then
        print_success "ArqSysIA installed successfully!"
        arqsysia --version
    else
        print_error "Installation verification failed"
        exit 1
    fi
}

# Run tests
run_tests() {
    read -p "Do you want to run tests? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Running tests..."
        pytest tests/ -v
        print_success "All tests passed!"
    fi
}

# Main installation flow
main() {
    echo "========================================"
    echo "  ArqSysIA Installation Script"
    echo "========================================"
    echo ""
    
    check_python
    create_venv
    activate_venv
    install_dependencies
    verify_installation
    run_tests
    
    echo ""
    echo "========================================"
    print_success "Installation complete!"
    echo "========================================"
    echo ""
    echo "To use ArqSysIA:"
    echo "  1. Activate virtual environment: source venv/bin/activate"
    echo "  2. Run: arqsysia MyProject"
    echo ""
    echo "For more information, visit:"
    echo "  https://github.com/Krl05oP11/ArqSysIA"
    echo ""
}

# Run main
main
