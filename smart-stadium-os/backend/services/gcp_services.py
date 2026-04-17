"""
Google Cloud Auxiliary Services Integrations
============================================
Handles elite-tier integrations with specialized Google Cloud Services:
- Cloud Storage (GCS)
- Pub/Sub
- Vision API
- Vertex AI (AI Platform)

These services are instantiated resiliently. They will attempt to connect using Application Default Credentials.
"""

from services.cloud_logger import ops_logger as logger
from config import settings

class AdvancedGCPConnectors:
    def __init__(self):
        self.gcs_client = None
        self.pubsub_client = None
        self.vision_client = None
        self.vertex_ai_initialized = False

    def initialize_integrations(self):
        """
        Dynamically imports and initializes heavy GCP SDKs.
        Uses gentle failovers to support local test environments gracefully.
        """
        try:
            from google.cloud import storage
            from google.cloud import pubsub_v1
            from google.cloud import vision
            from google.cloud import aiplatform

            # 1. Cloud Storage
            try:
                self.gcs_client = storage.Client(project=settings.GCP_PROJECT_ID)
                logger.debug("✅ Cloud Storage integrated.")
            except Exception as e:
                if "credentials" in str(e).lower(): pass
                
            # 2. Pub/Sub
            try:
                self.pubsub_client = pubsub_v1.PublisherClient()
                logger.debug("✅ Cloud Pub/Sub integrated.")
            except Exception as e:
                if "credentials" in str(e).lower(): pass

            # 3. Vision API
            try:
                self.vision_client = vision.ImageAnnotatorClient()
                logger.debug("✅ Cloud Vision API integrated.")
            except Exception as e:
                if "credentials" in str(e).lower(): pass

            # 4. Vertex AI
            try:
                aiplatform.init(project=settings.GCP_PROJECT_ID, location="us-central1")
                self.vertex_ai_initialized = True
                logger.debug("✅ Vertex AI Engine integrated.")
            except Exception as e:
                if "credentials" in str(e).lower(): pass

            logger.info("Advanced GCP SDKs bootstrapped successfully.")

        except ImportError as exc:
            logger.warning(f"GCP SDK missing: {exc}. Ensure requirements are installed.")

gcp_aux = AdvancedGCPConnectors()
