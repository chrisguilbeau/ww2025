var eventSource = new EventSource('/stream');
eventSource.onmessage = function(event) {
    ww.process(event.data);
};

var ww = {
    process: function(data) {
        console.log(data);
        $('#output').append(data + '<br>');
        // data is id:url
        var parts = data.split(':');
        var id = parts[0];
        var url = parts[1];
        $('#' + id).load(url);
        $.get(url, function(data) {$("#" + id).replaceWith(data);});
    }
};

var action = {
    act: function(url, kwargs, jsKeys) {
        // keys in jsKeys need to be evaluated before sending
        console.log(url);
        console.log(kwargs);
        console.log(jsKeys);
        for (var i = 0; i < jsKeys.length; i++) {
            var key = jsKeys[i];
            kwargs[key] = eval(kwargs[key]);
        }
        console.log(kwargs);
        $.ajax({
            url: url,
            type: 'POST',
            data: JSON.stringify(kwargs),
            contentType: 'application/json',
            success: function(data) {
                console.log(data);
            }
        });
    }
};
