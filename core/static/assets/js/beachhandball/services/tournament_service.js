tournament_service = 
{
    alarmFunc: function() {
        alert("FUNC");
      },

    getCourts: function() {
        var text = '{ "courts" : [' +
'{ "name":"Center" , "number":"1" },' +
'{ "name":"Court 2" , "number":"2" },' +
'{ "name":"Court 3" , "number":"3" } ]}'; 
        return JSON.parse(text).courts;
    }
}