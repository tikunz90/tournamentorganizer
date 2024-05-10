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

  md.initFormExtendedDatetimepickers();
  $.fn.dataTable.moment("HH:mm (DD.MM.YYYY)");

  setupDatetime();
  setupTable();

  setupRows();
  setupRowClick();
}); // Closing doc ready

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

      this.addEventListener("contextmenu", showContextMenu);

      //console.log($row.find('#id_starttime').val());
    });
  doRowColoring();
}

function doRowColoring() {
  selectedRowColor = "";
  selectedSecondRowColor = "";
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
      $starttime = $(this).find("#id_starttime");

      if ($starttime.length == 0) {
        return;
      }

      if (isFirst) {
        isFirst = false;
        actTime = $starttime.val();
        $(this).css("background-color", colors[colorIdx]);
      }

      if ($starttime.val() == actTime) {
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
  $(".game-list-datetime").each(function (i, datetime_input) {
    var userDate = datetime_input.attributes.value.value;
    var date_string = moment(userDate, "YYYY-MM-DD HH:mm:ss").format(
      "MM/DD/YYYY HH:mm"
    );
    $(datetime_input).val(date_string);
  });
}

function setupTable() {
  var table = $("#table-games").DataTable({
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

$(".game-list-datetime-label").on("dblclick", function () {
  $(this).attr("hidden", true);
  var close = $(this).parent().children(".game-list-datetime-input");
  $(close[0]).attr("hidden", false);
});
$(".game-list-datetime").on("keyup", function (e) {
  var code = e.key; // recommended to use e.key, it's normalized across devices and languages
  if (code === "Enter") e.preventDefault();
  if (code === " " || code === "Enter" || code === "," || code === ";") {
    var game_id = $(this).data("game_id");
    var date_string = moment($(this).val(), "MM/DD/YYYY HH:mm").format(
      "YYYY-MM-DD HH:mm:ss"
    );
    var data = postUpdateGameDateTime(game_id, date_string);
    $(this).closest(".game-list-datetime-input").first().attr("hidden", true);
    var close = $(this)
      .closest(".game-list-datetime-td")
      .first()
      .children(".game-list-datetime-label");
    $(close[0]).attr("hidden", false);
    var table = $("#table-games").DataTable();
    var order = table.order([1, "asc"]);

    doRowColoring();
  } // missing closing if brace
});

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
  var table = $("#table-games").DataTable();
  var order = table.order([1, "asc"]);
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
updateGameModalForm();

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
  updateGameModalForm();
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
      ).format("HH:mm (DD.MM.YYYY)");
      var date_input = moment(
        response.new_datetime,
        "YYYY-MM-DD HH:mm:ss"
      ).format("MM/DD/YYYY HH:mm");

      var game_td = $("#game-list-td-id-" + response.game);
      $(game_td).children(".game-list-datetime-label").first().text(date_label);
      $(game_td)
        .children(".game-list-datetime-input")
        .first()
        .children()
        .each(function (i, input) {
          $(input).val(date_input);
        });
      $(game_td)
        .children(".game-list-datetime-input")
        .find("#id_starttime")[0].value = date_input;
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
    },
    complete: function () {
      console.debug("complete");
    },
    error: function (xhr, textStatus, thrownError) {
      console.debug("error");
    },
  });
}
