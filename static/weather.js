var weather= {
    refresh: function() {
	console.log('Refreshing weather data');
	framework.process('weather');
    }
};

var fifteenMinutes = 1000 * 60 * 15;
var weatherRefresher = setInterval(weather.refresh, fifteenMinutes);
