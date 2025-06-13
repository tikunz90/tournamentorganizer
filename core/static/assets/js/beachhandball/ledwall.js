var clientMqtt;
var mqtt_interval;
var topicNameBase = "beach_livescore";
var topicLedWallNameBase = "led_wall";
var topicName = "";
var topicLedWallName = "";
var topicLedWallError = "";
var isConnected = false;

var gameData;
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
    const timeString = `${hours}:${minutes}`;
    document.getElementById('clock').textContent = timeString;
}

setInterval(updateClock, 1000);
updateClock(); // Initial call to set the clock immediately



// attach an event listener to the "load" event of the window object
window.addEventListener("load", function () {
    // your code here
    console.log("ledwall loaded...");
    connectMqtt();

    showPage("info");
    //showPage("weatherforecast");
    fetchWeather();
    setTimeout(() => {
        fetchWeather();
        //document.querySelector('.logo-container').classList.add('hidden');
        //document.querySelector('.advertise-container').classList.add('hidden');
        //document.querySelector('.content').classList.add('visible');
    }, 300000); // 5000 milliseconds = 5 seconds
});


var images = [
    "/static/assets/img/gbo_logo.png",
    "/static/assets/img/beachandthegang.png",
    "/static/assets/img/advertise/ring.png",
    "/static/assets/img/advertise/swag.png",
    "/static/assets/img/advertise/voba.png",
    "/static/assets/img/advertise/dig.png",
    "/static/assets/img/advertise/gl.png",
    "/static/assets/img/advertise/ht.png",
    "/static/assets/img/advertise/Horn.jpg",
    "/static/assets/img/advertise/zelser.png",
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
    newImage.style.maxHeight = '550px';

    // Append new image to container
    container.innerHTML = '';
    container.appendChild(newImage);

    // After a short delay, fade in the new image
    setTimeout(function () {
        newImage.classList.add("active");
    }, 100); // Adjust as needed for transition timing

    // Update current image index
    currentImageIndex = randomIndex;
}


displayRandomImage();

// Change the image every 2 seconds
setInterval(displayRandomImage, 8000);

function onMessageArrived(message) {
    //console.log("onMessageArrived:" + message.payloadString);
    var data;
    try {
        data = JSON.parse(message.payloadString);
    } catch (e) {
        console.error("Error parsing JSON: " + e);
        if (isConnected) {
            clientMqtt.send(topicLedWallError, "Error parsing JSON: " + e);
        }
        return;
    }
    if (data) {
        console.log("onMessageArrived: " + data['command']);
        if (data['command'] == 'showPage') {
            showPage(data['content']);
        } else if (data['command'] == 'score') {
            updateGameData(data);
        }

    }
}

function showPage(pagename) {

    if(pagename == "weatherforecast") {
        fetchWeather();
    }
    document.querySelectorAll('.imagecontainer').forEach(function (element) {
        element.classList.remove('visible');
    });
    document.querySelectorAll('.imagecontainer').forEach(function (element) {
        element.classList.add('hidden');
    });

    var selector = '[data-id="' + pagename + '"]';
    var element = document.querySelector(selector);
    if (element) {
        element.classList.remove('hidden');
        element.classList.add('visible');
    } else {
        console.log('The element with class ' + pagename + ' does not exist.');
    }
}

function updateGameData(data) {

    try {

        if (data.id == -1) {
            return;
        }
        gameData = data;

        var headerTournamentState = document.getElementById('gameTournamentState');
        var headerTeamA = document.getElementById('gameTeamA_Name');
        var headerTeamB = document.getElementById('gameTeamB_Name');

        var tevent = data.tournament_event;
        var category = tevent.category;
        var tstate = data.tournament_state;
        var teamA = data.team_a;
        var teamB = data.team_b;
        var playersA = data.player_st_a;
        var playersB = data.player_st_b;

        var catLetter = "M";
        if (category.category.includes("woman")) {
            catLetter = "W";
        }
        var tstateName = catLetter + " - " + tstate.name;
        headerTournamentState.textContent = tstateName;

        headerTeamA.textContent = teamA.name;
        headerTeamB.textContent = teamB.name;

        fillPlayersTable("gamePlayersA", playersA);
        fillPlayersTable("gamePlayersB", playersB);

    } catch (error) {
        if (isConnected) {
            clientMqtt.send(topicLedWallError, "Error updateGameData: " + error);
        }
        console.log("Error updateGameData: " + error);
    }
}

function fillPlayersTable(tableId, jsonData) {
    var tableBody = document.querySelector(`#${tableId} tbody`);
    tableBody.innerHTML = ''; // Clear any existing rows

    jsonData.slice(0, 12).forEach(player => {
        var playerInfo = player.seasonPlayer.seasonSubject.subject.user;
        var number = player.seasonPlayer.number;
        var name = playerInfo.name;
        var familyName = playerInfo.family_name;
        var initial = name.charAt(0) + ".";
        var score = player.score;

        var row = document.createElement('tr');

        var numberCell = document.createElement('td');
        numberCell.classList.add('centered', 'numbercol');
        numberCell.textContent = number;

        var nameCell = document.createElement('td');
        nameCell.classList.add('namecol');
        nameCell.textContent = `${familyName}, ${name}`;

        var scoreCell = document.createElement('td');
        scoreCell.classList.add('centered', 'numbercol');
        scoreCell.textContent = score;

        row.appendChild(numberCell);
        row.appendChild(nameCell);
        row.appendChild(scoreCell);

        tableBody.appendChild(row);
    });
}

function fetchWeather() {
    console.log("ENTER featchWeather");
    try {
        fetch(`https://api.openweathermap.org/data/2.5/weather?lat=50.136181&lon=8.450800&appid=cb4b76afff33313fc2d263c5b83c82b6`)
            .then(response => response.json())
            .then(data => {
                const weatherResult = document.getElementById('weatherResult');
                if (data.cod === 200) {
                    var iconUrl = `https://openweathermap.org/img/wn/${data.weather[0].icon}@2x.png`;
                    document.getElementById('weather-icon').src = iconUrl;
                    weatherResult.textContent = `${roundToNearestHalf(data.main.temp -273.15)}°C`;
                } else {
                    console.log("Error weather:" + data.cod);
                }
            })
            .catch(error => {
                console.error('Error fetching weather data:', error);
                document.getElementById('weatherResult').innerHTML = `<p>Error fetching weather data</p>`;
            });
    } catch (error) {

    }


    try {
        console.log("Check weather")
        fetch(`https://api.openweathermap.org/data/2.5/forecast?lat=50.136181&lon=8.450800&appid=cb4b76afff33313fc2d263c5b83c82b6`)
        .then(response => response.json())
        .then(data => {
            if (data.cod == "200") {

                const forecastContainer = document.querySelector('#weatherforecast-container');

                forecastContainer.innerHTML = '';

                let itemCount = 0;
                data.list.forEach(forecast => {
                    if (itemCount >= 3) {
                        // If three items are already added, exit the loop
                        return;
                    }

                    
                    const forecastItem = document.createElement('div');
                    forecastItem.classList.add('forecast-item', 'd-flex', 'align-items-center', 'justify-content-between', 'mb-3');

                    var time = unixTimestampToHHMM(forecast.dt);
                    const weatherTime = document.createElement('h2');
                    weatherTime.classList.add('forecastTime', 'mb-2');
                    weatherTime.textContent = time;
                
                    var iconUrl = `https://openweathermap.org/img/wn/${forecast.weather[0].icon}@2x.png`;

                    const weatherIcon = document.createElement('img');
                    weatherIcon.classList.add('weather-icon', 'mb-2');
                    weatherIcon.src = iconUrl;
                    weatherIcon.alt = 'Weather Icon';

                    var wind = forecast.wind.speed * 3.6;
                    const weatherWind = document.createElement('h2');
                    weatherWind.classList.add('forecastWind', 'mb-2');
                    weatherWind.textContent = `${Math.round(wind)} km/h`;
                
                    const weatherResult = document.createElement('h2');
                    weatherResult.classList.add('weatherResult', 'mb-2');
                    weatherResult.textContent = `${roundToNearestHalf(forecast.main.temp -273.15)}°C`;
                
                    forecastItem.appendChild(weatherTime);
                    forecastItem.appendChild(weatherIcon);
                    //forecastItem.appendChild(weatherWind);
                    forecastItem.appendChild(weatherResult);
                
                    forecastContainer.appendChild(forecastItem);

                    itemCount++;
                });

            } else {
                console.log("Error Forecast:" + data.cod);
            }
        })
        .catch(error => {
            console.error('Error fetching weather data:', error);
            document.getElementById('weatherResult').innerHTML = `<p>Error fetching weather data</p>`;
        });


        

    } catch (error) {
        
    }

}

function unixTimestampToHHMM(unixTimestamp) {
    // Convert Unix timestamp to milliseconds
    const milliseconds = unixTimestamp * 1000;

    // Create a new Date object
    const dateObject = new Date(milliseconds);

    // Get hours and minutes from the Date object
    const hours = dateObject.getHours();
    const minutes = dateObject.getMinutes();

    // Format hours and minutes to have leading zeros if necessary
    const formattedHours = String(hours).padStart(2, '0');
    const formattedMinutes = String(minutes).padStart(2, '0');

    // Concatenate hours and minutes with a colon separator
    const formattedTime = `${formattedHours}:${formattedMinutes}`;

    return formattedTime;
}

function roundToNearestHalf(num) {
    return Math.round(num * 2) / 2;
}

function connectMqtt() {
    console.log("connect mqtt...");
    var headerTournId = document.getElementById('tournament_id');
    var headerCourtId = document.getElementById('court_id');
    var headerGameId = document.getElementById('game_id');
    //topicName = topicNameBase + "/tournament_" + headerTournId.textContent + "/court_" + headerCourtId.textContent + "/";
    topicName = topicNameBase + "/court_" + headerCourtId.textContent + "/";
    //topicLedWallName = topicLedWallNameBase + "/tournament_" + headerTournId.textContent + "/court_" + headerCourtId.textContent + "/";
    topicLedWallName = topicLedWallNameBase + "/court_" + headerCourtId.textContent + "/";
    topicLedWallError = topicLedWallNameBase + "/error/";

    var urlParams = new URLSearchParams(window.location.search);
    // Get the value of the "myparam" parameter
    var passedTopicName = urlParams.get('court');

    if (passedTopicName != null) {
        topicName = topicNameBase + "/" + passedTopicName + "/";
    }

    console.log("Topic: " + topicName);
    var headerMqttBroker = document.getElementById('mqtt_broker');
    var headerMqttPort = document.getElementById('mqtt_port');

    var useSSL = false;
    var portNumber = 8082;
    if (location.protocol == 'https:') {
        //console.log("https: ");
        //useSSL = true;
        //portNumber = 8083;
    }

    console.log("Mqtt: " + headerMqttBroker.textContent + ":" + portNumber);
    let uniqueId = Date.now().toString(36) + Math.random().toString(36).substring(2);
    clientMqtt = new Paho.MQTT.Client(headerMqttBroker.textContent, portNumber, "/ws", "livescore_display_beach_" + uniqueId);

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
    clientMqtt.send(topicName, "Hello"); // Replace "topic" with the topic you want to publish the message to
    clientMqtt.subscribe(topicName);
    clientMqtt.subscribe(topicLedWallName);
}

function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost:" + responseObject.errorMessage);
        isConnected = false;
    }
}