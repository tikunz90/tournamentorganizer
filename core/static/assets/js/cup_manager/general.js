/**
 * Shows a loading spinner overlay on the main content area only
 * Used when navigating between different views or loading data
 */
function modalShowSpinner() {
    // Find the loading indicator element
    const loadingIndicator = document.getElementById('loading-indicator');

    // Find the main content area - this is where we want to show the spinner
    const mainContent = document.getElementById('dynamic-content');

    if (!mainContent) {
        console.warn("Main content area not found, using fallback to body");
    }

    // If the loading indicator doesn't exist, create it
    if (!loadingIndicator) {
        const indicator = document.createElement('div');
        indicator.id = 'loading-indicator';

        // Changed from fixed inset-0 to absolute positioning relative to the content area
        indicator.className = 'absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-50';
        indicator.innerHTML = `
            <div class="flex flex-col items-center">
                <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500 mb-3"></div>
                <p class="text-gray-700 font-medium">Loading...</p>
            </div>
        `;

        // Append to main content area instead of body if it exists
        if (mainContent) {
            // Ensure the main content has position relative for absolute positioning to work
            if (!mainContent.style.position) {
                mainContent.style.position = 'relative';
            }
            mainContent.appendChild(indicator);
        } else {
            document.body.appendChild(indicator);
        }
    } else {
        // If it exists, just show it
        loadingIndicator.classList.remove('hidden');
    }

    // Automatically hide the spinner after a timeout (as a fallback)
    setTimeout(() => {
        hideSpinner();
    }, 15000); // 15 seconds timeout as a safety measure
}
/**
 * Hides the loading spinner
 * Should be called when content is loaded and ready to display
 */
function hideSpinner() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.classList.add('hidden');
    }
}

function showToast(message, success = true) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = `fixed bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded shadow-lg text-sm z-50 transition-opacity duration-300 ${success ? "bg-green-500 text-white" : "bg-red-500 text-white"
        }`;
    toast.classList.remove("hidden");

    setTimeout(() => {
        toast.classList.add("hidden");
    }, 1500);
}

let deleteAction = null;

function showDeleteModal(message, onConfirm) {
    document.getElementById("delete-message").textContent = message;
    document.getElementById("delete-modal").classList.remove("hidden");
    deleteAction = onConfirm;

    document.getElementById("delete-confirm-btn").addEventListener("click", () => {
        if (deleteAction) deleteAction();
        hideDeleteModal();
    });
}

function hideDeleteModal() {
    document.getElementById("delete-modal").classList.add("hidden");
    deleteAction = null;
}


// Main content loading controller
document.addEventListener('DOMContentLoaded', function () {
    // Get the current event ID from the data attribute
    const appData = document.getElementById('app-data');
    const eventId = appData ? appData.dataset.currentEvent : null;
    const currentView = appData ? appData.dataset.currentView : 'basic_setup';

    // Show loading indicator
    function showLoading() {
        document.getElementById('loading-indicator').classList.remove('hidden');
    }

    // Hide loading indicator
    function hideLoading() {
        document.getElementById('loading-indicator').classList.add('hidden');
    }

    // Function to handle showing spinner
    window.modalShowSpinner = function () {
        showLoading();
    }

    // Initialize the page with event data if available
    if (eventId) {
        showLoading();
        try {
            // Dispatch an event to notify Alpine.js about the event ID
            window.dispatchEvent(new CustomEvent('load-event', {
                detail: { eventId: eventId }
            }));

            // Load the appropriate content based on the current view
            switch (currentView) {
                case 'structure':
                    loadEventData(eventId);
                    break;
                case 'teams':
                    manageTeams(eventId);
                    break;
                case 'game_plan':
                    loadGamePlan(eventId);
                    break;
                case 'results':
                    loadResults(eventId);
                    break;
                case 'basic_setup':
                    loadBasicSetup(eventId);
                    break;
                default:
                    // Default dashboard view
                    loadEventData(eventId);
            }
        } catch (e) {
            console.error('Error loading initial data:', e);
        } finally {
            hideLoading();
        }
    }
});

/**
 * Highlights the active menu item in the sidebar and changes icon color
 * @param {string} viewName - The name of the view to highlight (e.g., 'basic-setup', 'teams', 'structure')
 */
function highlightSidebarMenu(viewName) {
    console.debug(`Highlighting sidebar menu: ${viewName}`);

    // First, remove highlight from all menu items and reset icon colors
    const sidebarMenuItems = document.querySelectorAll('.sidebar-menu-item');
    sidebarMenuItems.forEach(item => {
        // Remove background highlight
        item.classList.remove('bg-gray-800', 'text-gray-100');

        // Reset icon color
        const icon = item.querySelector('svg');
        if (icon) {
            icon.classList.remove('text-white');
            icon.classList.add('text-gray-800');
        }
    });

    // Add highlight to the specific menu item
    let selector;

    switch (viewName) {
        case 'basic-setup':
            selector = '[data-menu="basic-setup"]';
            break;
        case 'teams':
            selector = '[data-menu="teams"]';
            break;
        case 'structure':
            selector = '[data-menu="structure"]';
            break;
        case 'game-plan':
            selector = '[data-menu="game-plan"]';
            break;
        case 'results':
            selector = '[data-menu="results"]';
            break;
        default:
            console.warn(`Unknown view name: ${viewName}`);
            return;
    }

    const menuItem = document.querySelector(selector);
    if (menuItem) {
        // Add background highlight
        menuItem.classList.add('bg-gray-800', 'text-gray-100');

        // Change icon color to white for higher contrast
        const icon = menuItem.querySelector('svg');
        if (icon) {
            icon.classList.remove('text-gray-800');
            icon.classList.add('text-white');
        }
    } else {
        console.warn(`Menu item not found for view: ${viewName}`);
    }
}


/**
 * Get the CSRF token from either cookie or the hidden input field
 * @returns {string} CSRF token
 */
function getCSRFToken() {
    // First try to get from cookie
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }

    // If cookie not found, try to get from the hidden input field
    if (!cookieValue) {
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            cookieValue = csrfInput.value;
        }
    }

    return cookieValue;
}

// Expose CSRF token as a global variable for all scripts
const csrftoken = getCSRFToken();

// Log for debugging, can be removed in production
if (csrftoken) {
    console.debug("CSRF token loaded successfully");
} else {
    console.warn("CSRF token not found - AJAX requests that modify data will fail");
}
