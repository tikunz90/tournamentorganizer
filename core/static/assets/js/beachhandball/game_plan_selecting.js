$(document).ready(function () {
  window.addEventListener("click", hideContextMenu);

  window.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      selectedRow = null;
      if (selectedGameTimeRow != null) {
        $(selectedGameTimeRow).find("#id_starttime").datetimepicker("hide");
      }
      selectedGameTimeRow = null;
      hideContextMenu();
      $(".game-row").removeClass("selected-row");
      doRowColoring();
    }
    else if (event.key === "Enter") {
      if (selectedGameTimeRow != null) {
        changeGameTime(selectedGameTimeRow);
      }
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

  // Get Source Row Info
  var game_id_src = $(row_src).find("#id_starttime").eq(0).data("game_id");
  var gamestate_src = $(row_src).find("#" + game_id_src + "_gamestate")[0]
    .innerText;
  var game_counter_src = $(row_src).find("#game_id_counter")[0].innerText;

  var date_label_src = moment(date_string_src, "YYYY-MM-DD HH:mm:ss").format(
    "HH:mm (DD.MM.YYYY)"
  );
  var date_input_src = moment(date_string_src, "YYYY-MM-DD HH:mm:ss").format(
    "MM/DD/YYYY HH:mm"
  );

  var court_col_src = $(row_src).find("#game-list-td-court-" + game_id_src);
  var court_id_src = court_col_src.data("content");
  var court_name_src = $(court_col_src)
    .children(".game-list-court-label")
    .first()
    .text();
  var bg_color_src = $(row_src).css("background-color");

  // Get Target Row Info
  var game_id_target = $(row_tgt).find("#id_starttime").eq(0).data("game_id");
  var gamestate_tgt = $(row_tgt).find("#" + game_id_target + "_gamestate")[0]
    .innerText;
  var game_counter_target = $(row_tgt).find("#game_id_counter")[0].innerText;
  var date_label_target = moment(date_string_tgt, "YYYY-MM-DD HH:mm:ss").format(
    "HH:mm (DD.MM.YYYY)"
  );
  var date_input_target = moment(date_string_tgt, "YYYY-MM-DD HH:mm:ss").format(
    "MM/DD/YYYY HH:mm"
  );
  var court_col_tgt = $(row_tgt).find("#game-list-td-court-" + game_id_target);
  var court_id_tgt = court_col_tgt.data("content");
  var court_name_tgt = $(court_col_tgt)
    .children(".game-list-court-label")
    .first()
    .text();
  var bg_color_target = $(row_tgt).css("background-color");

  if (gamestate_src != "APPENDING") {
    return;
  }

  if (gamestate_tgt != "APPENDING") {
    return;
  }

  // Change Target Row
  $(row_tgt).find("#id_starttime_label")[0].innerText = date_label_src;
  $(row_tgt).find("#id_starttime")[0].value = date_input_src;
  $(row_tgt).find("#game_id_counter")[0].innerText = game_counter_src;
  $(row_tgt).find("#initial-id_starttime")[0].value = moment(
    date_string_src,
    "YYYY-MM-DD HH:mm:ss"
  ).format("YYYY-MM-DD HH:mm:ss");
  court_col_tgt.data("content", court_id_src);
  $(court_col_tgt)
    .children(".game-list-court-label")
    .first()
    .text(court_name_src);
  $(row_tgt).css("background-color", bg_color_src);

  // Change Source Row
  $(row_src).find("#id_starttime_label")[0].innerText = date_label_target;
  $(row_src).find("#id_starttime")[0].value = date_input_target;
  $(row_src).find("#game_id_counter")[0].innerText = game_counter_target;
  $(row_src).find("#initial-id_starttime")[0].value = moment(
    date_string_tgt,
    "YYYY-MM-DD HH:mm:ss"
  ).format("YYYY-MM-DD HH:mm:ss");
  court_col_src.data("content", court_id_tgt);
  $(court_col_src)
    .children(".game-list-court-label")
    .first()
    .text(court_name_tgt);
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
    court_id: parseInt(court_id_tgt),
  };
  postUpdateGameAfterDrag(game_id_src, gameJsonSrc);

  var gameJsonTarget = {
    game: game_id_target,
    datetime: moment(
      $(row_tgt).find("#id_starttime")[0].value,
      "MM/DD/YYYY HH:mm"
    ).format("YYYY-MM-DD HH:mm:ss"),
    game_counter: parseInt(game_counter_src),
    court_id: parseInt(court_id_src),
  };
  postUpdateGameAfterDrag(game_id_target, gameJsonTarget);
}

function showContextMenu(event, clickedColumnIndex) {
  if (
    clickedColumnIndex == 0 ||
    clickedColumnIndex == 1 ||
    clickedColumnIndex == 2
  ) {
    console.log("click on row  at col 0 1");
    selectedGameTimeRow = event.currentTarget;
    event.preventDefault();
    contextMenuDateTime.style.display = "block";
    contextMenuDateTime.style.left = event.clientX + "px";
    contextMenuDateTime.style.top = event.clientY + "px";
    return;
  }
  console.log("click on row");
  if (selectedRow == null) {
    event.preventDefault();
    return;
  }
  if (selectedSecondRow != null) {
    event.preventDefault();
    return;
  }
  if (selectedRow === event.currentTarget) {
    event.preventDefault();
    return;
  }
  event.preventDefault();

  var game_id = $(event.currentTarget)
    .find("#id_starttime")
    .eq(0)
    .data("game_id");
  var gamestate = $(event.currentTarget).find("#" + game_id + "_gamestate")[0]
    .innerText;
  if (gamestate != "APPENDING") {
    return;
  }

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
  } else if (action == "editDateTimeBtn") {
    $(selectedGameTimeRow)
      .find("#id_starttime")
      .datetimepicker("widgetParent", $(selectedGameTimeRow));
    $(selectedGameTimeRow).find("#id_starttime").datetimepicker("show");
    return;
  }
  hideContextMenu();
  clearCssSelectedRow();
  doRowColoring();
}

function hideContextMenu() {
  contextMenu.style.display = "none";
  contextMenuDateTime.style.display = "none";
  if (selectedSecondRow != null) {
    $(selectedSecondRow).css("background-color", selectedSecondRowColor);
  }
  selectedSecondRow = null;
  //selectedGameTimeRow = null;
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
