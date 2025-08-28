#!/usr/bin/env node

/**
 * Build script for Assignment Calendar Sync Electron app
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

function log(color, message) {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function logStep(step, total, message) {
    log('blue', `\n[${step}/${total}] ${message}`);
}

function logSuccess(message) {
    log('green', `✅ ${message}`);
}

function logError(message) {
    log('red', `❌ ${message}`);
}

function logWarning(message) {
    log('yellow', `⚠️  ${message}`);
}

function runCommand(command, args = [], options = {}) {
    return new Promise((resolve, reject) => {
        const proc = spawn(command, args, { stdio: 'inherit', ...options });
        
        proc.on('close', (code) => {
            if (code === 0) {
                resolve(code);
            } else {
                reject(new Error(`Command failed with code ${code}: ${command} ${args.join(' ')}`));
            }
        });
        
        proc.on('error', (error) => {
            reject(error);
        });
    });
}

function checkFile(filePath, description) {
    if (fs.existsSync(filePath)) {
        logSuccess(`${description} found`);
        return true;
    } else {
        logError(`${description} missing: ${filePath}`);
        return false;
    }
}

async function checkPrerequisites() {
    logStep(1, 6, 'Checking prerequisites...');
    
    let allGood = true;
    
    // Check Node.js/npm
    try {
        await runCommand('npm', ['--version'], { stdio: 'pipe' });
        logSuccess('npm is available');
    } catch (error) {
        logError('npm not found. Please install Node.js');
        allGood = false;
    }
    
    // Check Python
    try {
        await runCommand('python3', ['--version'], { stdio: 'pipe' });
        logSuccess('Python 3 is available');
    } catch (error) {
        logError('Python 3 not found. Please install Python 3.7+');
        allGood = false;
    }
    
    // Check required files
    allGood = checkFile('package.json', 'package.json') && allGood;
    allGood = checkFile('electron/main.js', 'Electron main process') && allGood;
    allGood = checkFile('renderer/index.html', 'Frontend HTML') && allGood;
    allGood = checkFile('python/main.py', 'Python main script') && allGood;
    allGood = checkFile('python/requirements.txt', 'Python requirements') && allGood;
    
    if (!allGood) {
        throw new Error('Prerequisites check failed');
    }
    
    return true;
}

async function installDependencies() {
    logStep(2, 6, 'Installing Node.js dependencies...');
    
    try {
        await runCommand('npm', ['install']);
        logSuccess('Node.js dependencies installed');
    } catch (error) {
        throw new Error('Failed to install Node.js dependencies: ' + error.message);
    }
}

async function installPythonDependencies() {
    logStep(3, 6, 'Installing Python dependencies...');
    
    try {
        await runCommand('pip3', ['install', '-r', 'requirements.txt'], { cwd: 'python' });
        logSuccess('Python dependencies installed');
    } catch (error) {
        logWarning('Failed to install Python dependencies globally');
        log('yellow', 'You may need to install them manually:');
        log('yellow', '  cd python && pip3 install -r requirements.txt');
    }
}

async function createBuildAssets() {
    logStep(4, 6, 'Creating build assets...');
    
    // Create build directory
    if (!fs.existsSync('build')) {
        fs.mkdirSync('build');
        log('cyan', 'Created build directory');
    }
    
    // Create simple icon files (placeholder)
    const iconPaths = {
        'build/icon.png': createPngIcon(),
        'build/icon.ico': createIcoIcon(),
        'build/icon.icns': createIcnsIcon()
    };
    
    for (const [iconPath, iconData] of Object.entries(iconPaths)) {
        if (!fs.existsSync(iconPath)) {
            // For now, just create placeholder files
            // In a real app, you'd want proper icon files
            fs.writeFileSync(iconPath, iconData);
            log('cyan', `Created ${iconPath}`);
        }
    }
    
    logSuccess('Build assets ready');
}

function createPngIcon() {
    // This is a minimal 1x1 pixel PNG (placeholder)
    return Buffer.from([
        0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
        0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89, 0x00, 0x00, 0x00,
        0x0d, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9c, 0x63, 0xf8, 0xcf, 0x00, 0x00,
        0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44,
        0xae, 0x42, 0x60, 0x82
    ]);
}

function createIcoIcon() {
    // Minimal ICO file (placeholder)
    return Buffer.from([0x00, 0x00, 0x01, 0x00, 0x01, 0x00]);
}

function createIcnsIcon() {
    // Minimal ICNS file (placeholder)
    return Buffer.from([0x69, 0x63, 0x6e, 0x73, 0x00, 0x00, 0x00, 0x08]);
}

async function runBuild() {
    logStep(5, 6, 'Building Electron application...');
    
    const platform = process.argv[2] || 'current';
    let buildCommand = [];
    
    switch (platform) {
        case 'mac':
            buildCommand = ['run', 'build:mac'];
            break;
        case 'win':
            buildCommand = ['run', 'build:win'];
            break;
        case 'linux':
            buildCommand = ['run', 'build:linux'];
            break;
        case 'all':
            buildCommand = ['run', 'build:all'];
            break;
        default:
            buildCommand = ['run', 'build'];
            break;
    }
    
    try {
        await runCommand('npm', buildCommand);
        logSuccess('Build completed successfully!');
    } catch (error) {
        throw new Error('Build failed: ' + error.message);
    }
}

async function showResults() {
    logStep(6, 6, 'Build complete!');
    
    log('cyan', '\n📦 Build Results:');
    
    if (fs.existsSync('dist')) {
        const distFiles = fs.readdirSync('dist');
        distFiles.forEach(file => {
            const filePath = path.join('dist', file);
            const stats = fs.statSync(filePath);
            const sizeMB = (stats.size / (1024 * 1024)).toFixed(1);
            log('green', `  ✓ ${file} (${sizeMB} MB)`);
        });
    }
    
    log('cyan', '\n🚀 Next Steps:');
    log('white', '  1. Test the built application');
    log('white', '  2. Distribute to users');
    log('white', '  3. Celebrate! 🎉');
    
    log('cyan', '\n💡 Tips:');
    log('white', '  - Test on target platforms before distributing');
    log('white', '  - Consider code signing for production releases');
    log('white', '  - Set up auto-updates for easier maintenance');
}

async function main() {
    try {
        log('magenta', '🔨 Assignment Calendar Sync - Build Script');
        log('magenta', '============================================\n');
        
        await checkPrerequisites();
        await installDependencies();
        await installPythonDependencies();
        await createBuildAssets();
        await runBuild();
        await showResults();
        
        log('green', '\n🎉 Build completed successfully!\n');
        process.exit(0);
        
    } catch (error) {
        logError('\n❌ Build failed:');
        logError(error.message);
        
        if (error.stack && process.env.DEBUG) {
            console.error(error.stack);
        }
        
        log('cyan', '\n💡 Troubleshooting:');
        log('white', '  - Ensure Node.js and Python 3 are installed');
        log('white', '  - Check that all required files are present');
        log('white', '  - Try running: npm install');
        log('white', '  - Run with DEBUG=1 for detailed error info');
        
        process.exit(1);
    }
}

// Handle process signals
process.on('SIGINT', () => {
    log('yellow', '\n⚠️  Build interrupted by user');
    process.exit(1);
});

process.on('SIGTERM', () => {
    log('yellow', '\n⚠️  Build terminated');
    process.exit(1);
});

// Run the build
if (require.main === module) {
    main();
}