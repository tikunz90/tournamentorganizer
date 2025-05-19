async function loadCourts(eventId) {
    const res = await fetch(`/cup/api/courts/?event=${eventId}`);
    const courts = await res.json();
    const container = document.getElementById("courts");

    courts.sort((a, b) => a.court_number - b.court_number);

    container.innerHTML = courts.map(court => `
    <li class="bg-gray-100 rounded-full px-4 py-2 flex flex-col items-start gap-3 shadow-sm">
      <div class="flex items-center gap-3 w-full">
        <input
          class="bg-transparent border-b border-gray-300 focus:border-blue-500 outline-none w-28 font-medium"
          value="${court.name}"
          onchange="updateCourt(${eventId}, ${court.id}, 'name', this.value)"
          title="Click to edit name">

        <input
          type="number" min="1"
          class="bg-transparent border-b border-gray-300 focus:border-blue-500 outline-none w-16 text-center"
          value="${court.court_number}"
          onchange="updateCourt(${eventId}, ${court.id}, 'court_number', this.value)"
          title="Click to edit number">

        <button onclick="deleteCourt(${eventId}, ${court.id})"
          class="text-red-500 hover:text-red-700 text-lg font-bold" title="Delete">
          &times;
        </button>
      </div>

    </li>
  `).join('');

    // Append the "+" button at the end for adding courts
    container.innerHTML += `
    <li class="bg-blue-100 text-blue-600 rounded-full px-4 py-2 flex items-center justify-center cursor-pointer hover:bg-blue-200 shadow-sm"
        onclick="addCourt(${eventId})" title="Add court">
      <span class="text-xl font-bold">+</span>
    </li>
  `;
}

async function updateCourt(eventId, id, field, value) {
    const input = event.target;

    const res = await fetch(`/cup/api/courts/${id}/`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({ [field]: field === "court_number" ? parseInt(value) : value })
    });

    if (!res.ok) {
        const err = await res.json();
        const errorMessage = err?.[field]?.[0] || err?.detail || "Update failed";
        showToast(errorMessage, false);
        input.classList.add("border-red-500", "text-red-700");
        setTimeout(() => {
            input.classList.remove("border-red-500", "text-red-700");
            loadCourts(eventId); // use passed eventId
        }, 1500);
    } else {
        showToast("Saved!");
        input.classList.remove("border-red-500", "text-red-700");
    }
}

//async function deleteCourt(eventId, id) {
//    if (!confirm("Are you sure you want to delete this court?")) return;

//    const res = await fetch(`/cup/api/courts/${id}/`, {
//        method: "DELETE",
//        headers: {
//            "Content-Type": "application/json",
//            "X-CSRFToken": csrftoken // Include the CSRF token for delete
//        }
//    });

//    if (res.ok) {
//        showToast("Court deleted!");
//        loadCourts(eventId );  // Reload courts list
//} else {
//    const err = await res.json();
//    showToast(err?.detail || "Failed to delete court", false);
//}
//}

function deleteCourt(eventId, id) {
    showDeleteModal("Are you sure you want to delete this court?", async () => {
        const res = await fetch(`/cup/api/courts/${id}/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": csrftoken },
        });
        if (res.ok) {
            showToast("Court deleted");
            loadCourts(eventId);
        } else {
            showToast("Failed to delete", false);
        }
    });
}

async function addCourt(eventId) {
    // Get existing courts to determine the next available court number
    const res = await fetch(`/cup/api/courts/?event=${eventId}`);
    const courts = await res.json();

    // Find the next available court number
    const nextNumber = (Math.max(0, ...courts.map(c => c.court_number)) + 1);
    const name = `Court ${nextNumber}`;

    const createRes = await fetch("/cup/api/courts/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken  // Ensure CSRF token is included
        },
        body: JSON.stringify({
            event: eventId,        // The event ID for which the court is created
            name: name,            // The court name (auto-generated)
            court_number: nextNumber // The auto-generated court number
        })
    });

    if (createRes.ok) {
        showToast("Court added!");
        loadCourts(eventId); // Reload the courts list
    } else {
        const err = await createRes.json();
        console.error("Add court error:", err); // log to browser console
        showToast(err?.detail || "Failed to add court", false);
    }
}

async function addTimeSlot(event_id, courtId) {
    const start_time = prompt("Enter start time (YYYY-MM-DDTHH:MM):");
    const end_time = prompt("Enter end time (YYYY-MM-DDTHH:MM):");

    if (start_time && end_time) {
        const res = await fetch("/cup/api/timeslots/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({
                court: courtId,
                start_time: start_time,
                end_time: end_time
            })
        });

        if (res.ok) {
            alert("Time Slot Added!");
            loadCourts( event_id );
    } else {
        const err = await res.json();
        alert(err?.detail || "Failed to add time slot");
    }
}
}

async function deleteTimeSlot(event_id, timeSlotId, courtId) {
    const res = await fetch(`/cup/api/timeslots/${timeSlotId}/`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        }
    });

    if (res.ok) {
        alert("Time Slot Deleted!");
        loadCourts(event_id);
} else {
    const err = await res.json();
    alert(err?.detail || "Failed to delete time slot");
}
}