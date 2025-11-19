// AI Meeting Notes Generator - JavaScript Functions

// Global variables
let uploadInProgress = false;
let mediaRecorder = null;
let recordedBlob = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    console.log('AI Meeting Notes Generator initialized');

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Set default date to today
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = new Date().toISOString().split('T')[0];
        }
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        });
    }, 5000);
}

// File upload validation
function validateFileUpload(fileInput) {
    const file = fileInput.files[0];
    const maxSize = 100 * 1024 * 1024; // 100MB
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/m4a', 'audio/flac', 'audio/aac'];

    if (!file) {
        showAlert('Please select an audio file', 'warning');
        return false;
    }

    if (file.size > maxSize) {
        showAlert('File size must be less than 100MB', 'danger');
        return false;
    }

    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|m4a|flac|aac)$/i)) {
        showAlert('Please select a valid audio file (MP3, WAV, M4A, FLAC, AAC)', 'warning');
        return false;
    }

    return true;
}

// Show custom alert
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer') || createAlertContainer();

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    alertContainer.appendChild(alertDiv);

    // Auto-dismiss after duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }
    }, duration);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '9999';
    container.style.maxWidth = '400px';
    document.body.appendChild(container);
    return container;
}

// Progress bar utilities
function updateProgressBar(progressBar, percentage, text = '') {
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
        if (text) {
            progressBar.textContent = text;
        }
    }
}

function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
}

// Audio recording functions
async function startAudioRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 44100
            } 
        });

        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus'
        });

        const chunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                chunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            recordedBlob = new Blob(chunks, { type: 'audio/webm' });
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start(1000); // Collect data every second
        return true;

    } catch (error) {
        console.error('Error starting recording:', error);
        showAlert('Error accessing microphone: ' + error.message, 'danger');
        return false;
    }
}

function stopAudioRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        return true;
    }
    return false;
}

function downloadRecording(filename = 'meeting-recording.webm') {
    if (recordedBlob) {
        const url = URL.createObjectURL(recordedBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Form validation helpers
function validateMeetingForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// API helper functions
async function makeApiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();

    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Calendar integration
async function syncActionItemsToCalendar(meetingId, actionItemIds) {
    try {
        showAlert('Syncing action items to calendar...', 'info');

        const result = await makeApiCall('/calendar_integration', {
            method: 'POST',
            body: JSON.stringify({
                meeting_id: meetingId,
                action_items: actionItemIds
            })
        });

        if (result.success) {
            showAlert(`Successfully synced ${actionItemIds.length} action items to calendar!`, 'success');
        } else {
            throw new Error(result.error || 'Calendar sync failed');
        }

    } catch (error) {
        showAlert('Failed to sync to calendar: ' + error.message, 'danger');
    }
}

// Export functions
function exportToPDF(meetingId) {
    window.location.href = `/export/${meetingId}/pdf`;
}

function exportToText(meetingId) {
    window.location.href = `/export/${meetingId}/txt`;
}

// Copy to clipboard
function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    navigator.clipboard.writeText(text).then(() => {
        showAlert(successMessage, 'success', 2000);
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showAlert('Failed to copy to clipboard', 'danger');
    });
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

// Action item management
function toggleActionItem(itemId, completed) {
    // This would typically make an API call to update the database
    const checkbox = document.querySelector(`input[data-item-id="${itemId}"]`);
    if (checkbox) {
        const card = checkbox.closest('.action-item-card');
        if (completed) {
            card.style.opacity = '0.6';
            card.classList.add('text-muted');
        } else {
            card.style.opacity = '1';
            card.classList.remove('text-muted');
        }
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.querySelector('form');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) modal.hide();
        }
    }
});

// Service worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // You can register a service worker here for offline functionality
        console.log('Service Worker support detected');
    });
}