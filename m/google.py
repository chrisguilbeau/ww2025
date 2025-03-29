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
        if creds and creds.expired and creds.refresh_token:
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
        # Process events to split multi-day events into daily occurrences
        processed_events = []
        for event in events:
            start = event.get('start', {})
            end = event.get('end', {})

            # Get start and end datetime/date
            start_dt = start.get('dateTime') or start.get('date')
            end_dt = end.get('dateTime') or end.get('date')

            # Convert to datetime objects
            try:
                # Handle date strings (all-day events)
                if 'T' not in start_dt:
                    start_date = datetime.datetime.fromisoformat(start_dt)
                    end_date = datetime.datetime.fromisoformat(end_dt) - datetime.timedelta(days=1)  # End date is exclusive

                    # Check if this is a multi-day event
                    is_multi_day = (end_date - start_date).days > 0

                    # Create an event for each day
                    current_date = start_date
                    while current_date <= end_date:
                        # Skip days that have already passed
                        current_date_utc = current_date.replace(tzinfo=datetime.timezone.utc)
                        if current_date_utc >= estnow.replace(tzinfo=datetime.timezone.utc):
                            daily_event = event.copy()
                            date_str = current_date.isoformat()
                            daily_event['start'] = {'date': date_str}
                            daily_event['end'] = {'date': (current_date + datetime.timedelta(days=1)).isoformat()}
                            processed_events.append(daily_event)
                        current_date += datetime.timedelta(days=1)
                # Handle datetime strings (timed events)
                else:
                    start_dt_obj = datetime.datetime.fromisoformat(start_dt.replace('Z', '+00:00'))
                    end_dt_obj = datetime.datetime.fromisoformat(end_dt.replace('Z', '+00:00'))

                    # Check if event spans multiple days
                    is_multi_day = start_dt_obj.date() != end_dt_obj.date()

                    if is_multi_day:
                        # First day (partial)
                        first_day_end = datetime.datetime.combine(
                            start_dt_obj.date(),
                            datetime.time(23, 59, 59)
                        ).replace(tzinfo=start_dt_obj.tzinfo)

                        # Only include if the day hasn't fully passed
                        if first_day_end >= estnow.replace(tzinfo=datetime.timezone.utc):
                            daily_event = event.copy()
                            daily_event['start'] = {'dateTime': start_dt}
                            daily_event['end'] = {'dateTime': first_day_end.isoformat()}
                            processed_events.append(daily_event)

                        # Middle days (full days)
                        current_date = start_dt_obj.date() + datetime.timedelta(days=1)
                        while current_date < end_dt_obj.date():
                            # Skip days that have already passed
                            day_end = datetime.datetime.combine(
                                current_date,
                                datetime.time(23, 59, 59)
                            ).replace(tzinfo=start_dt_obj.tzinfo)

                            if day_end >= estnow.replace(tzinfo=datetime.timezone.utc):
                                daily_event = event.copy()
                                day_start = datetime.datetime.combine(
                                    current_date,
                                    datetime.time(0, 0)
                                ).replace(tzinfo=start_dt_obj.tzinfo)

                                daily_event['start'] = {'dateTime': day_start.isoformat()}
                                daily_event['end'] = {'dateTime': day_end.isoformat()}
                                processed_events.append(daily_event)
                            current_date += datetime.timedelta(days=1)

                        # Last day (partial)
                        if current_date == end_dt_obj.date():
                            # Only include if this day hasn't passed
                            if end_dt_obj >= estnow.replace(tzinfo=datetime.timezone.utc):
                                last_day_start = datetime.datetime.combine(
                                    end_dt_obj.date(),
                                    datetime.time(0, 0)
                                ).replace(tzinfo=end_dt_obj.tzinfo)

                                daily_event = event.copy()
                                daily_event['start'] = {'dateTime': last_day_start.isoformat()}
                                daily_event['end'] = {'dateTime': end_dt}
                                processed_events.append(daily_event)
                    else:
                        # Single day event, no splitting needed
                        processed_events.append(event)
            except Exception as e:
                # If there's an error processing this event, just include it as-is
                processed_events.append(event)

        # Filter out multi-day events and add the processed events to our list
        filtered_events = []
        for event in events:
            start = event.get('start', {})
            end = event.get('end', {})

            # Get start and end datetime/date
            start_dt = start.get('dateTime') or start.get('date')
            end_dt = end.get('dateTime') or end.get('date')

            # Determine if this is a multi-day event
            is_multi_day = False
            try:
                if 'T' not in start_dt:  # All-day event
                    start_date = datetime.datetime.fromisoformat(start_dt)
                    end_date = datetime.datetime.fromisoformat(end_dt)
                    is_multi_day = (end_date - start_date).days > 1  # More than 1 day (accounting for exclusive end date)
                else:  # Timed event
                    start_dt_obj = datetime.datetime.fromisoformat(start_dt.replace('Z', '+00:00'))
                    end_dt_obj = datetime.datetime.fromisoformat(end_dt.replace('Z', '+00:00'))
                    is_multi_day = start_dt_obj.date() != end_dt_obj.date()
            except Exception:
                pass

            # Only include non-multi-day events in our filtered list
            if not is_multi_day:
                filtered_events.append(event)

        all_events.extend(filtered_events)

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
