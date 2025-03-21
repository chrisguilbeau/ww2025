var framework = {
    es: null,
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
    messageInit: function(url, processor, errorAction) {
        // Flag to indicate an error occurred.
        let hadError = false;
        framework.es = new EventSource(url);
        framework.es.onmessage = event => {
            if (event.data !== 'keepalive') {
                processor(event.data);
            }
        };
        framework.es.onerror = event => {
            console.error("SSE error detected:", event);
            hadError = true;
            // Don't close or reinitialize; let EventSource handle reconnection.
        };
        framework.es.onopen = event => {
            // If an error was encountered earlier, then the connection was re-established.
            if (hadError) {
                console.log("SSE connection re-established.");
                errorAction();
                hadError = false; // Reset flag after handling the error.
            } else {
                console.log("SSE connection established.");
            }
        };
    },
    process: function(message){
        console.log(message);
        console.log(message === 'food');
        switch (message){
            case 'connected':
                break;
            case 'keepalive':
                break;
            default:
                let element = $('#' + message);
                url = element.data('url');
                $.ajax({
                    method: 'GET',
                    url: url,
                    dataType: 'html',
                    success: function(data){
                        element.replaceWith(data);
                    }
                });
        }
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
