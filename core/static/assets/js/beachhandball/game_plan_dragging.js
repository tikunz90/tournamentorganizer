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
    swapGameRows(draggedRow, this);
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
