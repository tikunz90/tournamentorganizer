async function editStructure(categoryId) {
    if (!categoryId) {
        console.warn("No category ID provided to editStructure");
        hideSpinner();
        return;
    }

    // Highlight the selected category in the sidebar
    highlightSidebarMenu('structure');

    // Highlight the category in the categories list
    highlightCategory(categoryId);

    // Show loading state
    const container = document.getElementById("structure-editor");
    container.classList.remove("hidden");
    container.innerHTML = `<p class="text-gray-600">Loading structure...</p>`;

    try {
        // Use the category cache system instead of direct fetch
        const category = await getCategory(categoryId);

        console.debug(`Loaded category ${category.id} with ${category.phases?.length || 0} phases`);

        // Continue with the structure rendering
        const phaseList = (category.phases || [])
            .sort((a, b) => a.order - b.order)
            .map(p => {
                // First check if phase is GROUP type to conditionally add the button
                const isGroupPhase = p.name === "GROUP";

                // Create group items list including groups and potentially the add button
                const groupItems = p.groups || [];

                // Create the group section HTML, with the Add Group button as the last item
                const groupSection = (p.groups || [])
                    .map(g => `
                    <div class="pl-6 py-2">
                        <table class="w-full border-collapse">
                            <thead>
                                <tr>
                                    <th class="text-left bg-gray-200 px-3 py-1 rounded-t-md flex items-center justify-between">
                                        <span class="font-semibold text-sm text-gray-800">${g.name}</span>
                                        <button onclick="confirmDeleteGroup(${g.id}, ${p.id}, ${categoryId})" 
                                            class="text-red-500 hover:text-red-700 text-xs" title="Delete Group">
                                            &times;
                                        </button>
                                    </th>
                                </tr>
                            </thead>
                            <tbody class="bg-white rounded-b-md shadow-sm">
                                ${((g.ordered_teams || []).length === 0) ?
                            `<tr><td class="py-2 px-3 text-center text-gray-400 text-sm">No teams</td></tr>` :
                            g.ordered_teams.map(item => {
                                const t = item.team;
                                // Check if this is an actual assigned team or just a slot
                                const isAssignedTeam = t.type !== 'SLOT';

                                return `
                                <tr class="border-t border-gray-100 ${isAssignedTeam ? 'bg-blue-50' : ''}" id="team-row-${t.id}">
                                    <td class="py-2 px-3 flex items-center justify-between">
                                        <div class="flex items-center">
                                            ${t.type === 'SLOT' ?
                                        `<span class="bg-gray-100 text-gray-800 text-xs font-medium mr-2 px-2 py-0.5 rounded">Slot</span>` :
                                        t.type === 'GBO' ?
                                            `<span class="bg-blue-100 text-blue-800 text-xs font-medium mr-2 px-2 py-0.5 rounded">GBO</span>` :
                                            `<span class="bg-green-100 text-green-800 text-xs font-medium mr-2 px-2 py-0.5 rounded">Fun</span>`
                                    }
                                            <span class="text-sm team-name-display ${isAssignedTeam ? 'font-medium' : ''}" id="team-name-${t.id}">
                                                ${t.name}
                                            </span>
                                        </div>
                                        <div class="team-name-edit hidden" id="team-edit-${t.id}">
                                            <input type="text" class="text-sm px-1 py-0.5 border rounded w-full" 
                                                id="team-input-${t.id}" value="${t.name}">
                                        </div>
                                        <div class="flex gap-1">
                                            <button onclick="openAssignTeamModal(${t.id}, ${g.id}, ${categoryId})" 
                                                class="text-xs text-purple-500 hover:text-purple-700" 
                                                id="assign-btn-${t.id}" title="${isAssignedTeam ? 'Change Team' : 'Assign Team'}">
                                                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                                                    <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                                                </svg>
                                            </button>
                                            ${isAssignedTeam ? `
                                            <button onclick="unassignTeam(${t.id}, ${g.id}, ${categoryId})" 
                                                class="text-xs text-orange-500 hover:text-orange-700" 
                                                id="unassign-btn-${t.id}" title="Unassign Team">
                                                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                                                    <path d="M11 6a3 3 0 11-6 0 3 3 0 016 0zM14 17a6 6 0 00-12 0h12z" />
                                                    <path fill-rule="evenodd" d="M18 10a1 1 0 01-1 1h-6a1 1 0 110-2h6a1 1 0 011 1z" clip-rule="evenodd" />
                                                </svg>
                                            </button>
                                            ` : ''}
                                            <button onclick="saveTeamName(${t.id}, ${categoryId})" 
                                                class="text-xs text-green-500 hover:text-green-700 hidden" 
                                                id="save-btn-${t.id}" title="Save">
                                                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                </svg>
                                            </button>
                                            <button onclick="cancelTeamEdit(${t.id}, '${t.name}')" 
                                                class="text-xs text-red-500 hover:text-red-700 hidden" 
                                                id="cancel-btn-${t.id}" title="Cancel">
                                                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                                                </svg>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            `}).join("")
                        }
                            </tbody>
                        </table>
                    </div>
                `).join("") +
                    // Only add the button if it's a GROUP phase
                    (isGroupPhase ? `
                    <div class="pl-6 py-2">
                        <button
                            onclick="addGroupToPhase(${p.id}, ${categoryId})"
                            class="bg-blue-100 text-blue-600 rounded-lg px-4 py-2 flex items-center justify-center cursor-pointer hover:bg-blue-200 shadow-sm"
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                            </svg>
                            + Add Group
                        </button>
                    </div>
                ` : '');

                return `
                <li class="bg-gray-100 rounded-xl px-4 py-2 shadow-sm">
                  <div class="flex items-center gap-3">
                    <input 
                      class="bg-transparent border-b border-gray-300 focus:border-blue-500 outline-none w-40 font-medium"
                      value="${p.name}" 
                      onchange="updatePhase(${p.id}, 'name', this.value)"
                      title="Click to edit name">

                    <button onclick="confirmDeletePhase(${p.id}, ${categoryId})" 
                      class="text-red-500 hover:text-red-700 text-lg font-bold" title="Delete">
                      &times;
                    </button>

                  </div>
                  <div id="groups-${p.id}" class="mt-2 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    ${groupSection || '<div class="text-sm text-gray-400 pl-6">No groups</div>'}
                  </div>
                </li>`;
            }).join("");


        container.innerHTML = `
        <h2 class="text-xl font-semibold">Structure for: <span class="text-blue-600">${category.name}(${category.id})</span></h2>
        <ul id="phases-list" class="space-y-2 mb-4">
          ${phaseList}
        <li class="flex gap-2 justify-center">
            <button
              class="bg-blue-100 text-blue-600 rounded-lg px-4 py-2 flex items-center justify-center cursor-pointer hover:bg-blue-200 shadow-sm"
              onclick="addGroupPhase(${categoryId})" title="Add Group Phase">
              <span class="font-bold">+ Group Phase</span>
            </button>
            <button 
              class="bg-green-100 text-green-600 rounded-lg px-4 py-2 flex items-center justify-center cursor-pointer hover:bg-green-200 shadow-sm"
              onclick="addKnockoutPhase(${categoryId})" title="Add Knockout Phase">
              <span class="font-bold">+ Knockout</span>
            </button>
            <button 
              class="bg-purple-100 text-purple-600 rounded-lg px-4 py-2 flex items-center justify-center cursor-pointer hover:bg-purple-200 shadow-sm"
              onclick="openAddPhaseModal(${categoryId})" title="Add Custom Phase">
              <span class="font-bold">+ Other Phase</span>
            </button>
          </li>

        </ul>
      `;
    } catch (error) {
        console.error("Error in editStructure:", error);
        container.innerHTML = `
            <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
                <p class="font-bold">Error</p>
                <p>Failed to load structure: ${error.message}</p>
            </div>
        `;
    } finally {
        // Hide the spinner
        hideSpinner();
    }
}

function togglePhaseGroups(phaseId) {
    const el = document.getElementById(`groups-${phaseId}`);
    if (el) {
        el.classList.toggle("hidden");
    }
}


let currentStructureId = null;
let currentCategoryId = null;

function openAddPhaseModal(structureId, categoryId) {
    currentStructureId = structureId;
    currentCategoryId = categoryId;
    document.getElementById("phase-type").value = "GROUP";
    document.getElementById("phase-order").value = "";
    document.getElementById("add-phase-modal").classList.remove("hidden");
}

document.addEventListener("DOMContentLoaded", () => {

    // Assign Team modal event listeners
    document.getElementById('cancel-assign-team').addEventListener('click', hideAssignTeamModal);
    document.getElementById('confirm-assign-team').addEventListener('click', confirmAssignTeam);

    // Add Group modal event listeners
    document.getElementById('cancel-add-group').addEventListener('click', hideAddGroupModal);
    document.getElementById('confirm-add-group').addEventListener('click', confirmAddGroup);

    // Add keyboard event handling for the modal
    document.getElementById('group-name').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            confirmAddGroup();
        }
    });

document.getElementById("cancel-add-phase").addEventListener("click", () => {
    document.getElementById("add-phase-modal").classList.add("hidden");
    currentStructureId = null;
});

document.getElementById("confirm-add-phase").addEventListener("click", async () => {
    const name = document.getElementById("phase-type").value;
    const order = parseInt(document.getElementById("phase-order").value);

    if (!name || isNaN(order)) {
        showToast("Please provide both phase type and order", false);
        return;
    }

    const res = await fetch("/cup/api/phases/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({ structure: currentStructureId, name, order })
    });

    if (res.ok) {
        showToast("Phase added!");
        await refreshCategoryData(currentCategoryId);
        editStructure(currentCategoryId);
        document.getElementById("add-phase-modal").classList.add("hidden");
    } else {
        const err = await res.json();
        showToast(err?.detail || "Failed to add phase", false);
    }

    currentStructureId = null;
});

});

// Function to add a Group phase directly
async function addGroupPhase(categoryId) {
    // Get the current highest order number
    console.log("addGroupPhase for category " + categoryId);
    const res = await fetch(`/cup/api/categories/${categoryId}/`);
    const category = await res.json();
    const phases = category.phases || [];
    const maxOrder = phases.length > 0
        ? Math.max(...phases.map(p => p.order))
        : 0;

    // Create a new Group phase with the next order number
    const response = await fetch("/cup/api/phases/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({
            category: categoryId,
            name: "GROUP",
            order: maxOrder + 1
        })
    });

    if (response.ok) {
        showToast("Group phase added!");

        await refreshCategoryData(categoryId);

        editStructure(categoryId);
    } else {
        const err = await response.json();
        showToast(err?.detail || "Failed to add group phase", false);
    }
}

// Function to add a Knockout phase directly
async function addKnockoutPhase(categoryId) {
    // Get the current highest order number
    const res = await fetch(`/cup/api/categories/${categoryId}/`);
    const category = await res.json();
    const phases = category.phases || [];
    const maxOrder = phases.length > 0
        ? Math.max(...phases.map(p => p.order))
        : 0;

    // Create a new Knockout phase with the next order number
    const response = await fetch("/cup/api/phases/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({
            category: categoryId,
            name: "KNOCKOUT",
            order: maxOrder + 1
        })
    });

    if (response.ok) {
        showToast("Knockout phase added!");

        await refreshCategoryData(categoryId);

        editStructure(categoryId);
    } else {
        const err = await response.json();
        showToast(err?.detail || "Failed to add knockout phase", false);
    }
}

async function updatePhase(phaseId, categoryId, field, value) {
    const res = await fetch(`/cup/api/phases/${phaseId}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
        body: JSON.stringify({ [field]: field === "order" ? parseInt(value) : value })
    });

    if (res.ok) {
        showToast("Saved!");
        editStructure(categoryId);
    } else {
        showToast("Update failed", false);
    }
}


function confirmDeletePhase(id, categoryId) {
    showDeleteModal("Are you sure you want to delete this phase?", async () => {
        const res = await fetch(`/cup/api/phases/${id}/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": csrftoken },
        });
        if (res.ok) {
            showToast("Phase deleted");
            await refreshCategoryData(categoryId);
            editStructure(categoryId);
        } else {
            showToast("Failed to delete", false);
        }
    });
}


// Add this function to open the "Add Group" modal
function addGroupToPhase(phaseId, categoryId) {
    // Set the current context for later use
    currentPhaseId = phaseId;
    currentCategoryId = categoryId;

    // Show the modal
    document.getElementById('add-group-modal').classList.remove('hidden');
    document.getElementById('add-group-modal').classList.add('flex');

    // Focus on the input field
    setTimeout(() => {
        document.getElementById('group-name').focus();
    }, 100);
}

// Add this function to handle the group creation
async function confirmAddGroup() {
    const groupName = document.getElementById('group-name').value.trim();
    const numTeams = parseInt(document.getElementById('group-num-teams').value) || 0;

    if (!groupName) {
        showToast('Please enter a group name', false);
        return;
    }

    const response = await fetch("/cup/api/groups/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({
            phase: currentPhaseId,
            name: groupName,
            num_teams: numTeams
        })
    });

    if (response.ok) {
        hideAddGroupModal();
        showToast(`Group ${groupName} with ${numTeams} team slots added!`);

        await refreshCategoryData(currentCategoryId);

        editStructure(currentCategoryId);
    } else {
        const err = await response.json();
        showToast(err?.detail || "Failed to add group", false);
    }
}

function hideAddGroupModal() {
    document.getElementById('add-group-modal').classList.add('hidden');
    document.getElementById('add-group-modal').classList.remove('flex');
    document.getElementById('group-name').value = '';
    document.getElementById('group-num-teams').value = '0';
}

// Function to delete a group
function confirmDeleteGroup(groupId, phaseId, categoryId) {
    showDeleteModal("Are you sure you want to delete this group? Slot teams will also be deleted.", async () => {
        const res = await fetch(`/cup/api/groups/${groupId}/`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            // Add a query parameter to indicate slots should be deleted
            body: JSON.stringify({
                delete_slots: true,
                preserve_real_teams: true
            })
        });

        if (res.ok) {
            showToast("Group and its slot teams deleted");
            await refreshCategoryData(categoryId);
            editStructure(categoryId);
        } else {
            showToast("Failed to delete group", false);
        }
    });
}

// Function to start inline editing of team name
function editTeamName(teamId, currentName, categoryId) {
    // Show the input field and hide the display text
    document.getElementById(`team-name-${teamId}`).classList.add('hidden');
    document.getElementById(`team-edit-${teamId}`).classList.remove('hidden');

    // Show save and cancel buttons, hide edit button
    document.getElementById(`edit-btn-${teamId}`).classList.add('hidden');
    document.getElementById(`save-btn-${teamId}`).classList.remove('hidden');
    document.getElementById(`cancel-btn-${teamId}`).classList.remove('hidden');

    // Focus on the input field
    const inputField = document.getElementById(`team-input-${teamId}`);
    inputField.focus();
    inputField.select();

    // Add keyboard event listener for Enter key to save
    inputField.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            saveTeamName(teamId, categoryId);
        } else if (e.key === 'Escape') {
            cancelTeamEdit(teamId, currentName);
        }
    });
}

// Function to save team name changes
async function saveTeamName(teamId, categoryId) {
    const newName = document.getElementById(`team-input-${teamId}`).value.trim();
    const oldName = document.getElementById(`team-name-${teamId}`).textContent;

    if (!newName) {
        showToast("Team name cannot be empty", false);
        return;
    }

    if (newName !== oldName) {
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
            showToast("Team name updated!");

            // Update the display immediately without full page refresh
            document.getElementById(`team-name-${teamId}`).textContent = newName;

            // Optional: Refresh the whole structure to ensure consistency
            // editStructure(categoryId);
        } else {
            const err = await response.json();
            showToast(err?.detail || "Failed to update team name", false);
        }
    }

    // Restore display mode
    exitEditMode(teamId);
}


// Helper function to exit edit mode
function exitEditMode(teamId) {
    // Hide the input field and show the display text
    document.getElementById(`team-name-${teamId}`).classList.remove('hidden');
    document.getElementById(`team-edit-${teamId}`).classList.add('hidden');

    // Hide save and cancel buttons, show edit button
    document.getElementById(`edit-btn-${teamId}`).classList.remove('hidden');
    document.getElementById(`save-btn-${teamId}`).classList.add('hidden');
    document.getElementById(`cancel-btn-${teamId}`).classList.add('hidden');
}








// Global variables for team assignment
let currentSlotId = null;
let currentGroupId = null;
let selectedTeamId = null;

// Function to open the team assignment modal
async function openAssignTeamModal(slotId, groupId, categoryId) {
    currentSlotId = slotId;
    currentGroupId = groupId;
    currentCategoryId = categoryId;
    selectedTeamId = null;

    // Show the modal
    const modal = document.getElementById('assign-team-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    // Clear previous list and show loading
    const teamsList = document.getElementById('available-teams-list');
    teamsList.innerHTML = '<div class="text-center py-4">Loading teams...</div>';

    try {
        // First get the current slot team details to determine if it's an assigned team
        const slotTeamRes = await fetch(`/cup/api/teams/${slotId}/`);
        const slotTeam = await slotTeamRes.json();
        const isAssignedSlot = slotTeam.type !== 'SLOT';

        // Fetch all teams from this specific category
        console.log(`Fetching teams for category ID: ${categoryId}`);
        const teamsRes = await fetch(`/cup/api/teams/?category=${categoryId}`);
        const teamsData = await teamsRes.json();
        console.log(`Found ${teamsData.length} teams in category`);

        // Get all slot teams to check their names
        const groupsRes = await fetch(`/cup/api/groups/?phase__category=${categoryId}`);
        const groupsData = await groupsRes.json();
        console.log(`Found ${groupsData.length} groups`);

        // Get all team names that are already being used in slots
        const assignedTeamNames = new Set();
        groupsData.forEach(group => {
            if (group.teams && Array.isArray(group.teams)) {
                group.teams.forEach(team => {
                    // If team is not a slot and not the current slot, add to assigned names
                    if (team.id !== currentSlotId && team.type !== 'SLOT') {
                        assignedTeamNames.add(team.name);
                    }
                });
            }
        });
        console.log(`${assignedTeamNames.size} team names already in use`);

        // Filter out teams whose names are already being used in slots
        // but include the currently assigned team if it's a real team
        const availableTeams = teamsData.filter(team => {
            // Include if it's not a slot team
            if (team.type === 'SLOT') return false;

            // Always include the team that matches the current slot's name if it's assigned
            if (isAssignedSlot && team.name === slotTeam.name) return true;

            // Exclude teams whose names are used in other slots
            return !assignedTeamNames.has(team.name);
        });

        console.log(`${availableTeams.length} teams available for assignment`);

        // Populate the list
        if (availableTeams.length > 0) {
            teamsList.innerHTML = availableTeams.map(team => `
                <li class="py-2 px-3 hover:bg-gray-100 cursor-pointer team-option ${isAssignedSlot && team.name === slotTeam.name ? 'bg-yellow-100' : ''
                }" 
                    data-team-id="${team.id}" onclick="selectTeam(${team.id})">
                    ${team.name}${isAssignedSlot && team.name === slotTeam.name ? ' (Current)' : ''
                }
                </li>
            `).join('');
        } else {
            teamsList.innerHTML = '<div class="text-center py-4 text-gray-500">No available teams in this category</div>';
        }

        // Focus the search input
        document.getElementById('team-search').focus();

    } catch (error) {
        console.error("Error fetching teams:", error);
        console.error(error.stack);
        teamsList.innerHTML = `<div class="text-center py-4 text-red-500">Error loading teams: ${error.message}</div>`;
    }
}

// Function to select a team from the list
function selectTeam(teamId) {
    // Remove highlight from all teams
    document.querySelectorAll('.team-option').forEach(el => {
        el.classList.remove('bg-blue-100');
    });

    // Highlight the selected team
    const teamElement = document.querySelector(`.team-option[data-team-id="${teamId}"]`);
    if (teamElement) {
        teamElement.classList.add('bg-blue-100');
        selectedTeamId = teamId;
    }
}

// Function to filter teams in the list based on search input
function filterTeams() {
    const searchValue = document.getElementById('team-search').value.toLowerCase();
    const teams = document.querySelectorAll('.team-option');

    teams.forEach(team => {
        const teamName = team.textContent.toLowerCase();
        if (teamName.includes(searchValue)) {
            team.style.display = '';
        } else {
            team.style.display = 'none';
        }
    });
}

// Function to assign the selected team to the slot
async function confirmAssignTeam() {
    if (!selectedTeamId) {
        showToast("Please select a team", false);
        return;
    }

    try {
        // Use the custom endpoint to establish the relationship
        const res = await fetch(`/cup/api/teams/${selectedTeamId}/assign_to_slot/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                slot_id: currentSlotId,
                group_id: currentGroupId
            })
        });

        if (res.ok) {
            hideAssignTeamModal();
            showToast("Team assigned successfully!");
            editStructure(currentCategoryId); // Refresh the view
        } else {
            const err = await res.json();
            showToast(err?.detail || "Failed to assign team", false);
        }

    } catch (error) {
        console.error("Error assigning team:", error);
        showToast("An error occurred while assigning the team", false);
    }
}

// Function to hide the assign team modal
function hideAssignTeamModal() {
    document.getElementById('assign-team-modal').classList.add('hidden');
    document.getElementById('assign-team-modal').classList.remove('flex');
    document.getElementById('team-search').value = '';
}

// Function to unassign a team
async function unassignTeam(teamId, groupId, categoryId) {
    try {
        // Use the custom endpoint to unassign the team
        const res = await fetch(`/cup/api/teams/${teamId}/unassign_from_group/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                group_id: groupId
            })
        });

        if (res.ok) {
            showToast("Team unassigned successfully");
            editStructure(categoryId); // Refresh the view
        } else {
            const err = await res.json();
            showToast(err?.detail || "Failed to unassign team", false);
        }
    } catch (error) {
        console.error("Error unassigning team:", error);
        showToast("An error occurred while unassigning the team", false);
    }
}