// Initialize when document is ready
$(document).ready(function () {
    // Handle clicks on update_game buttons
    $(document).on("click", ".update_game", function (e) {
        e.preventDefault();

        // Get data from button
        const gameId = $(this).data("id");
        const fromGameplan = $(this).data("from-gameplan") || 0;
        const pkTevent = $(this).data("pk-tevent");
        const pkTstage = $(this).data("pk-tstage");

        // Show loading overlay
        $.LoadingOverlay("show", {
            background: "rgba(0, 0, 0, 0.5)",
            text: "Loading game data...",
            textColor: "#fff"
        });

        // Make REST API call to get game data
        $.ajax({
            url: `/api/games/${gameId}/modal/`,
            type: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            },
            success: function (data) {
                // Hide loading overlay
                $.LoadingOverlay("hide");

                // Show the modal with data
                showGameUpdateModal(data, gameId, fromGameplan, pkTevent, pkTstage);
            },
            error: function (xhr, status, error) {
                // Hide loading overlay
                $.LoadingOverlay("hide");

                // Show error notification
                md.showNotification('top', 'center', 'Error loading game data. Please try again.', 'danger');
                console.error("Error loading game data:", error);
            }
        });
    });
});

// Function to display the modal with game data
function showGameUpdateModal(data, gameId, fromGameplan, pkTevent, pkTstage) {
    // Create modal if it doesn't exist yet
    if ($("#gameUpdateModal").length === 0) {
        const modalHtml = `
            <div class="modal fade" id="gameUpdateModal" tabindex="-1" role="dialog" aria-labelledby="gameUpdateModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="gameUpdateModalLabel">Update Game</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <form id="gameUpdateForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="starttime">Start Time</label>
                                            <input type="datetime-local" class="form-control" id="starttime" name="starttime">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="court">Court</label>
                                            <select class="form-control" id="court" name="court" style="width: 100%" data-placeholder="Choose a court"></select>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="team_st_a">Team A</label>
                                            <select class="form-control" id="team_st_a" name="team_st_a" style="width: 100%" data-placeholder="Choose a TeamA"></select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="team_st_b">Team B</label>
                                            <select class="form-control" id="team_st_b" name="team_st_b" style="width: 100%" data-placeholder="Choose a TeamB"></select>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="ref_a">Referee A</label>
                                            <select class="form-control" id="ref_a" name="ref_a" style="width: 100%" data-placeholder="Choose a Referee A"></select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="ref_b">Referee B</label>
                                            <select class="form-control" id="ref_b" name="ref_b" style="width: 100%" data-placeholder="Choose a Referee B"></select>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="gamestate">Game State</label>
                                            <select class="form-control" id="gamestate" name="gamestate" style="width: 100%" data-placeholder="Choose a Gamestate"></select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="gamingstate">Gaming State</label>
                                            <select class="form-control" id="gamingstate" name="gamingstate" style="width: 100%" data-placeholder="Choose a Gamingstate"></select>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="saveGameBtn">Save Changes</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('body').append(modalHtml);

        // Initialize selectpicker
        //$('#gameUpdateModal .selectpicker').selectpicker();
        $('#gameUpdateModal select').select2({
            dropdownParent: $('#gameUpdateModal'),
            placeholder: function () {
                return $(this).data('placeholder') || '';
            },
            allowClear: true,
            width: '100%'
        });

        // Setup save button handler
        $("#saveGameBtn").on("click", function () {
            saveGameChanges(gameId, fromGameplan, pkTevent, pkTstage);
        });
    }

    

    // Store references for save handler
    $("#gameUpdateModal").data({
        "gameId": gameId,
        "fromGameplan": fromGameplan,
        "pkTevent": pkTevent,
        "pkTstage": pkTstage
    });

    // Show the modal
    $("#gameUpdateModal").modal("show");

    // Populate form with data
    populateGameForm(data);
}

// Populate the form with game data
function populateGameForm(data) {
    const game = data.game;

    // Handle starttime (could be Unix timestamp or ISO string with timezone)
    if (game.starttime) {
        try {
            let date = new Date(game.starttime);

            // Check if it's a Unix timestamp (number) or ISO string
            if (typeof game.starttime === 'number' || /^\d+$/.test(game.starttime)) {
                // Handle as Unix timestamp
                const timestamp = typeof game.starttime === 'number' ?
                    game.starttime * 1000 : parseInt(game.starttime) * 1000;
                date = new Date(timestamp);
            } else {
                // Handle as ISO string
                // If format is like "2025-06-28T11:00:00+02:00"
                date = new Date(game.starttime);
            }

            // Check if date is valid
            if (!isNaN(date.getTime())) {
                // Format without timezone info for the datetime-local input
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');

                const formattedDate = `${year}-${month}-${day}T${hours}:${minutes}`;
                $("#starttime").val(formattedDate);
            } else {
                console.warn('Invalid date value:', game.starttime);
            }
        } catch (error) {
            console.error('Error formatting starttime:', error, game.starttime);
        }
    }

    // Populate dropdowns
    populateDropdown('court', data.courts, game.court);
    populateDropdown('team_st_a', data.team_stats, game.team_st_a);
    populateDropdown('team_st_b', data.team_stats, game.team_st_b);
    populateDropdown('ref_a', data.referees, game.ref_a);
    populateDropdown('ref_b', data.referees, game.ref_b);
    populateDropdown('gamestate', data.gamestate_choices, game.gamestate);
    populateDropdown('gamingstate', data.gamingstate_choices, game.gamingstate);
}


// Helper function to populate dropdowns
function populateDropdown(id, options, selectedValue) {
    const select = document.getElementById(id);
    select.innerHTML = '<option value=""></option>'; // empty option for clear

    if (!options || !Array.isArray(options)) return;

    options.forEach(option => {
        const optionElement = document.createElement('option');
        const optionValue = String(option.id || option.value || '');
        const optionText = option.name || option.text || option.number || '';

        optionElement.value = optionValue;
        optionElement.textContent = optionText;

        select.appendChild(optionElement);
    });

    let selectedOptionValue = '';
    if (selectedValue != null) {
        const selectedId = typeof selectedValue === 'object' ? selectedValue.id : selectedValue;
        selectedOptionValue = String(selectedId);
    }

    $(select).val(selectedOptionValue).trigger('change');

    console.log(`Dropdown #${id} set to:`, $(select).val());
}
function saveGameChanges(gameId, fromGameplan, pkTevent, pkTstage) {
    // Show loading overlay
    $.LoadingOverlay("show", {
        background: "rgba(0, 0, 0, 0.5)",
        text: "Saving game data...",
        textColor: "#fff"
    });

    // Collect form data
    const formData = {
        starttime: document.getElementById('starttime').value,
        court: document.getElementById('court').value || null,
        team_st_a: document.getElementById('team_st_a').value || null,
        team_st_b: document.getElementById('team_st_b').value || null,
        ref_a: document.getElementById('ref_a').value || null,
        ref_b: document.getElementById('ref_b').value || null,
        gamestate: document.getElementById('gamestate').value || null,
        gamingstate: document.getElementById('gamingstate').value || null
    };

    // Convert empty strings to null
    Object.keys(formData).forEach(key => {
        if (formData[key] === '') {
            formData[key] = null;
        }
    });

    // Convert starttime to Unix timestamp if needed
    if (formData.starttime) {
        try {
            const date = new Date(formData.starttime);
            // Convert from milliseconds to seconds for backend
            formData.starttime = Math.floor(date.getTime() / 1000);
        } catch (error) {
            console.error('Error converting starttime to timestamp:', error);
            delete formData.starttime; // Remove if invalid
        }
    }

    // Get CSRF token
    const csrfToken = getCSRFToken();

    // Send update request
    $.ajax({
        url: `/api/games/${gameId}/modal/`,
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        data: JSON.stringify(formData),
        success: function (data) {
            // Hide loading overlay
            $.LoadingOverlay("hide");

            // Show success notification
            md.showNotification('top', 'center', 'Game updated successfully', 'success');

            // Close modal
            $("#gameUpdateModal").modal("hide");

            // Redirect based on fromGameplan value
            if (parseInt(fromGameplan) === 1) {
                window.location.href = '/game_plan/';
            } else {
                window.location.href = `/structure_setup/${pkTevent}/?tab=${pkTstage}&tab_tstate=0`;
            }
        },
        error: function (xhr, status, error) {
            // Hide loading overlay
            $.LoadingOverlay("hide");

            // Show error notification
            md.showNotification('top', 'center', 'Error updating game. Please try again.', 'danger');
            console.error("Error updating game:", error);
        }
    });
}
