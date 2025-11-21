"""
Gmail API integration service.
Uses OAuth 2.0 for authentication and Gmail API for email access.
"""
import base64
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings


class GmailService:
    """Service for interacting with Gmail API."""

    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email'
    ]

    def __init__(self, access_token: str, refresh_token: str):
        """
        Initialize Gmail service with OAuth tokens.

        Args:
            access_token: OAuth access token
            refresh_token: OAuth refresh token
        """
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=self.SCOPES
        )

    def refresh_access_token(self) -> str:
        """
        Refresh access token using refresh token.

        Returns:
            New access token
        """
        try:
            self.credentials.refresh(Request())
            return self.credentials.token
        except Exception as e:
            raise ValueError(f"Failed to refresh access token: {e}")

    def get_user_email(self) -> Optional[str]:
        """
        Get the user's email address.

        Returns:
            Email address or None if error
        """
        try:
            service = build('gmail', 'v1', credentials=self.credentials)
            profile = service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress')
        except HttpError as e:
            print(f"Error fetching user email: {e}")
            return None

    def list_messages(
        self,
        max_results: int = 100,
        query: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict]:
        """
        List messages from Gmail inbox.

        Args:
            max_results: Maximum number of messages to return
            query: Gmail search query string
            days_back: Number of days to look back

        Returns:
            List of message dictionaries with metadata
        """
        try:
            service = build('gmail', 'v1', credentials=self.credentials)

            # Build query with date filter
            date_filter = datetime.now() - timedelta(days=days_back)
            date_str = date_filter.strftime('%Y/%m/%d')

            if query:
                full_query = f"{query} after:{date_str}"
            else:
                full_query = f"after:{date_str}"

            # List messages
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=full_query,
                labelIds=['INBOX']
            ).execute()

            messages = results.get('messages', [])

            # Fetch full message details for each
            detailed_messages = []
            for msg in messages:
                try:
                    message = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    detailed_messages.append(message)
                except HttpError as e:
                    print(f"Error fetching message {msg['id']}: {e}")
                    continue

            return detailed_messages

        except HttpError as e:
            print(f"Error listing messages: {e}")
            return []

    def parse_message(self, message: Dict) -> Dict:
        """
        Parse Gmail message into our format.

        Args:
            message: Raw Gmail message from API

        Returns:
            Parsed message dictionary
        """
        headers = {h['name']: h['value'] for h in message['payload']['headers']}

        # Get message ID and thread ID
        message_id = message['id']
        thread_id = message['threadId']

        # Parse headers
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', '')
        recipient = headers.get('To', '')
        date_str = headers.get('Date', '')

        # Parse date
        try:
            received_at = parsedate_to_datetime(date_str)
        except Exception:
            received_at = datetime.utcnow()

        # Get body
        body, snippet = self._extract_body(message['payload'])

        # Extract dates from content
        extracted_dates = self._extract_dates(subject + ' ' + body)

        # Determine if academic
        is_academic = self._is_academic_email(sender, subject, body)

        # Categorize email
        category = self._categorize_email(subject, body)

        return {
            'gmail_message_id': message_id,
            'thread_id': thread_id,
            'subject': subject,
            'sender': sender,
            'recipient': recipient,
            'body': body,
            'snippet': snippet,
            'received_at': received_at,
            'is_academic': is_academic,
            'category': category,
            'extracted_dates': extracted_dates,
            'extracted_action_items': [],  # TODO: Implement action item extraction
        }

    def _extract_body(self, payload: Dict) -> Tuple[str, str]:
        """
        Extract body text from message payload.

        Args:
            payload: Message payload from Gmail API

        Returns:
            Tuple of (body, snippet)
        """
        snippet = payload.get('snippet', '')
        body = ''

        # Check for multipart
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            # Single part message
            data = payload['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        # Fallback to snippet if no body
        if not body:
            body = snippet

        return body[:10000], snippet  # Limit body to 10k chars

    def _extract_dates(self, text: str) -> List[str]:
        """
        Extract date mentions from text.

        Args:
            text: Text to search for dates

        Returns:
            List of extracted date strings
        """
        dates = []
        patterns = [
            r'due (?:on |by )?(\d{1,2}/\d{1,2}/\d{2,4})',
            r'due (?:on |by )?(\w+ \d{1,2},? \d{4})',
            r'deadline[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})',
            r'deadline[:\s]+(\w+ \d{1,2},? \d{4})',
            r'submit by (\d{1,2}/\d{1,2}/\d{2,4})',
            r'submit by (\w+ \d{1,2},? \d{4})',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)

        return list(set(dates))[:5]  # Limit to 5 unique dates

    def _is_academic_email(self, sender: str, subject: str, body: str) -> bool:
        """
        Determine if email is academic-related.

        Args:
            sender: Email sender address
            subject: Email subject
            body: Email body

        Returns:
            True if academic, False otherwise
        """
        # Check sender domain
        academic_domains = [
            '.edu',
            'instructure.com',
            'canvas',
            'gradescope.com',
            'piazza.com',
            'blackboard.com',
            'moodle',
        ]

        sender_lower = sender.lower()
        if any(domain in sender_lower for domain in academic_domains):
            return True

        # Check keywords
        academic_keywords = [
            'assignment', 'homework', 'exam', 'quiz', 'test',
            'lecture', 'course', 'class', 'professor', 'instructor',
            'due date', 'deadline', 'syllabus', 'grade', 'gradebook'
        ]

        text = (subject + ' ' + body).lower()
        keyword_count = sum(1 for keyword in academic_keywords if keyword in text)

        return keyword_count >= 2

    def _categorize_email(self, subject: str, body: str) -> str:
        """
        Categorize email into types.

        Args:
            subject: Email subject
            body: Email body

        Returns:
            Category string
        """
        text = (subject + ' ' + body).lower()

        if any(word in text for word in ['assignment', 'homework', 'project']):
            return 'assignment'
        elif any(word in text for word in ['deadline', 'due', 'submit by']):
            return 'deadline'
        elif any(word in text for word in ['grade', 'graded', 'score', 'feedback']):
            return 'grade'
        elif any(word in text for word in ['announcement', 'reminder', 'notice']):
            return 'announcement'
        else:
            return 'other'

    @staticmethod
    def get_auth_url(state: str) -> str:
        """
        Generate OAuth authorization URL.

        Args:
            state: CSRF protection state parameter

        Returns:
            Authorization URL for user to visit
        """
        from google_auth_oauthlib.flow import Flow
        import json

        # Create flow from client config
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=GmailService.SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent to get refresh token
        )

        return auth_url

    @staticmethod
    def exchange_code(code: str) -> Dict[str, str]:
        """
        Exchange authorization code for tokens.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Dictionary with access_token and refresh_token
        """
        from google_auth_oauthlib.flow import Flow

        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=GmailService.SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(code=code)

        credentials = flow.credentials

        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
        }
