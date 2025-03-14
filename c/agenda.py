from dateutil                       import parser as date_parser
from google.auth.transport.requests import Request
from google.oauth2.credentials      import Credentials
from google_auth_oauthlib.flow      import InstalledAppFlow
from googleapiclient.discovery      import build
from itertools                      import groupby
from lib.framework                  import ControllerPublic
from lib.framework                  import letAs
from lib.framework                  import page
from lib.framework                  import returnAs
from lib.framework                  import t
from operator                       import itemgetter
import datetime
import os.path

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def getGoogleCalendarEvents():
    """
    Return the next 20 events from all of your Google Calendars.
    """
    creds = None
    # token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no valid credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    # make it midnight so we get the whole day
    now = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'  # 'Z' indicates UTC time

    # Get the list of all calendars for the user.
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])

    all_events = []

    # Iterate over each calendar and fetch events.
    for calendar in calendars:
        cal_id = calendar['id']
        events_result = service.events().list(
            calendarId=cal_id,
            timeMin=now,
            maxResults=20,  # Adjust if needed per calendar.
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        all_events.extend(events)

    def get_event_start(event):
        """Extract and normalize the start datetime of an event."""
        start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
        try:
            dt = date_parser.isoparse(start)
            # If datetime is offset-naive, assume UTC.
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except Exception:
            # If parsing fails, return a maximum datetime value.
            return datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)

    # Sort the combined events by their normalized start time.
    all_events.sort(key=get_event_start)

    return all_events

class index(ControllerPublic):
    def get(self):
        return page(
            title='Wonder Wall - Agenda',
            headStuff=(
                t.title('Wonder Wall - Agenda'),
                t.link(rel='stylesheet', href='/static/agenda.css'),
                ),
            bodyStuff=agenda.getNow(),
            )

class agenda(ControllerPublic):
    @returnAs(t.div, id='agenda', **{'data-url': '/agenda/agenda'})
    def get(self):
        events = getGoogleCalendarEvents()
        @letAs(tuple)
        def dateEvents():
            # return a tuple of (date, summary) where summary is the event summary
            # withe the time prepended if it's a timed event.
            for event in events:
                start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
                if start:
                    start = date_parser.isoparse(start)
                    if start.time() == datetime.time(0, 0):
                        summary = event.get('summary', 'No Title')
                    else:
                        summary = f'{start.strftime("%-I:%M %p")}: {event.get("summary", "No Title")}'
                    if 'Forecast' in summary:
                        continue
                    yield start.date(), summary
        for date, events in groupby(dateEvents, key=itemgetter(0)):
            yield t.div(
                t.h2(date.strftime('%A %B %d')),
                t.ul(
                    t.li(event[1])
                    for event in events
                    ),
                _class='agenda-day',
                )
