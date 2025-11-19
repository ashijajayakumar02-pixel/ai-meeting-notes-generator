
import os
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarService:
    def __init__(self):
        """Initialize Google Calendar service"""
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.service = None
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.json'

    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None

        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)

        # If there are no valid credentials available, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists(self.credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    print("Warning: Google credentials not found. Calendar integration disabled.")
                    return False

            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)
        return True

    def create_event(self, action_item):
        """
        Create calendar event for action item
        Args:
            action_item (dict): Action item details
        Returns:
            dict: Created event details
        """
        if not self.service:
            if not self.authenticate():
                raise Exception("Calendar authentication failed")

        try:
            # Parse due date
            due_date = self._parse_due_date(action_item.get('due_date', ''))

            event = {
                'summary': f"Action Item: {action_item['description'][:50]}...",
                'description': f"""
Action Item from Meeting

Description: {action_item['description']}
Assignee: {action_item.get('assignee', 'Unassigned')}
Priority: {action_item.get('priority', 'Medium')}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """.strip(),
                'start': {
                    'dateTime': due_date.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': (due_date + timedelta(hours=1)).isoformat(),
                    'timeZone': 'America/New_York',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},       # 1 hour before
                    ],
                },
            }

            # Add attendee if specified
            if action_item.get('assignee') and '@' in action_item.get('assignee', ''):
                event['attendees'] = [{'email': action_item['assignee']}]

            created_event = self.service.events().insert(calendarId='primary', body=event).execute()

            return {
                'id': created_event['id'],
                'htmlLink': created_event['htmlLink'],
                'summary': created_event['summary'],
                'start': created_event['start']['dateTime']
            }

        except HttpError as error:
            print(f'Calendar API error: {error}')
            raise Exception(f'Failed to create calendar event: {error}')
        except Exception as e:
            print(f'Error creating calendar event: {e}')
            raise Exception(f'Calendar integration failed: {e}')

    def _parse_due_date(self, due_date_str):
        """
        Parse due date string to datetime object
        Args:
            due_date_str (str): Due date as string
        Returns:
            datetime: Parsed datetime object
        """
        if not due_date_str or due_date_str == "No due date specified":
            # Default to 1 week from now
            return datetime.now() + timedelta(days=7)

        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M']:
                try:
                    return datetime.strptime(due_date_str, fmt)
                except ValueError:
                    continue

            # If no format matches, default to 1 week from now
            return datetime.now() + timedelta(days=7)

        except Exception:
            return datetime.now() + timedelta(days=7)

    def list_calendars(self):
        """List available calendars"""
        if not self.service:
            if not self.authenticate():
                return []

        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            return [{'id': cal['id'], 'summary': cal['summary']} for cal in calendars]
        except HttpError as error:
            print(f'Error listing calendars: {error}')
            return []

    def test_connection(self):
        """Test Google Calendar API connection"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False

            # Try to list calendars as a test
            self.service.calendarList().list().execute()
            return True
        except Exception as e:
            print(f'Calendar connection test failed: {e}')
            return False
