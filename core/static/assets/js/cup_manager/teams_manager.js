// Global variable to track the current category ID for team operations
let manageTeamsCategoryId = null;

/**
 * Main function to manage teams for a category
 * @param {number} categoryId - The ID of the category to manage teams for
 */
async function manageTeams(categoryId) {
    if (!categoryId) {
        console.warn("No category ID provided to manageTeams");
        hideSpinner();
        return;
    }

    console.debug("manageTeams " + categoryId);

    highlightSidebarMenu('teams');

    // Clear previous content - Get the main content area
    const mainContent = document.getElementById("dynamic-content");
    mainContent.innerHTML = '<div class="text-center py-8">Loading teams manager...</div>';

    try {
        // First, fetch category data using the cache system
        const category = await getCategory(categoryId);
        const eventId = category.event;

        // Now fetch the event categories using the cache system
        const categories = await getEventCategories(eventId);

        // Get the event name from the first category's event property or fallback
        const eventName = category.event_name || "Tournament";

        // Render the main page layout with two columns: categories and teams manager
        let html = `
            <h1 class="text-3xl font-bold text-center mb-8">
                👥 Teams Manager: <span class="text-blue-600">${eventName}</span>
            </h1>
            
            <!-- Main content area with two-column layout -->
            <div class="flex gap-6 max-w-7xl mx-auto">
                <!-- Left Column: Categories -->
                <div class="w-1/4">
                    <section class="bg-white rounded-2xl shadow p-6 sticky top-6">
                        <h2 class="text-xl font-semibold mb-4">Categories</h2>
                        <ul id="categories" class="flex flex-col gap-3">
                            <!-- Will be populated dynamically -->
                        </ul>
                    </section>
                </div>

                <!-- Right Column: Teams Manager -->
                <div class="w-3/4">
                    <!-- Teams Manager -->
                    <section id="teams-manager" class="bg-white rounded-2xl shadow p-6">
                        <!-- Will be populated with teams data -->
                    </section>
                </div>
            </div>
        `;

        // Update the main content
        mainContent.innerHTML = html;

        // Populate categories list using the cached categories
        const categoriesContainer = document.getElementById("categories");
        categoriesContainer.innerHTML =
            categories.map(cat => `
                <li class="bg-gray-100 p-4 rounded-xl hover:bg-gray-200 transition relative space-y-2 category-item cursor-pointer" 
                    data-category-id="${cat.id}" 
                    onclick="selectCategory(${cat.id})">
                    <div class="font-bold text-lg">${cat.name}</div>
                </li>
            `).join("");

        // Highlight the selected category and render its teams
        selectCategory(categoryId);

    } catch (error) {
        console.error("Error in manageTeams:", error);
        mainContent.innerHTML = `
            <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
                <p class="font-bold">Error</p>
                <p>Failed to load teams manager: ${error.message}</p>
            </div>
        `;
        hideSpinner();
    }
}

/**
 * Select a category and render its teams
 * @param {number} categoryId - The ID of the category to select
 */
async function selectCategory(categoryId) {
    if (!categoryId) {
        console.warn("No category ID provided to selectCategory");
        return;
    }

    // Update the global variable
    manageTeamsCategoryId = categoryId;

    // Highlight the selected category
    highlightCategory(categoryId);

    // Show loading state in the teams container
    const container = document.getElementById("teams-manager");
    container.innerHTML = `<p class="text-gray-600">Loading Teams...</p>`;

    try {
        // Fetch category data from cache
        const category = await getCategory(categoryId);

        // Fetch teams data - this is still needed as teams can change frequently
        const teamsRes = await fetch(`/cup/api/teams/?category=${categoryId}`);
        if (!teamsRes.ok) {
            throw new Error(`Failed to fetch teams: ${teamsRes.status}`);
        }
        const allTeams = await teamsRes.json();

        // Render teams content
        await renderTeamsContent(container, category, allTeams);

    } catch (error) {
        console.error("Error in selectCategory:", error);
        container.innerHTML = `
            <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
                <p class="font-bold">Error</p>
                <p>Failed to load teams: ${error.message}</p>
            </div>
        `;
    } finally {
        // Hide the spinner after all operations are done
        hideSpinner();
    }
}
/**
 * Render teams content for a specific category
 * @param {HTMLElement} container - The container element to render into
 * @param {Object} category - The category object
 * @param {Array} allTeams - All teams from the API
 */
async function renderTeamsContent(container, category, allTeams) {
    // Filter out SLOT type teams
    const teams = allTeams.filter(team => team.type !== 'SLOT');

    // Count of filtered vs. total teams
    const totalTeams = allTeams.length;
    const filteredTeams = teams.length;

    // Render the teams manager content
    container.innerHTML = `
        <div class="flex items-center justify-between mb-6">
            <div>
                <h2 class="text-xl font-semibold">
                    Teams for <span class="text-blue-600">${category.name}</span>
                </h2>
                <p class="text-sm text-gray-500">${teams.length} teams in this category</p>
            </div>

            <!-- Team Buttons -->
            <div class="flex justify-end mb-4 gap-2">
                <button
                    onclick="openImportTeamsModal(${category.id})" 
                    class="bg-blue-100 text-blue-700 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-200"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                    </svg>
                    Import Teams
                </button>
                <button 
                    onclick="openAddMultipleTeamsModal(${category.id})" 
                    class="bg-purple-100 text-purple-700 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-purple-200"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM14 11a1 1 0 011 1v1h1a1 1 0 110 2h-1v1a1 1 0 11-2 0v-1h-1a1 1 0 110-2h1v-1a1 1 0 011-1z" />
                    </svg>
                    Add Multiple Teams
                </button>
                <button 
                    onclick="openAddTeamModal(${category.id})" 
                    class="bg-green-100 text-green-700 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-green-200"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                    </svg>
                    Add Team
                </button>
            </div>
        </div>

        <!-- Teams List -->
        <div class="overflow-hidden rounded-lg border border-gray-200">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Team Name
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Type
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Assigned to Group
                        </th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                        </th>
                    </tr>
                </thead>
                <tbody id="teams-list" class="bg-white divide-y divide-gray-200">
                    ${teams.length === 0 ?
            `<tr><td colspan="4" class="px-6 py-4 text-center text-gray-500">No teams added yet</td></tr>` :
            teams.map(team => `
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm font-medium text-gray-900" id="team-name-display-${team.id}">
                                    ${team.name}
                                </div>
                                <div class="hidden" id="team-name-edit-${team.id}">
                                    <input type="text" class="border rounded px-2 py-1 text-sm w-full" 
                                        value="${team.name}" id="team-name-input-${team.id}">
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="${team.type === 'SLOT' ? 'bg-gray-100 text-gray-800' :
                    team.type === 'GBO' ? 'bg-blue-100 text-blue-800' :
                        'bg-green-100 text-green-800'} 
                                        text-xs font-medium px-2 py-0.5 rounded">
                                    ${team.type === 'SLOT' ? 'Slot' :
                    team.type === 'GBO' ? 'GBO' : 'Fun'}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="text-sm text-gray-500">
                                    ${getTeamAssignment(team.id, category.phases)}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                <div class="flex gap-2" id="team-actions-${team.id}">
                                    <button onclick="editTeam(${team.id})" class="text-blue-600 hover:text-blue-900">
                                        Edit
                                    </button>
                                    <button onclick="deleteTeam(${team.id}, ${category.id})" class="text-red-600 hover:text-red-900">
                                        Delete
                                    </button>
                                </div>
                                <div class="flex gap-2 hidden" id="team-edit-actions-${team.id}">
                                    <button onclick="saveTeamEdit(${team.id}, ${category.id})" class="text-green-600 hover:text-green-900">
                                        Save
                                    </button>
                                    <button onclick="cancelTeamEdit(${team.id})" class="text-gray-600 hover:text-gray-900">
                                        Cancel
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `).join('')
        }
                </tbody>
            </table>
        </div>
    `;
}
// Function to open the Import Teams modal
function openImportTeamsModal(categoryId) {
    manageTeamsCategoryId = categoryId;

    // Reset the form
    document.getElementById('teams-csv-file').value = '';
    document.getElementById('file-name-display').textContent = 'Click to browse or drop file here';
    document.getElementById('csv-preview').classList.add('hidden');
    document.getElementById('import-progress-container').classList.add('hidden');
    document.getElementById('confirm-import-teams').disabled = true;

    // Show the modal
    document.getElementById('import-teams-modal').classList.remove('hidden');
    document.getElementById('import-teams-modal').classList.add('flex');
}

// Function to hide the Import Teams modal
function hideImportTeamsModal() {
    document.getElementById('import-teams-modal').classList.add('hidden');
    document.getElementById('import-teams-modal').classList.remove('flex');
}

// Function to handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById('file-name-display').textContent = file.name;
        document.getElementById('confirm-import-teams').disabled = false;

        // Preview the file contents
        const reader = new FileReader();
        reader.onload = function (e) {
            // Show preview
            const content = e.target.result;
            const previewDiv = document.getElementById('preview-content');

            // Display first few lines as preview
            const lines = content.split('\n');
            const previewLines = lines.slice(0, 5).map(line => line.trim()).filter(line => line);

            if (previewLines.length > 0) {
                previewDiv.innerHTML = previewLines.map(line => `<div class="py-1">${line}</div>`).join('');
                if (lines.length > 5) {
                    previewDiv.innerHTML += `<div class="text-gray-500">...and ${lines.length - 5} more lines</div>`;
                }
                document.getElementById('csv-preview').classList.remove('hidden');
            } else {
                previewDiv.innerHTML = '<div class="text-amber-500">File appears to be empty</div>';
                document.getElementById('csv-preview').classList.remove('hidden');
            }
        };
        reader.readAsText(file);
    }
}

// Function to process the imported file
async function processImportFile() {
    const fileInput = document.getElementById('teams-csv-file');
    if (!fileInput.files || !fileInput.files[0]) {
        showToast("Please select a file", false);
        return;
    }

    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onload = async function (e) {
        const content = e.target.result;

        // Parse the file content
        const teamNames = [];

        // Check if it's comma-separated or line-by-line
        if (content.includes(',')) {
            // Comma-separated
            const items = content.split(',');
            for (const item of items) {
                const trimmed = item.trim();
                if (trimmed) teamNames.push(trimmed);
            }
        } else {
            // Line-by-line
            const lines = content.split('\n');
            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed) teamNames.push(trimmed);
            }
        }

        if (teamNames.length === 0) {
            showToast("No team names found in file", false);
            return;
        }

        // Show progress container and status
        const progressContainer = document.getElementById('import-progress-container');
        progressContainer.classList.remove('hidden');
        document.getElementById('import-status').textContent = `Importing ${teamNames.length} teams...`;

        // Disable buttons during import
        document.getElementById('cancel-import-teams').disabled = true;
        document.getElementById('confirm-import-teams').disabled = true;

        let successCount = 0;
        let failCount = 0;
        const progressBar = document.getElementById('import-progress-bar');

        for (let i = 0; i < teamNames.length; i++) {
            const name = teamNames[i];
            try {
                const res = await fetch('/cup/api/teams/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        name,
                        category: manageTeamsCategoryId
                    })
                });

                if (res.ok) {
                    successCount++;
                } else {
                    failCount++;
                }
            } catch (error) {
                console.error("Error adding team:", error);
                failCount++;
            }

            // Update progress bar
            const progressPct = Math.round(((i + 1) / teamNames.length) * 100);
            progressBar.style.width = `${progressPct}%`;
            document.getElementById('import-status').textContent = `Importing teams... ${i + 1}/${teamNames.length}`;
        }

        // Process complete
        document.getElementById('import-status').textContent = `Complete! Imported ${successCount} teams.`;

        // Show results and hide modal after a short delay
        setTimeout(() => {
            hideImportTeamsModal();

            // Show results toast
            if (successCount > 0 && failCount === 0) {
                showToast(`Imported ${successCount} teams successfully!`);
            } else if (successCount > 0 && failCount > 0) {
                showToast(`Imported ${successCount} teams. ${failCount} failed.`, false);
            } else {
                showToast(`Failed to import teams.`, false);
            }

            // Refresh the team list
            manageTeams(manageTeamsCategoryId);
        }, 1500);
    };

    reader.readAsText(file);
}
// Function to open the Add Multiple Teams modal
function openAddMultipleTeamsModal(categoryId) {
    manageTeamsCategoryId = categoryId;

    // Reset the form
    document.getElementById('multi-team-names').value = '';

    // Hide progress bar
    document.getElementById('teams-progress-container').classList.add('hidden');
    document.getElementById('teams-progress-bar').style.width = '0%';

    // Show the modal
    document.getElementById('add-multiple-teams-modal').classList.remove('hidden');
    document.getElementById('add-multiple-teams-modal').classList.add('flex');

    // Focus on the textarea
    setTimeout(() => {
        document.getElementById('multi-team-names').focus();
    }, 100);
}

// Function to hide the Add Multiple Teams modal
function hideAddMultipleTeamsModal() {
    document.getElementById('add-multiple-teams-modal').classList.add('hidden');
    document.getElementById('add-multiple-teams-modal').classList.remove('flex');
}

// Function to add multiple teams
async function confirmAddMultipleTeams() {
    const teamsText = document.getElementById('multi-team-names').value;
    const teamNames = teamsText.split('\n').filter(name => name.trim() !== '');

    if (teamNames.length === 0) {
        showToast("Please enter at least one team name", false);
        return;
    }

    // Show progress container and status
    const progressContainer = document.getElementById('teams-progress-container');
    progressContainer.classList.remove('hidden');
    document.getElementById('progress-status').textContent = `Adding ${teamNames.length} teams...`;

    // Hide buttons during process
    document.getElementById('cancel-add-multiple-teams').disabled = true;
    document.getElementById('confirm-add-multiple-teams').disabled = true;

    let successCount = 0;
    let failCount = 0;
    const progressBar = document.getElementById('teams-progress-bar');

    for (let i = 0; i < teamNames.length; i++) {
        const name = teamNames[i].trim();
        if (name) {
            try {
                const res = await fetch('/cup/api/teams/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({ name, category: manageTeamsCategoryId })
                });

                if (res.ok) {
                    successCount++;
                } else {
                    failCount++;
                }
            } catch (error) {
                console.error("Error adding team:", error);
                failCount++;
            }
        }

        // Update progress bar
        const progressPct = Math.round(((i + 1) / teamNames.length) * 100);
        progressBar.style.width = `${progressPct}%`;
        document.getElementById('progress-status').textContent = `Adding teams... ${i + 1}/${teamNames.length}`;
    }

    // Process complete
    document.getElementById('progress-status').textContent = `Complete! Added ${successCount} teams.`;

    // Show results and hide modal after a short delay
    setTimeout(() => {
        hideAddMultipleTeamsModal();

        // Show results toast
        if (successCount > 0 && failCount === 0) {
            showToast(`Added ${successCount} teams successfully!`);
        } else if (successCount > 0 && failCount > 0) {
            showToast(`Added ${successCount} teams. ${failCount} failed.`, false);
        } else {
            showToast(`Failed to add teams.`, false);
        }

        // Refresh the team list
        manageTeams(manageTeamsCategoryId);
    }, 1500);
}
// Function to open the Add Team modal
function openAddTeamModal(categoryId) {
    manageTeamsCategoryId = categoryId;

    // Reset the form
    document.getElementById('new-team-name').value = '';

    // Show the modal
    document.getElementById('add-team-modal').classList.remove('hidden');
    document.getElementById('add-team-modal').classList.add('flex');

    // Focus on the input field
    setTimeout(() => {
        document.getElementById('new-team-name').focus();
    }, 100);
}

// Function to hide the Add Team modal
function hideAddTeamModal() {
    document.getElementById('add-team-modal').classList.add('hidden');
    document.getElementById('add-team-modal').classList.remove('flex');
}

// Function to add a new team
async function confirmAddTeam() {
    const name = document.getElementById('new-team-name').value.trim();

    if (!name) {
        showToast('Please enter a team name', false);
        return;
    }

    try {
        const res = await fetch('/cup/api/teams/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                name,
                category: manageTeamsCategoryId,
                type: 'FUN'
            })
        });

        if (res.ok) {
            hideAddTeamModal();
            showToast('Team added successfully!');
            // Refresh the teams list
            manageTeams(manageTeamsCategoryId);
        } else {
            const err = await res.json();
            showToast(err?.detail || 'Failed to add team', false);
        }
    } catch (error) {
        console.error('Error adding team:', error);
        showToast('An error occurred while adding the team', false);
    }
}

// Add event listeners when the document loads
document.addEventListener('DOMContentLoaded', () => {
    // Import Teams modal event listeners
    document.getElementById('cancel-import-teams').addEventListener('click', hideImportTeamsModal);
    document.getElementById('confirm-import-teams').addEventListener('click', processImportFile);
    document.getElementById('teams-csv-file').addEventListener('change', handleFileSelect);

    // Setup drag and drop for file upload
    const dropZone = document.querySelector('label[for="teams-csv-file"]').parentElement;

    dropZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.classList.add('border-blue-500');
    });

    dropZone.addEventListener('dragleave', function (e) {
        e.preventDefault();
        this.classList.remove('border-blue-500');
    });

    dropZone.addEventListener('drop', function (e) {
        e.preventDefault();
        this.classList.remove('border-blue-500');

        if (e.dataTransfer.files.length) {
            document.getElementById('teams-csv-file').files = e.dataTransfer.files;
            handleFileSelect({ target: { files: e.dataTransfer.files } });
        }
    });

    // Add Multiple Teams modal event listeners
    document.getElementById('cancel-add-multiple-teams').addEventListener('click', hideAddMultipleTeamsModal);
    document.getElementById('confirm-add-multiple-teams').addEventListener('click', confirmAddMultipleTeams);

    // Add Team modal event listeners
    document.getElementById('cancel-add-team').addEventListener('click', hideAddTeamModal);
    document.getElementById('confirm-add-team').addEventListener('click', confirmAddTeam);

    // Add keyboard event listener for Enter key on the team name input
    document.getElementById('new-team-name').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            confirmAddTeam();
        }
    });
});

// Function to delete a team
async function deleteTeam(teamId, categoryId) {
    showDeleteModal("Are you sure you want to delete this team?", async () => {
        const res = await fetch(`/cup/api/teams/${teamId}/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": csrftoken },
        });

        if (res.ok) {
            showToast("Team deleted");
            manageTeams(categoryId); // Refresh the teams list
        } else {
            showToast("Failed to delete team", false);
        }
    });
}
// Helper function to determine if a team is assigned to any group
function getTeamAssignment(teamId, phases) {
    // Check all phases and their groups to see if team is assigned
    for (const phase of phases || []) {
        for (const group of phase.groups || []) {
            if (group.teams && group.teams.some(t => t.id === teamId)) {
                return `Group ${group.name} (${phase.name})`;
            }
        }
    }
    return "Not assigned";
}

// Function to edit team name inline
function editTeam(teamId) {
    // Show edit input field, hide display
    document.getElementById(`team-name-display-${teamId}`).classList.add('hidden');
    document.getElementById(`team-name-edit-${teamId}`).classList.remove('hidden');

    // Show save/cancel buttons, hide edit/delete buttons
    document.getElementById(`team-actions-${teamId}`).classList.add('hidden');
    document.getElementById(`team-edit-actions-${teamId}`).classList.remove('hidden');

    // Focus on the input field
    document.getElementById(`team-name-input-${teamId}`).focus();
}

// Function to save team name changes
async function saveTeamEdit(teamId, categoryId) {
    try {
        const nameInput = document.getElementById(`team-name-input-${teamId}`);
        if (!nameInput) {
            console.error("Could not find team name input element");
            showToast("Error updating team", false);
            return;
        }

        const newName = nameInput.value.trim();
        if (!newName) {
            showToast("Team name cannot be empty", false);
            return;
        }

        const response = await fetch(`/cup/api/teams/${teamId}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                name: newName
            })
        });

        if (response.ok) {
            // Update the display value if the element still exists
            const nameDisplay = document.getElementById(`team-name-display-${teamId}`);
            if (nameDisplay) {
                nameDisplay.textContent = newName;
            }

            showToast("Team updated!");

            // Exit edit mode - wrap in try/catch to handle any issues
            try {
                cancelTeamEdit(teamId);
            } catch (cancelError) {
                console.error("Error exiting edit mode:", cancelError);
                // If cancelTeamEdit fails, refresh the entire teams list
                manageTeams(categoryId);
            }
        } else {
            const error = await response.json();
            showToast(error.detail || "Failed to update team", false);
        }
    } catch (error) {
        console.error("Error updating team:", error);
        showToast("An error occurred while updating the team", false);

        // Refresh the teams list if there's an error
        if (categoryId) {
            manageTeams(categoryId);
        }
    }
}

// Function to cancel team name editing
// Function to cancel team name editing
function cancelTeamEdit(teamId) {
    try {
        // Get necessary elements
        const nameDisplay = document.getElementById(`team-name-display-${teamId}`);
        const nameInput = document.getElementById(`team-name-input-${teamId}`);
        const actionsDiv = document.getElementById(`team-actions-${teamId}`);
        const editActionsDiv = document.getElementById(`team-edit-actions-${teamId}`);
        const nameEditDiv = document.getElementById(`team-name-edit-${teamId}`);

        // Check if elements exist before manipulating them
        if (nameDisplay && nameInput && nameDisplay.textContent) {
            // Reset to original value
            nameInput.value = nameDisplay.textContent.trim();
        }

        // Toggle visibility of elements if they exist
        if (nameDisplay) nameDisplay.classList.remove('hidden');
        if (nameEditDiv) nameEditDiv.classList.add('hidden');
        if (actionsDiv) actionsDiv.classList.remove('hidden');
        if (editActionsDiv) editActionsDiv.classList.add('hidden');
    } catch (error) {
        console.error("Error in cancelTeamEdit:", error);
        // Still continue to show the toast if there was an error
        // We don't want to block the user from continuing their work
    }
}
