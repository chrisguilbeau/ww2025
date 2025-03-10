var weather = {
    process: function(data){
	console.log(data, 'for weather');
	$('#weather').load('/weather/inner');
    }
};
