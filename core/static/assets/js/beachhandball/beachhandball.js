bh = {
    misc: {
      navbar_menu_visible: 0,
      active_collapse: true,
      disabled_collapse_init: 0,
    },
  
    addCourtHTML: function(courtData) {
      
        //console.log(JSON.stringify( tournament_service.getCourts()));
        console.log("addCourtHTML()");
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
    $(card_header).addClass("card-header card-header-warning card-header-icon");
    $(card_icon).addClass("card-icon").html('<i class="material-icons">weekend</i>');
    
    var card_cat = document.createElement('p');
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
    $(card_footer_stats).addClass("stats").html('<i class="material-icons">weekend</i><a href="#pablo">Get More Space...</a>');
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
       
      }
}