$(document).on('click', '.edit-team-btn', function () {
    const teamId = $(this).data('team-id');
    const $row = $(this).closest('td').find('.team-name');
    const teamName = $row.data('team-name');
    const teamAbbr = $row.data('team-abbr');

    $('#editTeamId').val(teamId);
    $('#editTeamName').val(teamName);
    $('#editTeamAbbr').val(teamAbbr);

    $('#editTeamModal').modal('show');
});

$('#editTeamForm').on('submit', function (e) {
    e.preventDefault();
    const teamId = $('#editTeamId').val();
    const name = $('#editTeamName').val();
    const abbreviation = $('#editTeamAbbr').val();

    $.ajax({
        url: `/api/teams2/${teamId}/`, // Adjust if your API URL differs
        type: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify({ name, abbreviation }),
        headers: {
            'X-CSRFToken': getCSRFToken(), // Use your CSRF helper if needed
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function (data) {
            // Update the table cell in-place
            const $cell = $(`.edit-team-btn[data-team-id="${teamId}"]`).closest('td');
            $cell.find('.team-name')
                .text(`${data.name} (${data.abbreviation})`)
                .data('team-name', data.name)
                .data('team-abbr', data.abbreviation);
            $('#editTeamModal').modal('hide');
        },
        error: function (xhr) {
            alert('Error updating team.');
        }
    });
});