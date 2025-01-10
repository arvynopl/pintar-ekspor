# /backend/app/services/email/email_service.py
from typing import Optional, Dict
import httpx
from fastapi import HTTPException
from datetime import datetime, timedelta
from ...core.config import get_settings

settings = get_settings()

class EmailService:
    """
    Service class for handling email operations using FinTrackIt API.
    Implements token management and email sending functionality.
    """
    
    def __init__(self):
        self.auth_base_url = "https://api.fintrackit.my.id/v1/auth"
        self.email_base_url = "https://api.fintrackit.my.id/v1/secure"
        self.api_key = settings.FINTRACKIT_API_KEY
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        
    async def _get_access_token(self) -> str:
        """
        Get a valid access token, requesting a new one if necessary.
        
        Returns:
            str: Valid access token
            
        Raises:
            HTTPException: If token request fails
        """
        # Check if we have a valid token
        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._access_token
            
        # Request new token
        headers = {"X-API-Key": self.api_key}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_base_url}/token",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self._access_token = data["access_token"]
                    # Set expiry to slightly less than 1 hour to ensure token validity
                    self._token_expiry = datetime.now() + timedelta(minutes=55)
                    return self._access_token
                    
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to obtain access token: {response.text}"
                )
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Authentication service error: {str(e)}"
            )
            
    async def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """
        Internal method to send emails through FinTrackIt API.
        Handles token management and request retries.
        
        Args:
            recipient (str): Recipient email address
            subject (str): Email subject
            body (str): HTML formatted email body
            
        Returns:
            bool: True if email sent successfully
            
        Raises:
            HTTPException: If email sending fails
        """
        # Get valid token
        token = await self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "recipient_email": recipient,
            "subject": subject,
            "body": body
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.email_base_url}/send-email",
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return True
                
                # If token expired, try once more with new token
                if response.status_code == 401:
                    self._access_token = None  # Force new token request
                    token = await self._get_access_token()
                    headers["Authorization"] = f"Bearer {token}"
                    
                    response = await client.post(
                        f"{self.email_base_url}/send-email",
                        headers=headers,
                        json=payload,
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        return True
                        
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Email sending failed: {response.text}"
                )
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Email service error: {str(e)}"
            )
    
    async def send_api_key_notification(
        self,
        user_email: str,
        api_key: str,
        expiry_date: Optional[str] = None
    ) -> bool:
        """
        Send API key notification for developer access.
        
        Args:
            user_email (str): Developer's email address
            api_key (str): Generated API key
            expiry_date (Optional[str]): API key expiry date if applicable
            
        Returns:
            bool: True if email sent successfully
        """
        subject = "Your Pintar Ekspor API Key"
        body = f"""
        <h2>Your API Key Has Been Generated</h2>
        <p>Here is your API key for accessing Pintar Ekspor services:</p>
        <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">{api_key}</pre>
        """
        
        if expiry_date:
            body += f"<p>This API key will expire on: {expiry_date}</p>"
            
        body += """
        <p>Important Security Notes:</p>
        <ul>
            <li>Keep this API key secure and never share it with others</li>
            <li>Use this key only in secure, server-side environments</li>
            <li>If you suspect your key has been compromised, please contact support immediately</li>
        </ul>
        <p>To get started with the API, visit our <a href="/documentation">API documentation</a>.</p>
        <br>
        <p>Best regards,</p>
        <p>Pintar Ekspor Team</p>
        """
        
        return await self._send_email(user_email, subject, body)

# Create a singleton instance
email_service = EmailService()