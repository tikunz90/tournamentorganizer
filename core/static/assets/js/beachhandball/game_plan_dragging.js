let draggedRow = null;
let isDragging = false;
let lastMouseY = 0;

$(document).ready(function () {});

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
