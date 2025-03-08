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
    messageInit: function(url, processor) {
	let connectionRetryInterval = 3000; // for reconnecting the stream
	const maxConnectionRetryInterval = 60000;
	const maxProcessingAttempts = 5; // maximum number of processing attempts per message

	let evtSource;

	// This function handles processing of each message with retries
	function processMessage(data) {
	    let attempts = 0;
	    const initialProcessingDelay = 1000; // delay in ms between processing attempts

	    function tryProcess() {
		attempts++;
		try {
		    // Try to process the message
		    processor(data);
		} catch (err) {
		    console.error(`Processing error (attempt ${attempts}):`, err);
		    if (attempts < maxProcessingAttempts) {
			// If processing fails, wait a bit before retrying
			setTimeout(tryProcess, initialProcessingDelay * attempts);
		    } else {
			console.error("Max processing attempts reached; skipping this message.");
		    }
		}
	    }
	    tryProcess();
	}

	// Function to connect (and reconnect) the EventSource
	function connect() {
	    evtSource = new EventSource(url);

	    evtSource.onopen = function() {
		console.log("Connected to the event stream.");
		// Reset the connection retry interval on success
		connectionRetryInterval = 3000;
	    };

	    evtSource.onmessage = function(event) {
		processMessage(event.data);
	    };

	    evtSource.onerror = function(event) {
		console.error("EventSource encountered an error:", event);
		evtSource.close();
		// Attempt to reconnect with exponential backoff
		setTimeout(connect, connectionRetryInterval);
		connectionRetryInterval = Math.min(connectionRetryInterval * 2, maxConnectionRetryInterval);
	    };
	}

	connect();
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
