$(document).ready(function () {
  console.log("bh document ready");
  $("#bhAddCourtForm_OK").click(function () {
    bh.addCourt_Click();
  });
});

bh_gui = {};
var KNOCKOUT_NAMES = {
  2: "F",
  4: "SF",
  8: "QF",
  16: "R16",
  32: "R32",
  64: "R64",
  128: "R128",
};
var PLACEMENT_NAMES = {
  2: "P3",
  4: "P5",
  8: "P9",
  16: "P17",
  32: "R33",
  64: "R65",
  128: "R129",
};

var COLORS_GROUP_MEN = [
  "#00008B",
  "#0000FF",
  "#0096FF",
  "#ADD8E6",
  "#7DF9FF",
  "#00FFFF",
  "#F0FFFF",
  "#00008B",
  "#0000FF",
];

var COLORS_GROUP_WOMEN = [
  "#8B0000",
  "#FF0000",
  "#EE4B2B",
  "#E97451",
  "#FF4433",
  "#E0115F",
  "#F88379",
  "#8B0000",
  "#FF0000",
];

var COLORS_PLACEMENT_GROUP_MEN = [
  "#40E0D0",
  "#00CED1",
  "#5F9EA0",
  "#008080",
  "#E0FFFF",
  "#00FFFF",
];

var COLORS_PLACEMENT_GROUP_WOMEN = [
  "#FF7F50",
  "#F0E68C",
  "#FFA07A",
  "#FFA500",
  "#FFDAB9",
  "#FFFACD",
];

var wzNumOfGames = 0;
var wzNumOfGamesGroup = 0;
var wzNumOfGamesKO = 0;
var wzNumOfGamesPlacement = 0;
var wzNumOfGamesFinal = 0;

var tsCounter = 0;
var teamCounter = 0;
var tstatCounter = 0;
var tttCounter = 0;

var plAfterGroupContainer = document.getElementById("wz-placement-info-group");
var plCheckOptionsForms = document.getElementById("wz-enable-placement-form");
var plCheckOptions = document.getElementById("wz-enable-placement");
var plOptions = document.getElementById("wz-placement-options");
var plMode = document.getElementById("wz-sel-pl-mode");
var plModeSelected = $("#wz-sel-pl-mode").val();
var plModeOneGroup = document.getElementById("wz-pl-mode-onegroup");
var plModeMultiGroup = document.getElementById("wz-pl-mode-multigroup");
var plModeOnlyKo = document.getElementById("wz-pl-mode-onlyko");
var plModeOnlyKoExtraInfo = document.getElementById(
  "wz-pl-mode-onlyko-extrainfo"
);
var plPreviewPLAfterGroupCard = document.getElementById(
  "wz-ovw-tabPL-AfterGroup-card"
);
var plPreviewPLAfterGroupHeader = document.getElementById(
  "wz-ovw-tabPL-AfterGroup-header"
);
var plPreviewPLAfterGroup = document.getElementById("wz-ovw-tabPL_AfterGroup");
var plResultPLAfterGroup = document.getElementById("wz-ovw-PL_AfterGroup");
var plPreviewFinalsHeader = document.getElementById(
  "wz-ovw-tabPL-finals-header"
);
var plPreviewFinals = document.getElementById("wz-ovw-tabPL-finals");

bh = {
  misc: {
    test_mode_active: 1,
  },

  structureData: {
    max_num_teams: 0,
    groups: "",
    ko: "",
    placement: "",
    finals: "",
    transitions: {
      groups_to_ko: {},
      groups_to_placement: {},
      ko_to_pl: {},
    },
    tournament_states: [],
    teams: [],
    team_stats: [],
    ttt: [],
  },

  wzUpdateStructure: function () {
    wzNumOfGames = 0;
    tsCounter = 0;
    teamCounter = 0;
    tstatCounter = 0;
    tttCounter = 0;
    bh.structureData.tournament_states = [];
    bh.structureData.teams = [];
    bh.structureData.team_stats = [];
    bh.structureData.ttt = [];""
    wzInitUIElements();
    wzCalcGroups("wz-ovw-groups");
    wzCalcKnockout("wz-ovw-knockout");
    wzCalcPlacement("wz-ovw-placement");
    wzCalcFinals("wz-ovw-finals");

    $("#wz-structure-data").val(JSON.stringify(bh.structureData));
    wzNumOfGames =
      wzNumOfGamesGroup +
      wzNumOfGamesKO +
      wzNumOfGamesPlacement +
      wzNumOfGamesFinal;
    $("#wz-res_num_of_games_total").val(wzNumOfGames);

    console.log(JSON.stringify(bh.structureData));
  },

  tournamentData: "",
  numCourts: 0,
  minutesPerGame: 0,
  numGameDays: 0,
  DateTimeFirstGame: "",
  DateTimeLastGame: "",
  gameDays: [],
  GamesAll: [],

  num_games_total: 0,
  num_games_group: 0,
  num_games_ko: 0,
  num_games_pl: 0,
  num_games_f: 0,

  wzUpdateGamePlan: function () {
    console.log("wzUpdateGamePlan");
    bh.wzgpUpdateStart("wzgp-events-total");
    bh.wzgpUpdateGameDays("wzgp-gamedays");
    bh.calculateGamePlan();
    bh.updateUIGameDays("wzgp-gamedays");

    $("#wz-gameplan-data-all-games").val(JSON.stringify(bh.GamesAll));
    $("#wz-gameplan-data-gamedays").val(JSON.stringify(bh.gameDays));
    $("#wz-gameplan-data-num-courts").val(bh.numCourts);
  },

  wzgpUpdateStart: function (idRow) {
    var row = document.getElementById(idRow);
    $(row).empty();

    var startTime = $("#wzgp-GameDays_DateTimeFirstGame").val();
    if (startTime == "") {
      startTime = moment($("#wzgp-GameDays_DateTimeFirstGame").data("content"), "YYYY-MM-DD HH:mm:ssZ");
    }
    var dateFirstGame = moment(startTime);
    bh.DateTimeFirstGame = dateFirstGame.format("MM/DD/YYYY HH:mm");
    var recreateGameDays = false;
    var newNumCourts = $("#wzgp-num_courts").val();

      if (newNumCourts == "" || newNumCourts == "0") newNumCourts = 1;
    if (newNumCourts != bh.numCourts) recreateGameDays = true;
    bh.numCourts = newNumCourts;
    // --- Prevent infinite loop if numCourts is 0 or not a number ---
    if (!bh.numCourts || isNaN(bh.numCourts) || parseInt(bh.numCourts) <= 0) {
        // Optionally show a warning to the user
        console.warn("Number of courts must be greater than zero.");
        return;
    }
    bh.numCourts = parseInt(bh.numCourts);

    var newMinutesPerGame = $("#wzgp-time-slot").val();
    if (newMinutesPerGame == "") newMinutesPerGame = 30;
    if (newMinutesPerGame != bh.minutesPerGame) recreateGameDays = true;
    bh.minutesPerGame = newMinutesPerGame;

    bh.num_games_total = 0;
    bh.num_games_group = 0;
    bh.num_games_ko = 0;
    bh.num_games_pl = 0;
    bh.num_games_f = 0;

    var templateTotal = $("#templateEvent_total_games").clone();
    $(templateTotal).attr("id", "total_0");
    $(templateTotal).removeAttr("hidden");
    $(templateTotal).find("#template_name").text("Resulting games");
    var table = $(templateTotal).find("#wzgp-table-gamecounts");
    bh.tournamentData.events.forEach((event) => {
      event.stages.forEach((stage) => {
        var stage_counter = 0;
        stage["wz-games"] = [];
        stage.states.forEach((state) => {
          var n = state.ranking.length - 1;
          stage_counter += (n * n + n) / 2;

          state["wz-games"] = [];

          var teams = [];
          state.ranking.forEach((ranking) => {
            teams.push(JSON.parse(JSON.stringify(ranking)));
          });

          while (teams.length > 1) {
            var actTeam = teams[0];
            var actTeamCounter = 0;
            teams.shift();
            teams.forEach((t) => {
              var game = {
                  tournament_id: event.tournamentId,
                tournament_event_id: event.id,
                tournament_stage_id: stage.id,
                tournament_state_id: state.id,
                starttime: "",
                team_st_a_id: 0,
                team_st_b_id: 0,
                team_a_id: 0,
                team_b_id: 0,
                slot_name: "",
                court: "",
              };
              if (actTeamCounter % 2 === 0) {
                game.team_st_a_id = actTeam.id;
                game.team_a_id = actTeam.team.id;
                game.team_st_b_id = t.id;
                game.team_b_id = t.team.id;
              } else {
                game.team_st_a_id = t.id;
                game.team_a_id = t.team.id;
                game.team_st_b_id = actTeam.id;
                game.team_b_id = actTeam.team.id;
              }
              var cat_name = event.category.name;
              var cat_class = event.category.classification;
              game.slot_name =
                  cat_name.charAt(0).toUpperCase() + " (" + cat_class + ") -" + state.abbreviation;
              state["wz-games"].push(game);
              actTeamCounter += 1;
              bh.num_games_total++;
            });
          }
        });

        var allGamesListed = false;
        while (!allGamesListed) {
          var stateDoneCounter = 0;
          for (var i = 0; i < stage.states.length; i++) {
            if (stage.states[i]["wz-games"].length > 0) {
              stage["wz-games"].push(stage.states[i]["wz-games"].shift());
            } else {
              stateDoneCounter++;
            }
          }
          if (stage.states.length === stateDoneCounter) {
            allGamesListed = true;
          }
        }

        if (stage.tournament_stage === "GROUP_STAGE") {
          bh.num_games_group += stage_counter;
        } else if (stage.tournament_stage === "KNOCKOUT_STAGE") {
          bh.num_games_ko += stage_counter;
        } else if (stage.tournament_stage === "PLAYOFF_STAGE") {
          bh.num_games_pl += stage_counter;
        } else if (stage.tournament_stage === "FINAL") {
          bh.num_games_f += stage_counter;
        }
      });
    });
    $(row).append(templateTotal);
    console.log(
      "total games:" +
        (bh.num_games_group +
          bh.num_games_ko +
          bh.num_games_pl +
          bh.num_games_f)
    );

    var total_time_min =
      (bh.num_games_total * bh.minutesPerGame) / bh.numCourts;
    var total_time_hours = Math.floor(total_time_min / 60);
    var remaining_minutes = total_time_min - total_time_hours * 60;
    bh.numGameDays = Math.ceil(total_time_min / 60 / 10);

    var defaultHoursGameDay = 10;
      var dateFirstGame = moment(bh.DateTimeFirstGame);//, "MM/DD/YYYY HH:mm");
    if (bh.gameDays.length == 0 || recreateGameDays) {
      bh.gameDays = [];
      for (var i = 0; i < bh.numGameDays; i++) {
        var actMoment = moment(dateFirstGame).add(i, "days");
        var endMoment = moment(actMoment).add(defaultHoursGameDay, "hours");

        var limitMoment = moment(actMoment).set({ hour: 23, minute: 0, second: 0, millisecond: 0 });

        if (endMoment.isAfter(limitMoment)) {
            endMoment = limitMoment;
        }

        var gameDay = {
          id: i,
          starttime: actMoment.format("MM/DD/YYYY HH:mm"),
          endtime: endMoment.format("MM/DD/YYYY HH:mm"),
          game_slots: [],
        };
        bh.gameDays.push(gameDay);
      }
      if (bh.gameDays.length == 0) {
        var actMoment = moment(dateFirstGame).add(0, "days");
        var endMoment = moment(actMoment).add(defaultHoursGameDay, "hours");

        var gameDay = {
          id: i,
          starttime: actMoment.format("MM/DD/YYYY HH:mm"),
          endtime: endMoment.format("MM/DD/YYYY HH:mm"),
          game_slots: [],
        };
        bh.gameDays.push(gameDay);
      }
    }

    var time_gamedays = bh.calculateGameDayMinutes(bh.gameDays);
    if (time_gamedays <= total_time_min) {
      var residue_minutes = total_time_min - time_gamedays;
      var num_new_gamedays = Math.ceil(
        residue_minutes / (defaultHoursGameDay * 60)
      );
      for (var i = 0; i < num_new_gamedays; i++) {
        bh.addGameDay();
      }
    }

    $("#wz-res_num_of_games_total").val(bh.num_games_total);
    $("#wz-res_num_of_games_group").val(bh.num_games_group);
    $("#wz-res_num_of_games_ko").val(bh.num_games_ko);
    $("#wz-res_num_of_games_placement").val(bh.num_games_pl);
    $("#wz-res_num_of_games_final").val(bh.num_games_f);
    $("#wz-res_time").text(total_time_hours + "h " + remaining_minutes + " m");
    $("#wz-res_est_gamedays").text(bh.gameDays.length);
  },

  wzgpUpdateGameDays: function (idRow) {
      var dateLastGame = moment($("#wzgp-GameDays_DateTimeLastGame").val());//,"MM/DD/YYYY HH:mm");
    bh.DateTimeLastGame = dateLastGame.format("MM/DD/YYYY HH:mm");
  },

  calculateGamePlan: function () {
    if (bh.num_games_total == 0) {
      return;
    }
    var total_num_games = bh.num_games_total;
    var total_num_games_group = bh.num_games_group;
    var total_num_games_ko = bh.num_games_ko;
    var total_num_games_pl = bh.num_games_pl;
    var total_num_games_final = bh.num_games_f;
    var num_courts = bh.numCourts;
    var eventCounter = 0;

    var gameday_counter = 0;
      var firstDay = moment(bh.DateTimeFirstGame); //, "MM/DD/YYYY HH:mm");
    bh.gameDays[gameday_counter].endtime = moment(firstDay.format("MM/DD/YYYY") + " " +  moment(bh.gameDays[gameday_counter].endtime).format("HH:mm"));
    bh.gameDays[gameday_counter].starttime = moment(firstDay);
    var end_time = moment(bh.gameDays[gameday_counter].endtime);
    var act_time = moment(bh.gameDays[gameday_counter].starttime);
    var act_game_slot = { starttime: act_time.format("HH:mm"), games: [] };
    var slotCounter = 1;

    bh.GamesAll = [];
    bh.gameDays[gameday_counter].game_slots = [];

    bh.tournamentData.events.forEach((event) => {
      const knockoutStage = event.stages.find((stage) => stage.tournament_stage === "KNOCKOUT_STAGE");
      const playoffStage = event.stages.find((stage) => stage.tournament_stage === "PLAYOFF_STAGE");

      if (knockoutStage !== undefined) {
        knockoutStage.actHierarchy = 1;
      }

      if (playoffStage !== undefined) {
        playoffStage.actHierarchy = -1;
      }
    });

    var minutes_per_slot = parseInt(bh.minutesPerGame);
    while (total_num_games > 0) {
      while (total_num_games_group > 0) {
        if (
          bh.tournamentData.events[
            eventCounter % bh.tournamentData.events.length
          ].stages.length > 0
        ) {
          var gamesGroup = bh.tournamentData.events[
            eventCounter % bh.tournamentData.events.length
          ].stages.find((stage) => stage.tournament_stage == "GROUP_STAGE")[
            "wz-games"
          ];

          if (gamesGroup.length > 0) {
            var actGame = gamesGroup.shift();
            actGame.starttime = act_time.unix(); //act_time.format("YYYY-MM-DD HH:mm:ss");
            actGame.court = "C" + slotCounter;
            act_game_slot.games.push(actGame);
            bh.GamesAll.push(actGame);
            total_num_games_group--;
            total_num_games--;
            slotCounter++;
          }

          if (act_game_slot.games.length >= num_courts) {
            bh.gameDays[gameday_counter].game_slots.push(act_game_slot);
            act_time.add(minutes_per_slot, "minutes");
            act_game_slot = { starttime: act_time.format("HH:mm"), games: [] };
            slotCounter = 1;
            if (end_time.isBefore(act_time)) {
              gameday_counter++;

              if (gameday_counter >= bh.gameDays.length) {
                bh.addGameDay();
              }

              firstDay.add(1, "days");
              bh.gameDays[gameday_counter].endtime = moment(
                firstDay.format("MM/DD/YYYY") +
                  " " +
                  moment(
                    bh.gameDays[gameday_counter].endtime).format("HH:mm"));
              bh.gameDays[gameday_counter].starttime = moment(
                firstDay.format("MM/DD/YYYY") +
                  " " +
                  moment(
                    bh.gameDays[gameday_counter].starttime).format("HH:mm"));
              bh.gameDays[gameday_counter].game_slots = [];
              end_time = moment(
                bh.gameDays[gameday_counter].endtime);
              act_time = moment(
                bh.gameDays[gameday_counter].starttime);
              act_game_slot = {
                starttime: act_time.format("HH:mm"),
                games: [],
              };
            }
          }
        }

        eventCounter++;
      }
      eventCounter = 0;
      //window.alert("Set BreakPoint");
      while (total_num_games_ko > 0 || total_num_games_pl > 0) {
        if (
          bh.tournamentData.events[
            eventCounter % bh.tournamentData.events.length
          ].stages.length > 0
        ) {
          var stageKO = bh.tournamentData.events[
            eventCounter % bh.tournamentData.events.length
          ].stages.find((stage) => stage.tournament_stage == "KNOCKOUT_STAGE");
          var stagePL = bh.tournamentData.events[
            eventCounter % bh.tournamentData.events.length
          ].stages.find((stage) => stage.tournament_stage == "PLAYOFF_STAGE");

          if (stageKO !== undefined && stageKO["wz-games"].length > 0 && stagePL.actHierarchy == -1) {
            var actGame = stageKO["wz-games"][0];
            // handle KO of act hierarchy
            var statesKOActHierarchy = stageKO.states.find(
              (state) => state.id == actGame.tournament_state_id
            );
            if (statesKOActHierarchy.hierarchy == stageKO.actHierarchy) {
              actGame = stageKO["wz-games"].shift();
              actGame.starttime = act_time.unix(); //act_time.format("YYYY-MM-DD HH:mm:ss");
              actGame.court = "C" + slotCounter;
              act_game_slot.games.push(actGame);
              bh.GamesAll.push(actGame);
              total_num_games_ko--;
              total_num_games--;
              slotCounter++;

              if (act_game_slot.games.length >= num_courts) {
                bh.gameDays[gameday_counter].game_slots.push(act_game_slot);
                act_time.add(minutes_per_slot, "minutes");
                act_game_slot = {
                  starttime: act_time.format("HH:mm"),
                  games: [],
                };
                slotCounter = 1;
                if (end_time.isBefore(act_time)) {
                  gameday_counter++;

                  if (gameday_counter >= bh.gameDays.length) {
                    bh.addGameDay();
                  }

                  firstDay.add(1, "days");
                  bh.gameDays[gameday_counter].endtime = moment(
                    firstDay.format("MM/DD/YYYY") +
                      " " +
                      moment(
                        bh.gameDays[gameday_counter].endtime
                      ).format("HH:mm"));
                  bh.gameDays[gameday_counter].starttime = moment(
                    firstDay.format("MM/DD/YYYY") +
                      " " +
                      moment(
                        bh.gameDays[gameday_counter].starttime
                      ).format("HH:mm"));

                  bh.gameDays[gameday_counter].game_slots = [];
                  end_time = moment(
                    bh.gameDays[gameday_counter].endtime
                  );
                  act_time = moment(
                    bh.gameDays[gameday_counter].starttime
                  );
                  act_game_slot = {
                    starttime: act_time.format("HH:mm"),
                    games: [],
                  };
                }
              }
            } else {
              stagePL.actHierarchy = 500 + (stageKO.actHierarchy - 1);
              stageKO.actHierarchy = statesKOActHierarchy.hierarchy;
              eventCounter++;
            }
          } else if (
            stageKO !== undefined && 
            stageKO["wz-games"].length == 0 &&
            stagePL.actHierarchy == -1
          ) {
            stagePL.actHierarchy = 500 + (stageKO.actHierarchy - 1);
            stageKO.actHierarchy++;
            eventCounter++;
          } else if (
            stagePL !== undefined && 
            stagePL["wz-games"].length > 0 &&
            stagePL.actHierarchy >= 500
          ) {
            var actGame = stagePL["wz-games"][0];
            // handle KO of act hierarchy
            var statesPLActHierarchy = stagePL.states.find(
              (state) => state.id == actGame.tournament_state_id
            );
            if (statesPLActHierarchy.hierarchy == stagePL.actHierarchy) {
              actGame = stagePL["wz-games"].shift();
              actGame.starttime = act_time.unix(); //act_time.format("YYYY-MM-DD HH:mm:ss");
              actGame.court = "C" + slotCounter;
              act_game_slot.games.push(actGame);
              bh.GamesAll.push(actGame);
              total_num_games_pl--;
              total_num_games--;
              slotCounter++;

              if (act_game_slot.games.length >= num_courts) {
                bh.gameDays[gameday_counter].game_slots.push(act_game_slot);
                act_time.add(minutes_per_slot, "minutes");
                act_game_slot = {
                  starttime: act_time.format("HH:mm"),
                  games: [],
                };
                slotCounter = 1;
                if (end_time.isBefore(act_time)) {
                  gameday_counter++;

                  if (gameday_counter >= bh.gameDays.length) {
                    bh.addGameDay();
                  }

                  firstDay.add(1, "days");
                  bh.gameDays[gameday_counter].endtime = moment(
                    firstDay.format("MM/DD/YYYY") +
                      " " +
                      moment(
                        bh.gameDays[gameday_counter].endtime).format("HH:mm"));
                  bh.gameDays[gameday_counter].starttime = moment(
                    firstDay.format("MM/DD/YYYY") +
                      " " +
                      moment(
                        bh.gameDays[gameday_counter].starttime
                      ).format("HH:mm"));

                  bh.gameDays[gameday_counter].game_slots = [];
                  end_time = moment(
                    bh.gameDays[gameday_counter].endtime
                  );
                  act_time = moment(
                    bh.gameDays[gameday_counter].starttime
                  );
                  act_game_slot = {
                    starttime: act_time.format("HH:mm"),
                    games: [],
                  };
                }
              }
            } else {
              stagePL.actHierarchy = -1;
              eventCounter++;
            }
          } else if (
            stagePL !== undefined && 
            stagePL["wz-games"].length == 0 &&
            stagePL.actHierarchy >= 500
          ) {
            stagePL.actHierarchy = -1;
            eventCounter++;
          } else {
            eventCounter++;
          }
        }
        //eventCounter++;
      }

      eventCounter = 0;
      while (total_num_games_final > 0) {
        if (
          bh.tournamentData.events[
            eventCounter % bh.tournamentData.events.length
          ].stages.length > 0
        ) {
          var gamesFinal = bh.tournamentData.events[
            eventCounter % bh.tournamentData.events.length
          ].stages.find((stage) => stage.tournament_stage == "FINAL")[
            "wz-games"
          ];
          if (gamesFinal.length > 0) {
            var actGame = gamesFinal.shift();
            actGame.starttime = act_time.unix(); //act_time.format("YYYY-MM-DD HH:mm:ss");
            actGame.court = "C" + slotCounter;
            act_game_slot.games.push(actGame);
            bh.GamesAll.push(actGame);
            total_num_games_final--;
            total_num_games--;
            slotCounter++;
          }

          if (act_game_slot.games.length >= num_courts) {
            bh.gameDays[gameday_counter].game_slots.push(act_game_slot);
            act_time.add(minutes_per_slot, "minutes");
            act_game_slot = { starttime: act_time.format("HH:mm"), games: [] };
            slotCounter = 1;
            if (end_time.isBefore(act_time)) {
              gameday_counter++;

              if (gameday_counter >= bh.gameDays.length) {
                bh.addGameDay();
              }

              firstDay.add(1, "days");
              bh.gameDays[gameday_counter].endtime = moment(
                firstDay.format("MM/DD/YYYY") +
                  " " +
                  moment(
                    bh.gameDays[gameday_counter].endtime
                  ).format("HH:mm"));
              bh.gameDays[gameday_counter].starttime = moment(
                firstDay.format("MM/DD/YYYY") +
                  " " +
                  moment(
                    bh.gameDays[gameday_counter].starttime
                  ).format("HH:mm")
              );

              bh.gameDays[gameday_counter].game_slots = [];
              end_time = moment(
                bh.gameDays[gameday_counter].endtime);
              act_time = moment(
                bh.gameDays[gameday_counter].starttime);
              act_game_slot = {
                starttime: act_time.format("HH:mm"),
                games: [],
              };
            }
          }
        }
        eventCounter++;
      }

      if (total_num_games > 0) {
        window.confirm("Something went wrong! Contact helpdesk...");
        total_num_games = 0;
      }
    }

    if (gameday_counter <= bh.gameDays.length - 1) {
      var delta_days = bh.gameDays.length - 1 - gameday_counter;
      for (var i = 0; i < delta_days; i++) {
        bh.gameDays.pop();
      }
    }
  },
  calculateGameDayMinutes: function (gameDays) {
    var minutes = 0;
    gameDays.forEach(function (day) {
      var starttime = moment(day.starttime);
      var endtime = moment(day.endtime);
      minutes += endtime.diff(starttime, "minutes");
    });
    return minutes;
  },

  addGameDay: function () {
    var new_start = moment(bh.gameDays.at(-1).starttime)
      .add(1, "days")
      .set("hour", 8);
    var new_end = moment(new_start).set("hour", 18);
    var gameDay = {
      id: bh.gameDays.length,
      starttime: new_start.format("MM/DD/YYYY HH:mm"),
      endtime: moment(bh.gameDays.at(-1).endtime)
        .add(1, "days")
        .format("MM/DD/YYYY HH:mm"),
      game_slots: [],
    };
    bh.gameDays.push(gameDay);
    bh.numGameDays++;
    bh.updateUIGameDays("wzgp-gamedays");
  },

  updateUIGameDays: function (idRow) {
    var row = document.getElementById(idRow);
    $(row).empty();
    for (var i = 0; i < bh.gameDays.length; i++) {
      var gameDayData = bh.gameDays[i];

      var actMoment = moment(gameDayData.starttime);
      var endMoment = moment(gameDayData.endtime);

      var templateGD = $("#templateGameDay").clone();
      $(templateGD).attr("id", "gameday_" + i);
      $(templateGD).removeAttr("hidden");
      $(templateGD)
        .find("#templateGameDay_title")
        .text("Day " + (i + 1) + " - " + actMoment.format("DD.MM."));
      $(templateGD).find("#template_info").text("");

      var gameSlots = templateGD.find("#wz-game-slots");
      gameSlots.empty();
      var slotCounter = 0;
      gameDayData.game_slots.forEach((slot) => {
        var templateSlot = $("#template_gameslot").clone();
        $(templateSlot).attr("id", "slot_" + i);
        $(templateSlot).removeAttr("hidden");
        $(templateSlot).find("#template_time").text(slot.starttime);

        var slotList = $(templateSlot).find("#template_list");
        slot.games.forEach((game) => {
          var templateSlotItem = $("#template_slot").clone();
          $(templateSlotItem).attr("id", "slot_" + i);
          $(templateSlotItem).removeAttr("hidden");
          $(templateSlotItem).text(game.slot_name);
          $(templateSlotItem).find("#template_court").text(game.court);

          if (slotCounter % 2 == 0) {
            $(templateSlotItem).addClass("list-group-item-primary");
          } else {
            $(templateSlotItem).addClass("list-group-item-secondary");
          }

          slotList.append(templateSlotItem);
        });
        gameSlots.append(templateSlot);
        slotCounter++;
      });

      var inputTimeFirst_h = $(templateGD).find("#timeFirst_h");
      var inputTimeFirst_m = $(templateGD).find("#timeFirst_m");

      var inputTimeLast_h = $(templateGD).find("#timeLast_h");
      var inputTimeLast_m = $(templateGD).find("#timeLast_m");

      inputTimeFirst_h.val(actMoment.hour());
      inputTimeFirst_h.attr("name", "first_h_" + i);
      inputTimeFirst_m.val(actMoment.minutes());
      inputTimeFirst_m.attr("name", "first_m_" + i);

      inputTimeLast_h.val(endMoment.hour());
      inputTimeLast_h.attr("name", "last_h_" + i);
      inputTimeLast_m.val(endMoment.minutes());
      inputTimeLast_m.attr("name", "last_m_" + i);

      inputTimeFirst_h.on("change", bh.onChange_GameDay);
      inputTimeFirst_m.on("change", bh.onChange_GameDay);
      inputTimeLast_h.on("change", bh.onChange_GameDay);
      inputTimeLast_m.on("change", bh.onChange_GameDay);

      $(row).append(templateGD);
    }
  },

  onChange_GameDay: function () {
    console.log("onChange_GameDay " + this.getAttribute("name"));
    //console.log(arguments);
    //console.log(this);

    var split = this.getAttribute("name").split("_");
    var gd_id = split[2];

    var gameday = bh.gameDays.find((gd) => gd.id === parseInt(gd_id));
    var timeKey = "starttime";
    if (split[0] === "last") {
      timeKey = "endtime";
    }

    var actMoment = moment(gameday[timeKey]);

    if (split[1] === "h") actMoment.set("hour", this.value);
    else if (split[1] === "m") actMoment.set("minute", this.value);

    gameday[timeKey] = actMoment.format("MM/DD/YYYY HH:mm");

    bh.wzUpdateGamePlan();
  },

  addCourt_Click: function () {
    console.log("addCourt_Click");

    var form = document.getElementById("bhAddCourtForm");

    console.debug(form.checkValidity());
    console.debug($(form).serialize());

    console.debug($(form).serializeJSON());
    var data = $(form).serializeJSON();

    if (form.checkValidity()) {
      console.log("Close Modal");

      var response = tournament_service.createCourt(data);

      // Hide modal frame
      var modal = document.getElementById("bhAddCourtModal");
      $(modal).modal("toggle");

      // evaluate server request and set notification
      if (response.success == "true") {
        bh.addCourtHTML(response.data);
      }
      md.showNotification(
        "bottom",
        "center",
        response.message,
        response.message_type
      );
    } else {
      var validator = $(form).validate();
      validator.form();
    }
  },

  addCourtHTML: function (courtData) {
    var templateCourt = $("#templateCourt").clone();
    $(templateCourt).attr("id", "court_" + courtData.id);
    $(templateCourt).attr("obj_id", courtData.id);
    $(templateCourt).attr("data-obj", JSON.stringify(courtData));
    $(templateCourt).removeAttr("hidden");
    $(templateCourt)
      .find("#templateCourt_btnUpdate")
      .click(function () {
        bh.updateCourt_Click($(this));
      });
    $(templateCourt)
      .find("#templateCourt_btnRemove")
      .click(function () {
        bh.removeCourt_Click($(this));
      });
    $(templateCourt).find(".card-category").text(courtData.number);
    $(templateCourt).find(".card-title").text(courtData.name);
    $("#court_table").append(templateCourt);
    return;
  },

  updateCourt_Click: function (node) {
    console.log("updateCourt_Click");
    var topnode = node.parent().closest(".topnode");
    var court = JSON.parse(topnode.attr("data-obj"));
    console.log(topnode);
    console.log(court);
  },

  removeCourt_Click: function (node) {
    console.log("removeCourt_Click");
    var topnode = node.parent().closest(".topnode");
    var court = JSON.parse(topnode.attr("data-obj"));
    swal({
      title: "Are you sure delete " + court.name + "?",
      text: "Court " + court.name + " will be deleted!",
      type: "warning",
      showCancelButton: true,
      confirmButtonText: "Yes, delete it!",
      cancelButtonText: "No, keep it",
      confirmButtonClass: "btn btn-success",
      cancelButtonClass: "btn btn-danger",
      buttonsStyling: false,
    }).then(function (dismiss) {
      if (dismiss.dismiss !== "cancel") {
        var response = tournament_service.removeCourt(court.id);
        if (response.success == "true") {
          topnode.remove();
        }
      }
    });
  },

  addTournamentStateHTML: function (tsData, teams) {
    var templateTState = $("#templateTState").clone();
    $(templateTState).attr("id", "tstate_" + tsData.id);
    $(templateTState).attr("obj_id", tsData.id);
    $(templateTState).attr("data-obj", JSON.stringify(tsData));
    $(templateTState).removeAttr("hidden");
    var ch = $(templateTState).find("#templateTState_link_games").val();

    $(templateTState)
      .find("#templateTState_link_games")
      .attr("id", "templateTState_link_games_" + tsData.id);
    $(templateTState)
      .find("#templateTState_link_teams")
      .attr("id", "templateTState_link_teams_" + tsData.id);
    $(templateTState)
      .find("#templateTState_link_trans")
      .attr("id", "templateTState_link_trans_" + tsData.id);
    $(templateTState)
      .find("#templateTState_link_basic")
      .attr("id", "templateTState_link_basic_" + tsData.id);

    $(templateTState)
      .find("#templateTState_tab_overview")
      .attr("href", "#templateTState_link_overview_" + tsData.id);
    $(templateTState)
      .find("#templateTState_tab_teams")
      .attr("href", "#templateTState_link_teams_" + tsData.id);
    $(templateTState)
      .find("#templateTState_tab_trans")
      .attr("href", "#templateTState_link_trans_" + tsData.id);
    $(templateTState)
      .find("#templateTState_tab_basic")
      .attr("href", "#templateTState_link_basic_" + tsData.id);
    //$(templateTState).find("#templateTState_btnUpdate").click(function(){ bh.updateCourt_Click($(this)); });
    //$(templateTState).find("#templateTState_btnRemove").click(function(){ bh.removeCourt_Click($(this)); });
    //$(templateTState).find(".card-category").text(tsData.number);

    $(templateTState)
      .find("#templateTState_table_overview")
      .attr("id", "templateTState_table_overview_" + tsData.id);
    $(templateTState)
      .find("#templateTState_table_teams")
      .attr("id", "templateTState_table_teams_" + tsData.id);

    for (var i = 0, l = tsData.tstats.length; i < l; i++) {
      var tstat = tsData.tstats[i];
      var listitems = "";
      $.each(teams, function (key, value) {
        if (tstat.team_name === value.name) {
          listitems +=
            '<option selected="selected" value=' +
            key +
            ">" +
            value.name +
            "</option>";
        } else {
          listitems += "<option value=" + key + ">" + value.name + "</option>";
        }
      });
      markup =
        '<tr><td class="text-center">' +
        tstat.rank +
        "</td><td>" +
        tstat.team_name +
        "</td></tr>";
      //markup = '<tr><td class="text-center">' + tstat.rank + '</td><td><select class="selectpicker" data-style="select-with-transition" title="Choose Team" data-size="7">' + listitems + "</select></td></tr>";
      $(templateTState)
        .find("#templateTState_table_teams_" + tsData.id)
        .append(markup);
      markup_overview =
        '<tr><td class="text-center">' +
        tstat.rank +
        "</td><td>" +
        tstat.team_name +
        "</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>";
      $(templateTState)
        .find("#templateTState_table_overview_" + tsData.id)
        .append(markup_overview);
    }

    $(templateTState).find(".card-title").text(tsData.name);
    if (tsData.tournament_state_type === "GROUP_STAGE") {
      $("#tstate_table_gs").append(templateTState);
    } else if (tsData.tournament_state_type === "MAIN_ROUND") {
      $("#tstate_table_int").append(templateTState);
    } else if (tsData.tournament_state_type === "FINAL") {
      $("#tstate_table_final").append(templateTState);
    }

    return;
  },
};

function wzCalcGroups(idRow) {
  console.log("wzCalcGroups: " + idRow);
  var category = $("#wz-tevent-category").val();
  var colors = [];
  if (category == "man") {
    colors = COLORS_GROUP_MEN;
  } else if (category == "woman") {
    colors = COLORS_GROUP_WOMEN;
  }
  groupData = {
    num_groups: 0,
    teams_per_group: 0,
    num_teams_res: 0,
    teams_to_ko: 0,
    teams_next_stage: 0,
    items: [],
  };
  var transitions = {};
  bh.structureData.groups = groupData;

  wzNumOfGamesGroup = 0;
  var row = document.getElementById(idRow);
  $(row).empty();
  var rowTab = document.getElementById("wz-ovw-tabGroup");
  $(rowTab).empty();
  var num_teams = $("#wz-max_num_teams").val();
  var num_groups = $("#wz-num_of_groups").val();

  bh.structureData.max_num_teams = num_teams;

  var teams_per_group = Math.floor(num_teams / num_groups);
  var num_teams_res = num_teams % num_groups;
  //var teams_per_group = $("#wz-teams_per_groups").val();
  //var teams_next_stage = $("#wz-num_teams_group_next_stage").val();

  var sel_val = $("#wz-sel-teams-knockout").val();
  document.getElementById("wz-num_of_groups").max = sel_val;
  groupData.teams_total = parseInt(num_teams);
  groupData.teams_to_ko = parseInt(sel_val);
  groupData.teams_remaining = groupData.teams_total - groupData.teams_to_ko;
  var teams_next_stage_residue = sel_val % num_groups;
  groupData.teams_next_stage = Math.floor(sel_val / num_groups);
  $("#wz-sel-teams-knockout").empty();
  var sel_val_ranked = $("#wz-sel-teams-getting-ranked").val();
  if (parseInt(sel_val_ranked) > parseInt(sel_val)) {
    sel_val_ranked = sel_val;
  }
  $("#wz-sel-teams-getting-ranked").empty();
  var num_choices = Math.floor(Math.log(num_teams) / Math.log(2));
  for (let i = 1; i <= num_choices; i++) {
    var opt = "";
    if (Math.pow(2, i) == sel_val) {
      opt =
        "<option selected value=" +
        Math.pow(2, i) +
        ">" +
        Math.pow(2, i) +
        "</option>";
    } else {
      opt =
        "<option value=" + Math.pow(2, i) + ">" + Math.pow(2, i) + "</option>";
    }
    $("#wz-sel-teams-knockout").append(opt);
    if (Math.pow(2, i) == sel_val_ranked) {
      opt =
        "<option selected value=" +
        Math.pow(2, i) +
        ">" +
        Math.pow(2, i) +
        "</option>";
      $("#wz-sel-teams-getting-ranked").append(opt);
    } else if (Math.pow(2, i) <= sel_val) {
      opt =
        "<option value=" + Math.pow(2, i) + ">" + Math.pow(2, i) + "</option>";
      $("#wz-sel-teams-getting-ranked").append(opt);
    }
  }

  for (let i = 0; i < groupData.teams_to_ko / 2; i++) {
    transitions["ko_grp_" + i] = [];
  }

  groupData.num_groups = num_groups;
  groupData.teams_per_group = teams_per_group;
  groupData.num_teams_res = num_teams_res;
  console.log(
    "wzCalcGroups: #groups:" + num_groups + " teams p gr: " + teams_per_group
  );
  for (let i = 0; i < num_groups; i++) {
    actGroup = { idx: i, name: "Group " + (i + 1), teams: [] };
    tournament_state = {
      uid: tsCounter,
      id_db: 0,
      name: "Group " + (i + 1),
      abbreviation: "G" + (i + 1),
      hierarchy: 0,
      max_number_teams: teams_per_group,
      index: i - 1,
      direct_compare: true,
      round_type: "GROUP",
      order: i,
    };

    var GameCounter = 0;
    var templateGroup = $("#templateGroup").clone();
    $(templateGroup).attr("id", "group_" + i);
    $(templateGroup).removeAttr("hidden");
    $(templateGroup).find("#templateGroup_name").text(actGroup.name);
    $(templateGroup)
      .find("#templateGroup_name")
      .css("background-color", colors[i]);

    var body = $(templateGroup).find("#templateGroup_body");
    body.empty();
    var addedResidue = false;

    for (let iTeam = 0; iTeam < teams_per_group; iTeam++) {
      actTeam = {
        idx: iTeam,
        name: iTeam + 1 + ". TeamDummy",
        rank: 0,
        isWinning: 0,
        transition: {
          uid: tttCounter,
          tournament_state: tsCounter,
          origin_rank: iTeam + 1,
          origin_group_id: i,
          origin_group_name: actGroup.name,
          target_rank: 0,
          target_group_id: 0,
        },
      };
      teamData = {
        uid: teamCounter,
        tournament_state: tsCounter,
        name: iTeam + 1 + ". " + tournament_state.name,
        abbreviation: iTeam + 1 + ". " + tournament_state.abbreviation,
        category_id: 0,
        season_cup_tournament_id: 0,
        is_dummy: true,
      };
      teamStatData = {
        uid: tstatCounter,
        tournament_state: tsCounter,
        team_id: teamCounter,
        rank_initial: iTeam + 1,
        rank: iTeam + 1,
      };
      actTeam.rank = iTeam + 1;
      actTeam.transition.origin_rank = actTeam.rank;

      var tTeamItem = $("#templateTeamItem").clone();
      $(tTeamItem).attr("id", "teamitem_" + i + "_" + iTeam);
      $(tTeamItem).removeAttr("hidden");

      // transition
      var tar_gr_id = i + iTeam * num_groups;

      if (iTeam < groupData.teams_next_stage) {
        $(tTeamItem).find("#templateTeamItem_icon").text("arrow_upward");
        actTeam.isWinning = 1;
      } else if (teams_next_stage_residue > 0 && addedResidue == false) {
        $(tTeamItem).find("#templateTeamItem_icon").text("arrow_upward");
        addedResidue = true;
        teams_next_stage_residue--;
        actTeam.isWinning = 1;
      } else {
        $(tTeamItem).find("#templateTeamItem_icon").text("clear");
      }

      $(tTeamItem).find("#templateTeamItem_name").text(actTeam.name);
      body.append(tTeamItem);
      actGroup["teams"].push(actTeam);
      GameCounter++;
      bh.structureData.teams.push(teamData);
      teamCounter++;
      bh.structureData.team_stats.push(teamData);
      tstatCounter++;
    }
    if (num_teams_res > 0) {
      actTeam = {
        idx: teams_per_group,
        name: teams_per_group + 1 + ". TeamDummy",
        rank: 0,
        transition: {
          origin_rank: teams_per_group + 1,
          origin_group_id: i,
          origin_group_name: actGroup.name,
          target_rank: 0,
          target_group_id: 0,
        },
      };

      teamData = {
        uid: teamCounter,
        tournament_state: tsCounter,
        name: teams_per_group + 1 + ". " + tournament_state.name,
        abbreviation:
          teams_per_group + 1 + ". " + tournament_state.abbreviation,
        category_id: 0,
        season_cup_tournament_id: 0,
        is_dummy: true,
      };
      teamStatData = {
        uid: tstatCounter,
        tournament_state: tsCounter,
        team_id: teamCounter,
        rank_initial: teams_per_group + 1,
        rank: teams_per_group + 1,
      };

      actTeam.rank = teams_per_group + 1;
      actTeam.transition.origin_rank = actTeam.rank;
      var tTeamItem = $("#templateTeamItem").clone();
      $(tTeamItem).attr("id", "teamitem_" + (teams_per_group + 1));
      $(tTeamItem).removeAttr("hidden");
      if (teams_per_group < groupData.teams_next_stage) {
        $(tTeamItem).find("#templateTeamItem_icon").text("arrow_upward");
      } else {
        $(tTeamItem).find("#templateTeamItem_icon").text("clear");
        actTeam.transition.target_rank = -1;
        actTeam.transition.target_group_id = 999;
      }

      $(tTeamItem).find("#templateTeamItem_name").text(actTeam.name);
      body.append(tTeamItem);
      actGroup.teams.push(actTeam);
      GameCounter++;
      num_teams_res--;
      tournament_state.max_number_teams += 1;

      bh.structureData.teams.push(teamData);
      teamCounter++;
      bh.structureData.team_stats.push(teamData);
      tstatCounter++;
    }

    GameCounter--;
    wzNumOfGamesGroup += (GameCounter * (GameCounter + 1)) / 2;
    groupData.items.push(actGroup);
    $(row).append(templateGroup);
    $(rowTab).append(templateGroup.clone());
    bh.structureData.tournament_states.push(tournament_state);
    tsCounter++;
  }
  var grIdx = 0;
  var teamIdx = 0;
  var target_gr_idx = 0;
  var target_gr_idx_end = groupData.teams_to_ko / 2 - 1;
  for (let i = 1; i <= groupData.teams_to_ko; i++) {
    var targetRnk = 1;
    var targetGroup = target_gr_idx;
    if (i % 2 == 0) {
      targetRnk = 2;
      targetGroup = target_gr_idx_end;
      target_gr_idx_end--;
    } else {
      targetGroup = target_gr_idx;
      target_gr_idx++;
    }
    groupData.items[grIdx].teams[teamIdx].transition.target_rank = targetRnk;
    groupData.items[grIdx].teams[teamIdx].transition.target_group_id =
      targetGroup;
    transitions["ko_grp_" + targetGroup].push(
      groupData.items[grIdx].teams[teamIdx].transition
    );
    bh.structureData.ttt.push(groupData.items[grIdx].teams[teamIdx].transition);
    tttCounter++;

    grIdx++;
    if (grIdx >= groupData.items.length) {
      grIdx = 0;
      teamIdx++;
    }
  }
  bh.structureData.transitions.groups_to_ko = transitions;
  $("#wz-res_num_of_games_group").val(wzNumOfGamesGroup);
}

function wzCalcKnockout(idRow) {
  console.log("wzCalcKnockout: " + idRow);
  var category = $("#wz-tevent-category").val();
  var color = "#1F51FF";

  var koData = { levels: 0, num_teams_soll: 0, level: [] };
  var transitions_pl = {};
  wzNumOfGamesKO = 0;
  var row = document.getElementById(idRow);
  $(row).empty();
  var rowTab = document.getElementById("wz-ovw-tabKO");
  $(rowTab).empty();
  var num_teams = $("#wz-num_teams_group_next_stage").val();
  koData.num_teams_soll = $("#wz-sel-teams-knockout").val();
  koData.levels = Math.log(koData.num_teams_soll) / Math.log(2); // -1 because final is seperated by
  var actNaming = "";
  var lastNaming = "";
  var lastTransitions = [];
  for (let i = koData.levels; i > 1; i--) {
    var levelData = {
      idx: i,
      header: "",
      actNaming: "",
      groups: [],
      transitions: [],
    };
    var transFromGroup = bh.structureData.transitions.groups_to_ko;
    transitions_pl[KNOCKOUT_NAMES[Math.pow(2, i)]] = { idx: i, items: [] };
    var tLevel = $("#templateKO_level").clone();
    $(tLevel).attr("id", "level_" + i);
    $(tLevel).removeAttr("hidden");
    var width = 1;
    var offset = 0;
    var header = "Round of " + Math.pow(2, i);
    if (category == "man") {
      color = "#191970"; // midnight blue
    } else if (category == "woman") {
      color = "#880808"; // blood red
    }
    if (Math.pow(2, i) == 8) {
      header = "Quarter Finals";
      width = 3;
      if (category == "man") {
        color = "#3F00FF"; // indigo blue
      } else if (category == "woman") {
        color = "#80461B"; // russet red
      }
    }
    if (Math.pow(2, i) == 4) {
      header = "Semi Finals";
      width = 5;
      offset = 1;
      if (category == "man") {
        color = "#000080"; // navy blue
      } else if (category == "woman") {
        color = "#DC143C"; // crimson red
      }
    }
    levelData.actNaming = KNOCKOUT_NAMES[Math.pow(2, i)];
    $(tLevel).find("#templateKO_header").text(header);
    levelData.header = header;
    var tLevel_items = $(tLevel).find("#templateKO_items");
    var num_of_states = Math.pow(2, i - 1);
    var next_group_counter = 0;
    var next_group_counter_pl = 0;
    var act_target_rank_ko = 1;
    var act_target_rank_placement = 1;
    for (var j = 1; j <= num_of_states; j++) {
      var actGroup = {
        idx: j,
        name: levelData.actNaming + " " + j,
        teams: [],
      };
      var templateGroup = $("#templateGroup").clone();
      $(templateGroup).attr("id", "ko_grp_" + (j - 1));
      $(templateGroup).removeAttr("hidden");
      $(templateGroup).find("#templateGroup_name").text(actGroup.name);
      $(templateGroup)
        .find("#templateGroup_name")
        .css("background-color", color);
      $(templateGroup).attr(
        "class",
        "col-md-" + width + " offset-md-" + offset
      );
      var body = $(templateGroup).find("#templateGroup_body");
      body.empty();
      for (let iTeam = 0; iTeam < 2; iTeam++) {
        actTeam = {
          idx: iTeam,
          name: iTeam + 1 + ". TeamDummy",
          rank: 0,
          transition: {
            origin_rank: iTeam + 1,
            origin_group_id: j - 1,
            origin_group_name: levelData.actNaming + " " + j,
            target_rank: 0,
            target_lvl_id: 0,
            target_group_id: 0,
            isWinning: 0,
          },
        };
        var tTeamItem = $("#templateTeamItem").clone();
        $(tTeamItem).attr("id", "ko_teamitem_" + j + "_" + iTeam);
        $(tTeamItem).removeAttr("hidden");

        actTeam.transition.target_lvl_id = i - 1;

        // transition
        if (iTeam === 0) {
          actTeam.transition.target_rank = act_target_rank_ko;
          actTeam.transition.target_group_id = next_group_counter;
          actTeam.transition.isWinning = 1;
          act_target_rank_ko++;
          if(j > 0 && j % 2 == 0) {
            next_group_counter++;
            act_target_rank_ko = 1;
          }
          else {
            
          }
          
          if (next_group_counter >= Math.pow(2, i - 2)) {
            //act_target_rank_ko = 1;
            //next_group_counter = 0;
          }
        } else {
          actTeam.transition.target_rank = act_target_rank_placement;
          actTeam.transition.target_group_id = next_group_counter_pl;
          transitions_pl[levelData.actNaming].items.push(actTeam.transition);
          act_target_rank_placement++;
          if(j > 0 && j % 2 == 0) {
            next_group_counter_pl++;
            act_target_rank_placement = 1;
          }
          //if (
          //  next_group_counter_pl >= Math.pow(2, i - 2) &&
          //  act_target_rank_placement == 1
          //) {
          //  act_target_rank_placement = 2;
          //  next_group_counter_pl = 0;
          //}
        }

        if (i == koData.levels) {
          NameExtension = ". TeamDummy";
          // get name from transition
          var actTrans = transFromGroup["ko_grp_" + (j - 1)].find(
            (e) => e.target_rank === iTeam + 1
          );
          NameExtension =
            actTrans.origin_rank + ". " + actTrans.origin_group_name;
        } else {
          var actTrans = lastTransitions.find(
            (e) => e.target_rank === iTeam + 1 && e.target_group_id == j - 1 && e.isWinning == 1
          );
          NameExtension =
            actTrans.origin_rank + ". " + actTrans.origin_group_name;
        }
        if (iTeam == 0) {
          $(tTeamItem).find("#templateTeamItem_icon").text("arrow_upward");
          actTeam.rank = 1;
          actTeam.transition.origin_rank = 1;
        } else {
          $(tTeamItem).find("#templateTeamItem_icon").text("clear");
          actTeam.rank = 2;
          actTeam.transition.origin_rank = 2;
        }
        actTeam.name = NameExtension;
        $(tTeamItem).find("#templateTeamItem_name").text(actTeam.name);
        actGroup["teams"].push(actTeam);
        levelData.transitions.push(actTeam.transition);
        body.append(tTeamItem);
      }
      $(tLevel_items).append(templateGroup);
      levelData["groups"].push(actGroup);
      wzNumOfGamesKO++;
    }
    $(row).append(tLevel);
    $(rowTab).append(tLevel.clone());
    koData["level"].push(levelData);
    lastNaming = levelData.actNaming;
    lastTransitions = levelData.transitions;
  }
  bh.structureData.ko = koData;
  bh.structureData.transitions.ko_to_pl = transitions_pl;
  $("#wz-res_num_of_games_ko").val(wzNumOfGamesKO);
}

function wzInitUIElements() {
  plAfterGroupContainer = document.getElementById("wz-placement-info-group");
  plCheckOptionsForms = document.getElementById("wz-enable-placement-form");
  plCheckOptions = document.getElementById("wz-enable-placement");
  plOptions = document.getElementById("wz-placement-options");
  plMode = document.getElementById("wz-sel-pl-mode");
  plModeSelected = $("#wz-sel-pl-mode").val();
  plModeOneGroup = document.getElementById("wz-pl-mode-onegroup");
  plModeMultiGroup = document.getElementById("wz-pl-mode-multigroup");
  plModeOnlyKo = document.getElementById("wz-pl-mode-onlyko");
  plModeOnlyKoExtraInfo = document.getElementById(
    "wz-pl-mode-onlyko-extrainfo"
  );
  //plPreviewPLAfterGroupCard = document.getElementById("wz-ovw-tabPL-AfterGroup-card");
  //plPreviewPLAfterGroupHeader = document.getElementById("wz-ovw-tabPL-AfterGroup-header");
  plPreviewPLAfterGroup = document.getElementById("wz-ovw-tabPL_AfterGroup");
  plResultPLAfterGroup = document.getElementById("wz-ovw-PL_AfterGroup");
  //plPreviewFinalsHeader = document.getElementById("wz-ovw-tabPL-finals-header");
  //plPreviewFinals = document.getElementById("wz-ovw-tabPL-finals");
}

function wzCalcPlacement(idRow) {
  console.log("wzCalcPlacement: " + idRow);
  var plData = {
    levels_ranked: 0,
    num_teams_getting_ranked: 0,
    level: [],
    placement_type: -1,
    placement: {},
  };
  wzNumOfGamesPlacement = 0;
  var row = document.getElementById(idRow);
  $(row).empty();

  var rowTab = document.getElementById("wz-ovw-tabPL");
  $(rowTab).empty();

  plData.num_teams_getting_ranked = $("#wz-sel-teams-getting-ranked").val();

  var num_teams_soll = groupData.teams_to_ko;
  var num_teams_total = groupData.teams_total;
  var best_rank_placement = num_teams_soll + 1;

  // Enable/Disable Placement Options

  document.getElementById("wz-pl-mode-num_of_groups").max = Math.floor(
    (num_teams_total - num_teams_soll) / 2
  ).toString();

  plAfterGroupContainer.style.display = "none";
  plModeOneGroup.style.display = "none";
  plModeMultiGroup.style.display = "none";
  plModeOnlyKo.style.display = "none";
  plModeOnlyKoExtraInfo.style.display = "none";
  //plPreviewPLAfterGroupCard.style.display = 'none';
  //plPreviewPLAfterGroupHeader.style.display = 'none';
  plPreviewPLAfterGroup.style.display = "none";
  //plResultLAfterGroup.style.display = "none";
  //plPreviewFinalsHeader.style.display = 'none';
  //plPreviewFinals.style.display = 'none';

  var remainingTeamsForPL = groupData.teams_remaining;

  // Info Text Placement from KO
  if (
    parseInt(num_teams_soll) > 2 &&
    parseInt(plData.num_teams_getting_ranked) > 2
  ) {
    $("#wz-placement-info-ko").text(
      "Placement playing for Rank 3 to " +
        parseInt(plData.num_teams_getting_ranked)
    );
  } else {
    $("#wz-placement-info-ko").text(
      "Only 2 teams ranked. No Placement available"
    );
  }

  if (
    parseInt(num_teams_soll) > 2 &&
    parseInt(num_teams_soll) == parseInt(plData.num_teams_getting_ranked) &&
    parseInt(num_teams_total) - parseInt(num_teams_soll) > 0
  ) {
    plAfterGroupContainer.style.display = "block";
  }

  // Info Text for Placement
  if (num_teams_total - num_teams_soll - 1 > 0) {
    plCheckOptionsForms.style.display = "block";
    $("#wz-placement-info").text(
      "Define Placement after Group Stage playing for Rank " +
        best_rank_placement +
        " to " +
        num_teams_total +
        " (#teams: " +
        remainingTeamsForPL.toString() +
        ")"
    );
    
  } else {
    plCheckOptionsForms.style.display = "none";
    $("#wz-placement-info").text("No Placement after Group Stage possible");
  }

  plData.placement_type = parseInt(plModeSelected);

  if (plCheckOptions.checked) {
    plOptions.style.display = "block";
    switch (plModeSelected) {
      case "1":
        plData.placement = wzCalcPlacementOneGroup(
          best_rank_placement,
          remainingTeamsForPL
        );
        break;
      case "2":
        plData.placement = wzCalcPlacementMultiGroup(
          best_rank_placement,
          remainingTeamsForPL
        );
        break;
      case "3":
        plData.placement = wzCalcPlacementDirectKO(
          best_rank_placement,
          remainingTeamsForPL
        );
        break;
    }
  } else {
    plOptions.style.display = "none";
    plData.placement_type = -1;
  }

  var levels = Math.log(num_teams_soll) / Math.log(2) - 1; // -1 because final is seperated by
  plData.levels_ranked =
    Math.log(plData.num_teams_getting_ranked) / Math.log(2) - 1;

  for (let i = plData.levels_ranked; i >= 1; i--) {
    // this instance is the first instance when losers  come from knockout stage
    levelData = {
      idx: i,
      name: "",
      actNaming: "",
      bestRankWinner: 0,
      bestRankLoser: 0,
      num_groups: 0,
      groups: [],
      sublevel: [],
      transitions_w: [],
      transitions_l: [],
    };
    var tLevel = $("#templatePL_level").clone();

    var actTransFromKO =
      bh.structureData.transitions.ko_to_pl[KNOCKOUT_NAMES[Math.pow(2, i + 1)]];

    $(tLevel).attr("id", "level_" + i);
    $(tLevel).removeAttr("hidden");
    levelData.bestRankWinner = Math.pow(2, i) + 1; //Math.pow(2, i-1) + 1;
    levelData.bestRankLoser = 2 * Math.pow(2, i);
    var width = 3;
    var offset = 0;
    levelData.actNaming = PLACEMENT_NAMES[Math.pow(2, i)] + " ";
    levelData.name =
      "Placement for rank " +
      (Math.pow(2, i) + 1) +
      " to " +
      2 * Math.pow(2, i);
    $(tLevel).find("#templatePL_header").text(levelData.name);
    var tLevel_items = $("#templatePL_items").clone();
    $(tLevel_items).removeAttr("hidden");
    $(tLevel_items).attr("id", "level_items_" + i);
    levelData.num_groups = Math.pow(2, i - 1);
    var next_group_counter_winning = 0;
    var next_group_counter_losing = 0;
    var act_target_rank_winning = 1;
    var act_target_rank_losing = 1;
    for (var j = 1; j <= levelData.num_groups; j++) {
      actGroup = { idx: j, name: levelData.actNaming + j, teams: [] };
      var templateGroup = $("#templateGroup").clone();
      $(templateGroup).attr("id", "pl_group_" + j);
      $(templateGroup).removeAttr("hidden");
      $(templateGroup).find("#templateGroup_name").text(actGroup.name);
      $(templateGroup)
        .find("#templateGroup_name")
        .css("background-color", "#BABABA");
      $(templateGroup).attr(
        "class",
        "col-md-" + width + " offset-md-" + offset
      );
      var body = $(templateGroup).find("#templateGroup_body");
      body.empty();
      for (let iTeam = 0; iTeam < 2; iTeam++) {
        actTeam = {
          idx: iTeam,
          name: iTeam + 1 + ". TeamDummy",
          rank: 0,
          transition: {
            origin_rank: iTeam + 1,
            origin_group_id: j - 1,
            origin_group_name: levelData.actNaming + j,
            target_rank: 0,
            target_lvl_id: 0,
            target_group_id: 0,
          },
        };
        actTeam.rank = 1 + iTeam;
        var tTeamItem = $("#templateTeamItem").clone();
        $(tTeamItem).attr("id", "pl_teamitem_" + j + "_" + iTeam);
        $(tTeamItem).removeAttr("hidden");

        actTeam.transition.target_lvl_id = j - 1;

        var trans_from_ko = actTransFromKO.items.find(
          (trans) =>
            trans.target_group_id == j - 1 && trans.target_rank == actTeam.rank
        );
        var NameExtension =
          iTeam + 1 + ". Loser " + trans_from_ko.origin_group_name;

        if (iTeam == 0 && Math.pow(2, i - 1) > 1) {
          $(tTeamItem).find("#templateTeamItem_icon").text("arrow_upward");
          actTeam.transition.target_rank = act_target_rank_winning;
          actTeam.transition.target_group_id = next_group_counter_winning;
          levelData.transitions_w.push(actTeam.transition);
          next_group_counter_winning++;
          if (
            next_group_counter_winning >= Math.pow(2, i - 2) &&
            act_target_rank_winning == 1
          ) {
            act_target_rank_winning = 2;
            next_group_counter_winning = 0;
          }
        } else if (Math.pow(2, i - 1) > 1) {
          $(tTeamItem).find("#templateTeamItem_icon").text("clear");
          actTeam.transition.target_rank = act_target_rank_losing;
          actTeam.transition.target_group_id = next_group_counter_losing;
          levelData.transitions_l.push(actTeam.transition);
          next_group_counter_losing++;
          if (
            next_group_counter_losing >= Math.pow(2, i - 2) &&
            act_target_rank_losing == 1
          ) {
            act_target_rank_losing = 2;
            next_group_counter_losing = 0;
          }
        } else if (Math.pow(2, i - 1) == 1) {
          actTeam.rank = levelData.bestRankWinner + iTeam;
          actTeam.transition.target_rank = actTeam.rank;
          actTeam.transition.target_group_id = 999;
          $(tTeamItem).find("#templateTeamItem_icon").attr("hidden", "hidden");
          $(tTeamItem)
            .find("#templateTeamItem_rank")
            .text(actTeam.rank + ".");
          $(tTeamItem).find("#templateTeamItem_rank").removeAttr("hidden");
        }
        actTeam.name = NameExtension;
        $(tTeamItem).find("#templateTeamItem_name").text(actTeam.name);
        body.append(tTeamItem);
        actGroup["teams"].push(actTeam);
      }
      $(tLevel_items).append(templateGroup);
      levelData["groups"].push(actGroup);
      wzNumOfGamesPlacement++;
    }
    $(tLevel).find("#templatePL_body").append(tLevel_items);
    wzCalcPlacementLevel(
      $(tLevel).find("#templatePL_body"),
      i,
      levelData.bestRankWinner,
      levelData.actNaming,
      levelData
    );
    $(row).append(tLevel);
    $(rowTab).append(tLevel.clone());
    plData["level"].push(levelData);
  }
  bh.structureData.placement = plData;
  $("#wz-res_num_of_games_placement").val(wzNumOfGamesPlacement);
}

function wzCalcPlacementLevel(
  bodyLevel,
  levels,
  bestRankWinner,
  namingParent,
  levelData
) {
  if (levels <= 1) return;
  var sublevelDataLoser = {
    idx: 0,
    name: "Losing",
    actNaming: "",
    bestRank: 0,
    worstRank: 0,
    num_groups: 0,
    groups: [],
    sublevel: [],
    transitions_w: [],
    transitions_l: [],
  };
  var width = 3;
  var offset = 0;
  if (levels <= 3) {
    width = 5;
    offset = 1;
  }
  sublevelDataLoser.bestRank = bestRankWinner + Math.pow(2, levels - 1);
  sublevelDataLoser.worstRank =
    sublevelDataLoser.bestRank - 1 + Math.pow(2, levels - 1);
  sublevelDataLoser.idx = Math.pow(2, levels - 2);

  // Losing part
  var tLoser = $("#templatePLsub_level").clone();
  $(tLoser).attr("id", "level_l_" + sublevelDataLoser.bestRank);
  $(tLoser).removeAttr("hidden");
  sublevelDataLoser.name =
    "Placement for rank " +
    sublevelDataLoser.bestRank +
    " to " +
    sublevelDataLoser.worstRank;
  $(tLoser).find("#templatePLsub_header").text(sublevelDataLoser.name);
  var tLoser_items = $(tLoser).find("#templatePLsub_items");
  var actNamingLoser =
    "P" + sublevelDataLoser.bestRank + "to" + sublevelDataLoser.worstRank;
  var next_group_counter_winning = 0;
  var next_group_counter_losing = 0;
  var act_target_rank_winning = 1;
  var act_target_rank_losing = 1;
  for (var j = 1; j <= sublevelDataLoser.idx; j++) {
    actGroup = { idx: j, name: actNamingLoser + " " + j, teams: [] };
    var templateGroup = $("#templateGroup").clone();
    $(templateGroup).attr("id", "pl_level_l_" + levels + "_" + j);
    $(templateGroup).removeAttr("hidden");
    $(templateGroup).find("#templateGroup_name").text(actGroup.name);
    $(templateGroup)
      .find("#templateGroup_name")
      .css("background-color", "#BABABA");
    $(templateGroup).attr("class", "col-md-" + width + " offset-md-" + offset);
    var body = $(templateGroup).find("#templateGroup_body");
    body.empty();
    for (let iTeam = 0; iTeam < 2; iTeam++) {
      actTeam = {
        idx: iTeam,
        name: iTeam + 1 + ". TeamDummy",
        rank: iTeam + 1,
        transition: {
          origin_rank: iTeam + 1,
          origin_group_id: j - 1,
          origin_group_name: actNamingLoser + " " + j,
          target_rank: 0,
          target_lvl_id: 0,
          target_group_id: 0,
        },
      };
      var tTeamItem = $("#templateTeamItem").clone();
      $(tTeamItem).attr("id", "pl_level_teamitem_l_" + j + "_" + iTeam);
      $(tTeamItem).removeAttr("hidden");

      actTeam.transition.target_lvl_id = j - 1;

      var trans_from_pl = levelData.transitions_l.find(
        (trans) =>
          trans.target_group_id == j - 1 && trans.target_rank == actTeam.rank
      );
      var NameExtension =
        iTeam + 1 + ". Loser " + trans_from_pl.origin_group_name;

      if (iTeam == 0 && sublevelDataLoser.idx > 1) {
        $(tTeamItem).find("#templateTeamItem_icon").text("arrow_upward");
        actTeam.transition.target_rank = act_target_rank_winning;
        actTeam.transition.target_group_id = next_group_counter_winning;
        sublevelDataLoser.transitions_w.push(actTeam.transition);
        next_group_counter_winning++;
        if (
          next_group_counter_winning >= sublevelDataLoser.idx / 2 &&
          act_target_rank_winning == 1
        ) {
          act_target_rank_winning = 2;
          next_group_counter_winning = 0;
        }
      } else if (sublevelDataLoser.idx > 1) {
        $(tTeamItem).find("#templateTeamItem_icon").text("clear");
        actTeam.transition.target_rank = act_target_rank_losing;
        actTeam.transition.target_group_id = next_group_counter_losing;
        sublevelDataLoser.transitions_l.push(actTeam.transition);
        next_group_counter_losing++;
        if (
          next_group_counter_losing >= sublevelDataLoser.idx / 2 &&
          act_target_rank_losing == 1
        ) {
          act_target_rank_losing = 2;
          next_group_counter_losing = 0;
        }
      } else if (sublevelDataLoser.idx == 1) {
        actTeam.rank = sublevelDataLoser.bestRank + iTeam;
        actTeam.transition.target_rank = sublevelDataLoser.bestRank + iTeam;
        actTeam.transition.target_group_id = 999;
        $(tTeamItem).find("#templateTeamItem_icon").attr("hidden", "hidden");
        $(tTeamItem)
          .find("#templateTeamItem_rank")
          .text(sublevelDataLoser.bestRank + iTeam + ".");
        $(tTeamItem).find("#templateTeamItem_rank").removeAttr("hidden");
      }
      actTeam.name = NameExtension;
      $(tTeamItem).find("#templateTeamItem_name").text(actTeam.name);
      body.append(tTeamItem);
      actGroup["teams"].push(actTeam);
    }
    $(tLoser_items).append(templateGroup);
    sublevelDataLoser["groups"].push(actGroup);
    wzNumOfGamesPlacement++;
  }
  bodyLevel.append(tLoser);
  //var next_best_losing_rank = sublevelDataLoser.bestRank + (sublevelDataLoser.worstRank - sublevelDataLoser.bestRank + 1) / 2;
  wzCalcPlacementLevel(
    bodyLevel,
    levels - 1,
    sublevelDataLoser.bestRank,
    actNamingLoser,
    sublevelDataLoser
  );
  levelData["sublevel"].push(sublevelDataLoser);

  // Winning part
  var sublevelDataWinner = {
    idx: 0,
    name: "Winning",
    actNaming: "",
    bestRank: 0,
    worstRank: 0,
    num_groups: 0,
    groups: [],
    sublevel: [],
    transitions_w: [],
    transitions_l: [],
  };
  sublevelDataWinner.bestRank = bestRankWinner;
  sublevelDataWinner.worstRank = sublevelDataLoser.bestRank - 1; //(sublevelDataWinner.bestRank - 1 + Math.pow(2, levels-1));
  sublevelDataWinner.idx = Math.pow(2, levels - 2);
  sublevelDataWinner.name =
    "Placement for rank " +
    sublevelDataWinner.bestRank +
    " to " +
    sublevelDataWinner.worstRank;

  var tWinning = $("#templatePLsub_level").clone();
  $(tWinning).attr("id", "level_w_" + sublevelDataWinner.bestRank);
  $(tWinning).removeAttr("hidden");
  $(tWinning).find("#templatePLsub_header").text(sublevelDataWinner.name);
  var tWinning_items = $(tWinning).find("#templatePLsub_items");
  var actNaming =
    "P" + sublevelDataWinner.bestRank + "to" + sublevelDataWinner.worstRank;
  var lastNaming = "";

  next_group_counter_winning = 0;
  next_group_counter_losing = 0;
  act_target_rank_winning = 1;
  act_target_rank_losing = 1;
  for (var j = 1; j <= sublevelDataWinner.idx; j++) {
    actGroup = { idx: j, name: actNaming + " " + j, teams: [] };
    var templateGroup = $("#templateGroup").clone();
    $(templateGroup).attr("id", "pl_level_w_" + levels + "_" + j);
    $(templateGroup).removeAttr("hidden");
    $(templateGroup)
      .find("#templateGroup_name")
      .text(actNaming + " " + j);
    $(templateGroup).attr("class", "col-md-" + width + " offset-md-" + offset);
    var body = $(templateGroup).find("#templateGroup_body");
    body.empty();
    for (let iTeam = 0; iTeam < 2; iTeam++) {
      actTeam = {
        idx: iTeam,
        name: iTeam + 1 + ". TeamDummy",
        rank: iTeam + 1,
        transition: {
          origin_rank: iTeam + 1,
          origin_group_id: j - 1,
          origin_group_name: actNaming + " " + j,
          target_rank: 0,
          target_lvl_id: 0,
          target_group_id: 0,
        },
      };
      var tTeamItem = $("#templateTeamItem").clone();
      $(tTeamItem).attr("id", "pl_level_teamitem_" + j + "_" + iTeam);
      $(tTeamItem).removeAttr("hidden");

      actTeam.transition.target_lvl_id = j - 1;

      var trans_from_pl = levelData.transitions_w.find(
        (trans) =>
          trans.target_group_id == j - 1 && trans.target_rank == actTeam.rank
      );
      var NameExtension =
        iTeam + 1 + ". Winner " + trans_from_pl.origin_group_name;

      if (iTeam == 0 && sublevelDataWinner.idx > 1) {
        $(tTeamItem).find("#templateTeamItem_icon").text("arrow_upward");
        actTeam.transition.target_rank = act_target_rank_winning;
        actTeam.transition.target_group_id = next_group_counter_winning;
        sublevelDataWinner.transitions_w.push(actTeam.transition);
        next_group_counter_winning++;
        if (
          next_group_counter_winning >= sublevelDataWinner.idx / 2 &&
          act_target_rank_winning == 1
        ) {
          act_target_rank_winning = 2;
          next_group_counter_winning = 0;
        }
      } else if (sublevelDataWinner.idx > 1) {
        $(tTeamItem).find("#templateTeamItem_icon").text("clear");
        actTeam.transition.target_rank = act_target_rank_losing;
        actTeam.transition.target_group_id = next_group_counter_losing;
        sublevelDataWinner.transitions_l.push(actTeam.transition);
        next_group_counter_losing++;
        if (
          next_group_counter_losing >= sublevelDataWinner.idx / 2 &&
          act_target_rank_losing == 1
        ) {
          act_target_rank_losing = 2;
          next_group_counter_losing = 0;
        }
      } else if (sublevelDataWinner.idx == 1) {
        actTeam.rank = sublevelDataWinner.bestRank + iTeam;
        actTeam.transition.target_rank = sublevelDataWinner.bestRank + iTeam;
        actTeam.transition.target_group_id = 999;
        $(tTeamItem).find("#templateTeamItem_icon").attr("hidden", "hidden");
        $(tTeamItem)
          .find("#templateTeamItem_rank")
          .text(sublevelDataWinner.bestRank + iTeam + ".");
        $(tTeamItem).find("#templateTeamItem_rank").removeAttr("hidden");
      }
      actTeam.name = NameExtension;
      $(tTeamItem).find("#templateTeamItem_name").text(actTeam.name);
      body.append(tTeamItem);
      actGroup["teams"].push(actTeam);
    }
    $(tWinning_items).append(templateGroup);
    sublevelDataWinner["groups"].push(actGroup);
    wzNumOfGamesPlacement++;
  }
  bodyLevel.append(tWinning);
  wzCalcPlacementLevel(
    bodyLevel,
    levels - 1,
    sublevelDataWinner.bestRank,
    actNaming,
    sublevelDataWinner
  );
  levelData["sublevel"].push(sublevelDataWinner);
}

function wzCalcPlacementOneGroup(best_rank_placement, remainingTeamsForPL) {
  plModeOneGroup.style.display = "block";
  //plPreviewPLAfterGroupCard.style.display = 'block';
  //plPreviewPLAfterGroupHeader.style.display = 'block';
  plPreviewPLAfterGroup.style.display = "block";
  var row = document.getElementById("wz-ovw-PL_AfterGroup");
  var rowTab = document.getElementById("wz-ovw-tabPL_AfterGroup");
  row.style.display = '';
  rowTab.style.display = '';
  $(row).empty();
  $(rowTab).empty();

  var tstateName =
    "Placement for rank " +
    best_rank_placement +
    " to " +
    groupData.teams_total;
  var abbr = "PL" + best_rank_placement + "to" + groupData.teams_total;
  var newGroup = { idx: 0, name: tstateName, abbreviation: abbr, teams: [] };
  var transitions = {};
  var num_of_transistions = groupData.teams_total - groupData.teams_to_ko;
  var numTeams = parseInt(groupData.teams_total) - best_rank_placement - 1;
  wzNumOfGamesPlacement += (numTeams * (numTeams - 1)) / 2;

  var width = 6;
  var offset = 3;
  var templateGroup = $("#templateGroup").clone();
  $(templateGroup).attr("id", "pl_after_group_one_group");
  $(templateGroup).removeAttr("hidden");
  $(templateGroup).find("#templateGroup_name").text(tstateName);
  $(templateGroup)
    .find("#templateGroup_name")
    .css("background-color", "#BABABA");
  $(templateGroup).attr("class", "col-md-" + width + " offset-md-" + offset);
  var body = $(templateGroup).find("#templateGroup_body");
  body.empty();
  var actRank = best_rank_placement;
  for (let i = 0; i < groupData.items.length; i++) {
    var actGroup = groupData.items[i];
    for (let j = 0; j < actGroup.teams.length; j++) {
      var actTeam = actGroup.teams[j];
      if (actTeam.isWinning == 0) {
        var teamName = actTeam.rank.toString() + ". " + actGroup.name;

        newTeam = {
          idx: j,
          name: teamName,
          rank: j + 1,
          transition: {
            origin_rank: j + 1,
            origin_group_id: i,
            origin_group_name: actGroup.name,
            target_rank: actRank,
            target_group_id: 999,
          },
        };

        var tTeamItem = $("#templateTeamItem").clone();
        $(tTeamItem).find("#templateTeamItem_icon").attr("hidden", "hidden");
        $(tTeamItem).attr("id", "pl_after_group_one_group_" + i + "_" + j);
        $(tTeamItem)
          .find("#templateTeamItem_rank")
          .text(actRank.toString() + ".");
        $(tTeamItem).find("#templateTeamItem_rank").removeAttr("hidden");
        $(tTeamItem).removeAttr("hidden");
        $(tTeamItem).find("#templateTeamItem_name").text(teamName);
        body.append(tTeamItem);
        actRank++;

        newGroup.teams.push(newTeam);
      }
    }
  }
  $(row).append(templateGroup);
  $(rowTab).append(templateGroup.clone());

  return newGroup;
}

function wzCalcPlacementMultiGroup(best_rank_placement, remainingTeamsForPL) {
  plModeMultiGroup.style.display = "block";
  //plPreviewPLAfterGroupCard.style.display = 'block';
  //plPreviewPLAfterGroupHeader.style.display = 'block';
  plPreviewPLAfterGroup.style.display = "block";
  //plPreviewFinalsHeader.style.display = 'block';
  //plPreviewFinalsHeader.style.display = 'block';
  //plPreviewFinals.style.display = 'block';
  //plPreviewFinals.textContent = "Placement for rank " + best_rank_placement.toString() + " to " + (best_rank_placement + 1).toString();

  var tstateName =
    "Placement for rank " +
    best_rank_placement +
    " to " +
    groupData.teams_total;

  var tstateNameShort =
    "PL " + best_rank_placement + " to " + groupData.teams_total;
  var plData = { num_groups: 0, groups: [] };
  var templatesGroup = [];

  var row = document.getElementById("wz-ovw-PL_AfterGroup");
  var rowTab = document.getElementById("wz-ovw-tabPL_AfterGroup");
  row.style.display = '';
  rowTab.style.display = '';
  $(row).empty();
  $(rowTab).empty();

  var category = $("#wz-tevent-category").val();
  var colors = [];
  var colorIdx = 0;
  if (category == "man") {
    colors = COLORS_PLACEMENT_GROUP_MEN;
  } else if (category == "woman") {
    colors = COLORS_PLACEMENT_GROUP_WOMEN;
  }

  plData.num_groups = parseInt($("#wz-pl-mode-num_of_groups").val());

  for (let i = 0; i < plData.num_groups; i++) {
    actGroup = {
      idx: i,
      name: "Group " + (i + 1) + " - " + tstateNameShort,
      teams: [],
    };
    plData.groups.push(actGroup);

    var templateGroup = $("#templateGroup").clone();
    $(templateGroup).attr("id", "pl_group_" + i);
    $(templateGroup).removeAttr("hidden");
    $(templateGroup).find("#templateGroup_name").text(actGroup.name);
    $(templateGroup)
      .find("#templateGroup_name")
      .css("background-color", colors[colorIdx]);

    var body = $(templateGroup).find("#templateGroup_body");
    body.empty();
    colorIdx += 1;
    if (colorIdx == colors.length) {
      colorIdx = 0;
    }
    templatesGroup.push(templateGroup);
  }
  var groupIdx = 0;

  for (let i = 0; i < groupData.items.length; i++) {
    var actGroup = groupData.items[i];
    for (let j = 0; j < actGroup.teams.length; j++) {
      var actTeam = actGroup.teams[j];
      if (actTeam.isWinning == 0) {
        var teamName = actTeam.rank.toString() + ". " + actGroup.name;

        actTeam = {
          idx: j,
          name: teamName,
          rank: j + 1,
          transition: {
            origin_rank: j + 1,
            origin_group_id: i,
            origin_group_name: actGroup.name,
            target_rank: 0,
            target_group_id: 999,
          },
        };

        var tTeamItem = $("#templateTeamItem").clone();
        $(tTeamItem).attr("id", "teamitem_" + i + "_" + j);
        $(tTeamItem).removeAttr("hidden");

        $(tTeamItem).find("#templateTeamItem_name").text(actTeam.name);
        templatesGroup[groupIdx].find("#templateGroup_body").append(tTeamItem);

        plData.groups[groupIdx].teams.push(actTeam);

        groupIdx += 1;
        if (groupIdx == plData.num_groups) {
          groupIdx = 0;
        }
      }
    }
  }

  for (let i = 0; i < plData.num_groups; i++) {
    $(row).append(templatesGroup[i]);
    $(rowTab).append(templatesGroup[i].clone());

    wzNumOfGamesPlacement += (plData.groups[i].teams.length * (plData.groups[i].teams.length - 1)) / 2;
  }

  return plData;
}

function wzCalcPlacementDirectKO(best_rank_placement, remainingTeamsForPL) {
  plModeOnlyKo.style.display = "block";
  //plPreviewPLAfterGroupCard.style.display = 'block';
  //plPreviewPLAfterGroupHeader.style.display = 'block';
  plPreviewPLAfterGroup.style.display = "block";
  //plPreviewFinalsHeader.style.display = 'block';
  //plPreviewFinals.style.display = 'block';
  //plPreviewFinals.textContent = "Placement for rank " + best_rank_placement.toString() + " to " + (best_rank_placement + 1).toString();
  if (remainingTeamsForPL % 2 != 0) {
    plModeOnlyKoExtraInfo.style.display = "block";
    plModeOnlyKoExtraInfo.textContent =
      "Info: You have " +
      remainingTeamsForPL +
      " teams. Knockout works best if # of teams is 2, 4, 8, etc...";
  }
  var rowTab = document.getElementById("wz-ovw-tabPL_AfterGroup");
  $(rowTab).empty();
}

function wzCalcFinals(idRow) {
  console.log("wzCalcFinals: " + idRow);
  finalData = { levels_ranked: 0, groups: [] };
  wzNumOfGamesFinal = 0;
  var row = document.getElementById(idRow);
  $(row).empty();
  var rowTab = document.getElementById("wz-ovw-tabKO_Final");
  $(rowTab).empty();

  var num_teams_soll = $("#wz-sel-teams-knockout").val();
  var levels = Math.log(num_teams_soll) / Math.log(2);

  var width = 3;
  var offset = 0;
  actGroup = { idx: 0, name: "F", teams: [] };
  var templateGroup = $("#templateGroup").clone();
  $(templateGroup).attr("id", "f_group_1");
  $(templateGroup).removeAttr("hidden");
  $(templateGroup).find("#templateGroup_name").text(actGroup.name);
  $(templateGroup)
    .find("#templateGroup_name")
    .css("background-color", "#EFC501");
  $(templateGroup).attr("class", "col-md-" + width + " offset-md-" + offset);
  var body = $(templateGroup).find("#templateGroup_body");
  body.empty();
  for (let iTeam = 0; iTeam < 2; iTeam++) {
    actTeam = {
      idx: iTeam,
      name: iTeam + 1 + ". TeamDummy",
      rank: 0,
      transition: {
        origin_rank: iTeam + 1,
        origin_group_id: 0,
        origin_group_name: actGroup.name,
        target_rank: 0,
        target_lvl_id: 0,
        target_group_id: 0,
      },
    };
    var tTeamItem = $("#templateTeamItem").clone();
    $(tTeamItem).attr("id", "f_teamitem_" + iTeam);
    $(tTeamItem).removeAttr("hidden");
    if (iTeam == 0) {
      $(tTeamItem).find("#templateTeamItem_icon").text("looks_one");
    } else {
      $(tTeamItem).find("#templateTeamItem_icon").text("looks_two");
    }
    var tempName = iTeam + 1 + ". TeamDummy";
    if (levels > 1) tempName = iTeam + 1 + ". Winner SF" + (iTeam + 1);
    actTeam.rank = 1 + iTeam;
    actTeam.name = tempName;
    actTeam.rank = 1 + iTeam;
    actTeam.transition.target_rank = actTeam.rank;
    actTeam.transition.target_group_id = 999;
    $(tTeamItem).find("#templateTeamItem_name").text(tempName);
    body.append(tTeamItem);
    actGroup["teams"].push(actTeam);
  }
  $(row).append(templateGroup);
  $(rowTab).append(templateGroup.clone());
  finalData["groups"].push(actGroup);
  wzNumOfGamesFinal++;
  bh.structureData.finals = finalData;
  $("#wz-res_num_of_games_final").val(wzNumOfGamesFinal);
}
