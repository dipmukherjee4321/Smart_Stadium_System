"""
Google Cloud Secret Manager Service.
Handles secure retrieval of sensitive configurations (Firebase, JWT Secrets).
"""

import os
import json
from google.cloud import secretmanager
from services.cloud_logger import ops_logger as logger
from config import settings

class SecretManagerService:
    def __init__(self):
        self._client = None
        self.project_id = settings.GCP_PROJECT_ID

    @property
    def client(self):
        """Lazy client initialization to prevent crashes if credentials are missing."""
        if self._client is None:
            try:
                self._client = secretmanager.SecretManagerServiceClient()
            except Exception as e:
                logger.warning(f"Could not initialize Secret Manager client: {e}")
        return self._client

    def get_secret(self, secret_id: str, version_id: str = "latest") -> str:
        """
        Retrieves a secret from GCP Secret Manager.
        Falls back to environment variables if the API call fails or is local.
        """
        if not self.client:
            return os.getenv(secret_id, "")

        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.warning(f"Failed to fetch secret '{secret_id}' from GCP: {e}. Falling back to ENV.")
            return os.getenv(secret_id, "")

    def get_firebase_config(self) -> dict:
        """
        Fetches and parses the Firebase Service Account JSON from secrets.
        """
        secret_json = self.get_secret("FIREBASE_SERVICE_ACCOUNT")
        if not secret_json:
            return {}
        try:
            return json.loads(secret_json)
        except json.JSONDecodeError:
            logger.error("FIREBASE_SERVICE_ACCOUNT secret is not valid JSON.")
            return {}

# Singleton instance
secret_service = SecretManagerService()
