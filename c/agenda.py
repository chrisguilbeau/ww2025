from itertools     import groupby
from lib.framework import ControllerPublic
from lib.framework import letAs
from lib.framework import page
from lib.framework import returnAs
from lib.framework import t
from m.google      import getGoogleCalendarEvents
from m.hostaway    import getHostawayBookings
from operator      import itemgetter

import datetime

headStuff = (
    t.link(rel='stylesheet', href='/static/agenda.css'),
    )

class index(ControllerPublic):
    def get(self):
        return page(
            title='Wonder Wall - Agenda',
            headStuff=headStuff,
            bodyStuff=agenda.getNow(),
            )

class agenda(ControllerPublic):
    @returnAs(t.div, id='agenda', **{'data-url': '/agenda/agenda'})
    def get(self):
        googleEvents = getGoogleCalendarEvents()
        @letAs(sorted, key=lambda tup: tup[0])
        def dateEvents():
            pineappleEmoji = '&#x1F34D;'
            for date, summary in getHostawayBookings():
                yield date, pineappleEmoji + summary.replace('at Chipman Inn', ''), 'host'
            # return a tuple of (date, summary) where summary is the event summary
            # withe the time prepended if it's a timed event.
            for event in googleEvents:
                start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
                if start:
                    start = datetime.datetime.fromisoformat(start)
                    if start.time() == datetime.time(0, 0):
                        summary = event.get('summary', 'No Title')
                    else:
                        summary = f'{start.strftime("%-I:%M %p")}: {event.get("summary", "No Title")}'
                    if 'Forecast' in summary:
                        continue
                    yield start.date(), summary, 'goog'
        for date, events in groupby(dateEvents, key=itemgetter(0)):
            yield t.div(
                t.h2(date.strftime('%A %B %d')),
                t.ul(
                    t.li(summary, _class=_class)
                    for date, summary, _class in events
                    ),
                _class='agenda-day',
                )
