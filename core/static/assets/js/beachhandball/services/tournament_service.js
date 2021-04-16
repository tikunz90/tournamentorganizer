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
        
    },

    misc: {
        test_mode_active: 1,
      },
  
      mockData: {
          courts: [ { id: 1, created_at: "2020.10.10 10:11:12", name: "Center Court", number: 1},
          { id: 2, created_at: "2020.10.10 10:11:12", name: "Court", number: 2},
          { id: 3, created_at: "2020.10.10 10:11:12", name: "Court3", number: 3}]
      },

      saveMockData: function() {
        localStorage['mockData'] = JSON.stringify(tournament_service.mockData);
      },

      loadMockData: function() {
        tournament_service.mockData = JSON.parse(localStorage['mockData']);
      },
  
      getCourts: function() {
          if(tournament_service.misc.test_mode_active == 0)
          {
              return tournament_service.mockData.courts;
          }
          else
          {   
            tournament_service.loadMockData();
              var response = { message: "Get all courts" , data: JSON.parse(JSON.stringify(tournament_service.mockData.courts)), message_type: "success", success: "true"}
              return response;
          }
      },
      
      getCourt: function(id) {
          if(tournament_service.misc.test_mode_active == 0)
          {
              return tournament_service.mockData.courts.filter(court => { return court.id === id});
          }
          else
          {   
            tournament_service.loadMockData();
            var response = "";
            var court = tournament_service.mockData.courts.filter(court => { return court.id === id})
            if(court.length == 1)
                response = { message: "Get court " + id , data: JSON.parse(JSON.stringify(court[0])), message_type: "success", success: "true"}
            else
                response = { message: "Get court " + id , data: JSON.parse(JSON.stringify(court[0])), message_type: "danger", success: "false"}
            return response;
          }
      },
  
      createCourt: function(court_data) {
          if(tournament_service.misc.test_mode_active == 0)
          {
              return tournament_service.mockData.courts[0];
          }
          else
          {   
             tournament_service.loadMockData();
              var last = tournament_service.mockData.courts.slice(-1)[0];
              if( typeof last === 'undefined')
                last = { id: 0};
              court_data.id = last.id + 1;
              tournament_service.mockData.courts.push(court_data);
              tournament_service.saveMockData();
              var response = { message: `Created court ${court_data.name}` , data: JSON.parse(JSON.stringify(court_data)), message_type: "success", success: "true"}
              return response;
          }
      },
  
      updateCourt: function(court_data) {
          if(tournament_service.misc.test_mode_active == 0)
          {
              return tournament_service.mockData.courts[0];
          }
          else
          {  
            tournament_service.loadMockData(); 
              var last = tournament_service.mockData.courts.slice(-1)[0];
              court_data.id = last.id + 1;
              tournament_service.mockData.courts.push(court_data);
              var response = { message: "Court updated" , data: JSON.parse(JSON.stringify(court_data)), message_type: "success", success: "true"}
              tournament_service.saveMockData();
              return response;
          }
      },
  
      removeCourt: function(id) {
          if(tournament_service.misc.test_mode_active == 0)
          {
              return tournament_service.mockData.courts[0];
          }
          else
          {   
            tournament_service.loadMockData();
            tournament_service.mockData.courts = tournament_service.mockData.courts.filter(court => court.id != id);
            var response = { message: "Court removed" , data: {}, message_type: "success", success: "true"}
            tournament_service.saveMockData();
            return response;
          }
      },

      getData: function() {
        return $.ajax({
            type: 'GET',
            url: "/ajax/data/",
            async: false,
            dataType: 'json',
            done: function (data) {
              if (data) {
                console.debug(JSON.stringify(data));
                return data;
              }
            }
          });
      },
}