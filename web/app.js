/**
 * Academic Assistant - Modern Web Interface
 * Replaces the Electron app with a responsive web application
 */

class AcademicAssistant {
    constructor() {
        this.config = {};
        this.isConnected = false;
        this.isSyncing = false;
        this.syncProgress = 0;

        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadConfig();
        this.updateUI();
        this.loadRecentActivity();
        this.loadUpcomingAssignments();
        this.startStatusUpdates();
    }

    setupEventListeners() {
        // Quick action cards
        document.getElementById('syncNowCard').addEventListener('click', () => this.syncNow());
        document.getElementById('scheduleCard').addEventListener('click', () => this.toggleAutoSync());
        document.getElementById('calendarCard').addEventListener('click', () => this.openCalendar());
        document.getElementById('settingsCard').addEventListener('click', () => this.openSettings());

        // Navigation buttons
        document.getElementById('settingsBtn').addEventListener('click', () => this.openSettings());

        // Settings modal
        document.getElementById('closeSettings').addEventListener('click', () => this.closeSettings());
        document.getElementById('cancelSettings').addEventListener('click', () => this.closeSettings());
        document.getElementById('settingsForm').addEventListener('submit', (e) => this.saveSettings(e));

        // Login method toggle
        document.querySelectorAll('input[name="loginMethod"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                const directFields = document.getElementById('directLoginFields');
                if (e.target.value === 'direct') {
                    directFields.classList.remove('hidden');
                } else {
                    directFields.classList.add('hidden');
                }
            });
        });

        // Close modal when clicking outside
        document.getElementById('settingsModal').addEventListener('click', (e) => {
            if (e.target.id === 'settingsModal') {
                this.closeSettings();
            }
        });
    }

    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            if (response.ok) {
                this.config = await response.json();
                this.isConnected = true;
            } else {
                // Fallback to default config for demo
                this.config = this.getDefaultConfig();
                this.isConnected = false;
            }
        } catch (error) {
            console.log('Using demo mode');
            this.config = this.getDefaultConfig();
            this.isConnected = false;
        }
    }

    getDefaultConfig() {
        return {
            user: {
                email: "student@university.edu",
                university: "Your University"
            },
            gradescope: {
                method: "sso"
            },
            calendars: {
                ics: { enabled: true },
                google: { enabled: false },
                notion: { enabled: false }
            },
            sync: {
                frequency: "daily",
                time_window: 30,
                auto_start: true
            }
        };
    }

    updateUI() {
        // Update connection status
        const statusElement = document.getElementById('connectionStatus');
        const statusDot = statusElement.querySelector('.status-indicator');
        const statusText = statusElement.querySelector('span');

        if (this.isConnected) {
            statusDot.className = 'w-2 h-2 bg-green-500 rounded-full status-indicator mr-2';
            statusText.textContent = 'Connected';
        } else {
            statusDot.className = 'w-2 h-2 bg-yellow-500 rounded-full status-indicator mr-2';
            statusText.textContent = 'Demo Mode';
        }

        // Update stats
        document.getElementById('syncFrequency').textContent = this.config.sync?.frequency || 'Daily';
        document.getElementById('autoSyncStatus').textContent = this.config.sync?.auto_start ? 'Enabled' : 'Disabled';

        // Calculate calendar format
        const formats = [];
        if (this.config.calendars?.ics?.enabled) formats.push('ICS');
        if (this.config.calendars?.google?.enabled) formats.push('Google');
        if (this.config.calendars?.notion?.enabled) formats.push('Notion');
        document.getElementById('calendarFormat').textContent = formats.join(' + ') || 'ICS';

        // Populate settings form
        this.populateSettingsForm();
    }

    populateSettingsForm() {
        document.getElementById('userEmail').value = this.config.user?.email || '';
        document.getElementById('university').value = this.config.user?.university || '';

        // Login method
        const loginMethod = this.config.gradescope?.method || 'sso';
        document.querySelector(`input[name="loginMethod"][value="${loginMethod}"]`).checked = true;

        if (loginMethod === 'direct') {
            document.getElementById('directLoginFields').classList.remove('hidden');
            document.getElementById('gradescopeUsername').value = this.config.gradescope?.username || '';
            document.getElementById('gradescopePassword').value = this.config.gradescope?.password || '';
        }

        // Calendar settings
        document.getElementById('enableICS').checked = this.config.calendars?.ics?.enabled !== false;
        document.getElementById('enableGoogle').checked = this.config.calendars?.google?.enabled === true;
        document.getElementById('enableNotion').checked = this.config.calendars?.notion?.enabled === true;

        // Sync settings
        document.getElementById('syncFrequencySelect').value = this.config.sync?.frequency || 'daily';
        document.getElementById('timeWindow').value = this.config.sync?.time_window || 30;
    }

    async syncNow() {
        if (this.isSyncing) {
            this.showNotification('Sync already in progress', 'warning');
            return;
        }

        this.isSyncing = true;
        this.showProgress('Starting sync...', 0);

        try {
            // Simulate sync process
            await this.simulateSync();
            this.showNotification('Sync completed successfully!', 'success');
            this.updateLastSyncTime();
            this.loadRecentActivity();
            this.loadUpcomingAssignments();
        } catch (error) {
            this.showNotification('Sync failed: ' + error.message, 'error');
        } finally {
            this.isSyncing = false;
            this.hideProgress();
        }
    }

    async simulateSync() {
        const steps = [
            { text: 'Connecting to Gradescope...', duration: 1000 },
            { text: 'Fetching assignments...', duration: 2000 },
            { text: 'Processing data...', duration: 1500 },
            { text: 'Updating calendars...', duration: 1000 },
            { text: 'Finalizing sync...', duration: 500 }
        ];

        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            const progress = ((i + 1) / steps.length) * 100;

            this.showProgress(step.text, progress);
            await new Promise(resolve => setTimeout(resolve, step.duration));
        }
    }

    showProgress(text, percent) {
        const container = document.getElementById('progressContainer');
        const textElement = document.getElementById('progressText');
        const percentElement = document.getElementById('progressPercent');
        const progressBar = document.getElementById('progressBar');

        container.classList.remove('hidden');
        textElement.textContent = text;
        percentElement.textContent = Math.round(percent) + '%';
        progressBar.style.width = percent + '%';
    }

    hideProgress() {
        document.getElementById('progressContainer').classList.add('hidden');
    }

    toggleAutoSync() {
        const isEnabled = this.config.sync?.auto_start;
        this.config.sync.auto_start = !isEnabled;

        const newStatus = this.config.sync.auto_start ? 'Enabled' : 'Disabled';
        document.getElementById('autoSyncStatus').textContent = newStatus;

        this.showNotification(`Auto sync ${newStatus.toLowerCase()}`, 'success');
    }

    openCalendar() {
        if (this.config.calendars?.google?.enabled) {
            window.open('https://calendar.google.com', '_blank');
        } else {
            this.showNotification('Open your calendar app and import the generated ICS file', 'info');
        }
    }

    openSettings() {
        document.getElementById('settingsModal').classList.remove('hidden');
    }

    closeSettings() {
        document.getElementById('settingsModal').classList.add('hidden');
    }

    async saveSettings(e) {
        e.preventDefault();

        // Collect form data
        const formData = new FormData(e.target);
        const newConfig = {
            user: {
                email: document.getElementById('userEmail').value,
                university: document.getElementById('university').value
            },
            gradescope: {
                method: document.querySelector('input[name="loginMethod"]:checked').value,
                username: document.getElementById('gradescopeUsername').value,
                password: document.getElementById('gradescopePassword').value
            },
            calendars: {
                ics: { enabled: document.getElementById('enableICS').checked },
                google: { enabled: document.getElementById('enableGoogle').checked },
                notion: { enabled: document.getElementById('enableNotion').checked }
            },
            sync: {
                frequency: document.getElementById('syncFrequencySelect').value,
                time_window: parseInt(document.getElementById('timeWindow').value),
                auto_start: this.config.sync?.auto_start || true
            }
        };

        try {
            // Save config (in real implementation, this would be an API call)
            this.config = newConfig;
            this.updateUI();
            this.closeSettings();
            this.showNotification('Settings saved successfully!', 'success');
        } catch (error) {
            this.showNotification('Failed to save settings: ' + error.message, 'error');
        }
    }

    loadRecentActivity() {
        const activityList = document.getElementById('activityList');

        // Demo data
        const activities = [
            {
                time: '2 hours ago',
                action: 'Sync completed',
                details: '5 new assignments found',
                icon: 'fas fa-sync',
                iconColor: 'text-green-600'
            },
            {
                time: '1 day ago',
                action: 'Calendar updated',
                details: 'Google Calendar synced',
                icon: 'fas fa-calendar',
                iconColor: 'text-blue-600'
            },
            {
                time: '2 days ago',
                action: 'Settings changed',
                details: 'Auto-sync enabled',
                icon: 'fas fa-cog',
                iconColor: 'text-gray-600'
            }
        ];

        activityList.innerHTML = activities.map(activity => `
            <div class="flex items-center space-x-4">
                <div class="bg-gray-100 p-2 rounded-lg">
                    <i class="${activity.icon} ${activity.iconColor}"></i>
                </div>
                <div class="flex-1">
                    <div class="font-medium text-gray-900">${activity.action}</div>
                    <div class="text-sm text-gray-600">${activity.details}</div>
                </div>
                <div class="text-sm text-gray-500">${activity.time}</div>
            </div>
        `).join('');
    }

    loadUpcomingAssignments() {
        const upcomingList = document.getElementById('upcomingList');

        // Demo data
        const assignments = [
            {
                title: 'Problem Set 3',
                course: 'CS 106A',
                dueDate: 'Tomorrow',
                urgency: 'high'
            },
            {
                title: 'Essay Draft',
                course: 'ENGLISH 101',
                dueDate: 'In 3 days',
                urgency: 'medium'
            },
            {
                title: 'Lab Report',
                course: 'CHEM 101',
                dueDate: 'Next week',
                urgency: 'low'
            }
        ];

        const urgencyColors = {
            high: 'text-red-600 bg-red-100',
            medium: 'text-orange-600 bg-orange-100',
            low: 'text-green-600 bg-green-100'
        };

        upcomingList.innerHTML = assignments.map(assignment => `
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <div class="font-medium text-gray-900">${assignment.title}</div>
                    <div class="text-sm text-gray-600">${assignment.course}</div>
                </div>
                <div class="text-right">
                    <div class="text-sm font-medium text-gray-900">${assignment.dueDate}</div>
                    <div class="text-xs px-2 py-1 rounded-full ${urgencyColors[assignment.urgency]}">
                        ${assignment.urgency}
                    </div>
                </div>
            </div>
        `).join('');

        // Update stats
        document.getElementById('totalAssignments').textContent = '12';
        document.getElementById('upcomingAssignments').textContent = assignments.length.toString();
        document.getElementById('coursesCount').textContent = '4';
        document.getElementById('syncedCalendars').textContent = Object.values(this.config.calendars || {}).filter(cal => cal.enabled).length.toString();
    }

    updateLastSyncTime() {
        const now = new Date();
        const timeString = 'Just now';

        document.getElementById('lastSyncTime').textContent = timeString;
        document.getElementById('lastSyncStat').textContent = timeString;
    }

    startStatusUpdates() {
        // Update relative times every minute
        setInterval(() => {
            // In a real implementation, this would fetch actual status
            // For demo, we'll just update the mock data
        }, 60000);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm transform transition-all duration-300 translate-x-full`;

        const colors = {
            success: 'bg-green-100 text-green-800 border border-green-200',
            error: 'bg-red-100 text-red-800 border border-red-200',
            warning: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
            info: 'bg-blue-100 text-blue-800 border border-blue-200'
        };

        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        notification.className += ` ${colors[type]}`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="${icons[type]} mr-3"></i>
                <span class="flex-1">${message}</span>
                <button class="ml-4 text-current opacity-70 hover:opacity-100" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AcademicAssistant();
});