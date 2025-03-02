var action = {
    prompt: function(url, params){
	let html = $('html');
	let screen = $('<div/>', {class: 'action-screen'});
	let prompt = $('<div/>', {class: 'action-prompt'});
	screen.append(prompt);
	html.append(screen);
	$.get(url, params, function(data){
	    prompt.html(data);
	});
    },
    killPrompt: function(target){
	$(target).parents('.action-screen').remove();
    },
    killTopScreen: function(){
	$('.action-screen').last().remove();
    },
    act: function(url, params, evalKeys){
	var newParams = {};
	for (var key in params){
	    if (evalKeys.includes(key)){
		newParams[key] = eval(params[key]);
	    } else {
		newParams[key] = params[key];
	    }
	}
	$.ajax({
	    method: 'POST',
	    url: url,
	    data: newParams,
	    dataType: 'json',
	    success: function(data){
		var js = data.js || [];
		for (var i = 0; i < js.length; i++){
		    eval(js[i]);
		}
	    }});
    },
};
