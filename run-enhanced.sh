#!/bin/bash

# Enhanced Academic Assistant Runner
# Supports both old .env and new config.yaml formats
# Includes web server for modern interface

set -e

# Colors for output
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

# Show usage
show_usage() {
    echo "Academic Assistant - Enhanced Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --sync            Run sync only (no GUI)"
    echo "  --web             Start web interface"
    echo "  --setup           Run setup wizard"
    echo "  --test            Test configuration"
    echo "  --dry-run         Preview sync without applying changes"
    echo "  --migrate         Migrate from old .env to new config.yaml"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                Start with best interface available"
    echo "  $0 --web          Start web interface on http://localhost:3000"
    echo "  $0 --sync         Run sync in background"
    echo "  $0 --test         Test your configuration"
    echo ""
}

# Check Python virtual environment
check_venv() {
    if [[ ! -d "venv" ]]; then
        log_warning "Python virtual environment not found"
        log_info "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt 2>/dev/null || pip install selenium google-api-python-client python-dotenv beautifulsoup4 requests lxml pyyaml
    else
        source venv/bin/activate
    fi
}

# Check Node.js dependencies
check_node() {
    if [[ ! -d "node_modules" ]]; then
        log_warning "Node.js dependencies not found"
        log_info "Installing dependencies..."
        npm install
    fi
}

# Migrate from .env to config.yaml
migrate_config() {
    log_info "Migrating configuration from .env to config.yaml..."

    if [[ ! -f ".env" ]]; then
        log_error "No .env file found to migrate"
        return 1
    fi

    if [[ -f "config.yaml" ]]; then
        read -p "config.yaml already exists. Overwrite? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            log_info "Migration cancelled"
            return 0
        fi
    fi

    # Run Python migration script
    python3 -c "
from python.config_manager import create_config_from_legacy_env
config = create_config_from_legacy_env()
print('Migration completed successfully!')
"
    log_success "Configuration migrated to config.yaml"
    log_info "Old .env file backed up to .env.backup"
}

# Test configuration
test_config() {
    log_info "Testing configuration..."

    # Check if config exists
    if [[ -f "config.yaml" ]]; then
        python3 -c "
from python.config_manager import ConfigManager
config = ConfigManager()
config.load()
is_valid, issues = config.validate()

if is_valid:
    print('✅ Configuration is valid!')
else:
    print('❌ Configuration has issues:')
    for issue in issues:
        print(f'  - {issue}')
        exit(1)
"
    elif [[ -f ".env" ]]; then
        log_warning "Found old .env configuration"
        log_info "Run with --migrate to upgrade to the new format"
        # Test old format
        python3 python/main.py --test 2>/dev/null || {
            log_error "Configuration test failed"
            return 1
        }
    else {
        log_error "No configuration found"
        log_info "Run with --setup to create configuration"
        return 1
    fi

    log_success "Configuration test passed!"
}

# Run setup wizard
run_setup() {
    log_info "Starting setup wizard..."

    # Check if we should migrate first
    if [[ -f ".env" && ! -f "config.yaml" ]]; then
        read -p "Found old .env configuration. Migrate to new format? (Y/n): " migrate
        if [[ ! $migrate =~ ^[Nn]$ ]]; then
            migrate_config
            return 0
        fi
    fi

    # Run Python setup
    python3 -c "
from python.config_manager import ConfigManager
import yaml

config = ConfigManager()

print('Academic Assistant Setup Wizard')
print('=' * 40)
print()

# Get user email
email = input('Enter your university email: ').strip()
config.set('user.email', email)

# Auto-detect university
university = config.auto_detect_university()
if university:
    print(f'Detected university: {university}')
    use_detected = input('Use detected university? (Y/n): ').strip()
    if not use_detected.lower().startswith('n'):
        config.set('user.university', university)
    else:
        custom_university = input('Enter university name: ').strip()
        config.set('user.university', custom_university)
else:
    university = input('Enter university name (optional): ').strip()
    if university:
        config.set('user.university', university)

print()
print('Gradescope Login Setup:')
print('1. SSO (Single Sign-On) - Recommended')
print('2. Direct login with username/password')
choice = input('Choose login method (1 or 2): ').strip()

if choice == '2':
    config.set('gradescope.method', 'direct')
    username = input('Gradescope username: ').strip()
    password = input('Gradescope password: ').strip()
    config.set('gradescope.username', username)
    config.set('gradescope.password', password)
else:
    config.set('gradescope.method', 'sso')

print()
google_sync = input('Enable Google Calendar sync? (y/N): ').strip()
if google_sync.lower().startswith('y'):
    config.set('calendars.google.enabled', True)
    print('Google Calendar setup will be completed on first sync')

print()
notion_sync = input('Enable Notion Calendar sync? (y/N): ').strip()
if notion_sync.lower().startswith('y'):
    config.set('calendars.notion.enabled', True)
    token = input('Notion API token: ').strip()
    database_id = input('Notion database ID: ').strip()
    config.set('calendars.notion.token', token)
    config.set('calendars.notion.database_id', database_id)

config.save()
print()
print('✅ Setup completed successfully!')
print('Configuration saved to config.yaml')
print()
print('Next steps:')
print('  1. Test your configuration: ./run-enhanced.sh --test')
print('  2. Run your first sync: ./run-enhanced.sh --sync')
print('  3. Start the web interface: ./run-enhanced.sh --web')
"
}

# Start web server
start_web_server() {
    log_info "Starting web interface..."

    # Check if port 3000 is available
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "Port 3000 is already in use"
        log_info "Trying to find an available port..."

        for port in {3001..3010}; do
            if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                WEB_PORT=$port
                break
            fi
        done

        if [[ -z "$WEB_PORT" ]]; then
            log_error "No available ports found"
            return 1
        fi
    else
        WEB_PORT=3000
    fi

    # Create simple web server
    cat > web_server.js << 'EOF'
const express = require('express');
const path = require('path');
const { exec } = require('child_process');
const fs = require('fs');
const yaml = require('js-yaml');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static('web'));
app.use(express.json());

// API endpoints
app.get('/api/config', (req, res) => {
    try {
        if (fs.existsSync('config.yaml')) {
            const config = yaml.load(fs.readFileSync('config.yaml', 'utf8'));
            res.json(config);
        } else {
            res.status(404).json({ error: 'Configuration not found' });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/config', (req, res) => {
    try {
        const yamlStr = yaml.dump(req.body);
        fs.writeFileSync('config.yaml', yamlStr);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/sync', (req, res) => {
    exec('python3 python/main.py', (error, stdout, stderr) => {
        if (error) {
            res.status(500).json({ error: error.message, stderr });
        } else {
            res.json({ success: true, output: stdout });
        }
    });
});

app.post('/api/test', (req, res) => {
    exec('python3 python/main.py --test', (error, stdout, stderr) => {
        if (error) {
            res.status(500).json({ error: error.message, stderr });
        } else {
            res.json({ success: true, output: stdout });
        }
    });
});

app.listen(PORT, () => {
    console.log(`Academic Assistant web interface running at http://localhost:${PORT}`);
});
EOF

    # Install required packages if not present
    if [[ ! -f "package.json" ]] || ! grep -q "express" package.json; then
        log_info "Installing web server dependencies..."
        npm init -y >/dev/null 2>&1
        npm install express js-yaml >/dev/null 2>&1
    fi

    # Start the server
    PORT=$WEB_PORT node web_server.js &
    WEB_PID=$!

    # Store PID for cleanup
    echo $WEB_PID > .web_server.pid

    log_success "Web interface started at http://localhost:$WEB_PORT"

    # Open browser if available
    if command -v open >/dev/null 2>&1; then
        open "http://localhost:$WEB_PORT"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:$WEB_PORT"
    else
        log_info "Open http://localhost:$WEB_PORT in your web browser"
    fi

    # Wait for Ctrl+C
    trap "kill $WEB_PID 2>/dev/null; rm -f .web_server.pid; exit 0" INT
    wait $WEB_PID
}

# Run sync only
run_sync() {
    log_info "Starting sync..."

    if [[ -f "config.yaml" ]]; then
        # Use new config system
        python3 -c "
from python.config_manager import ConfigManager
from python.main import main

config = ConfigManager()
config.load()

# Convert to legacy env for compatibility
env_vars = config.to_legacy_env()
import os
for key, value in env_vars.items():
    os.environ[key] = value

# Run sync
main()
"
    else
        # Use legacy system
        python3 python/main.py
    fi
}

# Main function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --sync)
                MODE="sync"
                shift
                ;;
            --web)
                MODE="web"
                shift
                ;;
            --setup)
                MODE="setup"
                shift
                ;;
            --test)
                MODE="test"
                shift
                ;;
            --dry-run)
                export DRY_RUN=true
                MODE="sync"
                shift
                ;;
            --migrate)
                MODE="migrate"
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Default mode: intelligent selection
    if [[ -z "$MODE" ]]; then
        if [[ -f "config.yaml" ]] || [[ -f ".env" ]]; then
            MODE="web"
        else
            MODE="setup"
        fi
    fi

    # Check prerequisites
    log_info "Checking prerequisites..."
    check_venv

    if [[ "$MODE" == "web" ]]; then
        check_node
    fi

    # Execute based on mode
    case $MODE in
        "sync")
            run_sync
            ;;
        "web")
            start_web_server
            ;;
        "setup")
            run_setup
            ;;
        "test")
            test_config
            ;;
        "migrate")
            migrate_config
            ;;
        *)
            log_error "Invalid mode: $MODE"
            exit 1
            ;;
    esac
}

# Check if we're in the right directory
if [[ ! -f "package.json" ]] && [[ ! -d "python" ]]; then
    log_error "Please run this script from the assignment-calendar-sync directory"
    exit 1
fi

main "$@"