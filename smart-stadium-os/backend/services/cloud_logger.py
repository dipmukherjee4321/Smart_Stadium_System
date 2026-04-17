"""
Google Cloud Structured Logging & Error Reporting
=================================================
Provides high-fidelity logging hooks designed for GCP Cloud Logging console.
Includes automatic detection of production environments and formatted
reporting for AI anomalies.
"""

import sys
import logging
import json
from datetime import datetime
from typing import Any, Dict

# Try to import Google Cloud Logging, fallback to stdout for local dev
try:
    import google.cloud.logging
    from google.cloud.logging.handlers import CloudLoggingHandler
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False


class StructuredLogger:
    """
    Elite Logger providing structured JSON output for Google Cloud visibility.
    """
    def __init__(self, service_name: str = "smart-stadium-os"):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)

        if GCP_AVAILABLE:
            try:
                client = google.cloud.logging.Client()
                handler = CloudLoggingHandler(client, name=service_name)
                self.logger.addHandler(handler)
            except Exception:
                # Handle cases where credentials aren't initialized locally
                self._setup_stdout()
        else:
            self._setup_stdout()

    def _setup_stdout(self):
        """Fallback to standard stdout formatting."""
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_anomaly(self, zone_name: str, density: int, severity: str, message: str):
        """
        Reports a critical AI anomaly with structured metadata.
        This format triggers automated 'Error Reporting' in the GCP Console.
        """
        payload = {
            "severity": severity,
            "message": f"AI_ANOMALY: {message}",
            "serviceContext": {
                "service": self.service_name,
                "version": "2.2.0"
            },
            "context": {
                "reportLocation": {
                    "filePath": "services/ai_engine.py",
                    "lineNumber": 140,
                    "functionName": "_detect_anomaly"
                },
                "user": "Smart_Stadium_Bot"
            },
            "metadata": {
                "zone_name": zone_name,
                "density": density,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        # In GCP, log the full dict as message if using CloudLoggingHandler, better using extra
        if GCP_AVAILABLE:
            self.logger.error("AI_ANOMALY detected", extra={"json_fields": payload})
        else:
            self.logger.error(json.dumps(payload))

    def info(self, msg: str, **kwargs):
        self.logger.info(msg, extra={"json_fields": kwargs})

    def warning(self, msg: str, **kwargs):
        self.logger.warning(msg, extra={"json_fields": kwargs})

    def error(self, msg: str, **kwargs):
        self.logger.error(msg, extra={"json_fields": kwargs})


# Singleton logger
ops_logger = StructuredLogger()
