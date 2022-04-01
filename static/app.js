var map;
var iconBase;
var infowindow = null;

function initCharts(){
	google.charts.load('current',{'packages':['corechart']});
	google.charts.setOnLoadCallback(initMap);
}

function initMap(){
	fetch("/stations").then(response => {
		return response.json()
	}).then(data => {
		//console.log("data: ", data);

		map = new google.maps.Map(document.getElementById("map"),{
				center: {lat: 53.34632331338235, lng: -6.26150959615664},
				zoom: 13,
		});

        var stationStr = "";

		data.forEach(station => {
		    stationStr = stationStr + "<li><a href='javascript:showInfowindow(" + station.number + ")'>" + formatStationName(str=station.name) + "</a></li>";
            // get marker colour url
            if (station.available_bikes/station.bike_stands < 0.25){
                colourUrl = 'red-square.png';
            } else if (station.available_bikes/station.bike_stands > 0.70){
                colourUrl = 'grn-circle.png';
            } else {
                colourUrl = 'ylw-diamond.png';
            }

            iconBase = 'https://maps.google.com/mapfiles/kml/paddle/';

		    //make markers
			const marker = new google.maps.Marker({
				position: {lat: station.pos_lat, lng: station.pos_long},
				map: map,
				icon: {
				    url: iconBase + colourUrl,
				    scaledSize: new google.maps.Size(50,50)
				}
			});

            var infoStr = "<div><h4>" + formatStationName(station.name) + "</h4><p>Available Bikes: "
                + station.available_bikes + "<br>Available Bike Stands: " + station.available_bike_stands + "</p></div>";

			//add listeners to markers
			marker.addListener("click", () => {
			    map.setCenter(marker.getPosition());
				//Close info window in this line to fix bug a
				if (infowindow) {
				    infowindow.close();
				}
				infowindow = new google.maps.InfoWindow({
					content: infoStr +
						"<div id='pred"+station.number+"' class='prediction'></div>" +
						"<div id='w"+station.number+"' class='weather'></div>"
				});
				infowindow.open(map, marker);
				//console.log("calling drawOccupancyWeekly " + station.number);
				drawOccupancyDaily(station.number);
				drawOccupancyWeekly(station.number);
				get_weather(station.number);
				get_prediction(station.number);
			});
		});
        document.getElementById("stationList").innerHTML = stationStr;

		const bikeLayer = new google.maps.BicyclingLayer();
  		bikeLayer.setMap(map);

  		setlegend();

  		map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(document.getElementById('legend'));
	}).catch(err => {
		console.log("OOPS!", err);
	})
}

function setlegend(){
    const icons = {
        red: {
            name: "Station occupancy < 25%",
            icon: iconBase + "red-square.png",
        },
        green: {
            name: "Station occupancy > 70%",
            icon: iconBase + "grn-circle.png",
        },
        yellow: {
            name: "25% < Station occupancy < 70%",
            icon: iconBase + "ylw-diamond.png",
        },
    };
    var legend = document.getElementById('legend');

    for (var key in icons){
        var type = icons[key];
        var icon = type.icon;
        var name = type.name;
        var div = document.createElement('div');
        div.innerHTML = '<img src="' + icon + '" width="30" height="30"> ' + name;
        legend.appendChild(div);
    }
}

function drawOccupancyDaily(station_number) {
	// called when user clicks marker
	// use google charts to draw chart

	fetch( "/occupancyD/" + station_number).then(response => {
	    //console.log("get_occupancy response:",response);
		return response.json()
	}).then( data => {
		//console.log("occupancy data:",data);

		var options = {
            title: "Average Bike Availability per day",
            legend: "none",
            backgroundColor: {
                fill: '#f1f1f1',
                opacity: 80
            },
            hAxis: {
                title: "Date"
            },
            vAxis: {
                title: "Avg Number of Bikes"
            }
		}

		var chart = new google.visualization.LineChart(document.getElementById('chartL'));
		var chart_data = new google.visualization.DataTable();
		chart_data.addColumn('datetime', "Date");
		chart_data.addColumn('number', "Avg Bike Availability");

		data.forEach(v => {
			chart_data.addRow([new Date(v.last_update), v.available_bikes]);
		})
		chart.draw(chart_data, options);
	})
}

function drawOccupancyWeekly(station_number) {
	// called when user clicks marker
	// use google charts to draw chart

	fetch( "/occupancyW/" + station_number).then(response => {
	    //console.log("get_occupancy response:",response);
		return response.json()
	}).then( data => {
		//console.log("occupancy data:",data);

		var options = {
			title: "Average Bike Availability per week",
			legend: "none",
			backgroundColor: {
                fill: '#f1f1f1',
                opacity: 80
            },
            vAxis: {
                title: "Avg Number of Bikes"
            }
		}

		var chart = new google.visualization.ColumnChart(document.getElementById('chartR'));
		var chart_data = new google.visualization.DataTable();
		chart_data.addColumn('string', "Day");
		chart_data.addColumn('number', "Avg Bike Availability");

		data.forEach(v => {
			chart_data.addRow([v.last_update_day, v.available_bikes]);
		})
		chart.draw(chart_data, options);
	})
}

function formatStationName(str){
    var words = str.toLowerCase().split(",");
    for (let i = 0; i < words.length; i++) {
        words[i] = words[i][0].toUpperCase() + words[i].substr(1);
    }
    return words.join(" ");
}

function showInfowindow(station_number) {
	fetch( "/sideBar/" + station_number).then(response => {
	    //console.log("get_occupancy response:",response);
		return response.json()
	}).then( data => {
		var v = data[0];
        var infoStr = "<div><h4>" + formatStationName(v.name) + "</h4><p>Available Bikes: "
                + v.available_bikes + "<br>Available Bike Stands: " + v.available_bike_stands + "</p></div>";
        if (infowindow) {
                infowindow.close();
            }
        infowindow = new google.maps.InfoWindow({
            content: infoStr +
						"<div id='pred"+station_number+"' class='prediction'></div>" +
						"<div id='w"+station_number+"' class='weather'></div>",
            position:  new google.maps.LatLng({lat:  v.pos_lat, lng: v.pos_long})
        });
		infowindow.open(map);

		drawOccupancyDaily(station_number);
		drawOccupancyWeekly(station_number);
		get_weather(station_number);
		get_prediction(station_number);
	})
}

var weather = {}
function current_weather() {
	fetch("/weather").then(response => {
		return response.json();
	}).then(data => {
		weather = data[0];
	})
}

current_weather();

function show_weather(station_number, w_data, weather_type) {
	document.getElementById('w'+station_number).innerHTML = "<img src='/static/images/"+w_data['weather_icon']+".png'>" +
		"<p><b>"+weather_type+":</b> " + w_data['weather_description'] + "</p>" +
		"<p>Temperature " + parseInt(w_data['temp'] - 273.15) + "&#8451;</p>" +
		"<p>Feels like " + parseInt(w_data['feels_like'] - 273.15) + "&#8451;</p>" +
		"<p>Humidity " + w_data['humidity'] + "%</p>" +
		"<p>Clouds " + w_data['clouds'] + "%</p>" +
		"<p>Wind speed " + w_data['wind_speed'] + " m/s</p>";
}

function get_weather(station_number) {
		var time = document.getElementById('time').value;
		var day = document.getElementById('day').value;
		if (time != null && day != null) {
			// get weather forecast
			fetch("/weather/"+day+"/"+time).then(response => {
				return response.json()
			}).then(weather_data => {
				weather_data = weather_data[0];
				if(weather_data && Object.keys(weather_data).length !== 0 && buttonPressed) {
					show_weather(station_number, weather_data, 'Weather forecast');
				} else {
					show_weather(station_number, weather, 'Current weather');
				}
			});
		}
}

function get_prediction(station_number) {
		var time = document.getElementById('time').value;
		var day = document.getElementById('day').value;
		if (time != null && day != null && buttonPressed) {
			// get prediction
			fetch("/predict/"+station_number+"/"+day+"/"+time).then(response => {
				return response.json()
			}).then(data => {
					if(data['error'] != null) {
						document.getElementById('pred' + station_number).innerHTML = data['error'];
					} else {
						document.getElementById('pred' + station_number).innerHTML = '<b>Predicted bikes: ' + data['predicted_bikes'] + '</b>';
					}
			})
		}
}

var buttonPressed = false;
function updateState() {
	buttonPressed = true;
}