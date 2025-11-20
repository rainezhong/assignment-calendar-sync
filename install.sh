#!/bin/bash

# Academic Assistant - One-Click Installer
# Automatically sets up all dependencies and configuration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Progress tracking
show_progress() {
    local current=$1
    local total=$2
    local description=$3
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))

    printf "\r${BLUE}[%3d%%]${NC} [" $percentage
    for ((i=0; i<completed; i++)); do printf "▓"; done
    for ((i=completed; i<width; i++)); do printf "░"; done
    printf "] %s" "$description"

    if [ $current -eq $total ]; then
        echo ""
    fi
}

# System detection
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Python if needed
install_python() {
    log_info "Checking Python installation..."

    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ $(echo "$PYTHON_VERSION >= 3.7" | bc -l) -eq 1 ]]; then
            log_success "Python $PYTHON_VERSION found"
            return 0
        fi
    fi

    log_info "Installing Python 3.8+..."
    OS=$(detect_os)

    case $OS in
        "macos")
            if command_exists brew; then
                brew install python@3.9
            else
                log_error "Please install Homebrew first: https://brew.sh"
                exit 1
            fi
            ;;
        "linux")
            if command_exists apt; then
                sudo apt update && sudo apt install -y python3 python3-pip python3-venv
            elif command_exists yum; then
                sudo yum install -y python3 python3-pip
            else
                log_error "Please install Python 3.8+ manually"
                exit 1
            fi
            ;;
        *)
            log_error "Please install Python 3.8+ manually"
            exit 1
            ;;
    esac
}

# Install Node.js if needed
install_nodejs() {
    log_info "Checking Node.js installation..."

    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [[ $NODE_VERSION -ge 16 ]]; then
            log_success "Node.js v$(node --version | cut -d'v' -f2) found"
            return 0
        fi
    fi

    log_info "Installing Node.js 18..."
    OS=$(detect_os)

    case $OS in
        "macos")
            if command_exists brew; then
                brew install node@18
            else
                curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
                export NVM_DIR="$HOME/.nvm"
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
                nvm install 18
                nvm use 18
            fi
            ;;
        "linux")
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        *)
            log_error "Please install Node.js 16+ manually"
            exit 1
            ;;
    esac
}

# Install Chrome/Chromium
install_chrome() {
    log_info "Checking Chrome installation..."

    if command_exists google-chrome || command_exists chromium-browser || command_exists chromium || [[ -d "/Applications/Google Chrome.app" ]]; then
        log_success "Chrome/Chromium found"
        return 0
    fi

    log_info "Installing Chrome..."
    OS=$(detect_os)

    case $OS in
        "macos")
            log_info "Please install Chrome manually: https://www.google.com/chrome/"
            log_info "Or use: brew install --cask google-chrome"
            ;;
        "linux")
            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
            sudo apt update && sudo apt install -y google-chrome-stable
            ;;
        *)
            log_warning "Please install Chrome manually"
            ;;
    esac
}

# Setup Python virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."

    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi

    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt 2>/dev/null || pip install selenium google-api-python-client python-dotenv beautifulsoup4 requests lxml

    log_success "Python environment ready"
}

# Install Node.js dependencies
setup_node() {
    log_info "Installing Node.js dependencies..."
    npm install
    log_success "Node.js dependencies installed"
}

# Create simplified configuration
create_config() {
    log_info "Creating configuration template..."

    cat > config.yaml << 'EOF'
# Academic Assistant Configuration
# Edit this file to customize your settings

user:
  email: ""  # Your university email
  university: ""  # Your university name (optional)

# Login credentials for Gradescope
gradescope:
  method: "sso"  # Options: "sso" (recommended) or "direct"
  username: ""   # Only needed for direct login
  password: ""   # Only needed for direct login

# Calendar integration
calendars:
  # ICS files (works with all calendar apps)
  ics:
    enabled: true
    filename: "assignments.ics"

  # Google Calendar (optional)
  google:
    enabled: false
    calendar_id: "primary"  # or specific calendar ID

  # Notion (optional)
  notion:
    enabled: false
    token: ""
    database_id: ""

# Sync preferences
sync:
  frequency: "daily"        # Options: manual, daily, hourly
  time_window: 30          # Days ahead to sync (default: 30)
  auto_start: true         # Start automatically on system boot

# Course filtering
courses:
  auto_detect: true        # Automatically sync all current courses
  include_only: []         # List specific courses if auto_detect is false
  exclude: []              # Courses to always exclude

# Advanced options
advanced:
  dry_run: false           # Preview changes without applying
  debug_mode: false        # Enable detailed logging
  browser_headless: true   # Run browser in background
  retry_attempts: 3        # Number of retries on failure
EOF

    log_success "Configuration template created: config.yaml"
}

# Interactive setup wizard
run_setup_wizard() {
    log_info "Starting interactive setup wizard..."
    echo ""

    # Get user email
    read -p "Enter your university email: " user_email
    sed -i.bak "s/email: \"\"/email: \"$user_email\"/" config.yaml

    # Get university name
    read -p "Enter your university name (optional): " university
    sed -i.bak "s/university: \"\"/university: \"$university\"/" config.yaml

    # Setup Gradescope login
    echo ""
    echo "Gradescope Login Setup:"
    echo "1. SSO (Single Sign-On) - Recommended"
    echo "2. Direct login with username/password"
    read -p "Choose login method (1 or 2): " login_choice

    if [[ $login_choice == "2" ]]; then
        sed -i.bak 's/method: "sso"/method: "direct"/' config.yaml
        read -p "Gradescope username: " gs_username
        read -s -p "Gradescope password: " gs_password
        echo ""
        sed -i.bak "s/username: \"\"/username: \"$gs_username\"/" config.yaml
        sed -i.bak "s/password: \"\"/password: \"$gs_password\"/" config.yaml
    fi

    # Google Calendar setup
    echo ""
    read -p "Enable Google Calendar sync? (y/n): " enable_google
    if [[ $enable_google =~ ^[Yy]$ ]]; then
        sed -i.bak 's/enabled: false/enabled: true/' config.yaml
        log_info "Google Calendar setup will be completed on first run"
    fi

    # Clean up backup files
    rm -f config.yaml.bak

    log_success "Configuration complete!"
}

# Create desktop launcher
create_launcher() {
    log_info "Creating desktop launcher..."

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    case $(detect_os) in
        "macos")
            cat > ~/Desktop/Academic\ Assistant.command << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
./run.sh
EOF
            chmod +x ~/Desktop/Academic\ Assistant.command
            ;;
        "linux")
            cat > ~/.local/share/applications/academic-assistant.desktop << EOF
[Desktop Entry]
Name=Academic Assistant
Comment=Sync assignments to your calendar
Exec=$SCRIPT_DIR/run.sh
Icon=$SCRIPT_DIR/assets/icon.png
Terminal=false
Type=Application
Categories=Education;Office;
EOF
            chmod +x ~/.local/share/applications/academic-assistant.desktop
            ;;
    esac

    log_success "Desktop launcher created"
}

# Main installation process
main() {
    echo ""
    echo "=================================================="
    echo "  Academic Assistant - One-Click Installer"
    echo "=================================================="
    echo ""

    local total_steps=8
    local current_step=0

    # Step 1: System check
    ((current_step++))
    show_progress $current_step $total_steps "Checking system requirements"
    sleep 1

    # Step 2: Install Python
    ((current_step++))
    show_progress $current_step $total_steps "Installing Python"
    install_python

    # Step 3: Install Node.js
    ((current_step++))
    show_progress $current_step $total_steps "Installing Node.js"
    install_nodejs

    # Step 4: Install Chrome
    ((current_step++))
    show_progress $current_step $total_steps "Installing Chrome/Chromium"
    install_chrome

    # Step 5: Setup Python environment
    ((current_step++))
    show_progress $current_step $total_steps "Setting up Python environment"
    setup_venv

    # Step 6: Setup Node.js dependencies
    ((current_step++))
    show_progress $current_step $total_steps "Installing Node.js dependencies"
    setup_node

    # Step 7: Create configuration
    ((current_step++))
    show_progress $current_step $total_steps "Creating configuration"
    create_config

    # Step 8: Interactive setup
    ((current_step++))
    show_progress $current_step $total_steps "Running setup wizard"
    sleep 1

    echo ""
    echo ""
    run_setup_wizard
    create_launcher

    echo ""
    echo "=================================================="
    log_success "Installation Complete!"
    echo "=================================================="
    echo ""
    echo "Quick Start:"
    echo "  1. Run: ./run.sh"
    echo "  2. Or use the desktop launcher"
    echo "  3. Edit config.yaml to customize settings"
    echo ""
    echo "First-time setup:"
    echo "  - Test your configuration with: ./run.sh --test"
    echo "  - Run a sync preview with: ./run.sh --dry-run"
    echo ""
    echo "Need help? Check README.md or run: ./run.sh --help"
    echo ""
}

# Check if we're in the right directory
if [[ ! -f "package.json" ]] || [[ ! -d "python" ]]; then
    log_error "Please run this installer from the assignment-calendar-sync directory"
    exit 1
fi

main "$@"