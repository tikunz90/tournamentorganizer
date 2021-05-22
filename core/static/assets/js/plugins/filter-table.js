(function ($) {

  $.fn.filterTable = function ( id ) {

    if (!id) {
      console.error('You must provide filter input ID in options!');
      return null;
    }

    // var settings = $.extend({
    //   // These are the defaults.
    //   id: ''
    // }, options );

    var filterID = id;
    var table = $(this);
    
    $(filterID).on("keyup", function() {
      var value = $(this).val().toUpperCase();
      var filter_obj = {'col': '__all__', 'filter': value};
      try {
        filter_obj = JSON.parse( $(this).val() );
      }
      catch(e)
      {
        console.error(e);
      }
      var filters = filter_obj.filter.split("§");
      filters = filters.map(function(x){ return x.toUpperCase(); });
      //var filter_obj = JSON.parse( '{ "col": "__all__", "filter": "SuperStars" }' );
      var col_idx = [];

      table.find('tr').each(function(index) {

        $row = $(this);
        // skip the headers from search
        if ($row.find("th").length > 0 && filter_obj.col.indexOf('__all__') > -1) { 
          $row.find("th").each(function(ii, th) {
            col_idx.push(ii);
          });
          return; 
        }
        else if ($row.find("th").length > 0 && filter_obj.col.indexOf('__all__') == -1)  {
          $row.find("th").each(function(ii, th) {
            $cell = $(th).text().toUpperCase();
            if ($cell.indexOf(filter_obj.col.toUpperCase()) > -1) {  
              col_idx.push(ii);
            }
          });
          return;
        }
        let bool = false;

        $row.find("td").each(function(ii, td) {
          //console.debug(td);
          $cell = $(td).data("content").toString().toUpperCase();
          if (col_idx.includes(ii) && filters.includes($cell)) {  
              bool = true;
          }
          //if (value.indexOf($cell) > -1){
          //  bool = true;
          //}
        });

        if (bool) {  
          $row.show();
        }
        else {
          $row.hide();
        }
      }); // table each

    }); // search keyup

    return this;
  }

})(jQuery)