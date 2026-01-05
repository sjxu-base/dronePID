#!/bin/bash
set -e  # return on error

# Color codes for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
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

# Check python, pip3 and venv module
check_requirements() {
    log_info "Checking Python version and os requirements..."
    
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        log_success "Python version $PYTHON_VERSION found."
    else
        log_error "Python3 not found. Please install Python 3.6 or higher."
        exit 1
    fi
    
    # Check pip3
    if command -v pip3 &>/dev/null; then
        log_success "pip3 found"
    else
        log_warning "pip3 not found, please install pip3."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install python3
        else
            log_error "Unsupported OS. Please install pip3 manually."
            exit 1
        fi
    fi
    
    # Check venv module
    if python3 -c "import venv" &>/dev/null; then
        log_success "Python venv import successful."
    else
        log_error "Python venv modeule not found. Please ensure you have Python 3.3+ installed."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    local venv_name="$1"
    
    log_info "Creating Python venv: $venv_name"
    
    if [ -d "$venv_name" ]; then
        log_warning "Virtual environment '$venv_name' already exists."
        read -p "Should we recreate venv? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$venv_name"
            python3 -m venv "$venv_name"
            log_success "Virtual environment '$venv_name' recreated successfully."
        else
            log_info "Using existing virtual environment."
        fi
    else
        python3 -m venv "$venv_name"
        log_success "Virtual environment '$venv_name' created successfully"
    fi
}

# Activate virtual environment
activate_venv() {
    local venv_name="$1"
    
    log_info "Activating virtual environment: $venv_name"
    
    # Check if already in a virtual environment
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ -f "$venv_name/bin/activate" ]; then
            source "$venv_name/bin/activate"
            log_success "Virtual environment activated."
        else
            log_error "Cannot find activation script: $venv_name/bin/activate"
            exit 1
        fi
    else
        log_info "Already in virtual environment: $VIRTUAL_ENV"
    fi
}

# pip Upgrade
upgrade_pip() {
    log_info "Upgrading pip..."
    pip install --upgrade pip
    log_success "pip upgraded successfully"
}

# generate requirements.txt
generate_requirements() {
    log_info "Regenerating requirements.txt..."
    if [ -f "requirements.txt" ]; then
        log_warning "requirements.txt already exists."
        read -p "Regenerate requirements.txt? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pip freeze > requirements.txt
            log_success "requirements.txt regenerated successfully"
        else
            log_info "Using existing requirements.txt"
        fi
    else
        # Install pipreqs if not present
        if ! command -v pipreqs &>/dev/null; then
            log_info "Installing pipreqs to automatically detect dependencies..."
            pip install pipreqs
        fi
        
        # 使用pipreqs生成requirements.txt
        if pipreqs . --force 2>/dev/null; then
            log_success "requirements.txt regenerated successfully"
        else
            log_warning "pipreqs failed, using pip freeze"
            pip freeze > requirements.txt
        fi
    fi
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        log_warning "requirements.txt does not exist, trying to generate..."
        generate_requirements
    fi
    
    # Install basic dependencies
    log_info "Installing basic dependencies..."
    pip install numpy matplotlib scipy

    # Install dependencies from requirements.txt
    if [ -f "requirements.txt" ]; then
        log_info "Installing dependencies from requirements.txt..."
        pip install -r requirements.txt
    fi

    # Install development dependencies (optional)
    read -p "if you want to install development dependencies? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installing development dependencies..."
        pip install pylint autopep8 jupyter ipython
    fi
    
    log_success "All dependencies installed successfully."
}

# Main script execution
check_requirements
create_venv "pid_venv"
activate_venv "pid_venv"
upgrade_pip
install_dependencies