"""
Firebase Realtime Synchronization Service
=========================================
Handles the backend mirroring of AI inference results to Firebase RTDB.
Ensures cross-platform data persistence and resilient live updates.
"""

from __future__ import annotations
import os
import json
import logging
from typing import Dict, Any

try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_ENABLED = True
except ImportError:
    FIREBASE_ENABLED = False

from config import settings
from services.cloud_logger import ops_logger

class FirebaseSyncService:
    """
    Elite service for pushing stadium state to Google Firebase.
    """
    def __init__(self):
        self.enabled = FIREBASE_ENABLED and settings.SYNC_TO_FIREBASE
        self.app = None
        
        if self.enabled:
            try:
                # In production (Cloud Run), it uses the compute engine service account.
                # Locally, it looks for the credential file in environment variables.
                cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    self.app = firebase_admin.initialize_app(cred, {
                        'databaseURL': settings.FIREBASE_DB_URL
                    })
                else:
                    # Fallback to Application Default Credentials (ADC)
                    self.app = firebase_admin.initialize_app(options={
                        'databaseURL': settings.FIREBASE_DB_URL
                    })
                
                ops_logger.info(f"✅ Firebase Cloud Sync initialized: {settings.FIREBASE_DB_URL}")
            except Exception as e:
                ops_logger.error(f"❌ Firebase initialization failed: {e}")
                self.enabled = False

    def sync_stadium_state(self, zones_data: Dict[str, Any], insights: list, alerts: list):
        """
        Pushes a snapshot of the current AI state to the stadium_live_ops node.
        """
        if not self.enabled:
            return

        try:
            ref = db.reference('stadium_live_ops')
            ref.set({
                "zones": zones_data,
                "insights": insights,
                "alerts": alerts,
                "last_sync": {".sv": "timestamp"},  # Server-side timestamp
                "system_status": "OPTIMAL"
            })
        except Exception as e:
            error_str = str(e)
            ops_logger.error(f"❌ Firebase Sync Error: {e}")
            if "default credentials" in error_str.lower() or "credentials" in error_str.lower():
                ops_logger.warning("Disabling Firebase Sync to prevent log spam due to missing credentials.")
                self.enabled = False

    def report_event(self, event_type: str, data: Dict[str, Any]):
        """
        Logs high-priority operational events to the event_log node.
        """
        if not self.enabled:
            return
            
        try:
            event_ref = db.reference('event_log').push()
            event_ref.set({
                "type": event_type,
                "timestamp": {".sv": "timestamp"},
                "data": data
            })
        except Exception as e:
            error_str = str(e)
            ops_logger.error(f"❌ Firebase Event Reporting Error: {e}")
            if "default credentials" in error_str.lower() or "credentials" in error_str.lower():
                self.enabled = False


# Singleton instance
firebase_sync = FirebaseSyncService()
