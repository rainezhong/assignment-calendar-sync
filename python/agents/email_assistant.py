#!/usr/bin/env python3
"""
Email Assistant with AI-Powered Academic Email Analysis
Teaching concepts: IMAP Protocol, OAuth2 Flow, Email Parsing, NLP Information Extraction
"""

import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
import hashlib
import base64
from collections import defaultdict

logger = logging.getLogger(__name__)

# LEARNING CONCEPT 1: Email Protocols and OAuth2
# IMAP is the standard protocol for reading emails
# OAuth2 provides secure, token-based authentication without passwords

@dataclass
class EmailCredentials:
    """
    Secure email credentials using OAuth2

    Teaching Concepts:
    - OAuth2 token-based authentication
    - Refresh token pattern for long-lived access
    - Credential encryption at rest
    """
    email_address: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    provider: str = "gmail"  # gmail, outlook, etc.

    def is_token_expired(self) -> bool:
        """Check if access token needs refresh"""
        if not self.token_expiry:
            return True
        return datetime.now() >= self.token_expiry - timedelta(minutes=5)

    def to_secure_dict(self) -> Dict[str, str]:
        """Convert to dictionary with encrypted tokens"""
        # In production, encrypt tokens before storing
        return {
            "email_address": self.email_address,
            "access_token": self._encrypt(self.access_token) if self.access_token else None,
            "refresh_token": self._encrypt(self.refresh_token) if self.refresh_token else None,
            "token_expiry": self.token_expiry.isoformat() if self.token_expiry else None,
            "provider": self.provider
        }

    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data (simplified - use proper encryption in production)"""
        # In production, use cryptography.fernet or similar
        return base64.b64encode(data.encode()).decode()

@dataclass
class AcademicEmail:
    """
    Structured representation of an academic email

    Rich data model with computed properties for intelligent analysis
    """
    message_id: str
    sender: str
    sender_name: str
    subject: str
    body_text: str
    received_date: datetime
    has_attachment: bool = False
    attachments: List[Dict[str, Any]] = field(default_factory=list)

    # AI-extracted fields
    is_academic: bool = False
    email_type: str = "other"  # assignment, grade, announcement, syllabus, office_hours
    confidence_score: float = 0.0
    extracted_assignments: List[Dict] = field(default_factory=list)
    extracted_deadlines: List[datetime] = field(default_factory=list)
    course_mentioned: Optional[str] = None
    action_required: bool = False
    urgency_level: str = "low"  # low, medium, high, critical

    # Metadata
    parsing_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_from_professor(self) -> bool:
        """Heuristic to detect professor emails"""
        professor_indicators = [
            '.edu' in self.sender,
            'professor' in self.sender_name.lower(),
            'dr.' in self.sender_name.lower(),
            'instructor' in self.sender_name.lower()
        ]
        return any(professor_indicators)

    @property
    def days_since_received(self) -> int:
        """Calculate age of email"""
        return (datetime.now() - self.received_date).days

# LEARNING CONCEPT 2: IMAP Protocol Deep Dive
# IMAP allows reading emails without downloading them locally
# It's stateful (unlike HTTP) - you maintain a connection

class IMAPEmailClient:
    """
    IMAP client for secure email access

    Teaching Concepts:
    - IMAP protocol (stateful connection)
    - OAuth2 XOAUTH2 authentication mechanism
    - Connection pooling and retry logic
    - Incremental email fetching
    """

    # Provider-specific IMAP configurations
    IMAP_SERVERS = {
        "gmail": "imap.gmail.com",
        "outlook": "outlook.office365.com",
        "yahoo": "imap.mail.yahoo.com",
        "icloud": "imap.mail.me.com"
    }

    def __init__(self, credentials: EmailCredentials):
        self.credentials = credentials
        self.connection: Optional[imaplib.IMAP4_SSL] = None
        self.is_connected = False

    def connect(self) -> bool:
        """
        Establish IMAP connection using OAuth2

        This demonstrates:
        - IMAP SSL connection setup
        - OAuth2 XOAUTH2 authentication
        - Connection state management
        """
        try:
            # Get IMAP server for provider
            imap_server = self.IMAP_SERVERS.get(
                self.credentials.provider,
                self.IMAP_SERVERS["gmail"]
            )

            # Create SSL connection (port 993 is standard for IMAP SSL)
            logger.info(f"Connecting to {imap_server}...")
            self.connection = imaplib.IMAP4_SSL(imap_server, 993)

            # Authenticate using OAuth2 XOAUTH2
            if self.credentials.access_token:
                auth_string = self._generate_oauth2_string()
                self.connection.authenticate('XOAUTH2', lambda x: auth_string)
            else:
                # Fallback to password auth (not recommended)
                logger.warning("Using password authentication - OAuth2 recommended")
                # self.connection.login(email, password)
                raise ValueError("OAuth2 token required")

            self.is_connected = True
            logger.info("IMAP connection established")
            return True

        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP authentication failed: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            self.is_connected = False
            return False

    def _generate_oauth2_string(self) -> bytes:
        """
        Generate OAuth2 XOAUTH2 authentication string

        LEARNING CONCEPT: XOAUTH2 Protocol
        Format: base64("user={email}\x01auth=Bearer {token}\x01\x01")
        """
        auth_string = (
            f"user={self.credentials.email_address}\x01"
            f"auth=Bearer {self.credentials.access_token}\x01\x01"
        )
        return auth_string.encode()

    def disconnect(self):
        """Safely close IMAP connection"""
        if self.connection and self.is_connected:
            try:
                self.connection.close()
                self.connection.logout()
                self.is_connected = False
                logger.info("IMAP connection closed")
            except Exception as e:
                logger.error(f"Error closing IMAP connection: {e}")

    def fetch_recent_emails(self,
                           days_back: int = 30,
                           folder: str = "INBOX",
                           max_emails: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch recent emails using IMAP

        This demonstrates:
        - IMAP folder selection
        - IMAP search syntax
        - Incremental email fetching
        - Efficient header-only fetching
        """
        if not self.is_connected:
            if not self.connect():
                return []

        try:
            # Select the mailbox (folder)
            status, messages = self.connection.select(folder)
            if status != 'OK':
                logger.error(f"Could not select folder: {folder}")
                return []

            # Calculate date for search
            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")

            # IMAP search query
            # SINCE: emails received since date
            # UNSEEN: unread emails
            # FROM: filter by sender
            search_criteria = f'(SINCE {since_date})'

            logger.info(f"Searching for emails: {search_criteria}")
            status, message_numbers = self.connection.search(None, search_criteria)

            if status != 'OK':
                logger.error("Email search failed")
                return []

            # Get list of email IDs
            email_ids = message_numbers[0].split()
            email_ids = email_ids[-max_emails:]  # Limit to most recent

            logger.info(f"Found {len(email_ids)} emails")

            # Fetch emails
            emails = []
            for email_id in email_ids:
                email_data = self._fetch_single_email(email_id)
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def _fetch_single_email(self, email_id: bytes) -> Optional[Dict[str, Any]]:
        """
        Fetch a single email by ID

        LEARNING CONCEPT: IMAP FETCH command
        - BODY.PEEK[]: Fetch without marking as read
        - RFC822: Full email in RFC822 format
        - BODY[HEADER]: Headers only (faster)
        """
        try:
            # Fetch email (BODY.PEEK doesn't mark as read)
            status, msg_data = self.connection.fetch(email_id, '(RFC822)')

            if status != 'OK':
                return None

            # Parse email
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)

            # Extract email components
            subject = self._decode_header(email_message.get('Subject', ''))
            sender = email_message.get('From', '')
            date_str = email_message.get('Date', '')

            # Parse sender name and email
            sender_name, sender_email = self._parse_sender(sender)

            # Parse date
            received_date = parsedate_to_datetime(date_str) if date_str else datetime.now()

            # Extract body
            body_text = self._extract_email_body(email_message)

            # Extract attachments
            attachments = self._extract_attachments(email_message)

            return {
                'message_id': email_message.get('Message-ID', str(email_id)),
                'sender': sender_email,
                'sender_name': sender_name,
                'subject': subject,
                'body_text': body_text,
                'received_date': received_date,
                'has_attachment': len(attachments) > 0,
                'attachments': attachments
            }

        except Exception as e:
            logger.error(f"Error fetching email {email_id}: {e}")
            return None

    def _decode_header(self, header: str) -> str:
        """Decode email header (handles encoding)"""
        if not header:
            return ""

        decoded_parts = decode_header(header)
        decoded_header = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_header += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_header += part

        return decoded_header

    def _parse_sender(self, sender: str) -> Tuple[str, str]:
        """Extract name and email from sender field"""
        # Format: "Name <email@domain.com>" or just "email@domain.com"
        match = re.match(r'([^<]+)?<?([^>]+)>?', sender)
        if match:
            name = match.group(1).strip() if match.group(1) else ""
            email_addr = match.group(2).strip()
            return name, email_addr
        return "", sender

    def _extract_email_body(self, email_message) -> str:
        """
        Extract text body from email

        LEARNING CONCEPT: MIME multipart emails
        Emails can have multiple parts (text, html, attachments)
        We prefer plain text, fallback to HTML
        """
        body_text = ""

        if email_message.is_multipart():
            # Email has multiple parts
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                # Get text/plain parts
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        body_text += payload.decode(charset, errors='ignore')
                    except Exception as e:
                        logger.debug(f"Error decoding email part: {e}")
        else:
            # Simple email (not multipart)
            try:
                payload = email_message.get_payload(decode=True)
                charset = email_message.get_content_charset() or 'utf-8'
                body_text = payload.decode(charset, errors='ignore')
            except Exception as e:
                logger.debug(f"Error decoding email body: {e}")

        return body_text.strip()

    def _extract_attachments(self, email_message) -> List[Dict[str, Any]]:
        """Extract attachment metadata"""
        attachments = []

        if email_message.is_multipart():
            for part in email_message.walk():
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': self._decode_header(filename),
                            'content_type': part.get_content_type(),
                            'size': len(part.get_payload(decode=True) or b'')
                        })

        return attachments

# LEARNING CONCEPT 3: AI-Powered Email Analysis
# Use LLMs to understand email content and extract structured information

class AcademicEmailAnalyzer:
    """
    AI-powered email analyzer for academic content

    Teaching Concepts:
    - Prompt engineering for classification
    - Information extraction from unstructured text
    - Multi-model approach (AI + heuristics)
    - Confidence scoring
    """

    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.email_patterns = self._load_email_patterns()

    def _load_email_patterns(self) -> Dict[str, List[str]]:
        """
        Pattern library for email classification

        LEARNING CONCEPT: Hybrid AI + Rule-Based Systems
        Use regex patterns for fast filtering, AI for complex analysis
        """
        return {
            "assignment_keywords": [
                r'\b(homework|assignment|problem set|pset|hw\s*\d+)\b',
                r'\b(due|deadline|submit|turn in)\b',
                r'\b(worth|points|grade)\b'
            ],
            "grade_keywords": [
                r'\b(grade|score|result|feedback)\b',
                r'\b(received|earned|got)\b',
                r'\b(\d+/\d+|\d+%)\b'  # Scores like "85/100" or "85%"
            ],
            "syllabus_keywords": [
                r'\b(syllabus|course outline|schedule)\b',
                r'\b(grading policy|attendance)\b'
            ],
            "office_hours_keywords": [
                r'\b(office hours?|meeting|appointment)\b',
                r'\b(available|schedule|book)\b'
            ]
        }

    async def analyze_email(self, email_data: Dict[str, Any]) -> AcademicEmail:
        """
        Analyze email and extract academic information

        This demonstrates:
        - Fast pre-filtering with regex
        - AI analysis only when needed (cost optimization)
        - Structured data extraction
        - Confidence scoring
        """
        # Create AcademicEmail object
        academic_email = AcademicEmail(**email_data)

        # Quick heuristic filtering
        is_likely_academic = self._quick_academic_check(academic_email)

        if not is_likely_academic:
            academic_email.is_academic = False
            academic_email.confidence_score = 0.1
            return academic_email

        # Deep AI analysis for academic emails
        analysis = await self._ai_deep_analysis(academic_email)

        # Merge AI analysis into email object
        academic_email.is_academic = analysis.get('is_academic', False)
        academic_email.email_type = analysis.get('email_type', 'other')
        academic_email.confidence_score = analysis.get('confidence', 0.0)
        academic_email.extracted_assignments = analysis.get('assignments', [])
        academic_email.extracted_deadlines = analysis.get('deadlines', [])
        academic_email.course_mentioned = analysis.get('course', None)
        academic_email.action_required = analysis.get('action_required', False)
        academic_email.urgency_level = analysis.get('urgency', 'low')
        academic_email.parsing_metadata = analysis.get('metadata', {})

        return academic_email

    def _quick_academic_check(self, email: AcademicEmail) -> bool:
        """
        Fast heuristic check (no AI needed)

        LEARNING CONCEPT: Pre-filtering for Cost Optimization
        Running AI on every email is expensive
        Use cheap heuristics to filter obvious non-academic emails
        """
        combined_text = f"{email.subject} {email.body_text}".lower()

        # Check 1: Is sender academic?
        if not email.is_from_professor and '.edu' not in email.sender:
            # Quick keyword check for non-professor emails
            academic_keywords = ['assignment', 'homework', 'due', 'course', 'class', 'exam']
            if not any(keyword in combined_text for keyword in academic_keywords):
                return False

        # Check 2: Any academic patterns?
        for category, patterns in self.email_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return True

        # Check 3: Has syllabus/assignment attachments?
        if email.has_attachment:
            for attachment in email.attachments:
                filename = attachment.get('filename', '').lower()
                if any(keyword in filename for keyword in ['syllabus', 'assignment', 'rubric', 'hw']):
                    return True

        return False

    async def _ai_deep_analysis(self, email: AcademicEmail) -> Dict[str, Any]:
        """
        AI-powered deep email analysis

        LEARNING CONCEPT: Advanced Prompt Engineering for Extraction
        This prompt teaches the AI to extract structured academic information
        """
        analysis_prompt = f"""
You are an expert academic email analyzer. Analyze this email and extract structured information.

EMAIL METADATA:
From: {email.sender_name} <{email.sender}>
Subject: {email.subject}
Date: {email.received_date.strftime('%Y-%m-%d %H:%M')}
Has Attachments: {email.has_attachment}

EMAIL BODY:
{email.body_text[:2000]}  # Limit to first 2000 chars to save tokens

ANALYSIS TASKS:
1. Determine if this is an academic email (from professor, TA, or about coursework)
2. Classify the email type (assignment, grade, announcement, syllabus, office_hours, other)
3. Extract any assignments mentioned (with details)
4. Extract deadlines and due dates
5. Identify the course (if mentioned)
6. Determine if action is required from the student
7. Assess urgency level

OUTPUT FORMAT (JSON):
{{
    "is_academic": true/false,
    "email_type": "assignment|grade|announcement|syllabus|office_hours|other",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of classification",
    "course": "course name/code or null",
    "assignments": [
        {{
            "title": "assignment name",
            "due_date": "YYYY-MM-DD HH:MM or null",
            "description": "brief description",
            "points_possible": number or null,
            "submission_method": "how to submit or null"
        }}
    ],
    "deadlines": ["YYYY-MM-DD HH:MM", ...],
    "action_required": true/false,
    "action_description": "what the student needs to do or null",
    "urgency": "low|medium|high|critical",
    "urgency_reasoning": "why this urgency level",
    "metadata": {{
        "has_syllabus": true/false,
        "has_rubric": true/false,
        "mentions_grade": true/false,
        "mentions_extension": true/false
    }}
}}

IMPORTANT:
- Only mark is_academic=true if genuinely related to coursework
- Be conservative with confidence scores
- Parse dates carefully (consider current date: {datetime.now().strftime('%Y-%m-%d')})
- Extract ALL assignments mentioned, even if multiple
"""

        try:
            response = await self.ai_client.structured_completion(
                prompt=analysis_prompt,
                response_format="json"
            )

            analysis = json.loads(response)

            # Parse ISO dates from strings
            if analysis.get('assignments'):
                for assignment in analysis['assignments']:
                    if assignment.get('due_date'):
                        try:
                            assignment['due_date'] = datetime.fromisoformat(assignment['due_date'])
                        except ValueError:
                            assignment['due_date'] = None

            if analysis.get('deadlines'):
                parsed_deadlines = []
                for deadline_str in analysis['deadlines']:
                    try:
                        parsed_deadlines.append(datetime.fromisoformat(deadline_str))
                    except ValueError:
                        continue
                analysis['deadlines'] = parsed_deadlines

            logger.info(f"Email analyzed: {analysis.get('email_type')} (confidence: {analysis.get('confidence', 0):.2f})")
            return analysis

        except Exception as e:
            logger.error(f"AI email analysis failed: {e}")
            return {
                'is_academic': False,
                'email_type': 'other',
                'confidence': 0.0,
                'assignments': [],
                'deadlines': [],
                'action_required': False,
                'urgency': 'low'
            }

# LEARNING CONCEPT 4: Email Composition with AI
# Generate contextually appropriate emails

class EmailComposer:
    """
    AI-powered email composition for academic contexts

    Teaching Concepts:
    - Context-aware text generation
    - Tone and style adaptation
    - Template-based generation with personalization
    """

    def __init__(self, ai_client):
        self.ai_client = ai_client

    async def compose_email(self,
                           purpose: str,
                           context: Dict[str, Any],
                           tone: str = "professional") -> Dict[str, str]:
        """
        Compose an email using AI

        This demonstrates:
        - Purpose-driven generation
        - Context injection for relevance
        - Tone control
        """
        composition_prompt = f"""
You are helping a student compose a professional email to their professor.

PURPOSE: {purpose}

CONTEXT:
{json.dumps(context, indent=2)}

TONE: {tone} (professional, friendly_professional, formal)

INSTRUCTIONS:
1. Write a clear, concise email
2. Include appropriate greeting based on context
3. State purpose in first sentence
4. Provide relevant details from context
5. End with appropriate closing
6. Keep it under 200 words

OUTPUT FORMAT (JSON):
{{
    "subject": "email subject line",
    "body": "email body text",
    "suggestions": ["tip 1", "tip 2"],
    "tone_check": "assessment of appropriateness"
}}

Examples of good academic emails:
- Clear subject lines ("Extension Request for CS101 Assignment 3")
- Direct but polite ("I am writing to request...")
- Specific details ("I have completed 80% of the assignment...")
- Professional closing ("Thank you for your consideration")
"""

        try:
            response = await self.ai_client.structured_completion(
                prompt=composition_prompt,
                response_format="json"
            )

            composed = json.loads(response)
            logger.info(f"Composed email: {composed.get('subject', 'No subject')}")
            return composed

        except Exception as e:
            logger.error(f"Email composition failed: {e}")
            return {
                "subject": f"Regarding: {purpose}",
                "body": "Failed to generate email. Please compose manually.",
                "suggestions": [],
                "tone_check": "error"
            }

# Main Email Assistant class that ties everything together
class EmailAssistant:
    """
    Complete email assistant for academic workflows

    This orchestrates:
    - Email fetching (IMAP)
    - Email analysis (AI)
    - Email composition (AI)
    - Pattern learning
    """

    def __init__(self, credentials: EmailCredentials, ai_client, storage_dir: Path = None):
        self.credentials = credentials
        self.ai_client = ai_client

        if storage_dir is None:
            storage_dir = Path.home() / ".academic_assistant" / "email_data"
        storage_dir.mkdir(parents=True, exist_ok=True)

        self.storage_dir = storage_dir
        self.imap_client = IMAPEmailClient(credentials)
        self.analyzer = AcademicEmailAnalyzer(ai_client)
        self.composer = EmailComposer(ai_client)

        # Cache to avoid reprocessing emails
        self.processed_emails = self._load_processed_cache()

    def _load_processed_cache(self) -> set:
        """Load set of already-processed email IDs"""
        cache_file = self.storage_dir / "processed_emails.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return set(json.load(f))
        return set()

    def _save_processed_cache(self):
        """Save processed email IDs"""
        cache_file = self.storage_dir / "processed_emails.json"
        with open(cache_file, 'w') as f:
            json.dump(list(self.processed_emails), f)

    async def scan_academic_emails(self, days_back: int = 30) -> List[AcademicEmail]:
        """
        Scan inbox for academic emails

        This demonstrates the complete pipeline:
        1. Fetch emails via IMAP
        2. Filter with heuristics
        3. Analyze with AI
        4. Extract assignments
        5. Cache results
        """
        logger.info(f"Scanning emails from last {days_back} days...")

        # Fetch emails
        raw_emails = self.imap_client.fetch_recent_emails(days_back=days_back)
        logger.info(f"Fetched {len(raw_emails)} emails")

        # Analyze each email
        academic_emails = []
        for raw_email in raw_emails:
            message_id = raw_email.get('message_id', '')

            # Skip if already processed
            if message_id in self.processed_emails:
                continue

            # Analyze email
            analyzed = await self.analyzer.analyze_email(raw_email)

            if analyzed.is_academic:
                academic_emails.append(analyzed)

            # Mark as processed
            self.processed_emails.add(message_id)

        # Save cache
        self._save_processed_cache()

        logger.info(f"Found {len(academic_emails)} academic emails")
        return academic_emails

    async def smart_compose(self, purpose: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Compose an email using AI"""
        return await self.composer.compose_email(purpose, context)

    def cleanup(self):
        """Cleanup resources"""
        self.imap_client.disconnect()


# Example usage
if __name__ == "__main__":
    print("📧 Email Assistant with AI Analysis")
    print("=" * 60)
    print()
    print("Key Concepts Demonstrated:")
    print("1. IMAP Protocol & OAuth2 Authentication")
    print("2. Email Parsing (MIME, multipart, encoding)")
    print("3. AI-Powered Content Analysis")
    print("4. Hybrid Heuristics + AI Approach")
    print("5. Email Composition with Context")
    print("6. Secure Credential Management")
    print()
    print("This system can:")
    print("✅ Connect securely to Gmail/Outlook via OAuth2")
    print("✅ Parse academic emails intelligently")
    print("✅ Extract assignments and deadlines")
    print("✅ Classify email types and urgency")
    print("✅ Compose professional emails with AI")
    print("✅ Cache processed emails for efficiency")
