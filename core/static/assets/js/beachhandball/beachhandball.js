$(document).ready(function() {
console.log("bh document ready");
    $("#bhAddCourtForm_OK").click(function(){ bh.addCourt_Click(); });
});

bh = {
    misc: {
      navbar_menu_visible: 0,
      active_collapse: true,
      disabled_collapse_init: 0,
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

            var response = tournament_service.postCourt(data);

            // ONLY FOR TESTING
            if(data.number == 777)
            {
                response.success = 'false';
            }
            
            // Hide modal frame
            var modal = document.getElementById("bhAddCourtModal");
            $(modal).modal('toggle');

            // evaluate server request and set notification
            var message = "";
            var message_type = 'success';
            if(response.success == "true")
            {
                message = `Created court ${data.name}`;
                bh.addCourtHTML(response.court);
            }
            else
            {
                message = "Creating court failed! Try again...";
                message_type = 'danger';
            }
            md.showNotification('bottom','center', message, message_type);
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
        $(templateCourt).removeAttr('hidden');
        
        $(templateCourt).find(".card-category").text(courtData.number);
        $(templateCourt).find(".card-title").text(courtData.name);
        $("#court_table").append(templateCourt);
        return;
        //console.log(JSON.stringify( tournament_service.getCourts()));
        console.log("addCourtHTML()" + courtData);
    var title = courtData.name;
    var category = courtData.number;
    var court_table = document.getElementById("court_table");
    var d = document.createElement('div');
    var card = document.createElement('div');
    var card_header = document.createElement('div');
    var card_icon = document.createElement('div');
    var card_footer = document.createElement('div');
    $(d).addClass("col-md-3");   
    $(card).addClass("card card-stats");

    //Header
    $(card_header).addClass("card-header card-header- card-header-icon");
    $(card_icon).addClass("card-icon").html('<i class="material-icons">view_array</i>');
    
    var card_cat = document.createElement('h4');
    $(card_cat).addClass("card-category");
    card_cat.innerHTML = category;
    var card_title = document.createElement('h3');
    $(card_title).addClass("card-title");
    card_title.innerHTML = title;

    card_header.appendChild(card_icon);
    card_header.appendChild(card_cat);
    card_header.appendChild(card_title);

    // footer
    $(card_footer).addClass("card-footer");
    var card_footer_stats = document.createElement('div');
    $(card_footer_stats).addClass("stats").html('<i class="material-icons">groups</i><a href="#">1500 spectators...</a>');
    card_footer.appendChild(card_footer_stats);

    // add child

    card.appendChild(card_header);
    card.appendChild(card_footer);
    d.appendChild(card);
    court_table.appendChild(d);
    //var newdiv = document.createElement("div");
    //court_table.append(document.parseHTML("<div id='dynamic'>HUHU</div>"));

    tournament_service.getCourts().forEach(element => {console.log(element.name)});
    md.showNotification('bottom','center', "Court created", 'success');
       
    },
}