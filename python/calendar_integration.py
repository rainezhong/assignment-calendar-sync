"""Simple Google Calendar integration for assignment events"""

import os
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config
from utils import (
    logger, retry_on_failure, handle_common_errors,
    handle_google_api_errors, CalendarError
)


# Google Calendar API scope - only need calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarIntegration:
    """Simple Google Calendar integration for creating assignment events"""
    
    def __init__(self):
        self.service = None
        self.calendar_id = config.GOOGLE_CALENDAR_ID
        self.authenticate()
    
    @handle_common_errors
    def authenticate(self):
        """Handle OAuth2 authentication with Google Calendar"""
        logger.info("Authenticating with Google Calendar...")
        creds = None
        
        # Check if we have saved credentials
        if os.path.exists(config.TOKEN_FILE):
            try:
                logger.debug(f"Loading saved credentials from {config.TOKEN_FILE}")
                creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, SCOPES)
            except Exception as e:
                logger.warning(f"Error loading saved credentials: {e}")
                logger.debug("Removing invalid token file")
                try:
                    os.remove(config.TOKEN_FILE)
                except:
                    pass
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refreshing expired credentials...")
                    creds.refresh(Request())
                    logger.debug("Credentials refreshed successfully")
                except Exception as e:
                    logger.warning(f"Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                logger.info("Starting OAuth2 authentication flow...")
                logger.info("Your browser will open to authenticate with Google Calendar")
                
                # Validate credentials first
                if not config.GOOGLE_CLIENT_ID or not config.GOOGLE_CLIENT_SECRET:
                    raise CalendarError(
                        "Missing Google Calendar credentials. Please check GOOGLE_CLIENT_ID "
                        "and GOOGLE_CLIENT_SECRET in your .env file."
                    )
                
                try:
                    # Create OAuth flow
                    client_config = {
                        "installed": {
                            "client_id": config.GOOGLE_CLIENT_ID,
                            "client_secret": config.GOOGLE_CLIENT_SECRET,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["http://localhost"]
                        }
                    }
                    
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                    creds = flow.run_local_server(port=0)
                    
                    logger.success("OAuth2 authentication successful!")
                    
                except Exception as e:
                    error_msg = handle_google_api_errors(e)
                    logger.error(f"OAuth2 authentication failed: {error_msg}")
                    raise CalendarError(f"Authentication failed: {error_msg}")
            
            # Save credentials for future runs
            try:
                with open(config.TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                logger.debug(f"Credentials saved to {config.TOKEN_FILE}")
            except Exception as e:
                logger.warning(f"Failed to save credentials: {e}")
                # Continue anyway - we have working creds
        
        # Build the service
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            logger.success("Connected to Google Calendar API")
            
        except Exception as e:
            error_msg = handle_google_api_errors(e)
            logger.error(f"Failed to connect to Google Calendar: {error_msg}")
            raise CalendarError(f"Failed to connect to Google Calendar: {error_msg}")
    
    @retry_on_failure(max_attempts=2, delay=2, exceptions=(HttpError,))
    @handle_common_errors
    def create_assignment_event(self, assignment):
        """Create a calendar event for an assignment"""
        if not assignment.get('due_date'):
            logger.debug("Skipping assignment without due date")
            return None
        
        assignment_name = assignment.get('name', 'Unknown Assignment')
        course_name = assignment.get('course', 'Unknown Course')
        
        # Format event title: "CS 101: Assignment 1 Due"
        event_title = f"{course_name}: {assignment_name} Due"
        
        logger.debug(f"Creating calendar event: {event_title}")
        
        # Set event time - make it 1 hour before due date to due date
        due_date = assignment['due_date']
        start_time = due_date - timedelta(hours=1)
        
        # Create event description
        description_parts = [
            f"Assignment: {assignment_name}",
            f"Course: {course_name}"
        ]
        
        if assignment.get('url'):
            description_parts.append(f"Link: {assignment['url']}")
        
        if assignment.get('status'):
            description_parts.append(f"Status: {assignment['status']}")
        
        description = "\n".join(description_parts)
        
        # Build event object
        event = {
            'summary': event_title,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': config.TIMEZONE,
            },
            'end': {
                'dateTime': due_date.isoformat(),
                'timeZone': config.TIMEZONE,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 60},       # 1 hour before
                ],
            },
        }
        
        try:
            created_event = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event
            ).execute()
            
            event_id = created_event.get('id')
            logger.debug(f"Successfully created event with ID: {event_id}")
            return event_id
            
        except HttpError as error:
            error_msg = handle_google_api_errors(error)
            logger.error(f"Failed to create event '{event_title}': {error_msg}")
            
            # Check for specific error codes
            if error.resp.status == 403:
                raise CalendarError(f"Permission denied creating calendar event. Check calendar permissions.")
            elif error.resp.status == 404:
                raise CalendarError(f"Calendar not found. Check GOOGLE_CALENDAR_ID in .env file.")
            else:
                # Don't raise for other HTTP errors, just log and return None
                logger.warning(f"Event creation failed but continuing: {error_msg}")
                return None
            
        except Exception as e:
            logger.error(f"Unexpected error creating event '{event_title}': {e}")
            return None
    
    def check_for_duplicates(self, assignment):
        """Check if an event already exists for this assignment"""
        if not assignment.get('due_date'):
            return True  # Consider it a duplicate to skip
        
        # Create the title we would use
        event_title = f"{assignment['course']}: {assignment['name']} Due"
        
        # Search for existing events around the due date
        due_date = assignment['due_date']
        time_min = (due_date - timedelta(days=1)).isoformat() + 'Z'
        time_max = (due_date + timedelta(days=1)).isoformat() + 'Z'
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                q=event_title,  # Search by title
                singleEvents=True
            ).execute()
            
            events = events_result.get('items', [])
            
            # Check for exact title match
            for event in events:
                if event.get('summary') == event_title:
                    return True
            
            return False
            
        except HttpError as error:
            print(f"Error checking for duplicates: {error}")
            return False  # If we can't check, assume no duplicate
    
    def sync_assignments(self, assignments):
        """Sync a list of assignments to Google Calendar"""
        if not assignments:
            print("No assignments to sync")
            return 0, 0
        
        print(f"\nSyncing {len(assignments)} assignments to Google Calendar...")
        
        created_count = 0
        skipped_count = 0
        
        for assignment in assignments:
            assignment_name = assignment.get('name', 'Unknown Assignment')
            course_name = assignment.get('course', 'Unknown Course')
            
            # Skip if no due date
            if not assignment.get('due_date'):
                print(f"  ⚠️  Skipping {course_name}: {assignment_name} (no due date)")
                skipped_count += 1
                continue
            
            # Check for duplicates
            if self.check_for_duplicates(assignment):
                print(f"  ⏭️  Skipping {course_name}: {assignment_name} (already exists)")
                skipped_count += 1
                continue
            
            # Create the event
            event_id = self.create_assignment_event(assignment)
            
            if event_id:
                due_str = assignment['due_date'].strftime('%m/%d %H:%M')
                print(f"  ✅ Created {course_name}: {assignment_name} (Due: {due_str})")
                created_count += 1
            else:
                print(f"  ❌ Failed to create {course_name}: {assignment_name}")
                skipped_count += 1
        
        return created_count, skipped_count
    
    def test_connection(self):
        """Test the connection to Google Calendar"""
        try:
            # Try to get calendar info
            calendar = self.service.calendars().get(calendarId=self.calendar_id).execute()
            print(f"✓ Connected to calendar: {calendar.get('summary', 'Unknown')}")
            return True
        except HttpError as error:
            print(f"❌ Connection test failed: {error}")
            return False


def test_calendar_integration():
    """Test function for calendar integration"""
    print("=" * 50)
    print("Testing Google Calendar Integration")
    print("=" * 50)
    
    try:
        # Initialize calendar integration
        calendar = GoogleCalendarIntegration()
        
        # Test connection
        if not calendar.test_connection():
            print("Failed to connect to Google Calendar")
            return False
        
        # Create a test assignment
        test_assignment = {
            'name': 'Test Assignment',
            'course': 'CS 101',
            'due_date': datetime.now() + timedelta(days=1, hours=2),
            'status': 'Not Started',
            'url': 'https://example.com/assignment'
        }
        
        print(f"\nTesting with assignment: {test_assignment['course']}: {test_assignment['name']}")
        
        # Check for duplicates
        if calendar.check_for_duplicates(test_assignment):
            print("Test assignment already exists - skipping creation")
        else:
            # Create event
            event_id = calendar.create_assignment_event(test_assignment)
            
            if event_id:
                print(f"✅ Successfully created test event (ID: {event_id[:20]}...)")
            else:
                print("❌ Failed to create test event")
        
        print("\n" + "=" * 50)
        print("Calendar integration test completed!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == '__main__':
    test_calendar_integration()