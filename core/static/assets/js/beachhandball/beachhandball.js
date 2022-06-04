$(document).ready(function() {
console.log("bh document ready");
    $("#bhAddCourtForm_OK").click(function(){ bh.addCourt_Click(); });
});

bh_gui = {
    
}
var KNOCKOUT_NAMES = {
    2: 'F',
    4: 'SF',
    8: 'QF',
    16: 'R16',
    32: 'R32',
    64: 'R64',
    128: 'R128'
}
var PLACEMENT_NAMES = {
    2: 'P3',
    4: 'P5',
    8: 'P9',
    16: 'P17',
    32: 'R33',
    64: 'R65',
    128: 'R129'
}
var wzNumOfGames = 0;
var wzNumOfGamesGroup = 0;
var wzNumOfGamesKO = 0;
var wzNumOfGamesPlacement = 0;
var wzNumOfGamesFinal = 0;

bh = {
    misc: {
      test_mode_active: 1,
    },

    structureData: {
        "max_num_teams": 0,
        "groups": "",
        "ko": "",
        "placement": "",
        "finals": "",
        "transitions": {
            "groups_to_ko":{},
            "ko_to_pl":{}
        }},

    wzUpdateStructure: function(){ 
        wzNumOfGames = 0;
        bh.wzCalcGroups("wz-ovw-groups");
        bh.wzCalcKnockout('wz-ovw-knockout');
        bh.wzCalcPlacement('wz-ovw-placement');
        bh.wzCalcFinals('wz-ovw-finals');

        $('#wz-structure-data').val(JSON.stringify(bh.structureData));
        wzNumOfGames = wzNumOfGamesGroup + wzNumOfGamesKO + wzNumOfGamesPlacement + wzNumOfGamesFinal;
        $('#wz-res_num_of_games_total').val(wzNumOfGames);
    },

    wzCalcGroups: function(idRow){ 
        console.log("wzCalcGroups: " + idRow);
        groupData = {"num_groups":0, "teams_per_group":0, "num_teams_res":0, "teams_to_ko":0, "teams_next_stage":0, "items": [] };
        var transitions = {};
        bh.structureData.groups = groupData;

        wzNumOfGamesGroup = 0;
        var row = document.getElementById(idRow);
        $(row).empty();
        var num_teams = $("#wz-max_num_teams").val();
        var num_groups = $("#wz-num_of_groups").val();

        bh.structureData.max_num_teams = num_teams;

        var teams_per_group = Math.floor(num_teams / num_groups);
        var num_teams_res = num_teams % num_groups;
        //var teams_per_group = $("#wz-teams_per_groups").val();
        //var teams_next_stage = $("#wz-num_teams_group_next_stage").val();

        var sel_val = $("#wz-sel-teams-knockout").val();
        document.getElementById("wz-num_of_groups").max = sel_val;
        groupData.teams_to_ko = parseInt(sel_val);
        var teams_next_stage_residue = sel_val % num_groups;
        groupData.teams_next_stage = Math.floor(sel_val / num_groups);
        $("#wz-sel-teams-knockout").empty();
        var sel_val_ranked = $("#wz-sel-teams-getting-ranked").val();
        if(sel_val_ranked > sel_val)
        {
            sel_val_ranked = sel_val;
        }
        $("#wz-sel-teams-getting-ranked").empty();
        var num_choices = Math.floor(Math.log(num_teams)/Math.log(2));
        for(let i = 1; i <= num_choices; i++)
        {
            var opt = '';
            if((Math.pow(2,i)) == sel_val)
            {
                opt = '<option selected value=' + Math.pow(2,i) + '>' + Math.pow(2,i) + '</option>';
            }
            else{
                opt = '<option value=' + Math.pow(2,i) + '>' + Math.pow(2,i) + '</option>';
            }
            $("#wz-sel-teams-knockout").append(opt);
            if((Math.pow(2,i)) == sel_val_ranked)
            {
                opt = '<option selected value=' + Math.pow(2,i) + '>' + Math.pow(2,i) + '</option>';
                $("#wz-sel-teams-getting-ranked").append(opt);
            }
            else if((Math.pow(2,i)) <= sel_val){
                opt = '<option value=' + Math.pow(2,i) + '>' + Math.pow(2,i) + '</option>';
                $("#wz-sel-teams-getting-ranked").append(opt);
            }
            
        }

        for(let i = 0; i < groupData.teams_to_ko / 2; i++)
        {
            transitions["ko_grp_" + i] = [];
        }

        groupData.num_groups = num_groups;
        groupData.teams_per_group = teams_per_group;
        groupData.num_teams_res = num_teams_res;
        console.log("wzCalcGroups: #groups:" + num_groups + " teams p gr: " + teams_per_group);
        for (let i = 0; i < num_groups; i++) {
            actGroup = {"idx":i, "name":'Group ' + (i+1), "teams": [] };
            var GameCounter = 0;
            var templateGroup = $("#templateGroup").clone();
            $(templateGroup).attr("id", 'group_' + i);
            $(templateGroup).removeAttr('hidden');
            $(templateGroup).find("#templateGroup_name").text(actGroup.name);

            
            var body = $(templateGroup).find("#templateGroup_body");
            body.empty();
            var addedResidue = false;
            for (let iTeam = 0; iTeam < teams_per_group; iTeam++) {
                actTeam = {"idx":iTeam, "name":(iTeam+1) + '. TeamDummy', "rank": 0, "transition": { "origin_rank": iTeam + 1, "origin_group_id": i, "origin_group_name": actGroup.name, "target_rank": 0, "target_group_id": 0} };
                actTeam.rank = iTeam + 1;
                actTeam.transition.origin_rank = actTeam.rank;
                
                var tTeamItem = $("#templateTeamItem").clone();
                $(tTeamItem).attr("id", 'teamitem_' + i + '_' + iTeam);
                $(tTeamItem).removeAttr('hidden');

                // transition
                var tar_gr_id = i + iTeam * num_groups;

                //console.log('iTeam=' + iTeam + ' tar_gr_id=' + tar_gr_id + ' team_ko_quote='+ team_ko_quote + ' ko_free_first_seats=' + ko_free_first_seats);
                // case if KO exists
                if(groupData.teams_to_ko / 2 > 2)
                {
                    if(tar_gr_id <  groupData.teams_to_ko / 2)
                    {
                        actTeam.transition.target_rank = 1;
                        actTeam.transition.target_group_id = tar_gr_id;
                        transitions["ko_grp_" + tar_gr_id].push(actTeam.transition);
                        //console.log('FIRST ko_counter=' + ko_counter + ' tar_gr_id=' + actTeam.transition.target_group_id);
                        //ko_counter++;
                    }
                    else if(tar_gr_id >= groupData.teams_to_ko / 2 && tar_gr_id < groupData.teams_to_ko)
                    {
                        actTeam.transition.target_rank = 2;
                        tar_gr_id = (groupData.teams_to_ko-1) - tar_gr_id ;
                        actTeam.transition.target_group_id = tar_gr_id;
                        transitions["ko_grp_" + tar_gr_id].push(actTeam.transition);
                        //console.log('2nd: ko_counter=' + ko_counter + ' tar_gr_id=' + actTeam.transition.target_group_id);
                    }
                    else
                    {
                        actTeam.transition.target_rank = -1;
                        actTeam.transition.target_group_id = 999; 
                    }
                }
                else // from group directly to final
                {}
                
                if( iTeam < groupData.teams_next_stage)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');                    
                }
                else if(teams_next_stage_residue > 0 && addedResidue == false)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                    addedResidue = true;
                    teams_next_stage_residue--;
                }
                else
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('clear');
                }
                
                $(tTeamItem).find("#templateTeamItem_name").text(actTeam.name);
                body.append(tTeamItem);
                actGroup["teams"].push(actTeam);
                GameCounter++;
            }
            if(num_teams_res > 0)
            {
                actTeam = {"idx":teams_per_group, "name":(teams_per_group+1) + '. TeamDummy' };
                var tTeamItem = $("#templateTeamItem").clone();
                $(tTeamItem).attr("id", 'teamitem_' + (teams_per_group+1));
                $(tTeamItem).removeAttr('hidden');
                if( teams_per_group < groupData.teams_next_stage)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                }
                else
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('clear');
                }
                
                $(tTeamItem).find("#templateTeamItem_name").text(actTeam.name);
                body.append(tTeamItem);
                actGroup.teams.push(actTeam);
                GameCounter++;
                num_teams_res--;
            }
            GameCounter--;
            wzNumOfGamesGroup += (GameCounter*(GameCounter+1)/2);
            groupData.items.push(actGroup);
            $(row).append(templateGroup);
        }
        bh.structureData.transitions.groups_to_ko = transitions;
        $('#wz-res_num_of_games_group').val(wzNumOfGamesGroup);
    },

    wzCalcPlacement: function(idRow){
        console.log("wzCalcPlacement: " + idRow);
        var plData = {"levels_ranked":0, "num_teams_getting_ranked":0, "level": [] };
        wzNumOfGamesPlacement = 0;
        var row = document.getElementById(idRow);
        $(row).empty();
        var num_teams_soll = $("#wz-sel-teams-knockout").val();
        plData.num_teams_getting_ranked = $("#wz-sel-teams-getting-ranked").val();
        var levels = (Math.log(num_teams_soll) / Math.log(2)) - 1; // -1 because final is seperated by
        plData.levels_ranked = (Math.log(plData.num_teams_getting_ranked) / Math.log(2)) - 1;
        
        for(let i = plData.levels_ranked; i >= 1; i--)
        {
            // this instance is the first instance when losers  come from knockout stage
            levelData = {"idx": i, "name":"", "actNaming":"", "bestRankWinner": 0, "bestRankLoser":0, "num_groups":0, "groups": [], "sublevel":[], "transitions_w":[], "transitions_l":[]};
            var tLevel= $("#templatePL_level").clone();
            
            var actTransFromKO = bh.structureData.transitions.ko_to_pl[KNOCKOUT_NAMES[Math.pow(2, i+1)]];

            $(tLevel).attr("id", 'level_' + i);
            $(tLevel).removeAttr('hidden');
            levelData.bestRankWinner = (Math.pow(2, i)+1); //Math.pow(2, i-1) + 1;
            levelData.bestRankLoser = ((2*Math.pow(2, i)));
            var width = 3;
            var offset = 0;
            levelData.actNaming = PLACEMENT_NAMES[Math.pow(2, i)] + ' ';
            levelData.name = 'Placement for rank ' + (Math.pow(2, i)+1) + ' to ' + ((2*Math.pow(2, i)));
            $(tLevel).find("#templatePL_header").text(levelData.name);
            var tLevel_items = $("#templatePL_items").clone();
            $(tLevel_items).removeAttr('hidden');
            $(tLevel_items).attr("id", 'level_items_' + i);
            levelData.num_groups = Math.pow(2, i-1);
            var next_group_counter_winning = 0;
            var next_group_counter_losing = 0;
            var act_target_rank_winning = 1;
            var act_target_rank_losing= 1;
            for(var j = 1; j <= levelData.num_groups; j++)
            {
                actGroup = {"idx":j, "name":levelData.actNaming + j, "teams": [] };
                var templateGroup = $("#templateGroup").clone();
                $(templateGroup).attr("id", 'pl_group_' + j);
                $(templateGroup).removeAttr('hidden');
                $(templateGroup).find("#templateGroup_name").text(actGroup.name);
                $(templateGroup).attr("class", 'col-md-' + width + ' offset-md-' + offset);
                var body = $(templateGroup).find("#templateGroup_body");
                body.empty();
                for (let iTeam = 0; iTeam < 2; iTeam++) {
                    actTeam = {"idx":iTeam, "name":(iTeam+1) + '. TeamDummy', "rank": 0, "transition": { "origin_rank": iTeam + 1, "origin_group_id": j-1, "origin_group_name": levelData.actNaming + j, "target_rank": 0, "target_lvl_id": 0, "target_group_id": 0} };
                    actTeam.rank = 1+iTeam;
                    var tTeamItem = $("#templateTeamItem").clone();
                    $(tTeamItem).attr("id", 'pl_teamitem_' + j + '_' + iTeam);
                    $(tTeamItem).removeAttr('hidden');

                    actTeam.transition.target_lvl_id = j - 1;

                    var trans_from_ko = actTransFromKO.items.find(trans => trans.target_group_id == (j-1) && trans.target_rank == actTeam.rank);
                    var NameExtension = (iTeam+1) + '. Loser ' + trans_from_ko.origin_group_name;                

                    if( iTeam == 0 && Math.pow(2, i-1) > 1)
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                        actTeam.transition.target_rank = act_target_rank_winning;
                        actTeam.transition.target_group_id = next_group_counter_winning;
                        levelData.transitions_w.push(actTeam.transition);
                        next_group_counter_winning++;
                        if(next_group_counter_winning >= Math.pow(2, i-2) && act_target_rank_winning == 1)
                        {
                            act_target_rank_winning = 2;
                            next_group_counter_winning = 0;
                        }
                    }
                    else if(Math.pow(2, i-1) > 1)
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").text('clear');
                        actTeam.transition.target_rank = act_target_rank_losing;
                        actTeam.transition.target_group_id = next_group_counter_losing;
                        levelData.transitions_l.push(actTeam.transition);
                        next_group_counter_losing++;
                        if(next_group_counter_losing >= Math.pow(2, i-2) && act_target_rank_losing == 1)
                        {
                            act_target_rank_losing = 2;
                            next_group_counter_losing = 0;
                        }
                    }
                    else if(Math.pow(2, i-1) == 1)
                    {
                        actTeam.rank = levelData.bestRankWinner+iTeam;
                        actTeam.transition.target_rank = actTeam.rank;
                        actTeam.transition.target_group_id = 999;
                        $(tTeamItem).find("#templateTeamItem_icon").attr('hidden', 'hidden');
                        $(tTeamItem).find("#templateTeamItem_rank").text((actTeam.rank) +'.');
                        $(tTeamItem).find("#templateTeamItem_rank").removeAttr('hidden');
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
            bh.wzCalcPlacementLevel($(tLevel).find("#templatePL_body"), i, levelData.bestRankWinner, levelData.actNaming, levelData);
            $(row).append(tLevel);
            plData["level"].push(levelData);
        }
        bh.structureData.placement = plData;
        $('#wz-res_num_of_games_placement').val(wzNumOfGamesPlacement);
    },

    wzCalcPlacementLevel(bodyLevel, levels, bestRankWinner, namingParent, levelData){
        if(levels <= 1)
            return;
        var sublevelDataLoser = {"idx": 0, "name":"Losing", "actNaming":"", "bestRank": 0, "worstRank":0, "num_groups":0, "groups": [], "sublevel":[], "transitions_w":[], "transitions_l":[]};
        var width = 3;
        var offset = 0;
        if(levels <= 3)
        {
            width = 5;
            offset = 1;
        }
        sublevelDataLoser.bestRank = bestRankWinner + Math.pow(2, levels-1);
        sublevelDataLoser.worstRank = (sublevelDataLoser.bestRank - 1 + Math.pow(2, levels-1));
        sublevelDataLoser.idx = Math.pow(2, levels-2);

        // Losing part
        var tLoser= $("#templatePLsub_level").clone();
        $(tLoser).attr("id", 'level_l_' + sublevelDataLoser.bestRank);
        $(tLoser).removeAttr('hidden');
        sublevelDataLoser.name = 'Placement for rank ' + sublevelDataLoser.bestRank +' to ' + sublevelDataLoser.worstRank;
        $(tLoser).find("#templatePLsub_header").text(sublevelDataLoser.name);
        var tLoser_items = $(tLoser).find("#templatePLsub_items");
        var actNamingLoser = 'P' + sublevelDataLoser.bestRank + 'to' + sublevelDataLoser.worstRank;
        var next_group_counter_winning = 0;
        var next_group_counter_losing = 0;
        var act_target_rank_winning = 1;
        var act_target_rank_losing= 1;
        for(var j = 1; j <= sublevelDataLoser.idx; j++)
        {
            actGroup = {"idx":j, "name":actNamingLoser + ' ' + j, "teams": [] };
            var templateGroup = $("#templateGroup").clone();
            $(templateGroup).attr("id", 'pl_level_l_' + levels + '_' + j);
            $(templateGroup).removeAttr('hidden');
            $(templateGroup).find("#templateGroup_name").text(actGroup.name);
            $(templateGroup).attr("class", 'col-md-' + width + ' offset-md-' + offset);
            var body = $(templateGroup).find("#templateGroup_body");
            body.empty();
            for (let iTeam = 0; iTeam < 2; iTeam++) {
                actTeam = {"idx":iTeam, "name":(iTeam+1) + '. TeamDummy', "rank": (iTeam + 1), "transition": { "origin_rank": iTeam + 1, "origin_group_id": j-1, "origin_group_name": actNamingLoser + ' ' + j, "target_rank": 0, "target_lvl_id": 0, "target_group_id": 0} };
                var tTeamItem = $("#templateTeamItem").clone();
                $(tTeamItem).attr("id", 'pl_level_teamitem_l_' + j + '_' + iTeam);
                $(tTeamItem).removeAttr('hidden');

                actTeam.transition.target_lvl_id = j - 1;

                var trans_from_pl = levelData.transitions_l.find(trans => trans.target_group_id == (j-1) && trans.target_rank == actTeam.rank);
                var NameExtension = (iTeam+1) + '. Loser ' + trans_from_pl.origin_group_name;

                if( iTeam == 0 && sublevelDataLoser.idx > 1)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                    actTeam.transition.target_rank = act_target_rank_winning;
                    actTeam.transition.target_group_id = next_group_counter_winning;
                    sublevelDataLoser.transitions_w.push(actTeam.transition);
                    next_group_counter_winning++;
                    if(next_group_counter_winning >= sublevelDataLoser.idx / 2 && act_target_rank_winning == 1)
                    {
                        act_target_rank_winning = 2;
                        next_group_counter_winning = 0;
                    }
                }
                else if(sublevelDataLoser.idx > 1)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('clear');
                    actTeam.transition.target_rank = act_target_rank_losing;
                    actTeam.transition.target_group_id = next_group_counter_losing;
                    sublevelDataLoser.transitions_l.push(actTeam.transition);
                    next_group_counter_losing++;
                    if(next_group_counter_losing >= sublevelDataLoser.idx / 2 && act_target_rank_losing == 1)
                    {
                        act_target_rank_losing = 2;
                        next_group_counter_losing = 0;
                    }
                }
                else if(sublevelDataLoser.idx == 1)
                {
                    actTeam.rank = (sublevelDataLoser.bestRank+iTeam);
                    actTeam.transition.target_rank = (sublevelDataLoser.bestRank+iTeam);
                    actTeam.transition.target_group_id = 999;
                    $(tTeamItem).find("#templateTeamItem_icon").attr('hidden', 'hidden');
                    $(tTeamItem).find("#templateTeamItem_rank").text( (sublevelDataLoser.bestRank+iTeam)+'.');
                    $(tTeamItem).find("#templateTeamItem_rank").removeAttr('hidden');
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
        bh.wzCalcPlacementLevel(bodyLevel, levels-1, sublevelDataLoser.bestRank, actNamingLoser, sublevelDataLoser);
        levelData["sublevel"].push(sublevelDataLoser);

        // Winning part
        var sublevelDataWinner = {"idx": 0, "name":"Winning", "actNaming":"", "bestRank": 0, "worstRank":0, "num_groups":0, "groups": [], "sublevel":[], "transitions_w":[], "transitions_l":[]};
        sublevelDataWinner.bestRank = bestRankWinner;
        sublevelDataWinner.worstRank = sublevelDataLoser.bestRank - 1;//(sublevelDataWinner.bestRank - 1 + Math.pow(2, levels-1));
        sublevelDataWinner.idx = Math.pow(2, levels-2);
        sublevelDataWinner.name = 'Placement for rank ' + sublevelDataWinner.bestRank +' to ' + sublevelDataWinner.worstRank;

        var tWinning= $("#templatePLsub_level").clone();
        $(tWinning).attr("id", 'level_w_' + sublevelDataWinner.bestRank);
        $(tWinning).removeAttr('hidden');
        $(tWinning).find("#templatePLsub_header").text(sublevelDataWinner.name);
        var tWinning_items = $(tWinning).find("#templatePLsub_items");
        var actNaming = 'P' + sublevelDataWinner.bestRank + 'to' + sublevelDataWinner.worstRank;
        var lastNaming = '';
        
        next_group_counter_winning = 0;
        next_group_counter_losing = 0;
        act_target_rank_winning = 1;
        act_target_rank_losing= 1;
        for(var j = 1; j <= sublevelDataWinner.idx; j++)
        {
            actGroup = {"idx":j, "name":actNaming + ' ' + j, "teams": [] };
            var templateGroup = $("#templateGroup").clone();
            $(templateGroup).attr("id", 'pl_level_w_' + levels + '_' + j);
            $(templateGroup).removeAttr('hidden');
            $(templateGroup).find("#templateGroup_name").text(actNaming + ' ' + j);
            $(templateGroup).attr("class", 'col-md-' + width + ' offset-md-' + offset);
            var body = $(templateGroup).find("#templateGroup_body");
            body.empty();
            for (let iTeam = 0; iTeam < 2; iTeam++) {
                actTeam = {"idx":iTeam, "name":(iTeam+1) + '. TeamDummy', "rank": (iTeam + 1), "transition": { "origin_rank": iTeam + 1, "origin_group_id": j-1, "origin_group_name": actNaming + ' ' + j, "target_rank": 0, "target_lvl_id": 0, "target_group_id": 0} };
                var tTeamItem = $("#templateTeamItem").clone();
                $(tTeamItem).attr("id", 'pl_level_teamitem_' + j + '_' + iTeam);
                $(tTeamItem).removeAttr('hidden');

                actTeam.transition.target_lvl_id = j - 1;

                var trans_from_pl = levelData.transitions_w.find(trans => trans.target_group_id == (j-1) && trans.target_rank == actTeam.rank);
                var NameExtension = (iTeam+1) + '. Winner ' + trans_from_pl.origin_group_name;
                
                if( iTeam == 0 && sublevelDataWinner.idx > 1)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                    actTeam.transition.target_rank = act_target_rank_winning;
                    actTeam.transition.target_group_id = next_group_counter_winning;
                    sublevelDataWinner.transitions_w.push(actTeam.transition);
                    next_group_counter_winning++;
                    if(next_group_counter_winning >= sublevelDataWinner.idx / 2 && act_target_rank_winning == 1)
                    {
                        act_target_rank_winning = 2;
                        next_group_counter_winning = 0;
                    }
                }
                else if(sublevelDataWinner.idx > 1)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('clear');
                    actTeam.transition.target_rank = act_target_rank_losing;
                    actTeam.transition.target_group_id = next_group_counter_losing;
                    sublevelDataWinner.transitions_l.push(actTeam.transition);
                    next_group_counter_losing++;
                    if(next_group_counter_losing >= sublevelDataWinner.idx / 2 && act_target_rank_losing == 1)
                    {
                        act_target_rank_losing = 2;
                        next_group_counter_losing = 0;
                    }
                }
                else if(sublevelDataWinner.idx == 1)
                {
                    actTeam.rank = (sublevelDataWinner.bestRank+iTeam);
                    actTeam.transition.target_rank = (sublevelDataWinner.bestRank + iTeam);
                    actTeam.transition.target_group_id = 999;
                    $(tTeamItem).find("#templateTeamItem_icon").attr('hidden', 'hidden');
                    $(tTeamItem).find("#templateTeamItem_rank").text((sublevelDataWinner.bestRank + iTeam)+'.');
                    $(tTeamItem).find("#templateTeamItem_rank").removeAttr('hidden');
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
        bh.wzCalcPlacementLevel(bodyLevel, levels-1, sublevelDataWinner.bestRank, actNaming, sublevelDataWinner);
        levelData["sublevel"].push(sublevelDataWinner);
    },

    wzCalcFinals: function(idRow) {
        console.log("wzCalcFinals: " + idRow);
        finalData = {"levels_ranked":0, "groups": [] };
        wzNumOfGamesFinal = 0;
        var row = document.getElementById(idRow);
        $(row).empty();

        var num_teams_soll = $("#wz-sel-teams-knockout").val();
        var levels = (Math.log(num_teams_soll) / Math.log(2));

        var width = 3;
        var offset = 0;
        actGroup = {"idx":0, "name":'F', "teams": [] };
        var templateGroup = $("#templateGroup").clone();
        $(templateGroup).attr("id", 'f_group_1');
        $(templateGroup).removeAttr('hidden');
        $(templateGroup).find("#templateGroup_name").text(actGroup.name);
        $(templateGroup).attr("class", 'col-md-' + width + ' offset-md-' + offset);
        var body = $(templateGroup).find("#templateGroup_body");
        body.empty();
        for (let iTeam = 0; iTeam < 2; iTeam++) {
            actTeam = {"idx":iTeam, "name":(iTeam+1) + '. TeamDummy', "rank": 0, "transition": { "origin_rank": iTeam+1, "origin_group_id": 0, "origin_group_name": actGroup.name, "target_rank": 0, "target_lvl_id": 0, "target_group_id": 0} };
            var tTeamItem = $("#templateTeamItem").clone();
            $(tTeamItem).attr("id", 'f_teamitem_' + iTeam);
            $(tTeamItem).removeAttr('hidden');
            if( iTeam == 0)
            {
                $(tTeamItem).find("#templateTeamItem_icon").text('looks_one');
            }
            else
            {
                $(tTeamItem).find("#templateTeamItem_icon").text('looks_two');
            }
            var tempName = (iTeam+1) + '. TeamDummy';
            if(levels > 1)
                tempName = (iTeam + 1) + '. Winner SF' + (iTeam + 1);
            actTeam.rank = (1+iTeam);
            actTeam.name = tempName;
            actTeam.rank = (1+iTeam);
            actTeam.transition.target_rank = actTeam.rank;
            actTeam.transition.target_group_id = 999;
            $(tTeamItem).find("#templateTeamItem_name").text(tempName);
            body.append(tTeamItem);
            actGroup["teams"].push(actTeam);
        }
        $(row).append(templateGroup);
        finalData["groups"].push(actGroup);
        wzNumOfGamesFinal++;
        bh.structureData.finals = finalData;
        $('#wz-res_num_of_games_final').val(wzNumOfGamesFinal);
    },

    wzCalcKnockout: function(idRow){
        console.log("wzCalcKnockout: " + idRow);
        var koData = {"levels":0, "num_teams_soll":0, "level": [] };
        var transitions_pl = {};
        wzNumOfGamesKO = 0;
        var row = document.getElementById(idRow);
        $(row).empty();
        var num_teams = $("#wz-num_teams_group_next_stage").val();
        koData.num_teams_soll = $("#wz-sel-teams-knockout").val();
        koData.levels = (Math.log(koData.num_teams_soll) / Math.log(2)); // -1 because final is seperated by
        var actNaming = '';
        var lastNaming = '';
        var lastTransitions = [];
        for(let i = koData.levels; i > 1; i--)
        {
            var levelData = {"idx":i, "header": "", "actNaming":"", "groups":[], "transitions": [] };
            var transFromGroup = bh.structureData.transitions.groups_to_ko;
            transitions_pl[KNOCKOUT_NAMES[Math.pow(2, i)]] = {"idx": i, "items": []};
            var tLevel= $("#templateKO_level").clone();
            $(tLevel).attr("id", 'level_' + i);
            $(tLevel).removeAttr('hidden');
            var width = 1;
            var offset = 0;
            var header = 'Round of ' + Math.pow(2, i);
            if(Math.pow(2, i) == 8)
            {
                header = 'Quarter Finals';
                width = 3;
            }
            if(Math.pow(2, i) == 4)
            {
                header = 'Semi Finals';
                width = 5;
                offset = 1;
            }
            levelData.actNaming = KNOCKOUT_NAMES[Math.pow(2, i)];
            $(tLevel).find("#templateKO_header").text(header);
            levelData.header = header;
            var tLevel_items = $(tLevel).find("#templateKO_items");
            var num_of_states = Math.pow(2, i-1);
            var next_group_counter = 0;
            var next_group_counter_pl = 0;
            var act_target_rank_ko = 1;
            var act_target_rank_placement = 1;
            for(var j = 1; j <= num_of_states; j++)
            {
                var actGroup = {"idx":j, "name":levelData.actNaming + ' ' + j, "teams": [] };
                var templateGroup = $("#templateGroup").clone();
                $(templateGroup).attr("id", 'ko_grp_' + (j-1));
                $(templateGroup).removeAttr('hidden');
                $(templateGroup).find("#templateGroup_name").text(actGroup.name);
                $(templateGroup).attr("class", 'col-md-' + width + ' offset-md-' + offset);
                var body = $(templateGroup).find("#templateGroup_body");
                body.empty();
                for (let iTeam = 0; iTeam < 2; iTeam++) {
                    actTeam = {"idx":iTeam, "name":(iTeam+1) + '. TeamDummy', "rank": 0, "transition": { "origin_rank": iTeam + 1, "origin_group_id": j-1, "origin_group_name": levelData.actNaming + ' ' + j, "target_rank": 0, "target_lvl_id": 0, "target_group_id": 0} };
                    var tTeamItem = $("#templateTeamItem").clone();
                    $(tTeamItem).attr("id", 'ko_teamitem_' + j + '_' + iTeam);
                    $(tTeamItem).removeAttr('hidden');

                    actTeam.transition.target_lvl_id = i - 1;

                    // transition
                    if(iTeam === 0)
                    {
                        actTeam.transition.target_rank = act_target_rank_ko;
                        actTeam.transition.target_group_id = next_group_counter;
                        next_group_counter++;
                        if(next_group_counter >= Math.pow(2, i-2) && act_target_rank_ko == 1)
                        {
                            act_target_rank_ko = 2;
                            next_group_counter = 0;
                        }
                    }
                    else
                    {
                        actTeam.transition.target_rank = act_target_rank_placement;
                        actTeam.transition.target_group_id = next_group_counter_pl;
                        transitions_pl[levelData.actNaming].items.push(actTeam.transition);
                        next_group_counter_pl++;
                        if(next_group_counter_pl >= Math.pow(2, i-2) && act_target_rank_placement == 1)
                        {
                            act_target_rank_placement = 2;
                            next_group_counter_pl = 0;
                        }
                    }
                    
                    if(i == koData.levels)
                    {
                        NameExtension = '. TeamDummy';
                        // get name from transition
                        var actTrans = transFromGroup["ko_grp_" + (j-1)].find(e => e.target_rank === iTeam + 1);
                        NameExtension = actTrans.origin_rank + '. ' + actTrans.origin_group_name;
                    }
                    else
                    {
                        var actTrans = lastTransitions.find(e => e.target_rank === iTeam + 1 && e.target_group_id == (j-1));
                        NameExtension = actTrans.origin_rank + '. ' + actTrans.origin_group_name;
                    }
                    if( iTeam == 0)
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                        actTeam.rank = 1;
                        actTeam.transition.origin_rank = 1;
                    }
                    else
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").text('clear');
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
            koData["level"].push(levelData);
            lastNaming = levelData.actNaming;
            lastTransitions = levelData.transitions
        }
        bh.structureData.ko = koData;
        bh.structureData.transitions.ko_to_pl = transitions_pl;
        $('#wz-res_num_of_games_ko').val(wzNumOfGamesKO);
    },

    tournamentData: "",
    numCourts: 0,
    minutesPerGame: 0,
    DateTimeFirstGame: "",
    DateTimeLastGame: "",
    gameDays: [],

    wzUpdateGamePlan: function(){
        console.log("wzUpdateGamePlan");
        bh.wzgpUpdateStart("wzgp-events-total");
        bh.wzgpUpdateGameDays("wzgp-gamedays");
    },

    wzgpUpdateStart: function(idRow){

        var row = document.getElementById(idRow);
        $(row).empty();

        bh.numCourts = $("#wzgp-num_courts").val();
        bh.minutesPerGame = $("#wzgp-time-slot").val();
        
        var num_games_total = 0;
        var num_games_group = 0;
        var num_games_ko = 0;
        var num_games_pl = 0;
        var num_games_f = 0;

        var templateTotal = $("#templateEvent_total_games").clone();
        $(templateTotal).attr("id", 'total_0');
        $(templateTotal).removeAttr('hidden');
        $(templateTotal).find("#template_name").text('Resulting games');
        var table = $(templateTotal).find("#wzgp-table-gamecounts");
        bh.tournamentData.events.forEach(event => {

            event.stages.forEach(stage => {
                var stage_counter = 0;
                stage.states.forEach(state => {
                    var n = state.ranking.length - 1;
                    stage_counter += (n*n + n) / 2;
                })

                if(stage.tournament_stage === "GROUP_STAGE")
                {
                    num_games_group = stage_counter;
                }
                else if(stage.tournament_stage === "KNOCKOUT_STAGE")
                {
                    num_games_ko = stage_counter;
                }
                else if(stage.tournament_stage === "PLAYOFF_STAGE")
                {
                    num_games_pl = stage_counter;
                }
                else if(stage.tournament_stage === "FINAL")
                {
                    num_games_f = stage_counter;
                }


            });
            
        });
        $(row).append(templateTotal);
        num_games_total = num_games_group + num_games_ko + num_games_pl + num_games_f;

        var total_time_min = num_games_total * bh.minutesPerGame / bh.numCourts;
        var total_time_hours = Math.floor(total_time_min / 60);
        var remaining_minutes = total_time_min - total_time_hours*60;

        $('#wz-res_num_of_games_total').val(num_games_total);
        $('#wz-res_num_of_games_group').val(num_games_group);
        $('#wz-res_num_of_games_ko').val(num_games_ko);
        $('#wz-res_num_of_games_placement').val(num_games_pl);
        $('#wz-res_num_of_games_final').val(num_games_f);
        $('#wz-res_time').text(total_time_hours + 'h ' + remaining_minutes + ' m');
    },

    wzgpUpdateGameDays: function(idRow){
        var row = document.getElementById(idRow);
        $(row).empty();

        var dateFirstGame = moment($("#wzgp-GameDays_DateTimeFirstGame").val(), "MM/DD/YYYY HH:mm");
        bh.DateTimeFirstGame = dateFirstGame.format("MM/DD/YYYY HH:mm");
        var dateLastGame = moment($("#wzgp-GameDays_DateTimeLastGame").val(), "MM/DD/YYYY HH:mm");
        bh.DateTimeLastGame = dateLastGame.format("MM/DD/YYYY HH:mm");

        if(dateLastGame.isBefore(dateFirstGame))
        {
            $(row).append('<h3>Last game is before first!</h3>');
            return;
        }
        else if(dateLastGame.diff(dateFirstGame, 'days') > 8)
        {
            $(row).append('<h3>Are you crazy? More than 8 Game Days, serious?</h3>');
            return;
        }

        bh.gameDays = [];

        for(var i = 0; i <= dateLastGame.diff(dateFirstGame, 'days');i++)
        {
            var actMoment = moment(dateFirstGame).add(i, 'days');
            var endMoment = moment(actMoment).add(8, 'hours');
            if(i == dateLastGame.diff(dateFirstGame, 'days'))
            {
                endMoment = moment(dateLastGame);
            }
            var gameDay = {"id": i, "starttime": actMoment.format("MM/DD/YYYY HH:mm"), "endtime": endMoment.format("MM/DD/YYYY HH:mm")};

            var templateGD = $("#templateGameDay").clone();
            $(templateGD).attr("id", 'gameday_' + i);
            $(templateGD).removeAttr('hidden');
            $(templateGD).find("#templateGameDay_title").text('Day ' + (i+1) + ' - ' + actMoment.format("DD.MM."));
            $(templateGD).find("#template_info").text("");

            $(templateGD).find("#timeFirst_h").val(actMoment.hour());
            $(templateGD).find("#timeFirst_m").val(actMoment.minutes());

            $(templateGD).find("#timeLast_h").val(endMoment.hour());
            $(templateGD).find("#timeLast_m").val(endMoment.minutes());
            

            $(row).append(templateGD);
            bh.gameDays.push(gameDay);
        }

    },

    addCourt_Click: function(){
        console.log("addCourt_Click");
        
        var form = document.getElementById("bhAddCourtForm");
        
        console.debug(form.checkValidity());
        console.debug($(form).serialize());
    
        console.debug($(form).serializeJSON());
        var data = $(form).serializeJSON();
        
        if(form.checkValidity())
        {
            console.log("Close Modal");

            var response = tournament_service.createCourt(data);
            
            // Hide modal frame
            var modal = document.getElementById("bhAddCourtModal");
            $(modal).modal('toggle');

            // evaluate server request and set notification
            if(response.success == "true")
            {
                bh.addCourtHTML(response.data);
            }
            md.showNotification('bottom','center', response.message, response.message_type);
        }
        else {
            var validator = $(form).validate();
            validator.form();
        }
    },

    addCourtHTML: function(courtData) {
        var templateCourt = $("#templateCourt").clone();
        $(templateCourt).attr("id", 'court_' + courtData.id);
        $(templateCourt).attr('obj_id', courtData.id);
        $(templateCourt).attr('data-obj', JSON.stringify(courtData));
        $(templateCourt).removeAttr('hidden');
        $(templateCourt).find("#templateCourt_btnUpdate").click(function(){ bh.updateCourt_Click($(this)); });
        $(templateCourt).find("#templateCourt_btnRemove").click(function(){ bh.removeCourt_Click($(this)); });
        $(templateCourt).find(".card-category").text(courtData.number);
        $(templateCourt).find(".card-title").text(courtData.name);
        $("#court_table").append(templateCourt);
        return;
    },

    updateCourt_Click: function(node){
        console.log("updateCourt_Click");
        var topnode = node.parent().closest('.topnode');
        var court = JSON.parse(topnode.attr('data-obj'));
        console.log(topnode);
        console.log(court);
    },

    removeCourt_Click: function(node){
        console.log("removeCourt_Click");
        var topnode = node.parent().closest('.topnode');
        var court = JSON.parse(topnode.attr('data-obj'));
        swal({
            title: 'Are you sure delete ' + court.name + '?',
            text: 'Court ' + court.name + ' will be deleted!',
            type: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'No, keep it',
            confirmButtonClass: "btn btn-success",
            cancelButtonClass: "btn btn-danger",
            buttonsStyling: false
          }).then(function(dismiss) {
            if (dismiss.dismiss !== 'cancel')
            {
                var response = tournament_service.removeCourt(court.id);
                if(response.success == "true")
                {
                    topnode.remove();
                }
            }
          })
    },

    addTournamentStateHTML: function(tsData, teams) {
        var templateTState = $("#templateTState").clone();
        $(templateTState).attr("id", 'tstate_' + tsData.id);
        $(templateTState).attr('obj_id', tsData.id);
        $(templateTState).attr('data-obj', JSON.stringify(tsData));
        $(templateTState).removeAttr('hidden');
        var ch = $(templateTState).find('#templateTState_link_games').val();
        
        $(templateTState).find("#templateTState_link_games").attr("id", 'templateTState_link_games_' + tsData.id);
        $(templateTState).find("#templateTState_link_teams").attr("id", 'templateTState_link_teams_' + tsData.id);
        $(templateTState).find("#templateTState_link_trans").attr("id", 'templateTState_link_trans_' + tsData.id);
        $(templateTState).find("#templateTState_link_basic").attr("id", 'templateTState_link_basic_' + tsData.id);

        $(templateTState).find("#templateTState_tab_overview").attr("href", '#templateTState_link_overview_' + tsData.id);
        $(templateTState).find("#templateTState_tab_teams").attr("href", '#templateTState_link_teams_' + tsData.id);
        $(templateTState).find("#templateTState_tab_trans").attr("href", '#templateTState_link_trans_' + tsData.id);
        $(templateTState).find("#templateTState_tab_basic").attr("href", '#templateTState_link_basic_' + tsData.id);
        //$(templateTState).find("#templateTState_btnUpdate").click(function(){ bh.updateCourt_Click($(this)); });
        //$(templateTState).find("#templateTState_btnRemove").click(function(){ bh.removeCourt_Click($(this)); });
        //$(templateTState).find(".card-category").text(tsData.number);
        
        $(templateTState).find("#templateTState_table_overview").attr("id", 'templateTState_table_overview_' + tsData.id);
        $(templateTState).find("#templateTState_table_teams").attr("id", 'templateTState_table_teams_' + tsData.id);
        
        

        for ( var i = 0, l = tsData.tstats.length; i < l; i++ ) {
            var tstat = tsData.tstats[ i ];
            var listitems = '';
            $.each(teams, function(key, value){
                if(tstat.team_name === value.name)
                {listitems += '<option selected="selected" value=' + key + '>' + value.name + '</option>';}
                else
                {listitems += '<option value=' + key + '>' + value.name + '</option>';}
            });
            markup = '<tr><td class="text-center">' + tstat.rank + '</td><td>' + tstat.team_name + "</td></tr>";
            //markup = '<tr><td class="text-center">' + tstat.rank + '</td><td><select class="selectpicker" data-style="select-with-transition" title="Choose Team" data-size="7">' + listitems + "</select></td></tr>";
            $(templateTState).find("#templateTState_table_teams_"  + tsData.id).append(markup);
            markup_overview = '<tr><td class="text-center">' + tstat.rank + '</td><td>' + tstat.team_name + "</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>";
            $(templateTState).find("#templateTState_table_overview_"  + tsData.id).append(markup_overview);
        }

        $(templateTState).find(".card-title").text(tsData.name);
        if(tsData.tournament_state_type  === "GROUP_STAGE")
        {
            $("#tstate_table_gs").append(templateTState);
        }
        else if (tsData.tournament_state_type  === "MAIN_ROUND")
        {
            $("#tstate_table_int").append(templateTState);
        }
        else if (tsData.tournament_state_type  === "FINAL")
        {
            $("#tstate_table_final").append(templateTState);
        }
        
        return;
    },
}
