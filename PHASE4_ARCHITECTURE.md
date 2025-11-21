# Phase 4 Architecture: Gmail Integration

## Overview

Add Gmail integration to automatically aggregate assignment-related emails from the user's inbox. Uses OAuth 2.0 for secure authentication and the Gmail API for email access.

## Architecture Components

### 1. OAuth 2.0 Flow

**Standard OAuth Flow:**
```
1. User clicks "Connect Gmail" → Frontend
2. Frontend requests auth URL → Backend /gmail/auth
3. Backend generates OAuth URL with scopes → Returns to frontend
4. Frontend redirects to Google OAuth consent screen
5. User grants permissions → Google redirects to callback URL
6. Callback receives auth code → Backend /gmail/callback?code=xxx
7. Backend exchanges code for tokens (access + refresh)
8. Backend encrypts and stores tokens → Database
9. Backend redirects to frontend success page
```

**Token Management:**
- Access token: Valid for 1 hour
- Refresh token: Long-lived (revocable)
- Store both encrypted in Credential model
- Refresh access token automatically when expired

### 2. Gmail API Client

**Required Scopes:**
```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
    'https://www.googleapis.com/auth/userinfo.email'    # Get user email
]
```

**Gmail Service (`backend/app/services/gmail_service.py`):**
- OAuth client initialization
- Token refresh logic
- Email fetching with filters
- Email parsing (subject, sender, body, date)
- Batch processing for multiple emails

### 3. Email Filtering Strategy

**Primary Filters:**
```python
# Query filters for Gmail API
filters = {
    'q': 'subject:(assignment OR homework OR due OR deadline OR exam OR quiz OR project)',
    'maxResults': 100,
    'labelIds': ['INBOX'],
}
```

**Additional Filtering (Server-side):**
- Academic domains: `.edu`, `instructure.com`, `gradescope.com`, etc.
- Date mentions: Parse for dates in subject/body
- Exclude: Promotional emails, newsletters, automated notifications

**Email Categories:**
- `assignment` - Assignment notifications
- `deadline` - Deadline reminders
- `grade` - Grade notifications
- `announcement` - Course announcements
- `other` - Uncategorized academic email

### 4. Data Extraction

**From Email Content:**
- **Subject**: Extract assignment name, course code
- **Sender**: Identify instructor, platform (Canvas, Gradescope)
- **Body**: Parse HTML/plain text for:
  - Due dates (regex patterns, date parsing)
  - Assignment details
  - Links to external platforms
  - Action items

**Date Extraction Patterns:**
```python
patterns = [
    r'due (?:on |by )?(\d{1,2}/\d{1,2}/\d{2,4})',
    r'deadline[:\s]+(\w+ \d{1,2},? \d{4})',
    r'submit by (\d{1,2}:\d{2} [AP]M)',
]
```

### 5. Database Schema (Email Model)

Already created in Phase 1:
```python
class Email(Base):
    user_id: int
    gmail_message_id: str (unique)
    thread_id: str
    subject: str
    sender: str
    recipient: str
    body: str (HTML or plain text)
    snippet: str (preview)
    received_at: datetime

    # Classification
    category: str (assignment, deadline, grade, etc.)
    is_academic: bool

    # Extracted data
    extracted_dates: List[str] (JSON)
    extracted_action_items: List[str] (JSON)

    # Relationships
    course_id: int (nullable)
    assignment_id: int (nullable)

    # Approval
    approved: bool (default False)
```

### 6. Backend API Endpoints

**GET `/api/v1/gmail/auth`**
```python
# Generate OAuth authorization URL
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

**GET `/api/v1/gmail/callback`**
```python
# OAuth callback (receives auth code)
# Query params: code, state
# Exchanges code for tokens
# Stores encrypted tokens
# Redirects to frontend: /settings?gmail=connected
```

**GET `/api/v1/gmail/status`**
```python
# Check Gmail connection status
{
  "connected": true,
  "email": "user@gmail.com",
  "last_synced": "2025-11-21T10:30:00Z",
  "last_sync_status": "success",
  "emails_count": 45
}
```

**POST `/api/v1/gmail/sync`**
```python
# Sync emails from Gmail
# Optional body: { "days_back": 30 }
{
  "status": "success",
  "emails_found": 28,
  "emails_new": 15,
  "emails_updated": 13
}
```

**POST `/api/v1/gmail/disconnect`**
```python
# Revoke tokens and delete credentials
{
  "status": "success",
  "message": "Gmail disconnected"
}
```

### 7. Frontend Components

**Settings Page Enhancement:**
- "Connect Gmail" button
- Opens OAuth popup or redirects
- Shows connection status
- "Sync Now" button (similar to Canvas)
- Last sync timestamp

**New: Emails Page (`/emails`):**
- List of synced emails
- Filter by category, date, course
- Pending approvals section
- Link email to assignment
- Create assignment from email

**OAuth Callback Page (`/auth/gmail/callback`):**
- Receives OAuth redirect
- Extracts code from URL params
- Calls backend callback endpoint
- Shows loading state
- Redirects to Settings with success message

### 8. Security Considerations

**Token Storage:**
- Encrypt OAuth tokens using encryption_service
- Store refresh token for long-term access
- Never expose tokens to frontend

**OAuth Security:**
- Use state parameter to prevent CSRF
- Validate state on callback
- Use HTTPS for all OAuth URLs
- Short-lived access tokens (1 hour)

**Scopes:**
- Request minimal scopes (readonly only)
- No email sending permission
- No email deletion permission

**Privacy:**
- User can disconnect anytime
- Clear what emails are accessed
- Emails stored with approval flag

### 9. Implementation Plan

**Step 1: Google Cloud Setup**
- Create Google Cloud project
- Enable Gmail API
- Create OAuth 2.0 credentials (Web application)
- Add authorized redirect URIs:
  - `https://assignment-calendar-sync-production.up.railway.app/api/v1/gmail/callback`
- Get Client ID and Client Secret

**Step 2: Backend - Gmail Service**
- Install dependencies: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
- Create `GmailService` class with OAuth flow
- Implement token refresh logic
- Implement email fetching with filters
- Implement email parsing

**Step 3: Backend - API Endpoints**
- Create `gmail.py` router
- Implement `/auth` endpoint (generate OAuth URL)
- Implement `/callback` endpoint (exchange code for tokens)
- Implement `/status` endpoint
- Implement `/sync` endpoint (fetch and store emails)
- Implement `/disconnect` endpoint

**Step 4: Backend - Email Processing**
- Email filtering logic
- Date extraction with regex
- Action item extraction
- Category classification (rule-based initially)

**Step 5: Frontend - Gmail Connection**
- Update Settings page with Gmail section
- Implement OAuth popup/redirect flow
- Create callback handler page
- Add sync button with loading states

**Step 6: Frontend - Email Display**
- Create new Emails page
- Email list component
- Filtering and search
- Approval workflow (similar to assignments)
- Link to assignment functionality

**Step 7: Testing**
- Test OAuth flow end-to-end
- Test email syncing with real Gmail account
- Test filtering and categorization
- Test approval workflow
- Test error handling

### 10. Dependencies

**Backend (requirements.txt):**
```
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.116.0
```

**Frontend:**
- No additional dependencies needed
- Use existing React Router for callback handling

### 11. Environment Variables

Add to backend `.env`:
```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=https://assignment-calendar-sync-production.up.railway.app/api/v1/gmail/callback
```

### 12. Future Enhancements

**Phase 4.1:**
- AI-powered email classification (OpenAI, Claude)
- Smart action item extraction
- Automatic assignment creation from emails

**Phase 4.2:**
- Email threading support
- Reply detection
- Conversation history

**Phase 4.3:**
- Email labels sync
- Custom filter rules
- Notification preferences

**Phase 4.4:**
- Calendar event extraction
- Meeting link detection
- Attachment handling

## Expected Outcomes

After Phase 4 completion:
- ✅ Users can connect Gmail with OAuth
- ✅ Automatically sync assignment-related emails
- ✅ Categorize and filter emails
- ✅ Extract due dates and action items
- ✅ Link emails to courses and assignments
- ✅ Approval workflow for email-based assignments
- ✅ Secure token storage with encryption

## Success Metrics

- OAuth flow completion rate: >95%
- Email sync accuracy: >90% (correct academic emails)
- Date extraction accuracy: >85%
- Average sync time: <10 seconds for 100 emails
- User approval rate: >70% (emails deemed useful)
