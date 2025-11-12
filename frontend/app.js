// Clerk Configuration - will be set from window object after HTML loads

// API base URL
const API_BASE = '/api';

// Clerk instance (will be initialized after Clerk loads)
let clerk = null;

// Initialize Clerk when script loads
async function initClerk() {
    // Get Clerk key from window object (set in index.html)
    const CLERK_PUBLISHABLE_KEY = window.CLERK_PUBLISHABLE_KEY || '';
    
    if (!CLERK_PUBLISHABLE_KEY || CLERK_PUBLISHABLE_KEY === '{{CLERK_PUBLISHABLE_KEY}}' || CLERK_PUBLISHABLE_KEY === '') {
        console.warn('CLERK_PUBLISHABLE_KEY not set. Authentication disabled.');
        console.warn('Current value:', CLERK_PUBLISHABLE_KEY);
        // Show dashboard without auth for development
        showDashboard();
        return;
    }

    try {
        // Wait for Clerk to be available (it loads asynchronously)
        let retries = 0;
        while (typeof window.Clerk === 'undefined' && retries < 20) {
            await new Promise(resolve => setTimeout(resolve, 200));
            retries++;
        }

        if (typeof window.Clerk === 'undefined') {
            console.error('Clerk SDK not loaded after timeout');
            console.error('window.Clerk:', typeof window.Clerk);
            // Show dashboard without auth if Clerk fails to load
            console.warn('Falling back to unauthenticated mode');
            showDashboard();
            return;
        }

        // Initialize Clerk with the key
        const clerkKey = window.CLERK_PUBLISHABLE_KEY;
        
        // Clerk SDK from @clerk/clerk-js exposes Clerk as a constructor
        // Initialize Clerk instance
        clerk = new window.Clerk(clerkKey);
        
        // Load Clerk and wait for it to be ready
        await clerk.load();
        
        // Set up auth state listener
        clerk.addListener((state) => {
            console.log('Clerk auth state changed:', state);
            if (state.user) {
                showDashboard();
            } else {
                showSignIn();
            }
        });

        // Check initial auth state
        const currentUser = await clerk.user;
        if (currentUser) {
            showDashboard();
        } else {
            showSignIn();
        }
    } catch (error) {
        console.error('Error initializing Clerk:', error);
        // Show dashboard without auth on error
        console.warn('Falling back to unauthenticated mode due to error');
        showDashboard();
    }
}

// Show sign-in UI
function showSignIn() {
    document.getElementById('dashboard-container').classList.add('hidden');
    document.getElementById('clerk-auth-container').classList.remove('hidden');
    
    if (clerk) {
        clerk.mountSignIn(document.getElementById('clerk-auth-container'));
    } else {
        document.getElementById('clerk-auth-container').innerHTML = `
            <div class="min-h-screen flex items-center justify-center">
                <div class="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
                    <h2 class="text-2xl font-bold text-gray-800 mb-4">Sign In Required</h2>
                    <p class="text-gray-600 mb-6">Please sign in to access the moderation dashboard.</p>
                    <button onclick="location.reload()" class="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                        Retry
                    </button>
                </div>
            </div>
        `;
    }
}

// Show dashboard
function showDashboard() {
    document.getElementById('clerk-auth-container').classList.add('hidden');
    document.getElementById('dashboard-container').classList.remove('hidden');
    
    if (clerk && clerk.user) {
        const email = clerk.user.primaryEmailAddress?.emailAddress || 'User';
        document.getElementById('user-email').textContent = email;
    }
    
    // Load data
    loadFlags();
    loadStats();
}

// Show auth error
function showAuthError() {
    document.getElementById('dashboard-container').classList.add('hidden');
    document.getElementById('clerk-auth-container').innerHTML = `
        <div class="min-h-screen flex items-center justify-center">
            <div class="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
                <h2 class="text-2xl font-bold text-red-600 mb-4">Authentication Error</h2>
                <p class="text-gray-600 mb-6">Unable to initialize authentication. Please check your Clerk configuration.</p>
                <button onclick="location.reload()" class="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                    Retry
                </button>
            </div>
        </div>
    `;
}

// Get authorization header for API requests
async function getAuthHeader() {
    if (!clerk) {
        return {};
    }
    
    try {
        // Get the session token from Clerk
        // Clerk SDK provides getToken() method on the session
        const session = await clerk.session;
        if (!session) {
            return {};
        }
        
        // Get token using Clerk's getToken method
        const token = await session.getToken();
        
        if (token) {
            return {
                'Authorization': `Bearer ${token}`
            };
        }
    } catch (error) {
        console.error('Error getting auth token:', error);
    }
    
    return {};
}

// Escape HTML to prevent XSS attacks
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load flags and stats on page load
document.addEventListener('DOMContentLoaded', () => {
    // Show loading state initially
    const dashboardContainer = document.getElementById('dashboard-container');
    const authContainer = document.getElementById('clerk-auth-container');
    
    if (dashboardContainer) {
        dashboardContainer.classList.remove('hidden');
    }
    if (authContainer) {
        authContainer.classList.add('hidden');
    }
    
    // Initialize Clerk (will handle auth if available)
    initClerk();
    
    // Set up sign out button
    document.getElementById('sign-out-btn')?.addEventListener('click', async () => {
        if (clerk) {
            try {
                await clerk.signOut();
                showSignIn();
            } catch (error) {
                console.error('Error signing out:', error);
                // Force reload on error
                window.location.reload();
            }
        } else {
            // If no Clerk, just reload
            window.location.reload();
        }
    });
});

// Load and display flagged items
async function loadFlags() {
    try {
        const authHeaders = await getAuthHeader();
        const response = await fetch(`${API_BASE}/flags`, {
            headers: {
                ...authHeaders,
                'Content-Type': 'application/json',
            }
        });
        
        if (response.status === 401) {
            // Unauthorized - redirect to sign in
            if (clerk) {
                showSignIn();
            }
            return;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const flags = await response.json();
        renderFlags(flags);
    } catch (error) {
        console.error('Error loading flags:', error);
        const tbody = document.getElementById('flags-table-body');
        if (tbody) {
            tbody.innerHTML = 
                '<tr><td colspan="6" class="px-6 py-4 text-center text-red-500">Error loading flags</td></tr>';
        }
    }
}

// Render flags table
function renderFlags(flags) {
    const tbody = document.getElementById('flags-table-body');
    if (!tbody) return;
    
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
        const authHeaders = await getAuthHeader();
        const response = await fetch(`${API_BASE}/stats`, {
            headers: {
                ...authHeaders,
                'Content-Type': 'application/json',
            }
        });
        
        if (response.status === 401) {
            return; // Unauthorized - will be handled by auth flow
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const stats = await response.json();
        
        const totalFlagsEl = document.getElementById('total-flags');
        const highPriorityEl = document.getElementById('high-priority');
        const pendingStatusEl = document.getElementById('pending-status');
        
        if (totalFlagsEl) totalFlagsEl.textContent = stats.total_flags;
        if (highPriorityEl) highPriorityEl.textContent = stats.high_priority;
        if (pendingStatusEl) pendingStatusEl.textContent = stats.pending_status;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Create a new flagged item
document.addEventListener('DOMContentLoaded', () => {
    const createForm = document.getElementById('create-form');
    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const content_type = formData.get('content_type');
            const content = formData.get('content');
            
            try {
                const authHeaders = await getAuthHeader();
                const response = await fetch(`${API_BASE}/flags`, {
                    method: 'POST',
                    headers: {
                        ...authHeaders,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ content_type, content }),
                });
                
                if (response.status === 401) {
                    alert('Please sign in to create flagged items');
                    if (clerk) {
                        showSignIn();
                    }
                    return;
                }
                
                if (response.ok) {
                    e.target.reset();
                    loadFlags();
                    loadStats();
                } else {
                    const error = await response.json().catch(() => ({ detail: 'Error creating flagged item' }));
                    alert(error.detail || 'Error creating flagged item');
                }
            } catch (error) {
                console.error('Error creating flag:', error);
                alert('Error creating flagged item');
            }
        });
    }
});

// Update flag status
async function updateFlagStatus(id, status) {
    try {
        const authHeaders = await getAuthHeader();
        const response = await fetch(`${API_BASE}/flags/${id}`, {
            method: 'PATCH',
            headers: {
                ...authHeaders,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status }),
        });
        
        if (response.status === 401) {
            alert('Please sign in to update flagged items');
            if (clerk) {
                showSignIn();
            }
            return;
        }
        
        if (response.ok) {
            loadFlags();
            loadStats();
        } else {
            const error = await response.json().catch(() => ({ detail: 'Error updating flag status' }));
            alert(error.detail || 'Error updating flag status');
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
        const authHeaders = await getAuthHeader();
        const response = await fetch(`${API_BASE}/flags/${id}`, {
            method: 'DELETE',
            headers: {
                ...authHeaders,
            },
        });
        
        if (response.status === 401) {
            alert('Please sign in to delete flagged items');
            if (clerk) {
                showSignIn();
            }
            return;
        }
        
        if (response.ok) {
            loadFlags();
            loadStats();
        } else {
            const error = await response.json().catch(() => ({ detail: 'Error deleting flagged item' }));
            alert(error.detail || 'Error deleting flagged item');
        }
    } catch (error) {
        console.error('Error deleting flag:', error);
        alert('Error deleting flagged item');
    }
}
