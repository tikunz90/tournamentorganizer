var clientMqtt;
var mqtt_interval;
var topicNameBase = "beach_livescore";
var topicLedWallNameBase = "led_wall";
var topicName = "";
topicLedWallName = "";
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

var active_halftime = 1; // 1=ht1, 2 = ht2, 3 = penalty
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

function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const timeString = `${hours}:${minutes}:${seconds}`;
    document.getElementById('clock').textContent = timeString;
}

setInterval(updateClock, 1000);
updateClock(); // Initial call to set the clock immediately


// attach an event listener to the "load" event of the window object
window.addEventListener("load", function() {
    // your code here
    console.log("ledwall loaded...");
    connectMqtt();

    showPage("info");

    setTimeout(() => {
        //document.querySelector('.logo-container').classList.add('hidden');
        //document.querySelector('.advertise-container').classList.add('hidden');
        //document.querySelector('.content').classList.add('visible');
    }, 500); // 5000 milliseconds = 5 seconds
  });

  var images = [
    "/static/assets/img/gbo_logo.png",
    "/static/assets/img/ball.png",
    "/static/assets/img/dhb_logo.png",
    "/static/assets/img/beachandthegang.png",
    // Add more image URLs as needed
  ];

  var currentImageIndex = -1;

// Function to get a random image index that is different from the current one
function getRandomImageIndex() {
  var newIndex;
  do {
    newIndex = Math.floor(Math.random() * images.length);
  } while (newIndex === currentImageIndex);
  return newIndex;
}

// Function to display a random image
function displayRandomImage() {
  var container = document.getElementById("image-container");
  var randomIndex = getRandomImageIndex();
  var randomImage = images[randomIndex];

  // Create new image element
  var newImage = new Image();
  newImage.src = randomImage;
  newImage.className = "fade";

  // Append new image to container
  container.innerHTML = '';
  container.appendChild(newImage);

  // After a short delay, fade in the new image
  setTimeout(function() {
    newImage.classList.add("active");
  }, 100); // Adjust as needed for transition timing

  // Update current image index
  currentImageIndex = randomIndex;
}
  

  displayRandomImage();

// Change the image every 2 seconds
setInterval(displayRandomImage, 4000);

// Show logo for 5 seconds, then transition to main content
//window.addEventListener('load', () => {
//    setTimeout(() => {
//        document.querySelector('.logo-container').classList.add('hidden');
//        document.querySelector('.advertise-container').classList.add('hidden');
//        document.querySelector('.content').classList.add('visible');
//
//        setTimeout(() => {
//            document.querySelector('.logo-container').classList.add('hidden');
//            document.querySelector('.content').classList.add('hidden');
//            document.querySelector('.advertise-container').classList.add('visible');
//        }, 5000);
//
//    }, 500); // 5000 milliseconds = 5 seconds
//});

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
        if(data['command'] == 'showPage')
        {
            showPage(data['content']);
        }
        
    }
}

function showPage(pagename){
    document.querySelectorAll('.imagecontainer').forEach(function(element) {
        element.classList.remove('visible');
    });
    document.querySelectorAll('.imagecontainer').forEach(function(element) {
        element.classList.add('hidden');
    });

    var selector = '[data-id="' + pagename + '"]';
    var element = document.querySelector(selector);
    if (element) {
        element.classList.remove('hidden');
        element.classList.add('visible');
    } else {
        console.log('The element with class '+ pagename +' does not exist.');
    }   
}
function connectMqtt() {
    console.log("connect mqtt...");
    var headerTournId = document.getElementById('tournament_id');
    var headerCourtId = document.getElementById('court_id');
    var headerGameId = document.getElementById('game_id');
    topicName = topicNameBase + "/tournament_" + headerTournId.textContent + "/court_" + headerCourtId.textContent + "/";
    topicLedWallName = topicLedWallNameBase + "/tournament_" + headerTournId.textContent + "/court_" + headerCourtId.textContent + "/";
    
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
    clientMqtt.subscribe(topicLedWallName);
}

function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
      console.log("onConnectionLost:"+responseObject.errorMessage);
      isConnected = false;
    }
}


