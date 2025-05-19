/**
 * Loads and renders the basic setup content for an event
 * @param {number|string} eventId - The ID of the event to load basic setup for
 */
async function loadBasicSetup(eventId) {
    if (!eventId) {
        console.warn("No event ID provided to loadBasicSetup");
        hideSpinner();
        return;
    }

    console.debug("loadBasicSetup " + eventId);

    highlightSidebarMenu('basic-setup');

    // Clear previous content and show loading state
    const mainContent = document.getElementById("dynamic-content");
    mainContent.innerHTML = '<div class="text-center py-8">Loading basic setup...</div>';

    try {
        // Fetch event data
        const eventResponse = await fetch(`/cup/api/events/${eventId}/`);
        if (!eventResponse.ok) {
            throw new Error('Failed to load event data');
        }

        const event = await eventResponse.json();


        // Fetch basic setup data - adjust endpoint as needed
        //const setupResponse = await fetch(`/cup/api/events/${eventId}/basic-setup/`);
        //if (!setupResponse.ok) {
        //    throw new Error('Failed to load basic setup data');
        //}

        //const setupData = await setupResponse.json();

        // Render the basic setup UI
        let html = `
            <h1 class="text-3xl font-bold text-center mb-8">
                ⚙️ Basic Setup: <span class="text-blue-600">${event.name}</span>
            </h1>
            
            <div class="max-w-5xl mx-auto">
                <!-- Event Information Section -->
                <section class="bg-white rounded-xl shadow-md p-6 mb-6">
                    <h2 class="text-xl font-semibold mb-4 border-b pb-2">Event Information</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Event Name</label>
                            <input 
                                type="text" 
                                id="event-name-input" 
                                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value="${event.name || ''}"
                                onchange="updateEventField(${eventId}, 'name', this.value)"
                            />
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Event Date</label>
                            <input 
                                type="date" 
                                id="event-date-input" 
                                class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value="${event.date || ''}"
                                onchange="updateEventField(${eventId}, 'date', this.value)"
                            />
                        </div>
                    </div>
                </section>
                
                <section class="bg-white rounded-xl shadow-md p-6 mb-6">
        <div class="flex justify-between items-center mb-4 border-b pb-2">
            <h2 class="text-xl font-semibold">Categories</h2>
        </div>

        <ul id="categories-list" class="flex flex-col gap-3">
            ${(event.categories || []).map(cat => `
                <li class="bg-gray-100 p-4 rounded-xl hover:bg-gray-200 transition relative space-y-2">
                    <div class="flex justify-between items-center">
                        <div>
                            <span class="font-bold text-lg">${cat.name}</span>
                            <input
                                class="bg-transparent border-b border-gray-300 focus:border-blue-500 outline-none w-full"
                                value="${cat.description || ''}" 
                                onchange="updateCategory(${cat.id}, 'description', this.value)"
                                placeholder="Add description..."
                                title="Click to edit description">
                        </div>
                        <div class="flex gap-2">
                            <button 
                                onclick="deleteCategory(${eventId}, ${cat.id})"
                                class="px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-xs"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </li>
            `).join('')}
            
            <!-- Add Category Button as the last list item -->
            <li onclick="addCategory(${eventId})" 
                class="cursor-pointer flex justify-center items-center bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-xl p-4 transition text-lg font-bold">
                + Add Category
            </li>
        </ul>
    </section>
                

                
              
            </div>
        `;

        // Update the main content
        mainContent.innerHTML = html;

    } catch (error) {
        console.error("Error loading basic setup:", error);
        mainContent.innerHTML = `
            <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
                <p class="font-bold">Error</p>
                <p>Failed to load basic setup: ${error.message}</p>
            </div>
        `;
    }
    finally {
        // Hide the spinner when done, whether successful or not
        hideSpinner();
    }
}

// Helper functions for basic setup

async function updateEventField(eventId, field, value) {
    try {
        const res = await fetch(`/cup/api/events/${eventId}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({ [field]: value }),
        });

        if (res.ok) {
            showToast(`Event ${field} updated!`);
        } else {
            const err = await res.json();
            throw new Error(err?.detail || `Failed to update ${field}`);
        }
    } catch (error) {
        showToast(error.message, false);
    }
}

async function updateEventSetting(eventId, setting, value) {
    try {
        const res = await fetch(`/cup/api/events/${eventId}/settings/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({ [setting]: value }),
        });

        if (res.ok) {
            showToast(`Setting updated!`);
        } else {
            const err = await res.json();
            throw new Error(err?.detail || `Failed to update setting`);
        }
    } catch (error) {
        showToast(error.message, false);
    }
}

function editCategory(categoryId) {
    // Show modal or inline edit form for category
    showToast("Category edit functionality to be implemented");
}

async function addCourt(eventId) {
    // Implementation would typically show a modal and handle form submission
    const courtName = prompt("Enter court name:");
    if (!courtName) return;

    try {
        const res = await fetch(`/cup/api/courts/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({
                event: eventId,
                name: courtName
            }),
        });

        if (res.ok) {
            showToast("Court added!");
            // Reload to show the new court
            loadBasicSetup(eventId);
        } else {
            const err = await res.json();
            throw new Error(err?.detail || "Failed to add court");
        }
    } catch (error) {
        showToast(error.message, false);
    }
}

function editCourt(courtId) {
    // Show modal or inline edit form for court
    showToast("Court edit functionality to be implemented");
}

async function deleteCourt(courtId) {
    showDeleteModal("Are you sure you want to delete this court?", async () => {
        try {
            const res = await fetch(`/cup/api/courts/${courtId}/`, {
                method: "DELETE",
                headers: { "X-CSRFToken": csrftoken },
            });

            if (res.ok) {
                showToast("Court deleted");
                // Get the event ID from the page
                const appData = document.getElementById('app-data');
                const eventId = appData ? appData.dataset.currentEvent : null;
                if (eventId) {
                    loadBasicSetup(eventId);
                }
            } else {
                throw new Error("Failed to delete court");
            }
        } catch (error) {
            showToast(error.message, false);
        }
    });
}










/**
 * Global category data cache to minimize API requests
 * {categoryId: {category object}, ...}
 */
const categoryCache = {};

/**
 * Cache for each event's categories
 * {eventId: [{category object}, ...], ...}
 */
const eventCategoriesCache = {};

/**
 * Fetch a category with caching
 * @param {number} categoryId - The category ID to fetch
 * @returns {Promise<Object>} - The category object
 */
async function getCategory(categoryId) {
    // Return from cache if available
    if (categoryCache[categoryId]) {
        console.debug(`Using cached category data for ID ${categoryId}`);
        return categoryCache[categoryId];
    }

    console.debug(`Fetching category data for ID ${categoryId}`);
    const catRes = await fetch(`/cup/api/categories/${categoryId}/`);
    if (!catRes.ok) {
        throw new Error(`Failed to fetch category: ${catRes.status}`);
    }

    const category = await catRes.json();
    // Store in cache
    categoryCache[categoryId] = category;
    return category;
}

/**
 * Fetch all categories for an event with caching
 * @param {number} eventId - The event ID to fetch categories for
 * @returns {Promise<Array>} - Array of category objects
 */
async function getEventCategories(eventId) {
    // Return from cache if available
    if (eventCategoriesCache[eventId]) {
        console.debug(`Using cached categories for event ID ${eventId}`);
        return eventCategoriesCache[eventId];
    }

    console.debug(`Fetching categories for event ID ${eventId}`);
    const eventRes = await fetch(`/cup/api/events/${eventId}/`);
    if (!eventRes.ok) {
        throw new Error(`Failed to fetch event: ${eventRes.status}`);
    }

    const event = await eventRes.json();

    // Cache each category individually
    if (event.categories && Array.isArray(event.categories)) {
        event.categories.forEach(category => {
            categoryCache[category.id] = category;
        });
    }

    // Store the categories list
    eventCategoriesCache[eventId] = event.categories || [];
    return eventCategoriesCache[eventId];
}

/**
 * Invalidate category in cache after updates
 * @param {number} categoryId - The category ID to invalidate
 */
function invalidateCategory(categoryId) {
    if (categoryCache[categoryId]) {
        delete categoryCache[categoryId];
        console.debug(`Invalidated cache for category ${categoryId}`);
    }

    // Also invalidate any event cache that might contain this category
    Object.keys(eventCategoriesCache).forEach(eventId => {
        // Force refetch of all categories for this event next time
        delete eventCategoriesCache[eventId];
    });
}

/**
* Add a category to an event
* @param {number} eventId - The ID of the event to add the category to
*/
function addCategory(eventId) {
    // Show modal for adding a category
    document.getElementById("category-name").value = "";
    document.getElementById("category-description").value = "";

    // Set up the save button for adding a category
    const saveButton = document.getElementById("save-category-button");
    saveButton.onclick = () => confirmAddCategory(eventId);

    const cancelButton = document.getElementById("cancel-category-button");
    cancelButton.onclick = () => hideCategoryModal();

    // Show the modal
    document.getElementById("add-category-modal").classList.remove("hidden");
    document.getElementById("add-category-modal").classList.add("flex");

    // Focus on name input
    setTimeout(() => {
        document.getElementById("category-name").focus();
    }, 100);
}

/**
 * Confirm adding a category
 * @param {number} eventId - The event ID to add the category to
 */
async function confirmAddCategory(eventId) {
    const name = document.getElementById("category-name").value.trim();
    const description = document.getElementById("category-description").value.trim();

    if (!name) {
        showToast("Category name is required", false);
        return;
    }

    try {
        const response = await fetch("/cup/api/categories/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                event: eventId,
                name: name,
                description: description
            })
        });

        if (response.ok) {
            const newCategory = await response.json();
            showToast("Category added successfully");
            hideCategoryModal();

            // Invalidate the cache to refresh data
            invalidateCategory(newCategory.id);

            // Reload the page to show the new category
            loadBasicSetup(eventId);
        } else {
            const error = await response.json();
            throw new Error(error?.detail || "Failed to add category");
        }
    } catch (error) {
        showToast(error.message, false);
    }
}

/**
 * Edit a category
 * @param {number} categoryId - The ID of the category to edit
 */
async function editCategory(categoryId) {
    try {
        // Fetch category data (using cache if available)
        const category = await getCategory(categoryId);

        // Set up the modal for editing
        document.getElementById("category-modal-title").textContent = "Edit Category";
        document.getElementById("category-name").value = category.name || "";
        document.getElementById("category-description").value = category.description || "";

        // Set up the save button for editing
        const saveButton = document.getElementById("save-category-button");
        saveButton.onclick = () => confirmEditCategory(categoryId, category.event);

        // Show the modal
        document.getElementById("category-modal").classList.remove("hidden");
        document.getElementById("category-modal").classList.add("flex");

        // Focus on name input
        setTimeout(() => {
            document.getElementById("category-name").focus();
        }, 100);
    } catch (error) {
        showToast("Error loading category: " + error.message, false);
    }
}

/**
 * Confirm editing a category
 * @param {number} categoryId - The ID of the category being edited
 * @param {number} eventId - The event ID this category belongs to
 */
async function confirmEditCategory(categoryId, eventId) {
    const name = document.getElementById("category-name").value.trim();
    const description = document.getElementById("category-description").value.trim();

    if (!name) {
        showToast("Category name is required", false);
        return;
    }

    try {
        const response = await fetch(`/cup/api/categories/${categoryId}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                name: name,
                description: description
            })
        });

        if (response.ok) {
            showToast("Category updated successfully");
            hideCategoryModal();

            // Invalidate the cache to refresh data
            invalidateCategory(categoryId);

            // Reload the page to show the updated category
            loadBasicSetup(eventId);
        } else {
            const error = await response.json();
            throw new Error(error?.detail || "Failed to update category");
        }
    } catch (error) {
        showToast(error.message, false);
    }
}

/**
 * Delete a category
 * @param {number} eventId - The ID of the event this category belongs to
 * @param {number} categoryId - The ID of the category to delete
 */
async function deleteCategory(eventId, categoryId) {
    showDeleteModal("Are you sure you want to delete this category? This will also delete all teams in this category.", async () => {
        try {
            const response = await fetch(`/cup/api/categories/${categoryId}/`, {
                method: "DELETE",
                headers: {
                    "X-CSRFToken": csrftoken
                }
            });

            if (response.ok) {
                showToast("Category deleted successfully");

                // Invalidate the cache
                invalidateCategory(categoryId);

                // Reload the page to reflect changes
                loadBasicSetup(eventId);
            } else {
                const error = await response.json();
                throw new Error(error?.detail || "Failed to delete category");
            }
        } catch (error) {
            showToast(error.message, false);
        }
    });
}


function hideCategoryModal() {
    //document.getElementById("add-category-modal").classList.add("hidden");

    document.getElementById("add-category-modal").classList.remove("flex");
    document.getElementById("add-category-modal").classList.add("hidden");
}

async function updateCategory(id, field, value) {
    const input = event.target;

    const res = await fetch(`/cup/api/categories/${id}/`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({ [field]: value }),
    });

    if (!res.ok) {
        const err = await res.json();
        const errorMessage = err?.[field]?.[0] || err?.detail || "Update failed";
        showToast(errorMessage, false);
        input.classList.add("border-red-500", "text-red-700");
        setTimeout(() => {
            input.classList.remove("border-red-500", "text-red-700");
        }, 1500);
    } else {
        showToast("Saved!");
        input.classList.remove("border-red-500", "text-red-700");
    }
}



function deleteCategory(eventId, id) {
    showDeleteModal("Are you sure you want to delete this category?", async () => {
        const res = await fetch(`/cup/api/categories/${id}/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": csrftoken },
        });
        if (res.ok) {
            showToast("Category deleted");
            loadEventData(eventId);
        } else {
            showToast("Failed to delete", false);
        }
    });
}

/**
 * Refreshes category data by invalidating cache and fetching fresh data
 * @param {number} categoryId - The ID of the category to refresh
 * @returns {Promise<Object>} - The fresh category data
 */
async function refreshCategoryData(categoryId) {
    if (!categoryId) {
        console.warn("No category ID provided to refreshCategoryData");
        return null;
    }

    try {
        // Invalidate the category in the cache if invalidateCategory function exists
        if (typeof invalidateCategory === 'function') {
            invalidateCategory(categoryId);
        }

        // Force a fresh fetch of data directly from the API
        console.debug(`Fetching fresh data for category ${categoryId}`);
        const response = await fetch(`/cup/api/categories/${categoryId}/`);

        if (!response.ok) {
            throw new Error(`Failed to fetch category: ${response.status}`);
        }

        const freshCategory = await response.json();

        // Update the cached version if the cache system exists
        if (typeof categoryCache !== 'undefined') {
            categoryCache[categoryId] = freshCategory;
            console.debug(`Updated cache for category ${categoryId}`);
        }

        return freshCategory;
    } catch (error) {
        console.error(`Error refreshing category ${categoryId}:`, error);
        throw error;
    }
}
