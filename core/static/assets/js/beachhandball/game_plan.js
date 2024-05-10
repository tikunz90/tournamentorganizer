let draggedRow = null;
let selectedRow = null;
let selectedSecondRow = null;
let selectedRowColor = "";
let selectedSecondRowColor = "";
let selectedGameId = 0;
let isDragging = false;
let lastMouseY = 0;

$(document).ready(function () {
  //md.initFullCalendar();
  //md.initFullCalendar2();
  $("#update-game-result-form").modal("hide");
  $("#update-game-result-form").LoadingOverlay("hide");

  window.addEventListener("click", hideContextMenu);
  attachEventListeners();

  var checkbox = document.getElementById("checkFilterHideFinished");
  checkbox.addEventListener("change", function () {
    if (this.checked) {
      hideFinishedGames(1);
    } else {
      hideFinishedGames(-1);
    }
  });

  $(document).on("mousemove", function (e) {
    // Check if dragging is in progress
    //console.log("MouseMove");
    if (isDragging) {
      console.log("MouseY: " + e.clientY + " Height: " + window.innerHeight);
      // Calculate the difference in mouse position since the last event
      const deltaY = (e.clientY - lastMouseY) * 2;
      var height = window.innerHeight;
      // Adjust the scroll position accordingly
      //$('#table-games').scrollTop($('#table-games').scrollTop() + deltaY);
      window.scrollBy(0, deltaY);
      // Update the last mouse position
      lastMouseY = e.clientY;

      // Check if the mouse is over the last row of the screen
      const containerTop = $("#table-games").offset().top;
      const containerHeight = $("#table-games").height();
      const lastRowOffset = $("#table-games tr:last").offset().top;
      const lastRowHeight = $("#table-games tr:last").height();

      if (e.clientY > lastRowOffset - containerTop - lastRowHeight) {
        // Mouse is over the last row of the screen
        console.log("Mouse over last row");
      }
    }
  });

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

  md.initFormExtendedDatetimepickers();
  $.fn.dataTable.moment("HH:mm (DD.MM.YYYY)");

  var table = $("#table-games").DataTable({
    searching: false,
    paging: false,
    order: [[1, "asc"]],
  });

  // Repair DateTime Form because datetimepicker.min.js deletes input value on load
  $(".game-list-datetime").each(function (i, datetime_input) {
    var userDate = datetime_input.attributes.value.value;
    var date_string = moment(userDate, "YYYY-MM-DD HH:mm:ss").format(
      "MM/DD/YYYY HH:mm"
    );
    $(datetime_input).val(date_string);
  });

  //$('table').tableFilter({});
  $("#table-games").filterTable("#games-filter");
  //$('table').tableFilter('filterRows', 'The Beachers');

  var actTime = "";
  var colors = ["#f2f2f2", "#d9d9d9"];
  var actColor = "red";
  var isFirst = true;
  var colorIdx = 0;
  $("#table-games")
    .find("tr")
    .each(function (index) {
      $row = $(this);
      $(this).on("dragstart", dragStart);
      $(this).on("dragover", dragOver);
      $(this).on("dragenter", dragEnter);
      $(this).on("dragleave", dragLeave);
      $(this).on("drop", drop);
      $(this).on("dragend", dragEnd);

      //$(this).addEventListener("click", handleRowClick);
      this.addEventListener("contextmenu", showContextMenu);

      //console.log($row.find('#id_starttime').val());
      $starttime = $row.find("#id_starttime");
      if ($starttime.length == 0) {
        return;
      }
      if (isFirst) {
        isFirst = false;
        actTime = $starttime.val();
        $row.css("background-color", colors[colorIdx]);
      }

      if ($starttime.val() == actTime) {
      } else {
        actTime = $starttime.val();
        colorIdx++;
        if (colorIdx == 2) {
          colorIdx = 0;
        }
      }

      $row.css("background-color", colors[colorIdx]);
    });

  $(".game-row").click(function () {
    clearCssSelectedRow();
    // Remove the 'selected-row' class from all rows
    $(".game-row").removeClass("selected-row");

    // Add the 'selected-row' class to the clicked row
    $(this).addClass("selected-row");
    selectedRowColor = $(this).css("background-color");
    $(this).css("background-color", "#ff6347");
    $(this).css("border", "2px solid black");

    selectedRow = $(this);
    var date_string_dragged = moment(
      selectedRow.find("#id_starttime")[0].value,
      "MM/DD/YYYY HH:mm"
    ).format("YYYY-MM-DD HH:mm:ss");
    selectedGameId = selectedRow
      .find("#game_id_counter")[0]
      .getAttribute("data-content");
    var game_cnt = selectedRow.find("#game_id_counter")[0].innerText;
    console.log(selectedGameId + " " + game_cnt + " " + date_string_dragged);
  });
}); // Closing doc ready

function showContextMenu(event) {
  if (selectedSecondRow != null) {
    return;
  }
  event.preventDefault();

  selectedSecondRow = $(event.currentTarget);
  selectedSecondRowColor = selectedSecondRow.css("background-color");
  selectedSecondRow.css("background-color", "#DC143C");

  contextMenu.style.display = "block";
  contextMenu.style.left = event.clientX + "px";
  contextMenu.style.top = event.clientY + "px";
}

function handleContextMenuClick(action) {
  console.log("Performing action: " + action);
  hideContextMenu();
}

function hideContextMenu() {
  contextMenu.style.display = "none";
  if (selectedSecondRow != null) {
    selectedSecondRow.css("background-color", selectedSecondRowColor);
  }
  selectedSecondRow = null;
}

function showModal() {
  var modal = document.getElementById("modal-row-options");
  modal.style.display = "block";
}

function hideModal() {
  var modal = document.getElementById("modal-row-options");
  modal.style.display = "none";
}

function attachEventListeners() {
  var menuItems = document.querySelectorAll(".context-menu li");
  menuItems.forEach(function (item) {
    item.addEventListener("click", function () {
      handleContextMenuClick(item.id);
    });
  });

  var buttons = document.querySelectorAll(
    ".modal-gameplan-row-selection-content button"
  );
  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      handleButtonClick(button.id);
    });
  });

  var closeBtn = document.querySelector(".modal-gameplan-row-selection-close");
  closeBtn.addEventListener("click", hideModal);

  window.onclick = function (event) {
    var modal = document.getElementById("modal-row-options");
    if (event.target == modal) {
      hideModal();
    }
  };
}
function handleButtonClick(action) {
  console.log("Performing action: " + action);
  // Perform action based on button clicked
  hideModal();
}

function clearCssSelectedRow() {
  var findSelectedRow = $(".selected-row:first");
  if (findSelectedRow.length > 0) {
    findSelectedRow.css("background-color", selectedRowColor);
    findSelectedRow.css("border", "none");
  }
}

function enable_dragging() {
  if (document.getElementById("checkBoxEnableDragging").checked) {
    $("#table-games")
      .find("tr")
      .each(function (index) {
        $(this).attr("draggable", "true");
      });
  } else {
    $("#table-games")
      .find("tr")
      .each(function (index) {
        $(this).attr("draggable", "false");
      });
  }
}

// Handle the start of a drag event
function dragStart(e) {
  console.log("drag start");
  draggedRow = e.target;
  console.log(
    "Dragged row ID:",
    $(draggedRow).find("#game_id_counter")[0].innerText
  );
  //draggedRow.classList.add('tr-dragged');
  //e.dataTransfer.setData('text/plain', ''); // Needed for Firefox
  //document.addEventListener('wheel', preventScroll, { passive: false });
  //$('#table-games').on('wheel', preventScroll);
  // Set dragging flag to true
  isDragging = true;
  // Save the initial mouse position
  lastMouseY = e.clientY;

  clearCssSelectedRow();
}

function preventScroll(e) {
  e.preventDefault();
}

// Handle the dragging over of a row
function dragOver(e) {
  const row = e.target.closest(".game-row");
  //console.log("Dragged OVER row ID:", $(row).find('#game_id_counter')[0].innerText);
  e.preventDefault();
  this.classList.add("tr-over");
}

// Handle the entering of a row during drag
function dragEnter(e) {
  const row = e.target.closest(".game-row");
  //console.log("drag enter ", $(row).find('#game_id_counter')[0].innerText, ' ' + $(draggedRow).find('#game_id_counter')[0].innerText);
  e.preventDefault();
  this.classList.add("tr-over");
  //$(row).css('border', '5px solid black');
}

// Handle the leaving of a row during drag
function dragLeave(e) {
  const row = e.target.closest(".game-row");
  //console.log("drag leave ", $(row).find('#game_id_counter')[0].innerText, ' ' + $(draggedRow).find('#game_id_counter')[0].innerText);
  this.classList.remove("tr-over");
  //$(row).css('border', '0px solid black');
}

// Handle the drop of a row
function drop(e) {
  console.log("drag drop");
  const row = e.target.closest(".game-row");
  const droppedRow = e.target;
  console.log(
    "Dragged DROP before row ID:",
    $(row).find("#game_id_counter")[0].innerText
  );
  e.preventDefault();

  let targetRow = $(this);
  if (targetRow.hasClass("tr-over") && draggedRow !== targetRow[0]) {
    var date_string_dragged = moment(
      $(draggedRow).find("#id_starttime")[0].value,
      "MM/DD/YYYY HH:mm"
    ).format("YYYY-MM-DD HH:mm:ss");
    var date_string_target = moment(
      targetRow.find("#id_starttime")[0].value,
      "MM/DD/YYYY HH:mm"
    ).format("YYYY-MM-DD HH:mm:ss");
    //console.log("datestring dragged ", date_string_dragged);
    var dateValueDragged = $(draggedRow).find("#id_starttime")[0].value;
    var dateValueTarget = targetRow.find("#id_starttime")[0].value;

    var game_id_dragged = $(draggedRow)
      .find("#id_starttime")
      .eq(0)
      .data("game_id");
    var game_counter_dragged =
      $(draggedRow).find("#game_id_counter")[0].innerText;
    var date_label_dragged = moment(
      date_string_dragged,
      "YYYY-MM-DD HH:mm:ss"
    ).format("HH:mm (DD.MM.YYYY)");
    var date_input_dragged = moment(
      date_string_dragged,
      "YYYY-MM-DD HH:mm:ss"
    ).format("MM/DD/YYYY HH:mm");
    var bg_color_dragged = $(draggedRow).css("background-color");

    var game_id_target = targetRow.find("#id_starttime").eq(0).data("game_id");
    var game_counter_target = targetRow.find("#game_id_counter")[0].innerText;
    var date_label_target = moment(
      date_string_target,
      "YYYY-MM-DD HH:mm:ss"
    ).format("HH:mm (DD.MM.YYYY)");
    var date_input_target = moment(
      date_string_target,
      "YYYY-MM-DD HH:mm:ss"
    ).format("MM/DD/YYYY HH:mm");
    var bg_color_target = targetRow.css("background-color");

    targetRow.find("#id_starttime_label")[0].innerText = date_label_dragged;
    targetRow.find("#id_starttime")[0].value = date_input_dragged;
    targetRow.find("#game_id_counter")[0].innerText = game_counter_dragged;
    targetRow.css("background-color", bg_color_dragged);

    $(draggedRow).find("#id_starttime_label")[0].innerText = date_label_target;
    $(draggedRow).find("#id_starttime")[0].value = date_input_target;
    $(draggedRow).find("#game_id_counter")[0].innerText = game_counter_target;
    $(draggedRow).css("background-color", bg_color_target);

    let parent = targetRow.parent();
    let draggedIndex = $(draggedRow).index();
    let targetIndex = targetRow.index();
    var draggedSibbling = $(draggedRow)[0].nextSibling;
    if (draggedIndex < targetIndex) {
      targetRow[0].parentNode.insertBefore(
        $(draggedRow)[0],
        targetRow[0].nextSibling
      );
      targetRow[0].parentNode.insertBefore(targetRow[0], draggedSibbling);
    } else {
      targetRow[0].parentNode.insertBefore($(draggedRow)[0], targetRow[0]);
      targetRow[0].parentNode.insertBefore(targetRow[0], draggedSibbling);
    }

    var gameJsonDragged = {
      game: game_id_dragged,
      datetime: moment(
        $(draggedRow).find("#id_starttime")[0].value,
        "MM/DD/YYYY HH:mm"
      ).format("YYYY-MM-DD HH:mm:ss"),
      game_counter: parseInt(game_counter_target),
    };
    postUpdateGameAfterDrag(game_id_dragged, gameJsonDragged);

    var gameJsonTarget = {
      game: game_id_target,
      datetime: moment(
        targetRow.find("#id_starttime")[0].value,
        "MM/DD/YYYY HH:mm"
      ).format("YYYY-MM-DD HH:mm:ss"),
      game_counter: parseInt(game_counter_dragged),
    };
    postUpdateGameAfterDrag(game_id_target, gameJsonTarget);
  }
}

// Handle the end of a drag event
function dragEnd(e) {
  console.log("drag end");
  draggedRow = null;
  isDragging = false;
  //document.removeEventListener('wheel', preventScroll);
  //$('#table-games').off('wheel', preventScroll);
  $("#table-games")
    .find("tr")
    .each(function (index) {
      $(this).removeClass("tr-over");
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

function postUpdateGameAfterDrag(game_id, gameJsonData) {
  return $.ajax({
    type: "POST",
    url: "ajax/update-game-after-drag/" + game_id + "/",
    data: gameJsonData,
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
      console.log("success: ");
    },
    complete: function () {
      console.debug("complete");
    },
    error: function (xhr, textStatus, thrownError) {
      console.debug("error");
    },
  });
}

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
