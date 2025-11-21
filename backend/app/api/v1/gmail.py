"""
Gmail integration endpoints.
"""
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.credential import Credential
from app.models.email import Email
from app.models.scrape_job import ScrapeJob
from app.services.gmail_service import GmailService
from app.services.encryption_service import encryption_service
from app.core.config import settings

router = APIRouter()

# In-memory state storage (in production, use Redis)
oauth_states = {}


# Pydantic schemas
class GmailAuthResponse(BaseModel):
    auth_url: str


class GmailStatus(BaseModel):
    connected: bool
    email: Optional[str] = None
    last_synced: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    last_error: Optional[str] = None
    emails_count: Optional[int] = None


class SyncGmailRequest(BaseModel):
    days_back: int = 30
    max_results: int = 100


class SyncGmailResponse(BaseModel):
    status: str
    message: str
    emails_found: int
    emails_new: int
    emails_updated: int


@router.get("/auth", response_model=GmailAuthResponse)
async def get_gmail_auth_url(
    current_user: User = Depends(get_current_user),
):
    """
    Generate Gmail OAuth authorization URL.
    """
    # Validate config
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.",
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = current_user.id

    # Generate auth URL
    auth_url = GmailService.get_auth_url(state)

    return GmailAuthResponse(auth_url=auth_url)


@router.get("/callback")
async def gmail_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth callback from Google.
    Exchanges authorization code for tokens and stores credentials.
    """
    # Validate state
    if state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter. Possible CSRF attack.",
        )

    user_id = oauth_states.pop(state)

    # Exchange code for tokens
    try:
        tokens = GmailService.exchange_code(code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {str(e)}",
        )

    # Get user email
    try:
        gmail_service = GmailService(
            tokens['access_token'],
            tokens['refresh_token']
        )
        user_email = gmail_service.get_user_email()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get user email: {str(e)}",
        )

    # Encrypt and store credentials
    credentials_data = {
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'email': user_email,
    }
    encrypted_data = encryption_service.encrypt_credentials(credentials_data)

    # Check if credential already exists
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == user_id,
            Credential.service == "gmail"
        )
    )
    existing_credential = result.scalar_one_or_none()

    if existing_credential:
        # Update existing
        existing_credential.encrypted_data = encrypted_data
        existing_credential.is_active = True
        existing_credential.last_error = None
    else:
        # Create new
        credential = Credential(
            user_id=user_id,
            service="gmail",
            encrypted_data=encrypted_data,
            is_active=True,
        )
        db.add(credential)

    await db.commit()

    # Redirect to frontend settings page
    frontend_url = settings.ALLOWED_ORIGINS[0] if settings.ALLOWED_ORIGINS else "http://localhost:3000"
    return RedirectResponse(url=f"{frontend_url}/settings?gmail=connected")


@router.get("/status", response_model=GmailStatus)
async def get_gmail_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check Gmail connection status.
    """
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id,
            Credential.service == "gmail"
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        return GmailStatus(connected=False)

    # Decrypt to get email
    try:
        creds = encryption_service.decrypt_credentials(credential.encrypted_data)
        user_email = creds.get('email')
    except Exception:
        user_email = None

    # Count emails
    result = await db.execute(
        select(Email).where(Email.user_id == current_user.id)
    )
    emails = result.scalars().all()
    emails_count = len(emails)

    return GmailStatus(
        connected=True,
        email=user_email,
        last_synced=credential.last_synced,
        last_sync_status=credential.last_sync_status,
        last_error=credential.last_error,
        emails_count=emails_count,
    )


@router.post("/sync", response_model=SyncGmailResponse)
async def sync_gmail(
    request: SyncGmailRequest = SyncGmailRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync emails from Gmail.
    """
    # Get Gmail credentials
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id,
            Credential.service == "gmail"
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gmail not connected. Please connect Gmail first.",
        )

    # Create scrape job
    scrape_job = ScrapeJob(
        user_id=current_user.id,
        credential_id=credential.id,
        service="gmail",
        job_type="email_sync",
        status="running",
        started_at=datetime.utcnow(),
    )
    db.add(scrape_job)
    await db.commit()
    await db.refresh(scrape_job)

    try:
        # Decrypt credentials
        creds = encryption_service.decrypt_credentials(credential.encrypted_data)

        # Initialize Gmail service
        gmail_service = GmailService(
            creds['access_token'],
            creds['refresh_token']
        )

        # Build query for academic emails
        query = 'subject:(assignment OR homework OR due OR deadline OR exam OR quiz OR project OR grade)'

        # Fetch messages
        messages = gmail_service.list_messages(
            max_results=request.max_results,
            query=query,
            days_back=request.days_back
        )

        emails_new = 0
        emails_updated = 0
        emails_found = len(messages)

        # Process each message
        for message in messages:
            parsed = gmail_service.parse_message(message)

            # Only process academic emails
            if not parsed['is_academic']:
                continue

            gmail_message_id = parsed['gmail_message_id']

            # Check if email already exists
            result = await db.execute(
                select(Email).where(
                    Email.user_id == current_user.id,
                    Email.gmail_message_id == gmail_message_id
                )
            )
            existing_email = result.scalar_one_or_none()

            if existing_email:
                # Update existing email
                for key, value in parsed.items():
                    if key not in ['gmail_message_id', 'user_id']:
                        setattr(existing_email, key, value)
                emails_updated += 1
            else:
                # Create new email
                new_email = Email(
                    user_id=current_user.id,
                    **parsed
                )
                db.add(new_email)
                emails_new += 1

        await db.commit()

        # Update scrape job
        scrape_job.status = "completed"
        scrape_job.completed_at = datetime.utcnow()
        scrape_job.items_found = emails_found
        scrape_job.items_new = emails_new
        scrape_job.results_summary = {
            'emails_found': emails_found,
            'emails_new': emails_new,
            'emails_updated': emails_updated,
        }

        # Update credential
        credential.last_synced = datetime.utcnow()
        credential.last_sync_status = "success"
        credential.sync_count = (credential.sync_count or 0) + 1

        await db.commit()

        return SyncGmailResponse(
            status="success",
            message=f"Successfully synced {emails_found} emails ({emails_new} new, {emails_updated} updated)",
            emails_found=emails_found,
            emails_new=emails_new,
            emails_updated=emails_updated,
        )

    except Exception as e:
        # Update scrape job with error
        scrape_job.status = "failed"
        scrape_job.completed_at = datetime.utcnow()
        scrape_job.error_message = str(e)

        credential.last_sync_status = "failed"
        credential.last_error = str(e)

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync Gmail data: {str(e)}",
        )


@router.post("/disconnect")
async def disconnect_gmail(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disconnect Gmail account (delete credentials).
    """
    result = await db.execute(
        select(Credential).where(
            Credential.user_id == current_user.id,
            Credential.service == "gmail"
        )
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gmail account not connected",
        )

    await db.delete(credential)
    await db.commit()

    return {"status": "success", "message": "Gmail account disconnected"}
