// API base URL
const API_BASE = '/api';

// Escape HTML to prevent XSS attacks
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load flags and stats on page load
document.addEventListener('DOMContentLoaded', () => {
    loadFlags();
    loadStats();
});

// Load and display flagged items
async function loadFlags() {
    try {
        const response = await fetch(`${API_BASE}/flags`);
        const flags = await response.json();
        renderFlags(flags);
    } catch (error) {
        console.error('Error loading flags:', error);
        document.getElementById('flags-table-body').innerHTML = 
            '<tr><td colspan="6" class="px-6 py-4 text-center text-red-500">Error loading flags</td></tr>';
    }
}

// Render flags table
function renderFlags(flags) {
    const tbody = document.getElementById('flags-table-body');
    
    if (flags.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">No flagged items</td></tr>';
        return;
    }
    
    tbody.innerHTML = flags.map(flag => {
        // Sanitize user-generated content to prevent XSS
        const safeContentType = escapeHtml(flag.content_type);
        const safePriority = escapeHtml(flag.priority);
        const safeStatus = escapeHtml(flag.status);
        const safeAiSummary = escapeHtml(flag.ai_summary);
        const safeId = escapeHtml(String(flag.id));
        
        return `
        <tr>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${safeId}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                    ${safeContentType}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 py-1 text-xs font-semibold rounded-full ${
                    flag.priority === 'high' ? 'bg-red-100 text-red-800' :
                    flag.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                }">
                    ${safePriority}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 py-1 text-xs font-semibold rounded-full ${
                    flag.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    flag.status === 'approved' ? 'bg-green-100 text-green-800' :
                    flag.status === 'rejected' ? 'bg-red-100 text-red-800' :
                    'bg-purple-100 text-purple-800'
                }">
                    ${safeStatus}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                <div class="max-w-xs truncate" title="${safeAiSummary}">
                    ${safeAiSummary}
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <select onchange="updateFlagStatus(${flag.id}, this.value)" 
                    class="text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500">
                    <option value="pending" ${flag.status === 'pending' ? 'selected' : ''}>Pending</option>
                    <option value="approved" ${flag.status === 'approved' ? 'selected' : ''}>Approve</option>
                    <option value="rejected" ${flag.status === 'rejected' ? 'selected' : ''}>Reject</option>
                    <option value="escalated" ${flag.status === 'escalated' ? 'selected' : ''}>Escalate</option>
                </select>
                <button onclick="deleteFlag(${flag.id})" 
                    class="ml-2 text-red-600 hover:text-red-900 text-xs">
                    Delete
                </button>
            </td>
        </tr>
    `;
    }).join('');
}

// Load and display statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();
        
        document.getElementById('total-flags').textContent = stats.total_flags;
        document.getElementById('high-priority').textContent = stats.high_priority;
        document.getElementById('pending-status').textContent = stats.pending_status;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Create a new flagged item
document.getElementById('create-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const content_type = formData.get('content_type');
    const content = formData.get('content');
    
    try {
        const response = await fetch(`${API_BASE}/flags`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content_type, content }),
        });
        
        if (response.ok) {
            e.target.reset();
            loadFlags();
            loadStats();
        } else {
            alert('Error creating flagged item');
        }
    } catch (error) {
        console.error('Error creating flag:', error);
        alert('Error creating flagged item');
    }
});

// Update flag status
async function updateFlagStatus(id, status) {
    try {
        const response = await fetch(`${API_BASE}/flags/${id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status }),
        });
        
        if (response.ok) {
            loadFlags();
            loadStats();
        } else {
            alert('Error updating flag status');
        }
    } catch (error) {
        console.error('Error updating flag:', error);
        alert('Error updating flag status');
    }
}

// Delete a flagged item
async function deleteFlag(id) {
    if (!confirm('Are you sure you want to delete this flagged item?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/flags/${id}`, {
            method: 'DELETE',
        });
        
        if (response.ok) {
            loadFlags();
            loadStats();
        } else {
            alert('Error deleting flagged item');
        }
    } catch (error) {
        console.error('Error deleting flag:', error);
        alert('Error deleting flagged item');
    }
}

