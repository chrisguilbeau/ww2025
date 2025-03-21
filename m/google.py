from google.auth.transport.requests import Request
from google.oauth2.credentials      import Credentials
from google_auth_oauthlib.flow      import InstalledAppFlow
from googleapiclient.discovery      import build
from lib.model                      import cacheOnDiskWithPickle

import datetime
import os

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_credentials():
    creds = None
    # token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no valid credentials, let the user log in.
    if not creds or not creds.valid:
        # if creds and creds.expired and creds.refresh_token:
        if True:
            print("Refreshing Google Calendar access token.")
            # Refresh the access token using the refresh token.
            creds.refresh(Request())
        else:
            print("Requesting Google Calendar access token.")
            # Request offline access to ensure a refresh token is issued.
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0, access_type='offline')
        # Save the credentials for the next run.
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    print("Google Calendar access token obtained.")
    return creds

@cacheOnDiskWithPickle('google_calendar_events.pkl')
def getGoogleCalendarEvents():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    utcnow = datetime.datetime.utcnow()
    estnow = utcnow - datetime.timedelta(hours=4)
    now = estnow.isoformat() + "Z"  # 'Z' indicates UTC time
    monthLater = (estnow + datetime.timedelta(days=30)).isoformat() + "Z"

    # Get the list of all calendars for the user.
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])

    all_events = []

    for calendar in calendars:
        cal_id = calendar['id']
        events_result = service.events().list(
            calendarId=cal_id,
            timeMin=now,
            timeMax=monthLater,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        all_events.extend(events)

    def get_event_start(event):
        """Extract and normalize the start datetime of an event."""
        start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
        try:
            dt = datetime.datetime.fromisoformat(start)
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
