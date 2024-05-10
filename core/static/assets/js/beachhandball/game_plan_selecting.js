$(document).ready(function () {
  window.addEventListener("click", hideContextMenu);

  window.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      hideContextMenu();
      $(".game-row").removeClass("selected-row");
      doRowColoring();
    }
  });

  attachEventListeners();
});

function swapGameRows(row_src, row_tgt) {
  if (row_src == null) {
    console.log("swapGameRows: row_src null");
    return;
  }
  if (row_tgt == null) {
    console.log("swapGameRows: row_tgt null");
    return;
  }
  if (row_src === row_tgt) {
    console.log("swapGameRows: rows are same");
    return;
  }

  var date_string_src = moment(
    $(row_src).find("#id_starttime")[0].value,
    "MM/DD/YYYY HH:mm"
  ).format("YYYY-MM-DD HH:mm:ss");
  var date_string_tgt = moment(
    $(row_tgt).find("#id_starttime")[0].value,
    "MM/DD/YYYY HH:mm"
  ).format("YYYY-MM-DD HH:mm:ss");

  var dateValueSource = $(row_src).find("#id_starttime")[0].value;
  var dateValueTarget = $(row_tgt).find("#id_starttime")[0].value;

  // Get Source Row Info
  var game_id_src = $(row_src).find("#id_starttime").eq(0).data("game_id");
  var game_counter_src = $(row_src).find("#game_id_counter")[0].innerText;

  var date_label_src = moment(date_string_src, "YYYY-MM-DD HH:mm:ss").format(
    "HH:mm (DD.MM.YYYY)"
  );
  var date_input_src = moment(date_string_src, "YYYY-MM-DD HH:mm:ss").format(
    "MM/DD/YYYY HH:mm"
  );
  var bg_color_src = $(row_src).css("background-color");

  // Get Target Row Info
  var game_id_target = $(row_tgt).find("#id_starttime").eq(0).data("game_id");
  var game_counter_target = $(row_tgt).find("#game_id_counter")[0].innerText;
  var date_label_target = moment(date_string_tgt, "YYYY-MM-DD HH:mm:ss").format(
    "HH:mm (DD.MM.YYYY)"
  );
  var date_input_target = moment(date_string_tgt, "YYYY-MM-DD HH:mm:ss").format(
    "MM/DD/YYYY HH:mm"
  );
  var bg_color_target = $(row_tgt).css("background-color");

  // Change Target Row
  $(row_tgt).find("#id_starttime_label")[0].innerText = date_label_src;
  $(row_tgt).find("#id_starttime")[0].value = date_input_src;
  $(row_tgt).find("#game_id_counter")[0].innerText = game_counter_src;
  $(row_tgt).css("background-color", bg_color_src);

  // Change Source Row
  $(row_src).find("#id_starttime_label")[0].innerText = date_label_target;
  $(row_src).find("#id_starttime")[0].value = date_input_target;
  $(row_src).find("#game_id_counter")[0].innerText = game_counter_target;
  $(row_src).css("background-color", bg_color_target);

  let srcIndex = $(row_src).index();
  let tgtIndex = $(row_tgt).index();
  var srcSibbling = $(row_src)[0].nextSibling;
  if (srcIndex < tgtIndex) {
    $(row_tgt)[0].parentNode.insertBefore(
      $(row_src)[0],
      $(row_tgt)[0].nextSibling
    );
    $(row_tgt)[0].parentNode.insertBefore($(row_tgt)[0], srcSibbling);
  } else {
    $(row_tgt)[0].parentNode.insertBefore($(row_src)[0], $(row_tgt)[0]);
    $(row_tgt)[0].parentNode.insertBefore($(row_tgt)[0], srcSibbling);
  }

  var gameJsonSrc = {
    game: game_id_src,
    datetime: moment(
      $(row_src).find("#id_starttime")[0].value,
      "MM/DD/YYYY HH:mm"
    ).format("YYYY-MM-DD HH:mm:ss"),
    game_counter: parseInt(game_counter_target),
  };
  postUpdateGameAfterDrag(game_id_src, gameJsonSrc);

  var gameJsonTarget = {
    game: game_id_target,
    datetime: moment(
      $(row_tgt).find("#id_starttime")[0].value,
      "MM/DD/YYYY HH:mm"
    ).format("YYYY-MM-DD HH:mm:ss"),
    game_counter: parseInt(game_counter_src),
  };
  postUpdateGameAfterDrag(game_id_target, gameJsonTarget);
}

function showContextMenu(event) {
  if (selectedSecondRow != null) {
    return;
  }
  event.preventDefault();

  selectedSecondRow = event.currentTarget;
  selectedSecondRowColor = $(selectedSecondRow).css("background-color");
  $(selectedSecondRow).css("background-color", "#DC143C");

  contextMenu.style.display = "block";
  contextMenu.style.left = event.clientX + "px";
  contextMenu.style.top = event.clientY + "px";
}

function handleContextMenuClick(action) {
  console.log("Performing action: " + action);
  if (action == "insertBeforeBtn") {
  } else if (action == "swapBtn") {
    swapGameRows(selectedRow, selectedSecondRow);
  } else if (action == "insertBehindBtn") {
  }
  hideContextMenu();
  clearCssSelectedRow();
  doRowColoring();
}

function hideContextMenu() {
  contextMenu.style.display = "none";
  if (selectedSecondRow != null) {
    $(selectedSecondRow).css("background-color", selectedSecondRowColor);
  }
  selectedSecondRow = null;
}

function attachEventListeners() {
  var menuItems = document.querySelectorAll(".context-menu li");
  menuItems.forEach(function (item) {
    item.addEventListener("click", function () {
      handleContextMenuClick(item.id);
    });
  });
}

function clearCssSelectedRow() {
  var findSelectedRow = $(".selected-row:first");
  if (findSelectedRow.length > 0) {
    findSelectedRow.css("background-color", selectedRowColor);
    findSelectedRow.css("border", "none");
  }
}
