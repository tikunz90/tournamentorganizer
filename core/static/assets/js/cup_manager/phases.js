async function generateMatches(phaseId) {
    const res = await fetch(`/cup/api/phases/${phaseId}/generate_matches/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        }
    });

    if (res.ok) {
        showToast("Matches generated!");
    } else {
        const err = await res.json();
        showToast(err?.detail || "Failed to generate matches", false);
    }
}

let currentPhaseId = null;
let currentPhaseType = null;

function openGenerateModal(phaseId, phaseName) {
    currentPhaseId = phaseId;
    currentPhaseType = phaseName.toUpperCase();

    if (currentPhaseType === "GROUP") {
        document.getElementById("generate-matches-modal").classList.remove("hidden");
    } else {
        confirmGenerateMatches(); // Auto-submit for knockout/placement
    }
}

function closeGenerateModal() {
    document.getElementById("generate-matches-modal").classList.add("hidden");
    currentPhaseId = null;
}

async function confirmGenerateMatches() {
    const data = currentPhaseType === "GROUP" ? {
        num_teams: parseInt(document.getElementById("num-teams").value),
        teams_per_group: parseInt(document.getElementById("teams-per-group").value),
    } : {};

    const res = await fetch(`/cup/api/phases/${currentPhaseId}/generate_matches/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify(data)
    });

    if (res.ok) {
        showToast("Matches generated!");
        closeGenerateModal();
    } else {
        const err = await res.json();
        showToast(err.detail || "Failed to generate matches", false);
    }
}