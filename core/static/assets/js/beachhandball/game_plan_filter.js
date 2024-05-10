$(document).ready(function () {
  var checkbox = document.getElementById("checkFilterHideFinished");
  checkbox.addEventListener("change", function () {
    if (this.checked) {
      hideFinishedGames(1);
    } else {
      hideFinishedGames(-1);
    }
  });

  //$("#table-games").filterTable("#games-filter");
});

function add_filter(filter) {
  var filter_obj = { col: "Team A", filter: filter };
  $("#games-filter").val(JSON.stringify(filter_obj));
  $("#games-filter").keyup();
}
function add_filter_tevent() {
  var opt_val = $("#filter-tevent").children("option:selected").val();
  if (opt_val == -1) {
    opt_val = "";
    $("#filter-tevent > option").each(function () {
      if (this.value == -1 || this.value == "") return;

      opt_val = opt_val + "§" + this.value;
    });
    opt_val = opt_val.substring(1, opt_val.length);
  }
  var filter_obj = { col: "tournament_event", filter: opt_val };
  $("#games-filter").val(JSON.stringify(filter_obj));
  $("#games-filter").keyup();
}
function add_filter_tstate() {
  var opt_val = $("#filter-tstate").children("option:selected").val();
  if (opt_val == -1) {
    opt_val = "";
    $("#filter-tstate > option").each(function () {
      if (this.value == -1 || this.value == "") return;

      opt_val = opt_val + "§" + this.value;
    });
    opt_val = opt_val.substring(1, opt_val.length);
  }
  var filter_obj = { col: "tournament_state", filter: opt_val };
  $("#games-filter").val(JSON.stringify(filter_obj));
  $("#games-filter").keyup();
}
function add_filter_court() {
  var opt_val = $("#filter-court").children("option:selected").val();
  if (opt_val == -1) {
    opt_val = "";
    $("#filter-court > option").each(function () {
      if (this.value == -1 || this.value == "") return;

      opt_val = opt_val + "§" + this.value;
    });
    opt_val = opt_val.substring(1, opt_val.length);
  }
  var filter_obj = { col: "court", filter: opt_val };
  $("#games-filter").val(JSON.stringify(filter_obj));
  $("#games-filter").keyup();
}
function add_filter_gamestate() {
  var opt_val = $("#filter-gamestate").children("option:selected").val();
  if (opt_val == -1) {
    opt_val = "";
    $("#filter-gamestate > option").each(function () {
      if (this.value == -1 || this.value == "") return;

      opt_val = opt_val + "§" + this.value;
    });
    opt_val = opt_val.substring(1, opt_val.length);
  }
  var filter_obj = { col: "gamestate", filter: opt_val };
  $("#games-filter").val(JSON.stringify(filter_obj));
  $("#games-filter").keyup();
}

function hideFinishedGames(hide) {
  if (hide == -1) {
    opt_val = "";
    $("#filter-gamestate > option").each(function () {
      if (this.value == -1 || this.value == "") return;

      opt_val = opt_val + "§" + this.value;
    });
    opt_val = opt_val.substring(1, opt_val.length);
  } else {
    opt_val = "§RUNNING§APPENDING";
  }
  var filter_obj = { col: "gamestate", filter: opt_val };
  $("#games-filter").val(JSON.stringify(filter_obj));
  $("#games-filter").keyup();
}

function add_filter_keyword() {
  var opt_val = $("#filter-keyword").val();

  var filter_obj = { col: "__all__", filter: opt_val };
  $("#games-filter").val(JSON.stringify(filter_obj));
  $("#games-filter").keyup();
}
