var ww = {
    timeAndDateInit: function(){
        // call timeAndDateUpdate every second
        setInterval(ww.timeAndDateUpdate, 1000);
    },
    process: function(message){
        let div = $('#message');
        div.html($('<div/>', {"class": 'ww-load'}));
        framework.process(message);
    },
    timeAndDateUpdate: function(){
        // fill the timeanddate div with two spans, one for the date and one for the time
        // i.e.
        // Thursday, March 13
        // 5:15 PM
        let timeAndDate = $('#timeanddate');
        let date = new Date();
        let dateText = date.toLocaleDateString('en-US', {weekday: 'short', month: 'long', day: 'numeric'});
        let timeText = date.toLocaleTimeString('en-US', {hour: 'numeric', minute: 'numeric'});
        let dateSpan = $('<span>').text(dateText);
        let timeSpan = $('<span>').text(timeText);
        let container = $('<div>')
            .append(dateSpan)
            .append(timeSpan);
        timeAndDate.html(container.html());
    },
};
