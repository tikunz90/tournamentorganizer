let selectedGameTimeRow = null;
let selectedRow = null;
let selectedSecondRow = null;
let selectedRowColor = "";
let selectedSecondRowColor = "";
let selectedGameId = 0;

$(document).ready(function () {
  $("#update-game-result-form").modal("hide");
  $("#update-game-result-form").LoadingOverlay("hide");

  setupExportButtons();
  setupAddMinutesButton();

    //md.initFormExtendedDatetimepickers();
    flatpickr('.datetimepicker', {
        enableTime: true,
        dateFormat: "Y-m-d H:i:S",
        time_24hr: true,
        allowInput: true,
        locale: "de", // Remove or change if you want a different locale
        onOpen: function (selectedDates, dateStr, instance) {
            instance._originalValue = instance.input.value;
            instance._changedByUser = false;
        },
        onValueUpdate: function (selectedDates, dateStr, instance) {
            // Only set changed if the update was from a calendar click, not just parsing
            if (instance.isOpen && instance._flatpickr && instance._flatpickr.latestSelectedDateObj) {
                // This is a real user selection
                instance._changedByUser = true;
            }
        },
        onClose: function (selectedDates, dateStr, instance) {
            if (!instance._changedByUser) {
                instance.input.value = instance._originalValue || '';
            }
            var $input = $(instance.input);
            var $inputDiv = $input.closest('.game-list-datetime-input');
            var $label = $inputDiv.siblings('.game-list-datetime-label');
            $label.attr('hidden', false);
            $input.attr('hidden', true);

            if (dateStr) {
                //var $td = $(instance.input).closest('td');
                //$td.contents().filter(function () {
                //    return this.nodeType === 3; // text node
                //}).first().replaceWith(dateStr);
                // Call updateGameTime with gameId and new time
                var gameId = $(instance.input).data('game_id');
                var data = postUpdateGameDateTime(gameId, dateStr);
            }
            
        }
    });
  $.fn.dataTable.moment("HH:mm (DD.MM.YYYY)");

  setupDatetime();
  setupTable();

  setupRows();
    setupRowClick();
    renderCourtView();

    setInterval(refreshTableGames, 5000);
    //setInterval(updateRunningGames, 5000);

    $('#print-court-view').on('click', function () {
        // Check which view is visible
        const courtView = document.getElementById('court-view');
        const defaultView = document.getElementById('default-view');
        if (courtView.style.display !== 'none') {
            printCourtView();
        } else if (defaultView.style.display !== 'none') {
            printTableGames();
        }
    });

    $("#table-games tbody tr").each(function () {
        var $gamestateTd = $(this).find('td[data-tag="gamestate"]');
        if ($gamestateTd.length && $gamestateTd.text().trim() === "APPENDING") {
            this.scrollIntoView({ behavior: "smooth", block: "center" });
            return false; // Stop after the first match
        }
    });

    function refreshTableGames() {
        $.ajax({
            url: '/api/games/table/',
            type: 'GET',
            dataType: 'json',
            success: function (games) {
                games.forEach(function (game) {
                    var $row = $('#table-games tbody').find(`tr.game-row[data-content="${game.id}"]`);
                    if ($row.length) {
                        // Update each <td> by index or data-tag as needed
                        //$row.find('td[data-tag="gamedate"] .game-list-datetime-label').text(
                        //    moment(game.starttime).format('DD.MM.')
                        //);
                        //$row.find('td[data-tag="gametime"]').contents().filter(function () {
                        //    return this.nodeType === 3;
                        //}).first().replaceWith(
                        //    moment(game.starttime).format('HH:mm') + ' '
                        //);
                        //$row.find('td[data-tag="cat"]').text(game.tournament_event?.category?.classification || '');
                        //$row.find('td[data-tag="tstate_id"] .btn-small').css('background', game.tournament_state?.color || '');
                        //$row.find('td[data-tag="tstate_id"] .btn-small a b').text(
                        //    (game.tournament_event?.category?.abbreviation || '') + ' ' +
                        //    (game.tournament_state?.abbreviation || '')
                        //);
                        //$row.find('td[data-tag="team_a"]').text(game.team_st_a?.team?.name || '');
                        //$row.find('td[data-tag="team_b"]').text(game.team_st_b?.team?.name || '');
                        //$row.find('.game-list-court-label').text(
                        //    (game.court?.name || '') + ' (' + (game.court?.number || '') + ')'
                        //);
                        $row.find(`#${game.id}_result_ht1`).text(`${game.score_team_a_halftime_1}:${game.score_team_b_halftime_1}`);
                        $row.find(`#${game.id}_result_ht2`).text(`${game.score_team_a_halftime_2}:${game.score_team_b_halftime_2}`);
                        $row.find(`#${game.id}_result_p`).text(`${game.score_team_a_penalty}:${game.score_team_b_penalty}`);
                        $row.find('td[data-tag="sets"]').text(`${game.setpoints_team_a}:${game.setpoints_team_b}`);
                        //$row.find(`#${game.id}_refs`).text(
                        //    (game.ref_a?.abbreviation || '-') + ' / ' + (game.ref_b?.abbreviation || '-')
                        //);
                        $row.find(`#${game.id}_gamestate`).text(game.gamestate);
                        $row.find('td[data-tag="gamestate"]').text(game.gamestate);
                    }
                    // Optionally: handle new games (not present in DOM) if needed
                });
            },
            error: function (xhr, status, error) {
                console.error('Failed to refresh table-games:', status, error);
            }
        });
    }
    function updateRunningGames() {
        $("#table-games tbody tr").each(function () {
            var $row = $(this);
            var $gamestateTd = $row.find('td[data-tag="gamestate"]');
            var gamestate = $gamestateTd.text().trim();
            if (gamestate === "RUNNING") {
                var gameId = $row.data("content");
                $.ajax({
                    url: `/api/games/${gameId}/?depth=0`, // Adjust endpoint as needed
                    type: 'GET',
                    dataType: 'json',
                    success: function (data) {
                        // Example: update score and gamestate columns
                        if (data) {
                            // Update results
                            $row.find(`#${gameId}_result_ht1`).text(`${data.score_team_a_halftime_1}:${data.score_team_b_halftime_1}`);
                            $row.find(`#${gameId}_result_ht2`).text(`${data.score_team_a_halftime_2}:${data.score_team_b_halftime_2}`);
                            $row.find(`#${gameId}_result_p`).text(`${data.score_team_a_penalty}:${data.score_team_b_penalty}`);
                            // Update sets
                            $row.find('td[data-tag="sets"]').text(`${data.setpoints_team_a}:${data.setpoints_team_b}`);
                            $row.find(`#${gameId}_gamestate`).text(`${data.gamestate}`);
                            // Update gamestate
                            $gamestateTd.text(data.gamestate);
                        }
                    },
                    error: function (xhr, status, error) {
                        // Handle the error here
                        console.error(`Failed to update game ${gameId}:`, status, error);
                        // Optionally, show a message in the UI:
                        // $row.find('td[data-tag="gamestate"]').text("Error");
                    }
                });
            }
        });
    }

}); // Closing doc ready

function renderCourtView() {
    // 1. Gather all games from #table-games
    let games = [];
    let courts = [];
    let courtMap = {};
    // Get court headers from #table-games
    $("#table-games thead th").each(function (idx, th) {
        let col = $(th).data("col");
        if (col === "court") {
            // Find all unique courts from the table body
            $("#table-games tbody tr").each(function () {
                let courtName = $(this).find(".game-list-court-label").text().trim();
                let courtId = $(this).find(".game-list-court-td").data("content");
                if (courtId && !courtMap[courtId]) {
                    courts.push({ id: courtId, name: courtName });
                    courtMap[courtId] = true;
                }
            });
        }
    });

    // Gather game data
    $("#table-games tbody tr").each(function () {
        let $row = $(this);
        let starttime = $row.find("#initial-id_starttime").val();
        let courtId = $row.find(".game-list-court-td").data("content");
        let teamA = $row.find("td[data-tag='team_a']").text().trim();
        let teamB = $row.find("td[data-tag='team_b']").text().trim();
        let stateColor = $row.find(".btn-small").css("background-color");
        let stateAbbr = $row.find(".btn-small").text().trim();
        let category = $row.find("td[data-tag='cat']").text().trim();
        let gameId = $row.data("content");
        //let res_halftime1 = $row.find("td[data-tag='res_ht1']").text().trim();
        //let res_halftime2 = $row.find("td[data-tag='res_ht2']").text().trim();
        //let res_halftimepenalty = $row.find("td[data-tag='res_p']").text().trim();
        let results = $row.find("td[data-tag='results']").text().trim();
        let sets = $row.find("td[data-tag='sets']").text().trim();
        let gamestate = $row.find("td[data-tag='gamestate']").text().trim();

        games.push({
            id: gameId,
            starttime: starttime,
            courtId: courtId,
            teamA: teamA,
            teamB: teamB,
            stateColor: stateColor,
            stateAbbr: stateAbbr,
            category: category,
            results: results,
            sets: sets,
            gamestate: gamestate
        });
    });

    // 2. Group games by starttime
    let grouped = {};
    games.forEach(game => {
        if (!grouped[game.starttime]) grouped[game.starttime] = {};
        grouped[game.starttime][game.courtId] = game;
    });

    // 3. Sort times and courts
    let times = Object.keys(grouped).sort();
    courts.sort((a, b) => a.name.localeCompare(b.name));

    // 4. Build HTML
    let html = '<table class="table body"><thead class="text-primary"><tr><th class="text-center" style="font-weight: bold;">Time</th>';
    courts.forEach(court => {
        html += `<th class="text-center" style="font-weight: bold;">${court.name}</th>`;
    });
    html += '</tr></thead><tbody>';

    // Day separator logic
    let prevDay = null;
    times.forEach(timeStr => {
        let dateObj = moment(timeStr, "YYYY-MM-DD HH:mm:ss");
        let dayStr = dateObj.format("dddd DD.MM.");
        if (prevDay !== dayStr) {
            html += `<tr><td class="text-left" colspan="${courts.length + 1}" style="background: #f5f5f5; font-weight: bold;">${dayStr}</td></tr>`;
            prevDay = dayStr;
        }
        html += `<tr><td class="text-center">${dateObj.format("HH:mm")}</td>`;
        courts.forEach(court => {
            let game = grouped[timeStr][court.id];
            if (game) {
                // --- Team name rendering with Material icon ---
                let teamA = game.teamA.startsWith("emoji_events")
                    ? `<span class="material-icons" style="vertical-align:middle;">emoji_events</span> ${game.teamA.replace(/^emoji_events/, '').trim()}`
                    : `<b>${game.teamA}</b>`;
                let teamB = game.teamB.startsWith("emoji_events")
                    ? `<span class="material-icons" style="vertical-align:middle;">emoji_events</span> ${game.teamB.replace(/^emoji_events/, '').trim()}`
                    : `<b>${game.teamB}</b>`;
                // ---------------------------------------------

                html += `<td>
        <table style="width:100%; border: none;">
            <tr>
                <td style="vertical-align:top; border:none; padding:0 4px 0 0; text-align:left;">
                    <div class="btn btn-small" style="background: ${game.stateColor}; margin-bottom:2px;">
                        ${game.category}   ${game.stateAbbr}
                    </div>
                    <div style="color:black;">
                        ${teamA} vs. ${teamB}
                    </div>
                    <div style="color:black;">
                        ${game.gamestate}
                    </div>
                </td>
                <td style="vertical-align:top; border:none; padding:0;">
                    <div style="font-size:90%; color:#333;">
                        <div>${game.results || ""}</div>
                        <div>Sets ${game.sets || ""}</div>
                    </div>
                </td>
            </tr>
        </table>
    </td>`;
            } else {
                html += "<td></td>";
            }
        });
        html += "</tr>";
    });
    html += "</tbody></table>";

    // 5. Render
    $("#court-view-table-container").html(html);
}

function printCourtView() {
    renderCourtView();
    var courtView = document.getElementById('court-view').cloneNode(true);
    var printBtn = courtView.querySelector('#print-court-view');
    if (printBtn) printBtn.parentNode.removeChild(printBtn);

    var printWindow = window.open('', '', 'width=900,height=700');
    printWindow.document.write('<html><head><title>Print Court View</title>');
    printWindow.document.write('<style>');
    printWindow.document.write('body { font-family: Arial, sans-serif; margin: 20px; }');
    printWindow.document.write('@media print {');
    printWindow.document.write('  body { background: white !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }');
    printWindow.document.write('  table { width: 100%; border-collapse: collapse; }');
    printWindow.document.write('  th, td { border: 1px solid #888; padding: 6px; }');
    printWindow.document.write('  .btn, .btn-small { color: #fff !important; font-weight: bold; border-radius: 4px; padding: 2px 6px; display: inline-block; }');
    printWindow.document.write('  .btn-small { font-size: 90%; }');
    printWindow.document.write('}');
    printWindow.document.write('</style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write('<h2 style="text-align:center;">Game Plan</h2>');
    printWindow.document.write(courtView.innerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();

    printWindow.onload = function () {
        printWindow.focus();
        printWindow.print();
        printWindow.close();
    };
}
function printTableGames() {
    // Clone the table-games node
    var tableGames = document.getElementById('table-games').cloneNode(true);

    // Remove action buttons from the clone (optional)
    var actionCells = tableGames.querySelectorAll('td.td-actions, th[data-col="actions"]');
    actionCells.forEach(function (cell) {
        cell.parentNode.removeChild(cell);
    });

    // Create a new window for printing
    var printWindow = window.open('', '', 'width=900,height=700');
    printWindow.document.write('<html><head><title>Print Game Plan</title>');
    printWindow.document.write('<style>');
    printWindow.document.write('body { font-family: Arial, sans-serif; margin: 20px; }');
    printWindow.document.write('@media print {');
    printWindow.document.write('  body { background: white !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }');
    printWindow.document.write('  table { width: 100%; border-collapse: collapse; }');
    printWindow.document.write('  th, td { border: 1px solid #888; padding: 6px; }');
    printWindow.document.write('  .btn, .btn-small { color: #fff !important; font-weight: bold; border-radius: 4px; padding: 2px 6px; display: inline-block; }');
    printWindow.document.write('  .btn-small { font-size: 90%; }');
    printWindow.document.write('}');
    printWindow.document.write('</style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write('<h2 style="text-align:center;">Game Plan</h2>');
    printWindow.document.write('<div style="width:100%;">');
    printWindow.document.write(tableGames.outerHTML);
    printWindow.document.write('</div>');
    printWindow.document.write('</body></html>');
    printWindow.document.close();

    // Wait for content to load, then print and close
    printWindow.onload = function () {
        printWindow.focus();
        printWindow.print();
        printWindow.close();
    };
}

function setupRows() {
  $("#table-games")
    .find("tr")
    .each(function (index) {
      //$row = $(this);
      this.addEventListener("dragstart", dragStart);
      this.addEventListener("dragover", dragOver);
      this.addEventListener("dragenter", dragEnter);
      this.addEventListener("dragleave", dragLeave);
      this.addEventListener("drop", drop);
      this.addEventListener("dragend", dragEnd);

      //this.addEventListener("contextmenu", showContextMenu);
      this.addEventListener("contextmenu", function (event) {
        // Get the clicked column index
        var clickedColumnIndex = getColumnIndex(event.target);
        // Call showContextMenu function with the clicked column index
        showContextMenu(event, clickedColumnIndex);
      });

      //console.log($row.find('#id_starttime').val());
    });
  doRowColoring();
}

function getColumnIndex(target) {
  // Navigate up the DOM to find the cell element (td)
  while (target && target.tagName !== "TD") {
    target = target.parentNode;
  }
  // If the cell element is found, return its index within the row
  if (target && target.tagName === "TD") {
    return target.cellIndex;
  }
  return -1; // Return -1 if the cell element is not found
}

function doRowColoring() {
  selectedRowColor = "";
  selectedSecondRowColor = "";
  $(".game-row").removeClass("selected-row");
  var actTime = "";
  var colors = ["#f2f2f2", "#d9d9d9"];
  var actColor = "red";
  var isFirst = true;
  var colorIdx = 0;
  var courts = [];
  var actCourt = "";
  var newCourt = "";
  $("#table-games")
    .find("tr")
    .each(function (index) {
      $starttime = $(this).find("#initial-id_starttime");

      if ($starttime.length == 0) {
        return;
      }

      if (isFirst) {
        isFirst = false;
        actTime = $starttime.val();
        $(this).css("background-color", colors[colorIdx]);
      }

      if ($starttime.val() == actTime) {
        $(this).css("background-color", colors[colorIdx]);
      } else {
        actTime = $starttime.val();
        courts = [];
        colorIdx++;
        if (colorIdx == 2) {
          colorIdx = 0;
        }
      }

      let selectedGameId = $(this)
        .find("#game_id_counter")[0]
        .getAttribute("data-content");

      colCourt = $(this).find("#game-list-td-court-" + selectedGameId);
      newCourt = colCourt.data("content");
      if (!courts.includes(newCourt)) {
        colCourt.css("background-color", colors[colorIdx]);
        // If not in array, add it
        courts.push(newCourt);
      } else {
        colCourt.css("background-color", "red");
      }

      $(this).css("background-color", colors[colorIdx]);
    });
}

function setupRowClick() {
  $(".game-row").click(function () {
    clearCssSelectedRow();
    // Remove the 'selected-row' class from all rows
    $(".game-row").removeClass("selected-row");

    if (selectedRow === this) {
      return;
    }

    // Add the 'selected-row' class to the clicked row
    $(this).addClass("selected-row");
    selectedRowColor = $(this).css("background-color");
    $(this).css("background-color", "#ff6347");
    $(this).css("border", "2px solid black");

    selectedRow = this;
    var date_string_dragged = moment(
      $(selectedRow).find("#id_starttime")[0].value,
      "MM/DD/YYYY HH:mm"
    ).format("YYYY-MM-DD HH:mm:ss");
    selectedGameId = $(selectedRow)
      .find("#game_id_counter")[0]
      .getAttribute("data-content");
    var game_cnt = $(selectedRow).find("#game_id_counter")[0].innerText;
    console.log(selectedGameId + " " + game_cnt + " " + date_string_dragged);
  });
}

function setupDatetime() {
  // Repair DateTime Form because datetimepicker.min.js deletes input value on load
  //$(".game-list-datetime").each(function (i, datetime_input) {
  //  var userDate = datetime_input.attributes.value.value;
  //  var date_string = moment(userDate, "YYYY-MM-DD HH:mm:ss").format(
  //    "MM/DD/YYYY HH:mm"
  //  );
  //  $(datetime_input).val(date_string);
  //});
  $(".game-list-datetime-init").each(function (i, datetime_input) {
    var userDate = datetime_input.attributes.value.value;
    var date_string = moment(userDate, "YYYY-MM-DD HH:mm:ss").format(
      "YYYY-MM-DD HH:mm:ss"
    );
    $(datetime_input).val(date_string);
  });
}

function setupTable() {
  var table = $("#table-games").DataTable({
    ordering: false,
    searching: false,
    paging: false,
    order: [[1, "asc"]],
  });

  $("#table-games").filterTable("#games-filter");
}

function setupExportButtons() {
  var exportButtons = document.querySelectorAll(".export-button");

  exportButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      // Get the table element

      var table = document.getElementById("table-games");

      // Initialize the output string with column headers
      var output = "Game Plan\n\n";
      //output += "#\tName\tPosition\tID\n";

      // Iterate over table rows and columns to build the output string
      for (var i = 0; i < table.rows.length; i++) {
        var row = table.rows[i];

        // Check if the row is hidden
        if (row.style.display !== "none") {
          for (var j = 0; j < row.cells.length; j++) {
            output += row.cells[j].innerText + "\t";
          }
          output += "\n";
        }
      }

      // Create a Blob with the text content
      var blob = new Blob([output], { type: "text/plain" });

      // Create a temporary link element to initiate the download
      var link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "game_plan_export.txt";

      // Simulate a click on the link to trigger the download
      link.click();
    });
  });
}

function setupAddMinutesButton() {
  var addMinutesButtons = document.querySelectorAll(".add-minutes-button");
  addMinutesButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var $table = $("#table-games");
      var gameFound = false;
      var minutesValue = 0;
      var actDay = 0;
      $table.find("tr").each(function (index) {
        var $row = $(this);
        var gameId = parseInt(
          $row.find("#game_id_counter").attr("data-content")
        );

        if (gameId == selectedGameId) {
          console.log("Found selected game");
          minutesValue = $("#minutes-input").val();
          console.log("Start Adding " + minutesValue);
          actDay = moment(
            $row.find("#id_starttime")[0].value,
            "MM/DD/YYYY HH:mm"
          ).date();
          gameFound = true;
        }
        if (gameFound) {
          var actDate = moment(
            $row.find("#id_starttime")[0].value,
            "MM/DD/YYYY HH:mm"
          );
          if (actDay == actDate.date()) {
            console.log("Adding " + gameId);
            var newDate = actDate.clone().add(minutesValue, "minutes");
            var gameJson = {
              game: gameId,
              datetime: newDate.format("YYYY-MM-DD HH:mm:ss"),
            };
            //postUpdateGameStartTime(gameJson, gameJson);
            var data = postUpdateGameDateTime(
              gameId,
              newDate.format("YYYY-MM-DD HH:mm:ss")
            );
            //$row.find('#id_starttime')[0].value = moment(data['new_datetime'], "YYYY-MM-DD HH:mm:ss").format("MM/DD/YYYY HH:mm");
          }
        }
      });
    });
  });
}

function changeGameTime(row) {
  if (selectedGameTimeRow == null) {
    return;
  }

  var game_id = $(row).data("content");
  var dateInput = $(selectedGameTimeRow).find("#id_starttime");
  var datetimeValue = dateInput.datetimepicker('date');
  var date_string = moment(datetimeValue, "MM/DD/YYYY HH:mm").format(
    "YYYY-MM-DD HH:mm:ss"
  );
  var data = postUpdateGameDateTime(game_id, date_string);
}

// Initialize flatpickr for all gametime-picker inputs
$('.gametime-picker').flatpickr({
    enableTime: true,
    noCalendar: true,
    dateFormat: "H:i",
    time_24hr: true,
    allowInput: true,
    onClose: function (selectedDates, dateStr, instance) {
        // Hide the input after picking
        $(instance.input).hide();
        // Optionally update the <td> text
        if (dateStr) {
            var $td = $(instance.input).closest('td');
            $td.contents().filter(function () {
                return this.nodeType === 3; // text node
            }).first().replaceWith(dateStr);
            // Call updateGameTime with gameId and new time
            var gameId = $(instance.input).data('game_id');
            updateGameTime(gameId, dateStr);
        }
    }
});

// Show the time picker input when <td> is clicked
$('.gametime-td').on('click', function () {
    var $input = $(this).find('.gametime-picker');
    $input.show().focus();
    if ($input[0]._flatpickr) {
        $input[0]._flatpickr.open();
    }
});

const csrfToken = getCSRFToken();
function updateGameTime(gameId, newTime) {
    // newTime should be in "HH:mm" format
    $.ajax({
        url: `/api/games/${gameId}/update_game_time/`, 
        type: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify({ starttime: newTime }),
        success: function (response) {

            // Update the visible time in the gametime-td
            //$("#" + gameId + "_gametime").contents().filter(function () {
            //    return this.nodeType === 3; // text node
            //}).first().replaceWith(newTime);

            var $tdGameTime = $("#" + response.game + "_gametime");
            // Find the first text node and replace its value
            $tdGameTime.contents().filter(function () {
                return this.nodeType === 3; // text node
            }).first().replaceWith(newTime + " ");
            // Update the input value and flatpickr instance
            var $picker = $tdGameTime.find('.gametime-picker');
            $picker.val(newTime);
            if ($picker[0] && $picker[0]._flatpickr) {
                $picker[0]._flatpickr.setDate(newTime, true);
            }

            // Update the datetime inputs in the corresponding row
            var $td = $("#game-list-td-id-" + gameId);
            // If your backend returns the new full datetime string, use it; otherwise, reconstruct it
            var newDatetime = response.new_datetime || response.starttime; // e.g. "2025-06-28 14:30:00"
            if (newDatetime) {
                var date_input = moment(
                    newDatetime
                ).format("YYYY-MM-DD HH:mm:ss");
                // Update both inputs
                $td.find('input.game-list-datetime').val(date_input);
                $td.find('input.game-list-datetime-init').val(date_input);

                // Also update flatpickr if present
                var $input = $td.find('input.game-list-datetime');
                if ($input[0] && $input[0]._flatpickr) {
                    $input[0]._flatpickr.setDate(date_input, true);
                }
            }

            var table = $("#table-games").DataTable();
            var order = table.order([1, "asc"]);
            $("#table-games").filterTable("#games-filter");
            clearCssSelectedRow();
            doRowColoring();


            // --- Update court-view table ---
            // Format new time and day
            var newDate = moment(response.new_datetime, "YYYY-MM-DD HH:mm:ss");
            var newTime = newDate.format("HH:mm");
            var newDay = newDate.format("dddd DD.MM.");

            // Find the court-view table
            var $courtTable = $("#court-view table.body");
            if ($courtTable.length) {
                // Find the row for the new time (by first column text)
                var $rows = $courtTable.find("tbody tr");
                var foundRow = null;
                $rows.each(function () {
                    var $firstTd = $(this).find("td").first();
                    if ($firstTd.text().trim() === newTime) {
                        foundRow = $(this);
                        return false; // break
                    }
                });

                // If not found, optionally create a new row (not shown here)
                if (foundRow) {
                    // Find the correct court column
                    var courtIdx = $courtTable.find("thead th").filter(function () {
                        return $(this).text().includes(response.court_name || response.court_id);
                    }).index();

                    // If you know the court index (e.g. court_id is 2nd court), you can use it directly:
                    // courtIdx = ... (calculate based on your courts order)

                    // Update the cell content
                    var $td = foundRow.find("td").eq(courtIdx);
                    // You may want to update with new info, e.g. teams, state, etc.
                    $td.html(
                        '<div class="btn btn-small" style="background: ' + (response.state_color || "#ccc") + '">' +
                        (response.state_abbr ? response.state_abbr : "") +
                        '</div>' +
                        '<div style="color:black;">' +
                        (response.team_a || "") + ' vs ' + (response.team_b || "") +
                        '</div>'
                    );
                }
            }
            console.log('Game time updated:', response);
        },
        error: function (xhr) {
            alert('Failed to update game time');
        }
    });
}

//$(".game-list-datetime-label").on("dblclick", function () {
//  $(this).attr("hidden", true);
//  var close = $(this).parent().children(".game-list-datetime-input");
//  $(close[0]).attr("hidden", false);
//});
$(".game-list-datetime-label").on("click", function () {
    $(this).attr("hidden", true);
    var $inputDiv = $(this).parent().children(".game-list-datetime-input");
    $inputDiv.attr("hidden", false);
    var $input = $inputDiv.find(".game-list-datetime");
    $input.focus();

    // If using flatpickr, open the picker immediately
    if ($input[0] && $input[0]._flatpickr) {
        $input[0]._flatpickr.open();
    }
});
//$(".game-list-datetime").on("keyup", function (e) {
//  var code = e.key; // recommended to use e.key, it's normalized across devices and languages
//  if (code === "Enter") e.preventDefault();
//  if (code === " " || code === "Enter" || code === "," || code === ";") {
//    var game_id = $(this).data("game_id");
//    var date_string = moment(
//        $(this).val(),
//        ["YYYY-MM-DD HH:mm:ss", "YYYY-MM-DD HH:mm", "MM/DD/YYYY HH:mm"]
//    ).format("YYYY-MM-DD HH:mm:ss");
//    var data = postUpdateGameDateTime(game_id, date_string);
//    $(this).closest(".game-list-datetime-input").first().attr("hidden", true);
//    var close = $(this)
//      .closest(".game-list-datetime-td")
//      .first()
//      .children(".game-list-datetime-label");
//    $(close[0]).attr("hidden", false);
//  } // missing closing if brace
//});

$(".game-list-court-label").on("dblclick", function () {
  $(this).attr("hidden", true);
  var close = $(this).parent().children(".game-list-court-select");
  $(close[0]).attr("hidden", false);
});
$(".game-list-court-select").on("change", function (e) {
  var game_id = $(this).data("game_id");
  var data = postUpdateGameCourt(game_id, $(e.target).val());
  $(this).closest(".game-list-court-select").first().attr("hidden", true);
  var close = $(this)
    .closest(".game-list-court-td")
    .first()
    .children(".game-list-court-label");
  $(close[0]).attr("hidden", false);
});

var asyncSuccessMessage2 = ["<div>", "</div>", "<script>", "</script>"].join();

function updateGameModalForm() {
  $(".update_game").each(function () {
    console.debug("#" + $(this).closest("table")[0].id);
    $(this).modalForm({
      modalID: "#game-modal",
      formURL: $(this).data("form-url"),
      asyncUpdate: false,
      asyncSettings: {
        closeOnSubmit: true,
        successMessage: asyncSuccessMessage2,
        dataUrl: $(this).data("list-url"),
        dataElementId: "#" + $(this).closest("table")[0].id,
        dataKey: "table",
        addModalFormFunction: reinstantiateModalForms,
      },
    });
  });
}
//updateGameModalForm();

function updateGameResultModalForm() {
  $(".update-game-result").each(function () {
    console.debug("#" + $(this).closest("table")[0].id);
    $(this).modalForm({
      modalID: "#game-modal",
      formURL: $(this).data("form-url"),
      asyncUpdate: true,
      asyncSettings: {
        closeOnSubmit: true,
        successMessage: asyncSuccessMessage2,
        dataUrl: $(this).data("list-url"),
        dataElementId: "#" + $(this).closest("table")[0].id,
        dataKey: "table",
        addModalFormFunction: reinstantiateModalForms,
      },
    });
  });
}
updateGameResultModalForm();
function reinstantiateModalForms() {
  updateGameResultModalForm();
  //updateGameModalForm();
}
function getUpdateGameDateTime(game_id) {
  return $.ajax({
    type: "GET",
    url: "ajax/update-game-date/" + game_id + "/",
    async: true,
    dataType: "json",
    done: function (data) {
      if (data) {
        console.debug(JSON.stringify(data));
        return data;
      }
    },
  });
}
function postUpdateGameDateTime(game_id, new_datetime) {
  return $.ajax({
    type: "POST",
    url: "ajax/update-game-date/" + game_id + "/",
    data: { game: game_id, datetime: new_datetime },
    async: true,
    dataType: "json",
    done: function (data) {
      console.debug("done");
      if (data) {
        console.debug(JSON.stringify(data));
        return data;
      }
    },
    success: function (response) {
      console.debug("success: ");

      var date_label = moment(
        response.new_datetime,
        "YYYY-MM-DD HH:mm:ss"
      ).format("DD.MM.");
      var time_label = moment(
        response.new_datetime,
        "YYYY-MM-DD HH:mm:ss"
      ).format("HH:mm");
      var date_input = moment(
        response.new_datetime,
        "YYYY-MM-DD HH:mm:ss"
      ).format("MM/DD/YYYY HH:mm");

        var $td = $("#" + response.game + "_gametime");
        // Find the first text node and replace its value
        $td.contents().filter(function () {
            return this.nodeType === 3; // text node
        }).first().replaceWith(time_label + " ");
        // Update the input value and flatpickr instance
        var $picker = $td.find('.gametime-picker');
        $picker.val(time_label);
        if ($picker[0] && $picker[0]._flatpickr) {
            $picker[0]._flatpickr.setDate(time_label, true);
        }

      var game_td = $("#game-list-td-id-" + response.game);
      $(game_td).children(".game-list-datetime-label").first().text(date_label);
        $(game_td)
            .children(".game-list-datetime-input")
            .find("input.game-list-datetime")
            .each(function (i, input) {
                if (input._flatpickr) {
                    input._flatpickr.setDate(date_input, true);
                } else {
                    $(input).val(date_input);
                }
            });
      $(game_td)
        .children(".game-list-datetime-input")
          .find("#initial-id_starttime")[0].value = time_label;
      //$(game_td)
      //  .children(".game-list-datetime-input")
      //  .find("#id_starttime")[0].value = date_input;

      if (selectedGameTimeRow != null) {
        $(selectedGameTimeRow).find("#id_starttime").datetimepicker("hide");
      }
      selectedGameTimeRow = null;

      var table = $("#table-games").DataTable();
      var order = table.order([1, "asc"]);
      $("#table-games").filterTable("#games-filter");
      clearCssSelectedRow();
        doRowColoring();


        // --- Update court-view table ---
        // Format new time and day
        var newDate = moment(response.new_datetime, "YYYY-MM-DD HH:mm:ss");
        var newTime = newDate.format("HH:mm");
        var newDay = newDate.format("dddd DD.MM.");

        // Find the court-view table
        var $courtTable = $("#court-view table.body");
        if ($courtTable.length) {
            // Find the row for the new time (by first column text)
            var $rows = $courtTable.find("tbody tr");
            var foundRow = null;
            $rows.each(function () {
                var $firstTd = $(this).find("td").first();
                if ($firstTd.text().trim() === newTime) {
                    foundRow = $(this);
                    return false; // break
                }
            });

            // If not found, optionally create a new row (not shown here)
            if (foundRow) {
                // Find the correct court column
                var courtIdx = $courtTable.find("thead th").filter(function () {
                    return $(this).text().includes(response.court_name || response.court_id);
                }).index();

                // If you know the court index (e.g. court_id is 2nd court), you can use it directly:
                // courtIdx = ... (calculate based on your courts order)

                // Update the cell content
                var $td = foundRow.find("td").eq(courtIdx);
                // You may want to update with new info, e.g. teams, state, etc.
                $td.html(
                    '<div class="btn btn-small" style="background: ' + (response.state_color || "#ccc") + '">' +
                    (response.state_abbr ? response.state_abbr : "") +
                    '</div>' +
                    '<div style="color:black;">' +
                    (response.team_a || "") + ' vs ' + (response.team_b || "") +
                    '</div>'
                );
            }
        }
    },
    complete: function () {
      console.debug("complete");
    },
    error: function (xhr, textStatus, thrownError) {
      console.debug("error");
    },
  });
}

function postUpdateGameCourt(game_id, new_court_id) {
  return $.ajax({
    type: "POST",
    url: "ajax/update-game-court/" + game_id + "/",
    data: { game: game_id, new_court: new_court_id },
    async: true,
    dataType: "json",
    done: function (data) {
      console.debug("done");
      if (data) {
        console.debug(JSON.stringify(data));
        return data;
      }
    },
    success: function (response) {
      console.debug("success: ");

      var game_td = $("#game-list-td-court-" + response.game);
      $(game_td)
        .children(".game-list-court-label")
        .first()
        .text(response.court);

      colCourt = $(this).closest(".game-list-court-td").first()[0];
      $(game_td).data("content", response.court_id);

      var table = $("#table-games").DataTable();
      var order = table.order([1, "asc"]);
      clearCssSelectedRow();
      doRowColoring();
    },
    complete: function () {
      console.debug("complete");
    },
    error: function (xhr, textStatus, thrownError) {
      console.debug("error");
    },
  });
}
