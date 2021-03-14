endpoint = "https://www.boredapi.com/api/activity";

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
    },

    postCourt: function(data) {
        console.debug("postCourt");
        data.id = 123;
        var result = { 
            answer : "DONE",
            court : data,
            success: "true"
        };
        return result;
        
    }
}