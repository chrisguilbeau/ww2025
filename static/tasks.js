var tasks = {
    process: function(data) {
	console.log(data);
	$('#output').append(data + '<br>');
	// data is id:url
	var parts = data.split(':');
	var id = parts[0];
	var url = parts[1];
	$('#' + id).load(url);
	$.get(url, function(data) {$("#" + id).replaceWith(data);});
    },
};
