// ReGear Admin Panel JavaScript

// Initialize tooltips and popovers on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializePopovers();
    handleFormSubmissions();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        new bootstrap.Tooltip(element);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
    const popoverElements = document.querySelectorAll('[data-bs-toggle="popover"]');
    popoverElements.forEach(element => {
        new bootstrap.Popover(element);
    });
}

/**
 * Handle form submissions with confirmation
 */
function handleFormSubmissions() {
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Search table functionality
 */
function searchTable(searchInputId, tableId) {
    const searchInput = document.getElementById(searchInputId);
    const table = document.getElementById(tableId);
    
    if (!searchInput || !table) return;

    searchInput.addEventListener('keyup', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

/**
 * Filter table by status
 */
function filterTableByStatus(selectId, tableId, columnIndex) {
    const selectElement = document.getElementById(selectId);
    const table = document.getElementById(tableId);
    
    if (!selectElement || !table) return;

    selectElement.addEventListener('change', function() {
        const filterValue = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const cell = row.cells[columnIndex];
            if (cell) {
                const cellText = cell.textContent.toLowerCase();
                row.style.display = filterValue === '' || cellText.includes(filterValue) ? '' : 'none';
            }
        });
    });
}

/**
 * Format date to readable format
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        showNotification('Failed to copy', 'error');
    });
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

/**
 * Export table to CSV
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        let csvRow = [];
        row.querySelectorAll('td, th').forEach(cell => {
            csvRow.push('"' + cell.textContent.trim().replace(/"/g, '""') + '"');
        });
        csv.push(csvRow.join(','));
    });

    downloadCSV(csv.join('\n'), filename);
}

/**
 * Download CSV file
 */
function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.href = URL.createObjectURL(csvFile);
    downloadLink.download = filename;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

/**
 * Confirm action with modal
 */
function confirmAction(message, onConfirm, onCancel = null) {
    const confirmed = confirm(message);
    if (confirmed && onConfirm) {
        onConfirm();
    } else if (!confirmed && onCancel) {
        onCancel();
    }
    return confirmed;
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0
    }).format(amount);
}

/**
 * Format large numbers
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num;
}

/**
 * Validate email
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone
 */
function isValidPhone(phone) {
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(phone.replace(/\D/g, ''));
}

/**
 * Loading spinner
 */
function showLoader(message = 'Loading...') {
    const loader = document.createElement('div');
    loader.id = 'loader';
    loader.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">${message}</span>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.remove();
    }
}

/**
 * Handle async API calls
 */
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(endpoint, options);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Call Failed:', error);
        showNotification('An error occurred', 'danger');
        throw error;
    }
}

/**
 * Setup AJAX form submission
 */
function setupAjaxForm(formId, endpoint, method = 'POST') {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const data = Object.fromEntries(formData);

        try {
            showLoader('Processing...');
            const response = await apiCall(endpoint, method, data);
            hideLoader();

            if (response.success) {
                showNotification(response.message || 'Success!', 'success');
                if (response.redirect) {
                    setTimeout(() => {
                        window.location.href = response.redirect;
                    }, 1000);
                } else {
                    form.reset();
                }
            } else {
                showNotification(response.message || 'Error occurred', 'danger');
            }
        } catch (error) {
            hideLoader();
            showNotification('Failed to process request', 'danger');
        }
    });
}

/**
 * Real-time data refresh
 */
function startAutoRefresh(endpoint, callback, interval = 5000) {
    setInterval(async () => {
        try {
            const data = await apiCall(endpoint);
            if (callback) {
                callback(data);
            }
        } catch (error) {
            console.error('Auto-refresh failed:', error);
        }
    }, interval);
}

/**
 * Sort table by column
 */
function makeTableSortable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const headers = table.querySelectorAll('thead th');
    
    headers.forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => sortTable(table, index));
    });
}

function sortTable(table, columnIndex) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isAscending = table.dataset.sortOrder !== 'asc';

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();

        if (!isNaN(aValue) && !isNaN(bValue)) {
            return isAscending ? aValue - bValue : bValue - aValue;
        }

        return isAscending ? 
            aValue.localeCompare(bValue) : 
            bValue.localeCompare(aValue);
    });

    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
    rows.forEach(row => table.querySelector('tbody').appendChild(row));
}

/**
 * Initialize DataTable-like features
 */
function initializeDataTable(tableId) {
    makeTableSortable(tableId);
}

// Export functions for global use
window.adminUtils = {
    searchTable,
    filterTableByStatus,
    formatDate,
    copyToClipboard,
    showNotification,
    exportTableToCSV,
    confirmAction,
    formatCurrency,
    formatNumber,
    isValidEmail,
    isValidPhone,
    apiCall,
    setupAjaxForm,
    startAutoRefresh,
    makeTableSortable,
    initializeDataTable
};
