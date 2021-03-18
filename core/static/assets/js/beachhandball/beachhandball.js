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
}
