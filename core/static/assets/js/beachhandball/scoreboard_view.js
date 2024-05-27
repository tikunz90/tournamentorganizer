var clientMqtt;
var mqtt_interval;
var topicNameBase = "beach_livescore";
var topicName = "";
var isConnected = false;

var start_time;
var elapsed_time;
var remaining_time;
var isRunning = false;
var hours = 0;
var minutes = 0;
var seconds = 0;
var milliseconds = 0;
var display_time = 0;
var display_time_str = "";
var stopwatch_interval;
var stopwatch_direction = -1; // 1 for counting up, -1 for counting down
var paused_time = 0;
var paused_timedelta = 0;
var max_time = 600000; // 10 minutes in milliseconds

var active_halftime = 3; // 1=ht1, 2 = ht2, 3 = penalty
var gameMode = 1; // 

var act_time = 0;
var teama_name = "A";
var score_teama_ht1 = 0;
var score_teama_ht2 = 0;
var score_teama_p = 0;
var score_teama_total = 0;

var teamb_name = "A";
var score_teamb_ht1 = 0;
var score_teamb_ht2 = 0;
var score_teamb_p = 0;
var score_teamb_total = 0;


// attach an event listener to the "load" event of the window object
window.addEventListener("load", function() {
    // your code here
    console.log("scoreboard loaded...");
    connectMqtt();
  });

function connectMqtt() {
    var headerTournId = document.getElementById('tournament_id');
    var headerCourtId = document.getElementById('court_id');
    var headerGameId = document.getElementById('game_id');
    topicName = topicNameBase + "/tournament_" + headerTournId.textContent + "/court_" + headerCourtId.textContent + "/";
    
    var urlParams = new URLSearchParams(window.location.search);
    // Get the value of the "myparam" parameter
    var passedTopicName = urlParams.get('court');

    if(passedTopicName != null)
    {
        topicName = topicNameBase + "/" + passedTopicName + "/";
    }
    
    console.log("Topic: " + topicName);
    var headerMqttBroker = document.getElementById('mqtt_broker');
    var headerMqttPort = document.getElementById('mqtt_port');

    var useSSL = false;
    var portNumber = 8082;
    if (location.protocol == 'https:') {
        console.log("https: ");
        useSSL = true;
        portNumber = 8083;
    }

    console.log("Mqtt: " + headerMqttBroker.textContent + ":" + portNumber);
    let uniqueId = Date.now().toString(36) + Math.random().toString(36).substring(2);
    clientMqtt = new Paho.MQTT.Client(headerMqttBroker.textContent, portNumber, "livescore_display_beach_" + uniqueId); 
    
    var options = {
        useSSL: useSSL,
        userName: "tim",
        password: "qs12fhw5",
        onSuccess: onConnectSuccess
    };
    clientMqtt.connect(options);

    clientMqtt.onConnectionLost = onConnectionLost;
    clientMqtt.onMessageArrived = onMessageArrived;
}

function onConnectSuccess(context) {
    console.log("mqtt connected...");
    isConnected = true;
    clientMqtt.send(topicName, "Hello");  // Replace "topic" with the topic you want to publish the message to
    clientMqtt.subscribe(topicName);

    update_score_display();
}

function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
      console.log("onConnectionLost:"+responseObject.errorMessage);
      isConnected = false;
    }
}

function onMessageArrived(message) {
    console.log("onMessageArrived:"+message.payloadString);
    var data;
    try {
    data = JSON.parse(message.payloadString);
    } catch (e) {
    console.error("Error parsing JSON: " + e);
    return;
    }
    if (data) {
        //document.getElementById('command').textContent = data['command'];

        paused_timedelta = data['paused_timedelta'];
        if(data['command'] == 'start')
        {
            gameMode = data['gameMode'];
            active_halftime = data['active_halftime'];
            paused_time = data['paused_time'];
            start_time = data['start_time'];
            start_stopwatch();
            isRunning = true;
        }
        else if(data['command'] == 'pause')
        {
            gameMode = data['gameMode'];
            active_halftime = data['active_halftime'];
            pause_stopwatch();
            isRunning = false;
            paused_time = data['paused_time'];
        }
        else if(data['command'] == 'reset')
        {
            gameMode = data['gameMode'];
            active_halftime = data['active_halftime'];
            reset_stopwatch();
            isRunning = false;
        }
        else if(data['command'] == 'score')
        {
            act_time = data['act_time'];
            update_stopwatch_display2()
            active_halftime = data['gamingstate'];
            score_teama_ht1 = data['score_team_a_halftime_1'];
            score_teama_ht2 = data['score_team_a_halftime_2'];
            score_teama_p = data['score_team_a_penalty'];
            score_teama_total = data['score_teama_total'];
            score_teamb_ht1 = data['score_team_b_halftime_1'];
            score_teamb_ht2 = data['score_team_b_halftime_2'];
            score_teamb_p = data['score_team_b_penalty'];
            score_teamb_total = data['score_teamb_total'];
            update_score_display();
            teama_name = data['team_a']['name']
            teamb_name = data['team_b']['name']
            update_game_display();
            return;
        }
        else if(data['command'] == 'active_halftime')
        {
            active_halftime = data['active_halftime'];
            update_score_display();
            return;
        }
        
        //elapsed_time = data['elapsed_time'];
        //remaining_time = data['remaining_time'];
        //stopwatch_interval = data['stopwatch_interval'];
        stopwatch_direction = data['stopwatch_direction'];
        
        
        max_time = data['duration_of_halftime'] * 1000;

        update_stopwatch_display();
    }
    else
    {
        document.getElementById('command').textContent = message.payloadString;
    }
}

function update_stopwatch_display() {
    var current_time = new Date().getTime();
    elapsed_time = current_time - start_time - paused_timedelta;
    remaining_time = max_time - elapsed_time;
    if (stopwatch_direction == 1) {
        display_time = elapsed_time;
        if(gameMode == 0) {
            display_time = display_time + (active_halftime - 1) * max_time;
        }
    } else {
        display_time = Math.max(0, max_time - elapsed_time);
    }
    
    hours = Math.floor(display_time / 3600000);
    minutes = Math.floor((display_time % 3600000) / 60000);
    seconds = Math.floor((display_time % 60000) / 1000);
    milliseconds = display_time % 1000;
    display_time_str = ('0' + minutes).slice(-2) + ':' + ('0' + seconds).slice(-2);// + '.' + ('00' + milliseconds).slice(-3);
    var labelStopwatch = document.getElementById('stopwatch');
    labelStopwatch.textContent = display_time_str;
    // Check if max_time has elapsed
    if (remaining_time == 0) {
        stop_stopwatch();
    }
}

function update_stopwatch_display2() {
    
    hours = Math.floor(act_time / 3600);
    minutes = Math.floor((act_time % 3600) / 60);
    seconds = Math.floor((act_time % 60));
    milliseconds = act_time % 1000;
    display_time_str = ('0' + minutes).slice(-2) + ':' + ('0' + seconds).slice(-2);// + '.' + ('00' + milliseconds).slice(-3);
    var labelStopwatch = document.getElementById('stopwatch');
    labelStopwatch.textContent = display_time_str;
}

function stop_stopwatch() {
    clearInterval(stopwatch_interval);
}

function start_stopwatch() {

    stopwatch_interval = setInterval(update_stopwatch_display, 25);
}

function pause_stopwatch() {
    clearInterval(stopwatch_interval);
    //paused_time = new Date().getTime();
}


function reset_stopwatch() {
    clearInterval(stopwatch_interval);
    paused_time = 0;
    paused_timedelta = 0;
    current_time = 0;
    elapsed_time = 0;
    if (stopwatch_direction == 1) {
        start_time = new Date().getTime();
    } else {
        start_time = new Date().getTime();
    }
    
    update_stopwatch_display();
}

function update_game_display() {
    var lblA_Name = document.getElementById("team_1");
    var lblB_Name = document.getElementById("team_2");

    lblA_Name.textContent = teama_name;
    lblB_Name.textContent = teamb_name;
}

function update_score_display() {
    var lblScoreA_H1 = document.getElementById("team_a_score_ht1");
    var lblScoreA_H2 = document.getElementById("team_a_score_ht2");
    var lblScoreA_P = document.getElementById("team_a_score_p");
    var lblScoreA_TOT = document.getElementById("team_a_score_total");

    var lblScoreB_H1 = document.getElementById("team_b_score_ht1");
    var lblScoreB_H2 = document.getElementById("team_b_score_ht2");
    var lblScoreB_P = document.getElementById("team_b_score_p");
    var lblScoreB_TOT = document.getElementById("team_b_score_total");

    var lblMoment = document.getElementById("moment");
    var lblHeader = document.getElementById("header");
    lblHeader.style.visibility = "hidden";
    var lblHalftime = document.getElementById("halftime");

    lblMoment.textContent = active_halftime;
    if(gameMode == 1 && active_halftime == 3) {
        lblMoment.textContent = "P";
        lblHeader.textContent = "SHOOTOUT";
        lblHeader.style.visibility = "visible";
        if (lblHalftime.classList.contains('boxovertimeoff')) {
            lblHalftime.classList.remove('boxovertimeoff');
            lblHalftime.classList.add('boxovertimeon');
        }
    }
    else if(gameMode == 1 && active_halftime < 3) {
        if (lblHalftime.classList.contains('boxovertimeon')) {
            lblHalftime.classList.remove('boxovertimeon');
            lblHalftime.classList.add('boxovertimeoff');
        }
    }


    lblScoreA_H1.textContent = score_teama_ht1;
    lblScoreA_H2.textContent = score_teama_ht2;
    lblScoreA_P.textContent = score_teama_p;
    lblScoreA_TOT.textContent = score_teama_total;

    lblScoreB_H1.textContent = score_teamb_ht1;
    lblScoreB_H2.textContent = score_teamb_ht2;
    lblScoreB_P.textContent = score_teamb_p;
    lblScoreB_TOT.textContent = score_teamb_total;

}
