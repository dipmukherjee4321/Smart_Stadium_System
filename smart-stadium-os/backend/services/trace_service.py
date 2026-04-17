"""
Google Cloud Trace Service.
Instruments the AI logic for production-grade observability.
Falls back to a no-op tracer in local/dev environments gracefully.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from config import settings
from services.cloud_logger import ops_logger as logger


class TraceService:
    """Wraps OpenTelemetry Tracer with GCP Cloud Trace export."""

    def __init__(self) -> None:
        self.project_id = settings.GCP_PROJECT_ID
        self.enabled = False
        self._tracer: trace.Tracer

        try:
            # Attempt to import the GCP exporter (requires google-cloud-trace)
            from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter  # type: ignore
            from opentelemetry.propagators.cloud_trace_propagator import CloudTraceFormatPropagator  # type: ignore
            from opentelemetry.propagate import set_global_textmap

            set_global_textmap(CloudTraceFormatPropagator())
            provider = TracerProvider()
            exporter = CloudTraceSpanExporter(project_id=self.project_id)
            provider.add_span_processor(SimpleSpanProcessor(exporter))
            trace.set_tracer_provider(provider)
            self._tracer = trace.get_tracer("smart-stadium-ai", "2.3.0")
            self.enabled = True
            logger.info("Cloud Trace instrumentation initialized successfully.")

        except Exception as e:
            # Fall back to in-memory (local dev) tracer so the app still starts
            logger.warning(f"Cloud Trace init skipped ({e}). Using in-memory tracer.")
            provider = TracerProvider()
            provider.add_span_processor(SimpleSpanProcessor(InMemorySpanExporter()))
            trace.set_tracer_provider(provider)
            self._tracer = trace.get_tracer("smart-stadium-ai-local", "2.3.0")

    def get_tracer(self) -> trace.Tracer:
        """Returns the configured OpenTelemetry tracer."""
        return self._tracer


# Singleton — import `tracer` directly to create spans
trace_service = TraceService()
tracer = trace_service.get_tracer()
