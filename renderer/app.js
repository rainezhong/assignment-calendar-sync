const { ipcRenderer } = require('electron');

// Application State
let currentScreen = 'dashboard';
let isLoading = false;
let syncInProgress = false;

// DOM Elements
let elements = {};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    setupEventListeners();
    loadSettings();
    checkPythonStatus();
    loadAppInfo();
    addRecentActivity('ℹ️', 'Application started. Configure settings to begin syncing.');
});

function initializeElements() {
    // Navigation elements
    elements.navDashboard = document.getElementById('nav-dashboard');
    elements.navSettings = document.getElementById('nav-settings');
    
    // Screen elements
    elements.dashboardScreen = document.getElementById('dashboard-screen');
    elements.settingsScreen = document.getElementById('settings-screen');
    
    // Status elements
    elements.statusDot = document.getElementById('status-dot');
    elements.statusText = document.getElementById('status-text');
    elements.lastSync = document.getElementById('last-sync');
    elements.eventsCreated = document.getElementById('events-created');
    elements.eventsSkipped = document.getElementById('events-skipped');
    elements.recentActivity = document.getElementById('recent-activity');
    
    // Action buttons
    elements.syncNowBtn = document.getElementById('sync-now-btn');
    elements.dryRunBtn = document.getElementById('dry-run-btn');
    
    // Quick settings
    elements.quickDays = document.getElementById('quick-days');
    elements.verboseMode = document.getElementById('verbose-mode');
    
    // Settings form elements
    elements.gradescopeEmail = document.getElementById('gradescope-email');
    elements.gradescopePassword = document.getElementById('gradescope-password');
    elements.googleClientId = document.getElementById('google-client-id');
    elements.googleClientSecret = document.getElementById('google-client-secret');
    elements.googleCalendarId = document.getElementById('google-calendar-id');
    elements.syncDaysAhead = document.getElementById('sync-days-ahead');
    elements.reminderMinutes = document.getElementById('reminder-minutes');
    elements.timezone = document.getElementById('timezone');
    elements.debugMode = document.getElementById('debug-mode');
    
    // Button elements
    elements.testGradescopeBtn = document.getElementById('test-gradescope-btn');
    elements.testCalendarBtn = document.getElementById('test-calendar-btn');
    elements.saveSettingsBtn = document.getElementById('save-settings-btn');
    elements.testConfigBtn = document.getElementById('test-config-btn');
    
    // Status elements
    elements.gradescopeStatus = document.getElementById('gradescope-status');
    elements.calendarStatus = document.getElementById('calendar-status');
    elements.settingsStatus = document.getElementById('settings-status');
    
    // Progress modal elements
    elements.progressModal = document.getElementById('progress-modal');
    elements.progressTitle = document.getElementById('progress-title');
    elements.progressStatus = document.getElementById('progress-status');
    elements.progressFill = document.getElementById('progress-fill');
    elements.progressLog = document.getElementById('progress-log');
    elements.cancelSyncBtn = document.getElementById('cancel-sync-btn');
    elements.closeProgressBtn = document.getElementById('close-progress-btn');
    
    // Footer elements
    elements.appVersion = document.getElementById('app-version');
    elements.pythonStatus = document.getElementById('python-status');
    
    // External links
    elements.googleConsoleLink = document.getElementById('google-console-link');
}

function setupEventListeners() {
    // Navigation
    elements.navDashboard.onclick = () => switchScreen('dashboard');
    elements.navSettings.onclick = () => switchScreen('settings');
    
    // Dashboard actions
    elements.syncNowBtn.onclick = () => runSync(false);
    elements.dryRunBtn.onclick = () => runSync(true);
    
    // Settings actions
    elements.testGradescopeBtn.onclick = testGradescope;
    elements.testCalendarBtn.onclick = testCalendar;
    elements.saveSettingsBtn.onclick = saveSettings;
    elements.testConfigBtn.onclick = testConfiguration;
    
    // Progress modal
    elements.cancelSyncBtn.onclick = cancelSync;
    elements.closeProgressBtn.onclick = closeProgressModal;
    
    // Quick settings sync with main settings
    elements.quickDays.onchange = (e) => {
        elements.syncDaysAhead.value = e.target.value;
    };
    
    // External links
    elements.googleConsoleLink.onclick = (e) => {
        e.preventDefault();
        openExternal('https://console.cloud.google.com/');
    };
    
    // Listen for Python process output
    ipcRenderer.on('sync-output', handleSyncOutput);
    ipcRenderer.on('sync-complete', handleSyncComplete);
}

function switchScreen(screenName) {
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.screen').forEach(screen => screen.classList.remove('active'));
    
    // Show selected screen
    if (screenName === 'dashboard') {
        elements.navDashboard.classList.add('active');
        elements.dashboardScreen.classList.add('active');
    } else if (screenName === 'settings') {
        elements.navSettings.classList.add('active');
        elements.settingsScreen.classList.add('active');
    }
    
    currentScreen = screenName;
}

async function loadSettings() {
    try {
        const result = await ipcRenderer.invoke('load-settings');
        if (result.success) {
            const settings = result.settings;
            
            // Populate form fields
            elements.gradescopeEmail.value = settings.gradescopeEmail || '';
            elements.gradescopePassword.value = settings.gradescopePassword || '';
            elements.googleClientId.value = settings.googleClientId || '';
            elements.googleClientSecret.value = settings.googleClientSecret || '';
            elements.googleCalendarId.value = settings.googleCalendarId || 'primary';
            elements.syncDaysAhead.value = settings.syncDaysAhead || 30;
            elements.reminderMinutes.value = settings.reminderMinutes || 60;
            elements.timezone.value = settings.timezone || 'America/New_York';
            elements.debugMode.checked = settings.debugMode || false;
            
            // Sync quick settings
            elements.quickDays.value = settings.syncDaysAhead || 30;
            
            addRecentActivity('✅', 'Settings loaded successfully.');
        }
    } catch (error) {
        console.error('Error loading settings:', error);
        addRecentActivity('❌', 'Failed to load settings: ' + error.message);
    }
}

async function saveSettings() {
    if (isLoading) return;
    
    setLoading(elements.saveSettingsBtn, true);
    hideStatus(elements.settingsStatus);
    
    try {
        const settings = {
            gradescopeEmail: elements.gradescopeEmail.value.trim(),
            gradescopePassword: elements.gradescopePassword.value,
            googleClientId: elements.googleClientId.value.trim(),
            googleClientSecret: elements.googleClientSecret.value.trim(),
            googleCalendarId: elements.googleCalendarId.value.trim() || 'primary',
            syncDaysAhead: parseInt(elements.syncDaysAhead.value) || 30,
            reminderMinutes: parseInt(elements.reminderMinutes.value) || 60,
            timezone: elements.timezone.value,
            debugMode: elements.debugMode.checked
        };
        
        const result = await ipcRenderer.invoke('save-settings', settings);
        
        if (result.success) {
            showStatus(elements.settingsStatus, 'success', 'Settings saved successfully!');
            
            // Sync quick settings
            elements.quickDays.value = settings.syncDaysAhead;
            
            addRecentActivity('✅', 'Settings saved and configuration updated.');
        } else {
            showStatus(elements.settingsStatus, 'error', 'Failed to save settings: ' + (result.error || 'Unknown error'));
            addRecentActivity('❌', 'Failed to save settings.');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showStatus(elements.settingsStatus, 'error', 'Error saving settings: ' + error.message);
        addRecentActivity('❌', 'Error saving settings: ' + error.message);
    } finally {
        setLoading(elements.saveSettingsBtn, false);
    }
}

async function testGradescope() {
    if (isLoading) return;
    
    setLoading(elements.testGradescopeBtn, true);
    showStatus(elements.gradescopeStatus, 'loading', 'Testing Gradescope login...');
    
    try {
        // First save current settings
        await saveSettings();
        
        // Then test configuration
        const result = await ipcRenderer.invoke('test-config');
        
        if (result.success) {
            showStatus(elements.gradescopeStatus, 'success', 'Gradescope login test successful!');
            addRecentActivity('✅', 'Gradescope login test passed.');
        } else {
            showStatus(elements.gradescopeStatus, 'error', 'Test failed: ' + (result.error || 'Unknown error'));
            addRecentActivity('❌', 'Gradescope login test failed.');
        }
    } catch (error) {
        console.error('Error testing Gradescope:', error);
        showStatus(elements.gradescopeStatus, 'error', 'Test error: ' + error.message);
        addRecentActivity('❌', 'Error testing Gradescope: ' + error.message);
    } finally {
        setLoading(elements.testGradescopeBtn, false);
    }
}

async function testCalendar() {
    if (isLoading) return;
    
    setLoading(elements.testCalendarBtn, true);
    showStatus(elements.calendarStatus, 'loading', 'Testing Google Calendar connection...');
    
    try {
        // First save current settings
        await saveSettings();
        
        // Then test configuration
        const result = await ipcRenderer.invoke('test-config');
        
        if (result.success) {
            showStatus(elements.calendarStatus, 'success', 'Google Calendar connection successful!');
            addRecentActivity('✅', 'Google Calendar connection test passed.');
        } else {
            showStatus(elements.calendarStatus, 'error', 'Test failed: ' + (result.error || 'Unknown error'));
            addRecentActivity('❌', 'Google Calendar connection test failed.');
        }
    } catch (error) {
        console.error('Error testing calendar:', error);
        showStatus(elements.calendarStatus, 'error', 'Test error: ' + error.message);
        addRecentActivity('❌', 'Error testing calendar: ' + error.message);
    } finally {
        setLoading(elements.testCalendarBtn, false);
    }
}

async function testConfiguration() {
    if (isLoading) return;
    
    setLoading(elements.testConfigBtn, true);
    showStatus(elements.settingsStatus, 'loading', 'Testing full configuration...');
    
    try {
        // First save current settings
        await saveSettings();
        
        const result = await ipcRenderer.invoke('test-config');
        
        if (result.success) {
            showStatus(elements.settingsStatus, 'success', 'Configuration test passed! Ready to sync.');
            updateStatus('ready', 'Ready to sync');
            addRecentActivity('✅', 'Full configuration test passed. Ready to sync assignments.');
        } else {
            showStatus(elements.settingsStatus, 'error', 'Configuration test failed: ' + (result.error || 'Unknown error'));
            updateStatus('error', 'Configuration error');
            addRecentActivity('❌', 'Configuration test failed.');
        }
    } catch (error) {
        console.error('Error testing configuration:', error);
        showStatus(elements.settingsStatus, 'error', 'Test error: ' + error.message);
        updateStatus('error', 'Test error');
        addRecentActivity('❌', 'Error testing configuration: ' + error.message);
    } finally {
        setLoading(elements.testConfigBtn, false);
    }
}

async function runSync(dryRun = false) {
    if (syncInProgress) return;
    
    try {
        // Save settings first
        await saveSettings();
        
        const options = {
            dryRun: dryRun,
            verbose: elements.verboseMode.checked,
            days: parseInt(elements.quickDays.value),
            all: false
        };
        
        showProgressModal(dryRun ? 'Dry Run - Preview Mode' : 'Syncing Assignments');
        syncInProgress = true;
        updateStatus('syncing', 'Syncing...');
        setProgress(0, 'Initializing sync process...');
        clearProgressLog();
        
        addRecentActivity('🔄', dryRun ? 'Starting dry run preview...' : 'Starting assignment sync...');
        
        const result = await ipcRenderer.invoke('run-sync', options);
        
        // The actual progress is handled by the sync-output and sync-complete events
        
    } catch (error) {
        console.error('Error running sync:', error);
        handleSyncComplete({ success: false, error: error.message });
        addRecentActivity('❌', 'Sync failed to start: ' + error.message);
    }
}

async function cancelSync() {
    try {
        const result = await ipcRenderer.invoke('cancel-sync');
        if (result.success) {
            addRecentActivity('⛔', 'Sync cancelled by user.');
        }
    } catch (error) {
        console.error('Error cancelling sync:', error);
    }
}

function handleSyncOutput(event, data) {
    if (data.type === 'stdout') {
        appendToProgressLog(data.data);
        
        // Parse output for progress indicators
        const text = data.data.toLowerCase();
        if (text.includes('step 1') || text.includes('scraping')) {
            setProgress(25, 'Scraping assignments from Gradescope...');
        } else if (text.includes('step 2') || text.includes('parsing')) {
            setProgress(50, 'Processing assignment dates...');
        } else if (text.includes('step 3') || text.includes('filtering')) {
            setProgress(75, 'Filtering assignments...');
        } else if (text.includes('step 4') || text.includes('creating') || text.includes('syncing')) {
            setProgress(90, 'Creating calendar events...');
        }
    } else if (data.type === 'stderr') {
        appendToProgressLog(`ERROR: ${data.data}`, 'error');
    }
}

function handleSyncComplete(event, data) {
    syncInProgress = false;
    
    if (data.success) {
        setProgress(100, 'Sync completed successfully!');
        updateStatus('success', 'Sync completed');
        addRecentActivity('✅', 'Sync completed successfully.');
        
        // Parse output for statistics
        const output = data.output || '';
        const createdMatch = output.match(/Events created:\s*(\d+)/i);
        const skippedMatch = output.match(/Events skipped:\s*(\d+)/i);
        
        if (createdMatch) {
            elements.eventsCreated.textContent = createdMatch[1];
        }
        if (skippedMatch) {
            elements.eventsSkipped.textContent = skippedMatch[1];
        }
        
        // Update last sync time
        elements.lastSync.textContent = new Date().toLocaleString();
        
    } else {
        setProgress(0, 'Sync failed');
        updateStatus('error', 'Sync failed');
        addRecentActivity('❌', 'Sync failed: ' + (data.error || 'Unknown error'));
        appendToProgressLog(`\nSYNC FAILED: ${data.error || 'Unknown error'}`, 'error');
    }
    
    // Auto-close progress modal after a delay (unless there was an error)
    if (data.success) {
        setTimeout(() => {
            closeProgressModal();
        }, 3000);
    }
}

function showProgressModal(title = 'Processing...') {
    elements.progressTitle.textContent = title;
    elements.progressModal.classList.add('active');
}

function closeProgressModal() {
    elements.progressModal.classList.remove('active');
    setProgress(0, '');
    clearProgressLog();
}

function setProgress(percentage, status) {
    elements.progressFill.style.width = `${percentage}%`;
    elements.progressStatus.textContent = status;
}

function clearProgressLog() {
    elements.progressLog.textContent = '';
}

function appendToProgressLog(text, type = 'info') {
    const log = elements.progressLog;
    const timestamp = new Date().toLocaleTimeString();
    
    let prefix = '';
    if (type === 'error') {
        prefix = '❌ ';
    } else if (type === 'success') {
        prefix = '✅ ';
    } else if (type === 'warning') {
        prefix = '⚠️ ';
    }
    
    log.textContent += `[${timestamp}] ${prefix}${text}\n`;
    log.scrollTop = log.scrollHeight;
}

function updateStatus(type, text) {
    elements.statusDot.className = `status-dot ${type}`;
    elements.statusText.textContent = text;
}

function addRecentActivity(icon, text) {
    const activityItem = document.createElement('div');
    activityItem.className = 'activity-item';
    
    const timestamp = new Date().toLocaleTimeString();
    
    activityItem.innerHTML = `
        <span class="activity-icon">${icon}</span>
        <span class="activity-text">[${timestamp}] ${text}</span>
    `;
    
    // Add to top of list
    elements.recentActivity.insertBefore(activityItem, elements.recentActivity.firstChild);
    
    // Keep only last 10 items
    const items = elements.recentActivity.querySelectorAll('.activity-item');
    if (items.length > 10) {
        elements.recentActivity.removeChild(items[items.length - 1]);
    }
}

function showStatus(element, type, message) {
    element.className = `test-status ${type}`;
    element.textContent = message;
}

function hideStatus(element) {
    element.className = 'test-status';
    element.style.display = 'none';
}

function setLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.classList.add('loading');
        isLoading = true;
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        isLoading = false;
    }
}

async function openExternal(url) {
    try {
        await ipcRenderer.invoke('open-external', url);
    } catch (error) {
        console.error('Error opening external URL:', error);
    }
}

async function checkPythonStatus() {
    try {
        const result = await ipcRenderer.invoke('test-python');
        if (result.success) {
            elements.pythonStatus.textContent = `Python: ${result.version}`;
            addRecentActivity('✅', 'Python environment detected.');
        } else {
            elements.pythonStatus.textContent = 'Python: Not found';
            addRecentActivity('❌', 'Python not found. Please install Python 3.7+');
        }
    } catch (error) {
        elements.pythonStatus.textContent = 'Python: Error';
        console.error('Error checking Python:', error);
    }
}

async function loadAppInfo() {
    try {
        const result = await ipcRenderer.invoke('get-app-info');
        elements.appVersion.textContent = `v${result.version}${result.isDev ? ' (dev)' : ''}`;
    } catch (error) {
        console.error('Error loading app info:', error);
    }
}