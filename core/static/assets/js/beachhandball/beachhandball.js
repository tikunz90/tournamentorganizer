$(document).ready(function() {
console.log("bh document ready");
    $("#bhAddCourtForm_OK").click(function(){ bh.addCourt_Click(); });
});

bh_gui = {
    
}

bh = {
    misc: {
      test_mode_active: 1,
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
