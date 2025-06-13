var clientMqtt;
var mqtt_interval;
var topicNameBase = "beach_livescore";
var topicLedWallNameBase = "led_wall";
var topicName = "";
var topicLedWallName = "";
var topicLedWallError = "";
var isConnected = false;



// attach an event listener to the "load" event of the window object
window.addEventListener("load", function() {
    // your code here
    console.log("ledwall loaded...");
    connectMqtt();

    var commandButtons = document.querySelectorAll(".command-button");

    commandButtons.forEach(function(button) {
      button.addEventListener("click", function() {
        // Get the table element
        var command = this.getAttribute("data-command").toString();
        var content = this.getAttribute("data-content").toString();

        let payload = {
            command: command,
            content: content
        }

        console.log("Button Click: send "+ command + " " + content);
        clientMqtt.send(topicLedWallName, JSON.stringify(payload));
      });
    });

  });


function onMessageArrived(message) {
    //console.log("onMessageArrived:"+message.payloadString);
    var data;
    try {
    data = JSON.parse(message.payloadString);
    } catch (e) {
    console.error("Error parsing JSON: " + e);
    return;
    }
    if (data) {       
    }
}

function connectMqtt() {
    console.log("connect mqtt...");
    var headerTournId = document.getElementById('tournament_id');
    var headerCourtId = document.getElementById('court_id');
    var headerGameId = document.getElementById('game_id');
    //topicName = topicNameBase + "/tournament_" + headerTournId.textContent + "/court_" + headerCourtId.textContent + "/";
    topicName = topicNameBase + "/court_" + headerCourtId.textContent + "/";
   // topicLedWallName = topicLedWallNameBase + "/tournament_" + headerTournId.textContent + "/court_" + headerCourtId.textContent + "/";
    topicLedWallName = topicLedWallNameBase + "/court_" + headerCourtId.textContent + "/";
    topicLedWallError = topicLedWallNameBase + "/error/";
    
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
    clientMqtt = new Paho.MQTT.Client(headerMqttBroker.textContent, portNumber, "/ws", "led_control_" + uniqueId); 
    
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
    clientMqtt.send(topicLedWallName, "Hello");
    clientMqtt.subscribe(topicName);
}

function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
      console.log("onConnectionLost:"+responseObject.errorMessage);
      isConnected = false;
    }
}


