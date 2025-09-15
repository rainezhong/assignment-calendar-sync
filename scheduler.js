#!/usr/bin/env node
/**
 * Assignment Calendar Sync - Automated Scheduler
 * Runs daily sync at specified time
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const SYNC_TIME = '08:00'; // Daily sync time (24-hour format)
const PYTHON_SCRIPT = path.join(__dirname, 'python', 'combined_sync.py');
const LOG_FILE = path.join(__dirname, 'logs', 'scheduler.log');

function log(message) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;
    
    console.log(message);
    
    // Ensure logs directory exists
    const logsDir = path.dirname(LOG_FILE);
    if (!fs.existsSync(logsDir)) {
        fs.mkdirSync(logsDir, { recursive: true });
    }
    
    fs.appendFileSync(LOG_FILE, logEntry);
}

function runSync() {
    log('🚀 Starting daily assignment sync...');
    
    const python = spawn('python3', [PYTHON_SCRIPT], {
        cwd: path.join(__dirname, 'python'),
        stdio: ['pipe', 'pipe', 'pipe']
    });
    
    python.stdout.on('data', (data) => {
        log(`SYNC: ${data.toString().trim()}`);
    });
    
    python.stderr.on('data', (data) => {
        log(`ERROR: ${data.toString().trim()}`);
    });
    
    python.on('close', (code) => {
        if (code === 0) {
            log('✅ Daily sync completed successfully');
        } else {
            log(`❌ Daily sync failed with exit code ${code}`);
        }
        scheduleNext();
    });
}

function scheduleNext() {
    const now = new Date();
    const [hours, minutes] = SYNC_TIME.split(':').map(Number);
    
    const nextSync = new Date();
    nextSync.setHours(hours, minutes, 0, 0);
    
    // If time has passed today, schedule for tomorrow
    if (nextSync <= now) {
        nextSync.setDate(nextSync.getDate() + 1);
    }
    
    const msUntilSync = nextSync.getTime() - now.getTime();
    const hoursUntil = Math.floor(msUntilSync / (1000 * 60 * 60));
    const minutesUntil = Math.floor((msUntilSync % (1000 * 60 * 60)) / (1000 * 60));
    
    log(`⏰ Next sync scheduled for ${nextSync.toLocaleString()} (in ${hoursUntil}h ${minutesUntil}m)`);
    
    setTimeout(runSync, msUntilSync);
}

// Start the scheduler
log('🤖 Assignment Calendar Sync Scheduler started');
log(`📅 Daily sync time: ${SYNC_TIME}`);
scheduleNext();

// Keep the process running
process.on('SIGINT', () => {
    log('🛑 Scheduler stopped');
    process.exit(0);
});

process.on('SIGTERM', () => {
    log('🛑 Scheduler terminated');
    process.exit(0);
});