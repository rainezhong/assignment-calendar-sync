"""
Encryption service for securely storing credentials.
Uses Fernet symmetric encryption with a secret key from environment.
"""
import json
from cryptography.fernet import Fernet
from typing import Dict, Optional
from app.core.config import settings


class EncryptionService:
    """Service for encrypting and decrypting credential data."""

    def __init__(self):
        """Initialize encryption service with key from settings."""
        # Use SECRET_KEY from settings as encryption key
        # Fernet requires a 32 url-safe base64-encoded bytes key
        # We'll derive it from SECRET_KEY
        self.cipher = self._get_cipher()

    def _get_cipher(self) -> Fernet:
        """
        Get Fernet cipher from settings.

        Returns:
            Fernet cipher instance
        """
        # For now, use SECRET_KEY directly
        # In production, use a dedicated ENCRYPTION_KEY
        key = settings.SECRET_KEY.encode()

        # Fernet needs exactly 32 url-safe base64-encoded bytes
        # We'll use a simple approach: hash the key and encode
        from base64 import urlsafe_b64encode
        from hashlib import sha256

        # Hash the secret key to get 32 bytes, then base64 encode
        key_bytes = sha256(key).digest()
        fernet_key = urlsafe_b64encode(key_bytes)

        return Fernet(fernet_key)

    def encrypt_credentials(self, credentials: Dict) -> str:
        """
        Encrypt credentials dictionary to string.

        Args:
            credentials: Dictionary of credential data

        Returns:
            Encrypted string (safe to store in database)
        """
        try:
            # Convert dict to JSON string
            json_data = json.dumps(credentials)

            # Encrypt
            encrypted_bytes = self.cipher.encrypt(json_data.encode())

            # Return as string
            return encrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Failed to encrypt credentials: {e}")

    def decrypt_credentials(self, encrypted_data: str) -> Dict:
        """
        Decrypt encrypted credentials string back to dictionary.

        Args:
            encrypted_data: Encrypted credentials string from database

        Returns:
            Decrypted credentials dictionary
        """
        try:
            # Decrypt
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())

            # Parse JSON
            json_data = decrypted_bytes.decode()
            credentials = json.loads(json_data)

            return credentials
        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {e}")


# Global instance
encryption_service = EncryptionService()
