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

    wzUpdateStructure: function(){ 
        wzNumOfGames = 0;
        bh.wzCalcGroups("wz-ovw-groups");
        bh.wzCalcKnockout('wz-ovw-knockout');
        bh.wzCalcPlacement('wz-ovw-placement');
        bh.wzCalcFinals('wz-ovw-finals');
        wzNumOfGames = wzNumOfGamesGroup + wzNumOfGamesKO + wzNumOfGamesPlacement + wzNumOfGamesFinal;
        $('#wz-res_num_of_games_total').val(wzNumOfGames);
    },

    wzCalcGroups: function(idRow){ 
        console.log("wzCalcGroups: " + idRow);
        wzNumOfGamesGroup = 0;
        var row = document.getElementById(idRow);
        $(row).empty();
        var num_teams = $("#wz-max_num_teams").val();
        var num_groups = $("#wz-num_of_groups").val();

        var teams_per_group = Math.floor(num_teams / num_groups);
        var num_teams_res = num_teams % num_groups;
        //var teams_per_group = $("#wz-teams_per_groups").val();
        //var teams_next_stage = $("#wz-num_teams_group_next_stage").val();
        
        var sel_val = $("#wz-sel-teams-knockout").val();
        document.getElementById("wz-num_of_groups").max = sel_val;
        var teams_next_stage_residue = sel_val % num_groups;
        var teams_next_stage = Math.floor(sel_val / num_groups);
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
        

        
        console.log("wzCalcGroups: #groups:" + num_groups + " teams p gr: " + teams_per_group);
        for (let i = 0; i < num_groups; i++) {
            var GameCounter = 0;
            var templateGroup = $("#templateGroup").clone();
            $(templateGroup).attr("id", 'group_' + i);
            $(templateGroup).removeAttr('hidden');
            $(templateGroup).find("#templateGroup_name").text('Group ' + (i+1));

            var body = $(templateGroup).find("#templateGroup_body");
            body.empty();
            var addedResidue = false;
            for (let iTeam = 0; iTeam < teams_per_group; iTeam++) {
                var tTeamItem = $("#templateTeamItem").clone();
                $(tTeamItem).attr("id", 'teamitem_' + i + '_' + iTeam);
                $(tTeamItem).removeAttr('hidden');
                
                if( iTeam < teams_next_stage)
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
                
                $(tTeamItem).find("#templateTeamItem_name").text((iTeam+1) + '. TeamDummy');
                body.append(tTeamItem);
                GameCounter++;
            }
            if(num_teams_res > 0)
            {
                var tTeamItem = $("#templateTeamItem").clone();
                $(tTeamItem).attr("id", 'teamitem_' + (teams_per_group+1));
                $(tTeamItem).removeAttr('hidden');
                if( teams_per_group < teams_next_stage)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                }
                else
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('clear');
                }
                
                $(tTeamItem).find("#templateTeamItem_name").text((teams_per_group+1) + '. TeamDummy');
                body.append(tTeamItem);
                GameCounter++;
                num_teams_res--;
            }
            GameCounter--;
            wzNumOfGamesGroup += (GameCounter*(GameCounter+1)/2);
            $(row).append(templateGroup);
        }
        $('#wz-res_num_of_games_group').val(wzNumOfGamesGroup);
    },

    wzCalcPlacement: function(idRow){
        console.log("wzCalcPlacement: " + idRow);
        wzNumOfGamesPlacement = 0;
        var row = document.getElementById(idRow);
        $(row).empty();
        var num_teams_soll = $("#wz-sel-teams-knockout").val();
        var num_teams_getting_ranked = $("#wz-sel-teams-getting-ranked").val();
        var levels = (Math.log(num_teams_soll) / Math.log(2)) - 1; // -1 because final is seperated by
        var levels_ranked = (Math.log(num_teams_getting_ranked) / Math.log(2)) - 1;
        for(let i = levels_ranked; i >= 1; i--)
        {
            var tLevel= $("#templatePL_level").clone();
            $(tLevel).attr("id", 'level_' + i);
            $(tLevel).removeAttr('hidden');
            var bestRankWinner = Math.pow(2, i-1) + 1;
            var width = 3;
            var offset = 0;
            var actNaming = PLACEMENT_NAMES[Math.pow(2, i)] + ' ';
            var lastNaming = KNOCKOUT_NAMES[Math.pow(2, i+1)] + ' ';
            $(tLevel).find("#templatePL_header").text('Placement for rank ' + (Math.pow(2, i)+1) + ' to ' + ((2*Math.pow(2, i))));
            var tLevel_items = $("#templatePL_items").clone();
            $(tLevel_items).removeAttr('hidden');
            $(tLevel_items).attr("id", 'level_items_' + i);
            for(var j = 1; j <= Math.pow(2, i-1); j++)
            {
                var templateGroup = $("#templateGroup").clone();
                $(templateGroup).attr("id", 'pl_group_' + j);
                $(templateGroup).removeAttr('hidden');
                $(templateGroup).find("#templateGroup_name").text(actNaming + j);
                $(templateGroup).attr("class", 'col-md-' + width + ' offset-md-' + offset);
                var body = $(templateGroup).find("#templateGroup_body");
                body.empty();
                for (let iTeam = 0; iTeam < 2; iTeam++) {
                    var tTeamItem = $("#templateTeamItem").clone();
                    $(tTeamItem).attr("id", 'pl_teamitem_' + j + '_' + iTeam);
                    $(tTeamItem).removeAttr('hidden');
                    var NameExtension = '. Loser ' + lastNaming + '' + ((j-1)*2 + iTeam + 1);
                    if(lastNaming == '')
                    {
                        NameExtension = '. TeamDummy';
                    }
                    if( iTeam == 0 && Math.pow(2, i-1) > 1)
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                    }
                    else if(Math.pow(2, i-1) > 1)
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").text('clear');
                    }
                    else if(Math.pow(2, i-1) == 1)
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").attr('hidden', 'hidden');
                        $(tTeamItem).find("#templateTeamItem_rank").text((bestRankWinner+1+iTeam)+'.');
                        $(tTeamItem).find("#templateTeamItem_rank").removeAttr('hidden');
                    }
                    
                    $(tTeamItem).find("#templateTeamItem_name").text((iTeam+1) + NameExtension);
                    body.append(tTeamItem);
                }
                $(tLevel_items).append(templateGroup);
                wzNumOfGamesPlacement++;
            }
            $(tLevel).find("#templatePL_body").append(tLevel_items);
            bh.wzCalcPlacementLevel($(tLevel).find("#templatePL_body"), i, Math.pow(2, i), actNaming);
            $(row).append(tLevel);
        }
        
        $('#wz-res_num_of_games_placement').val(wzNumOfGamesPlacement);
    },

    wzCalcPlacementLevel(bodyLevel, levels, bestRankWinner, namingParent){
        if(levels == 1)
            return;

        var width = 3;
        var offset = 0;
        if(levels <= 3)
        {
            width = 5;
            offset = 1;
        }
        //var bestRankWinner = Math.pow(2, levels);
        var bestRankLoser= (bestRankWinner+Math.pow(2, levels-1));
        var subLevel = Math.pow(2, levels-2);

        if(true)
        {
            // Losing part
            var tLoser= $("#templatePLsub_level").clone();
            $(tLoser).attr("id", 'level_l_' + bestRankLoser);
            $(tLoser).removeAttr('hidden');
            $(tLoser).find("#templatePLsub_header").text('Placement for rank ' + (bestRankLoser+1) +' to ' + (bestRankLoser+Math.pow(2, levels-1)));
            var tLoser_items = $(tLoser).find("#templatePLsub_items");
            var actNamingLoser = 'P' + (bestRankLoser+1) + 'to' + (bestRankLoser+Math.pow(2, levels-1)) + ' ';
            for(var j = 1; j <= subLevel; j++)
            {
                var templateGroup = $("#templateGroup").clone();
                $(templateGroup).attr("id", 'pl_level_l_' + levels + '_' + j);
                $(templateGroup).removeAttr('hidden');
                $(templateGroup).find("#templateGroup_name").text(actNamingLoser + j);
                $(templateGroup).attr("class", 'col-md-' + width + ' offset-md-' + offset);
                var body = $(templateGroup).find("#templateGroup_body");
                body.empty();
                for (let iTeam = 0; iTeam < 2; iTeam++) {
                    var tTeamItem = $("#templateTeamItem").clone();
                    $(tTeamItem).attr("id", 'pl_level_teamitem_l_' + j + '_' + iTeam);
                    $(tTeamItem).removeAttr('hidden');
                    var NameExtension = '. Loser ' + namingParent + '' + ((j-1)*2 + iTeam + 1);
                    
                    if( iTeam == 0 && subLevel > 1)
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                    }
                    else if(subLevel > 1)
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").text('clear');
                    }
                    else if(subLevel == 1)
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").attr('hidden', 'hidden');
                        $(tTeamItem).find("#templateTeamItem_rank").text((bestRankLoser+1+iTeam)+'.');
                        $(tTeamItem).find("#templateTeamItem_rank").removeAttr('hidden');
                    }
                    
                    $(tTeamItem).find("#templateTeamItem_name").text((iTeam+1) + NameExtension);
                    body.append(tTeamItem);
                }
                $(tLoser_items).append(templateGroup);
                wzNumOfGamesPlacement++;
            }
            bodyLevel.append(tLoser);
            bh.wzCalcPlacementLevel(bodyLevel, subLevel, bestRankLoser, actNamingLoser);
        }

        // Winning part
        var tWinning= $("#templatePLsub_level").clone();
        $(tWinning).attr("id", 'level_w_' + bestRankWinner);
        $(tWinning).removeAttr('hidden');
        $(tWinning).find("#templatePLsub_header").text('Placement for rank ' + (bestRankWinner+1) +' to ' + (bestRankWinner+Math.pow(2, levels-1)));
        var tWinning_items = $(tWinning).find("#templatePLsub_items");
        var actNaming = 'P' + (bestRankWinner+1) + 'to' + (bestRankWinner+Math.pow(2, levels-1)) + ' ';
        var lastNaming = '';
        
        for(var j = 1; j <= subLevel; j++)
        {
            var templateGroup = $("#templateGroup").clone();
            $(templateGroup).attr("id", 'pl_level_w_' + levels + '_' + j);
            $(templateGroup).removeAttr('hidden');
            $(templateGroup).find("#templateGroup_name").text(actNaming + j);
            $(templateGroup).attr("class", 'col-md-' + width + ' offset-md-' + offset);
            var body = $(templateGroup).find("#templateGroup_body");
            body.empty();
            for (let iTeam = 0; iTeam < 2; iTeam++) {
                var tTeamItem = $("#templateTeamItem").clone();
                $(tTeamItem).attr("id", 'pl_level_teamitem_' + j + '_' + iTeam);
                $(tTeamItem).removeAttr('hidden');
                var NameExtension = '. Winner ' + namingParent + '' + ((j-1)*2 + iTeam + 1);
                
                if( iTeam == 0 && subLevel > 1)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                }
                else if(subLevel > 1)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").text('clear');
                }
                else if(subLevel == 1)
                {
                    $(tTeamItem).find("#templateTeamItem_icon").attr('hidden', 'hidden');
                    $(tTeamItem).find("#templateTeamItem_rank").text((bestRankWinner+1+iTeam)+'.');
                    $(tTeamItem).find("#templateTeamItem_rank").removeAttr('hidden');
                }
                
                $(tTeamItem).find("#templateTeamItem_name").text((iTeam+1) + NameExtension);
                body.append(tTeamItem);
            }
            $(tWinning_items).append(templateGroup);
            wzNumOfGamesPlacement++;
        }
        bodyLevel.append(tWinning);

        

        bh.wzCalcPlacementLevel(bodyLevel, levels-1, bestRankWinner, actNaming);

    },

    wzCalcFinals: function(idRow) {
        console.log("wzCalcFinals: " + idRow);
        wzNumOfGamesFinal = 0;
        var row = document.getElementById(idRow);
        $(row).empty();

        var num_teams_soll = $("#wz-sel-teams-knockout").val();
        var levels = (Math.log(num_teams_soll) / Math.log(2));

        var width = 3;
        var offset = 0;
        var templateGroup = $("#templateGroup").clone();
        $(templateGroup).attr("id", 'f_group_1');
        $(templateGroup).removeAttr('hidden');
        $(templateGroup).find("#templateGroup_name").text('F');
        $(templateGroup).attr("class", 'col-md-' + width + ' offset-md-' + offset);
        var body = $(templateGroup).find("#templateGroup_body");
        body.empty();
        for (let iTeam = 0; iTeam < 2; iTeam++) {
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
            
            $(tTeamItem).find("#templateTeamItem_name").text(tempName);
            body.append(tTeamItem);
        }
        $(row).append(templateGroup);
        wzNumOfGamesFinal++;
        $('#wz-res_num_of_games_final').val(wzNumOfGamesFinal);
    },

    wzCalcKnockout: function(idRow){
        console.log("wzCalcKnockout: " + idRow);
        wzNumOfGamesKO = 0;
        var row = document.getElementById(idRow);
        $(row).empty();
        var num_teams = $("#wz-num_teams_group_next_stage").val();
        var num_teams_soll = $("#wz-sel-teams-knockout").val();
        var levels = (Math.log(num_teams_soll) / Math.log(2)); // -1 because final is seperated by
        var actNaming = '';
        var lastNaming = '';
        for(let i = levels; i > 1; i--)
        {
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
            var actNaming = KNOCKOUT_NAMES[Math.pow(2, i)] + ' ';
            $(tLevel).find("#templateKO_header").text(header);
            var tLevel_items = $(tLevel).find("#templateKO_items");
            for(var j = 1; j <= Math.pow(2, i-1); j++)
            {
                var templateGroup = $("#templateGroup").clone();
                $(templateGroup).attr("id", 'ko_group_' + j);
                $(templateGroup).removeAttr('hidden');
                $(templateGroup).find("#templateGroup_name").text(actNaming + j);
                $(templateGroup).attr("class", 'col-md-' + width + ' offset-md-' + offset);
                var body = $(templateGroup).find("#templateGroup_body");
                body.empty();
                for (let iTeam = 0; iTeam < 2; iTeam++) {
                    var tTeamItem = $("#templateTeamItem").clone();
                    $(tTeamItem).attr("id", 'ko_teamitem_' + j + '_' + iTeam);
                    $(tTeamItem).removeAttr('hidden');
                    var NameExtension = '. Winner ' + lastNaming + '' + ((j-1)*2 + iTeam + 1);
                    if(lastNaming == '')
                    {
                        NameExtension = '. TeamDummy';
                    }
                    if( iTeam == 0)
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").text('arrow_upward');
                    }
                    else
                    {
                        $(tTeamItem).find("#templateTeamItem_icon").text('clear');
                    }
                    
                    $(tTeamItem).find("#templateTeamItem_name").text((iTeam+1) + NameExtension);
                    body.append(tTeamItem);
                }
                $(tLevel_items).append(templateGroup);
                wzNumOfGamesKO++;
            }
            $(row).append(tLevel);
            lastNaming = actNaming;
        }
        $('#wz-res_num_of_games_ko').val(wzNumOfGamesKO);
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
