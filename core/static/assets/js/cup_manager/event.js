async function loadEventData(eventId) {
    if (!eventId) {
        console.warn("No event ID provided to loadEventData");
        hideSpinner();
        return;
    }

    console.debug("loadEventData " + eventId);

    // Clear previous content
    const mainContent = document.getElementById("dynamic-content");
    mainContent.innerHTML = '<div class="text-center py-8">Loading event data...</div>';

    try {
        // Properly await the fetch request
        const response = await fetch(`/cup/api/events/${eventId}/`);
        if (!response.ok) {
            throw new Error(`Failed to fetch data: ${response.status}`);
        }

        const event = await response.json();

        // Render the structure editor UI
        let html = `
            <h1 class="text-3xl font-bold text-center mb-8">
                🏆 Structure Editor: <span class="text-blue-600">${event.name}</span>
            </h1>
            
            <!-- Main content area with two-column layout -->
            <div class="flex gap-6 max-w-7xl mx-auto">
                <!-- Left Column: Categories -->
                <div class="w-1/3">
                    <section class="bg-white rounded-2xl shadow p-6 sticky top-6">
                        <h2 class="text-xl font-semibold mb-4">Categories</h2>
                        <ul id="categories" class="flex flex-col gap-3">
                            <!-- Will be populated dynamically -->
                        </ul>
                    </section>
                </div>

                <!-- Right Column: Structure Editor or Teams Manager -->
                <div class="w-2/3">
                    <!-- Structure Editor -->
                    <section id="structure-editor" class="bg-white rounded-2xl shadow p-6 hidden mb-6">
                        <!-- Will be populated dynamically -->
                    </section>

                    <!-- Teams Manager -->
                    <section id="teams-manager" class="bg-white rounded-2xl shadow p-6 hidden">
                        <!-- Will be populated dynamically -->
                    </section>
                </div>
            </div>
        `;

        // Update the main content
        mainContent.innerHTML = html;

        // Categories
        const categoriesContainer = document.getElementById("categories");
        categoriesContainer.innerHTML =
            event.categories.map(cat => `
                <li class="bg-gray-100 p-4 rounded-xl hover:bg-gray-200 transition relative space-y-2 category-item cursor-pointer"
                    data-category-id="${cat.id}" 
                    onclick="editStructure(${cat.id}); highlightCategory(${cat.id});">
                    <div class="font-bold text-lg">${cat.name} ${cat.description ? `<p class="text-sm text-gray-600">   ${cat.description}</p>` : ''}</div>
                </li>
            `).join("");

        // After rendering categories, check if there are any and show the first one
        if (event.categories && event.categories.length > 0) {
            // Get the first category
            const firstCategory = event.categories[0];

            // Show structure of first category
            setTimeout(() => {
                const firstCategoryBtn = document.querySelector(`[data-category-id="${firstCategory.id}"]`);
                if (firstCategoryBtn) {
                    // Call editStructure with the first category ID
                    editStructure(firstCategory.id);

                    // Optionally highlight this category as active
                    document.querySelectorAll('.category-item').forEach(item => {
                        item.classList.remove('bg-blue-100', 'border-blue-500');
                    });
                    firstCategoryBtn.classList.add('bg-blue-100', 'border-blue-500');
                }
            }, 100);
        }

    } catch (error) {
        console.error("Error loading event data:", error);
        mainContent.innerHTML = `
            <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
                <p class="font-bold">Error</p>
                <p>Failed to load event data: ${error.message}</p>
            </div>
        `;
    } finally {
        // Now the hideSpinner will be called after all awaited operations complete
        hideSpinner();
    }
}


function highlightCategory(categoryId) {
    // Remove highlight from all categories
    document.querySelectorAll('.category-item').forEach(item => {
        item.classList.remove('bg-blue-100', 'border-blue-500', 'border-2');
        item.classList.add('bg-gray-100');
    });

    // Add highlight to the selected category
    const selectedCategory = document.querySelector(`.category-item[data-category-id="${categoryId}"]`);
    if (selectedCategory) {
        selectedCategory.classList.remove('bg-gray-100');
        selectedCategory.classList.add('bg-blue-100', 'border-blue-500', 'border-2');
    }
}

async function submitTemplateForm(e) {
    e.preventDefault();
    const categoryId = document.getElementById("template-category-id").value;
    const type = document.getElementById("template-type").value;
    const numTeams = parseInt(document.getElementById("template-num-teams").value);
    const teamsPerGroup = parseInt(document.getElementById("template-teams-per-group").value);
    const numKnockout = parseInt(document.getElementById("template-num-knockout")?.value || 0);
    const numPlacement = parseInt(document.getElementById("template-num-placement")?.value || 0);

    const payload = {
        category_id: categoryId,
        type,
        num_teams: numTeams,
        teams_per_group: teamsPerGroup,
        num_knockout_teams: type !== "GROUP_ONLY" ? numKnockout : null,
        num_placement_teams: type === "GROUP_KO_PLACEMENT" ? numPlacement : null,
    };

    const res = await fetch("/cup/api/structure-template/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    const result = await res.json();
    if (res.ok) {
        closeTemplateModal();
        alert("Template saved successfully.");
    } else {
        alert("Failed to save: " + result.error);
    }
}

function openTemplateModal(categoryId) {

    // Now you can safely access the modal and set values
    document.getElementById("template-category-id").value = categoryId;
    document.getElementById("template-modal").classList.remove("hidden");
    document.getElementById("template-type").value = "GROUP_ONLY";
    updateTemplateParams(); // ensure the right fields are visible
}

function closeTemplateModal() {
    document.getElementById("template-modal").classList.add("hidden");
}

function updateTemplateParams() {
    const type = document.getElementById("template-type").value;
    document.getElementById("knockout-fields").classList.toggle("hidden", type === "GROUP_ONLY");
    document.getElementById("placement-fields").classList.toggle("hidden", type !== "GROUP_KO_PLACEMENT");
}

function toggleStructureConfig(categoryId) {
    const configEl = document.getElementById(`structure-config-${categoryId}`);
    configEl.classList.toggle("hidden");
}

function onTemplateChange(categoryId) {
    const select = document.getElementById(`template-select-${categoryId}`);
    const paramsDiv = document.getElementById(`params-${categoryId}`);
    const selected = select.value;

    let fields = "";
    if (selected === "group") {
        fields = `
      <input placeholder="Number of Teams" id="teams-${categoryId}" type="number" class="w-full p-2 border rounded" />
      <input placeholder="Teams per Group" id="pergroup-${categoryId}" type="number" class="w-full p-2 border rounded" />
    `;
    } else if (selected === "group_knockout") {
        fields = `
      <input placeholder="Number of Teams" id="teams-${categoryId}" type="number" class="w-full p-2 border rounded" />
      <input placeholder="Teams per Group" id="pergroup-${categoryId}" type="number" class="w-full p-2 border rounded" />
      <input placeholder="Teams in Knockout" id="knockout-${categoryId}" type="number" class="w-full p-2 border rounded" />
    `;
    } else if (selected === "group_knockout_placement") {
        fields = `
      <input placeholder="Number of Teams" id="teams-${categoryId}" type="number" class="w-full p-2 border rounded" />
      <input placeholder="Teams per Group" id="pergroup-${categoryId}" type="number" class="w-full p-2 border rounded" />
      <input placeholder="Teams in Knockout" id="knockout-${categoryId}" type="number" class="w-full p-2 border rounded" />
      <input placeholder="Teams in Placement" id="placement-${categoryId}" type="number" class="w-full p-2 border rounded" />
    `;
    }

    paramsDiv.innerHTML = fields;
}

async function saveStructureConfig(categoryId) {
    const template = document.getElementById(`template-select-${categoryId}`).value;
    const teams = +document.getElementById(`teams-${categoryId}`)?.value || 0;
    const perGroup = +document.getElementById(`pergroup-${categoryId}`)?.value || 0;
    const knockout = +document.getElementById(`knockout-${categoryId}`)?.value || 0;
    const placement = +document.getElementById(`placement-${categoryId}`)?.value || 0;

    const res = await fetch(`/cup/api/structure_template/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
            category_id: categoryId,
            template,
            number_of_teams: teams,
            teams_per_group: perGroup,
            teams_knockout: knockout,
            teams_placement: placement,
        }),
    });

    const data = await res.json();
    if (res.ok) {
        showToast("Structure saved!");
    } else {
        showToast(data?.detail || "Error saving structure", false);
    }
}

// Show/hide knockout/placement fields depending on template type
const typeSelector = document.getElementById("template-type");
typeSelector.addEventListener("change", () => {
    document.getElementById("knockout-fields").classList.toggle("hidden", typeSelector.value === "GROUP_ONLY");
    document.getElementById("placement-fields").classList.toggle("hidden", typeSelector.value !== "GROUP_KO_PLACEMENT");
});

// Cancel button
const cancelBtn = document.getElementById("cancel-template");
cancelBtn.addEventListener("click", () => {
    document.getElementById("template-modal").classList.add("hidden");
});

// Submit logic (replace fetch URL with your actual endpoint)
document.getElementById("template-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        category_id: parseInt(document.getElementById("template-category-id").value),
        type: typeSelector.value,
        num_teams: parseInt(document.getElementById("num-teams").value),
        teams_per_group: parseInt(document.getElementById("teams-per-group").value),
        num_knockout_teams: parseInt(document.getElementById("num-knockout-teams").value) || null,
        num_placement_teams: parseInt(document.getElementById("num-placement-teams").value) || null,
    };

    const res = await fetch(`/cup/api/structure-template/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(data)
    });

    if (res.ok) {
        showToast("Template saved!");
        document.getElementById("template-modal").classList.add("hidden");
    } else {
        const err = await res.json();
        showToast(err?.detail || "Failed to save template", false);
    }
});
