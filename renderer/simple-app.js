// Simple, user-friendly Assignment Calendar Sync App

const { ipcRenderer } = require('electron');

let settings = {};
let isFirstRun = true;
let courses = [];
let selectedCourses = new Set();

// DOM elements - will be initialized after DOM loads
let setupSection, courseSelectionSection, syncSection, setupForm, syncButton, outputArea, statusDiv;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    console.log('App initializing...');
    
    // Initialize DOM elements
    setupSection = document.getElementById('setup-section');
    courseSelectionSection = document.getElementById('course-selection-section');
    syncSection = document.getElementById('sync-section');
    setupForm = document.getElementById('setup-form');
    syncButton = document.getElementById('sync-button');
    outputArea = document.getElementById('output');
    statusDiv = document.getElementById('status');
    
    console.log('DOM elements found:', {
        setupSection: !!setupSection,
        courseSelectionSection: !!courseSelectionSection,
        syncSection: !!syncSection,
        setupForm: !!setupForm
    });
    
    // Load existing settings
    const result = await ipcRenderer.invoke('load-settings');
    if (result.success) {
        settings = result.settings;
        isFirstRun = settings.firstRun !== false;
        
        if (isFirstRun) {
            showSetup();
        } else {
            // Skip course selection for now, go directly to main app
            showMainApp();
        }
    } else {
        showSetup();
    }
});

function hideAllSections() {
    if (setupSection) setupSection.style.display = 'none';
    if (courseSelectionSection) courseSelectionSection.style.display = 'none';
    if (syncSection) syncSection.style.display = 'none';
}

function showSetup() {
    console.log('Showing setup...');
    hideAllSections();
    if (setupSection) {
        setupSection.style.display = 'block';
    } else {
        console.error('Setup section not found!');
    }
    
    // Pre-fill form if we have settings
    if (settings.gradescopeUseSSO !== undefined) {
        document.getElementById('sso-radio').checked = settings.gradescopeUseSSO;
        document.getElementById('direct-radio').checked = !settings.gradescopeUseSSO;
        toggleLoginFields();
    }
    
    document.getElementById('gradescope-email').value = settings.gradescopeEmail || '';
    document.getElementById('gradescope-password').value = settings.gradescopePassword || '';
    document.getElementById('notion-token').value = settings.notionToken || '';
    document.getElementById('notion-database').value = settings.notionDatabase || '';
    document.getElementById('sync-days').value = settings.syncDaysAhead || 30;
    document.getElementById('semester-select').value = settings.targetSemester || 'current';
    document.getElementById('timezone-select').value = settings.timezone || 'America/New_York';
}

function showCourseSelection() {
    console.log('Showing course selection...');
    hideAllSections();
    if (courseSelectionSection) {
        courseSelectionSection.style.display = 'block';
        loadCourses();
    } else {
        console.error('Course selection section not found!');
    }
}

function showMainApp() {
    console.log('Showing main app...');
    hideAllSections();
    if (syncSection) {
        syncSection.style.display = 'block';
    } else {
        console.error('Sync section not found!');
    }
    
    // Show current settings summary
    updateSettingsSummary();
}

function toggleLoginFields() {
    const useSSO = document.getElementById('sso-radio').checked;
    const emailField = document.getElementById('gradescope-email');
    const passwordField = document.getElementById('gradescope-password');
    
    emailField.disabled = useSSO;
    passwordField.disabled = useSSO;
    
    if (useSSO) {
        emailField.value = '';
        passwordField.value = '';
        emailField.placeholder = 'Not needed for SSO login';
        passwordField.placeholder = 'Not needed for SSO login';
    } else {
        emailField.placeholder = 'your.email@school.edu';
        passwordField.placeholder = 'Your Gradescope password';
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('sso-radio').addEventListener('change', toggleLoginFields);
    document.getElementById('direct-radio').addEventListener('change', toggleLoginFields);

    document.getElementById('setup-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('Setup form submitted...');
        
        // Get form values
        const useSSO = document.getElementById('sso-radio').checked;
        const newSettings = {
            gradescopeUseSSO: useSSO,
            gradescopeEmail: useSSO ? '' : document.getElementById('gradescope-email').value,
            gradescopePassword: useSSO ? '' : document.getElementById('gradescope-password').value,
            notionToken: document.getElementById('notion-token').value,
            notionDatabase: document.getElementById('notion-database').value,
            syncDaysAhead: parseInt(document.getElementById('sync-days').value) || 30,
            targetSemester: document.getElementById('semester-select').value,
            timezone: document.getElementById('timezone-select').value,
            firstRun: false
        };
        
        console.log('Saving settings:', newSettings);
        
        // Save settings
        const result = await ipcRenderer.invoke('save-settings', newSettings);
        
        if (result.success) {
            settings = newSettings;
            showMainApp(); // Skip course selection for now, go directly to sync
            showStatus('✅ Settings saved! Ready to sync.', 'success');
        } else {
            showStatus('❌ Error saving settings: ' + (result.error || 'Unknown error'), 'error');
        }
    });

    document.getElementById('sync-button').addEventListener('click', async () => {
        console.log('Sync button clicked...');
        
        syncButton.disabled = true;
        syncButton.textContent = 'Syncing...';
        outputArea.textContent = '';
        outputArea.style.display = 'block';
        
        showStatus('📚 Starting assignment sync...', 'info');
        
        try {
            const result = await ipcRenderer.invoke('run-sync');
            console.log('Sync result:', result);
            
            if (result.success) {
                showStatus('✅ Sync completed! Check the output above for your calendar file.', 'success');
            } else {
                showStatus('❌ Sync failed. See output for details.', 'error');
            }
        } catch (error) {
            console.error('Sync error:', error);
            showStatus('❌ Sync error: ' + error.message, 'error');
        } finally {
            syncButton.disabled = false;
            syncButton.textContent = '🚀 Sync My Assignments';
        }
    });

    document.getElementById('edit-settings-btn').addEventListener('click', () => {
        showSetup();
    });

    document.getElementById('edit-courses-btn').addEventListener('click', () => {
        showCourseSelection();
    });

    document.getElementById('help-btn').addEventListener('click', () => {
        ipcRenderer.invoke('open-external', 'https://github.com/yourusername/assignment-calendar-sync#readme');
    });
});

// Listen for sync output
ipcRenderer.on('sync-output', (event, data) => {
    console.log('Sync output:', data);
    if (outputArea) {
        outputArea.textContent += data.data;
        outputArea.scrollTop = outputArea.scrollHeight;
    }
});

ipcRenderer.on('sync-complete', (event, data) => {
    console.log('Sync complete:', data);
    
    if (data.success) {
        showStatus('✅ Sync completed successfully! Your calendar file has been created.', 'success');
    } else {
        showStatus('❌ Sync failed: ' + (data.error || 'Unknown error'), 'error');
    }
});

async function updateSettingsSummary() {
    const summary = document.getElementById('settings-summary');
    
    if (!summary) return;
    
    let html = '<h3>📋 Current Settings:</h3><ul>';
    html += `<li><strong>Gradescope:</strong> ${settings.gradescopeUseSSO ? 'SSO Login' : 'Email/Password'}</li>`;
    
    // Show selected courses
    try {
        const courseSelection = await ipcRenderer.invoke('load-course-selection');
        if (courseSelection.success && courseSelection.selection.length > 0) {
            html += `<li><strong>Selected Courses:</strong> ${courseSelection.selection.join(', ')}</li>`;
        } else {
            html += `<li><strong>Selected Courses:</strong> ❌ None selected</li>`;
        }
    } catch (error) {
        html += `<li><strong>Selected Courses:</strong> ❌ Error loading</li>`;
    }
    
    html += `<li><strong>Sync Window:</strong> Next ${settings.syncDaysAhead} days</li>`;
    html += `<li><strong>Timezone:</strong> ${settings.timezone}</li>`;
    html += '</ul>';
    
    summary.innerHTML = html;
}

function showStatus(message, type = 'info') {
    console.log('Status:', type, message);
    if (statusDiv) {
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        statusDiv.style.display = 'block';
        
        // Auto-hide after 10 seconds for non-error messages
        if (type !== 'error') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 10000);
        }
    }
}

// Course loading and selection functions
async function loadCourses() {
    console.log('Loading courses...');
    
    const loadingDiv = document.getElementById('course-loading');
    const listDiv = document.getElementById('course-list');
    const errorDiv = document.getElementById('course-error');
    
    // Show loading state
    loadingDiv.style.display = 'block';
    listDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    
    try {
        const result = await ipcRenderer.invoke('fetch-courses');
        
        if (result.success) {
            courses = result.courses;
            displayCourses(courses);
            await loadSavedSelection();
            
            loadingDiv.style.display = 'none';
            listDiv.style.display = 'block';
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Error loading courses:', error);
        
        loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        document.getElementById('course-error-message').textContent = error.message;
    }
}

function displayCourses(courseList) {
    const container = document.getElementById('course-checkboxes');
    container.innerHTML = '';
    
    courseList.forEach((course, index) => {
        const courseDiv = document.createElement('div');
        courseDiv.className = 'course-checkbox';
        courseDiv.innerHTML = `
            <input type="checkbox" id="course-${index}" value="${course.name}">
            <div class="course-info">
                <div class="course-name">${course.name}</div>
                <div class="course-details">
                    ${course.assignment_count} assignments
                    ${course.date_range ? ` • ${course.date_range}` : ''}
                </div>
                <div class="course-sample-assignments">
                    ${course.sample_assignments.length > 0 ? 
                        `Sample: ${course.sample_assignments.join(', ')}` : 
                        'No assignments'
                    }
                </div>
            </div>
        `;
        
        const checkbox = courseDiv.querySelector('input[type="checkbox"]');
        
        // Add event listeners
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                selectedCourses.add(course.name);
                courseDiv.classList.add('selected');
            } else {
                selectedCourses.delete(course.name);
                courseDiv.classList.remove('selected');
            }
        });
        
        courseDiv.addEventListener('click', (e) => {
            if (e.target.type !== 'checkbox') {
                checkbox.checked = !checkbox.checked;
                checkbox.dispatchEvent(new Event('change'));
            }
        });
        
        container.appendChild(courseDiv);
    });
}

async function loadSavedSelection() {
    try {
        const result = await ipcRenderer.invoke('load-course-selection');
        if (result.success && result.selection.length > 0) {
            selectedCourses = new Set(result.selection);
            
            // Update checkboxes
            courses.forEach((course, index) => {
                const checkbox = document.getElementById(`course-${index}`);
                const courseDiv = checkbox.parentElement;
                
                if (selectedCourses.has(course.name)) {
                    checkbox.checked = true;
                    courseDiv.classList.add('selected');
                }
            });
        }
    } catch (error) {
        console.error('Error loading saved selection:', error);
    }
}

// Event listeners for course selection
document.addEventListener('DOMContentLoaded', () => {
    // Select all courses button
    document.getElementById('select-all-courses')?.addEventListener('click', () => {
        courses.forEach((course, index) => {
            const checkbox = document.getElementById(`course-${index}`);
            if (checkbox && !checkbox.checked) {
                checkbox.checked = true;
                checkbox.dispatchEvent(new Event('change'));
            }
        });
    });
    
    // Clear all courses button
    document.getElementById('clear-course-selection')?.addEventListener('click', () => {
        courses.forEach((course, index) => {
            const checkbox = document.getElementById(`course-${index}`);
            if (checkbox && checkbox.checked) {
                checkbox.checked = false;
                checkbox.dispatchEvent(new Event('change'));
            }
        });
    });
    
    // Confirm selection button
    document.getElementById('confirm-course-selection')?.addEventListener('click', async () => {
        if (selectedCourses.size === 0) {
            showStatus('⚠️ Please select at least one course to continue.', 'error');
            return;
        }
        
        try {
            const result = await ipcRenderer.invoke('save-course-selection', Array.from(selectedCourses));
            
            if (result.success) {
                showStatus('✅ Course selection saved! Ready to sync.', 'success');
                showMainApp();
            } else {
                showStatus('❌ Error saving course selection: ' + (result.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Error saving course selection:', error);
            showStatus('❌ Error saving course selection: ' + error.message, 'error');
        }
    });
    
    // Retry course loading button
    document.getElementById('retry-course-loading')?.addEventListener('click', () => {
        loadCourses();
    });
});

// Listen for course fetch output
ipcRenderer.on('course-fetch-output', (event, data) => {
    console.log('Course fetch output:', data);
});

ipcRenderer.on('course-fetch-complete', (event, data) => {
    console.log('Course fetch complete:', data);
});

console.log('App script loaded successfully');