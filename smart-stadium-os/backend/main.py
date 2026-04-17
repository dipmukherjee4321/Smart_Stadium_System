"""
Smart Stadium OS — Enterprise AI Core
======================================
Main entry point for the FastAPI application.
Initialises middleware, routing, and background AI simulation.
"""

import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import settings
from routes import routing, alerts, health, security
from services.websocket_manager import manager
from services.ai_engine import ai_engine
from services.cloud_logger import ops_logger as logger
from utils.rate_limiter import RateLimiterMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown lifecycle events.
    Launches the background AI simulation engine.
    """
    logger.info("Initializing Smart Stadium AI Engine...")
    
    # Inject manager into engine for broadcasting
    ai_engine.set_manager(manager)
    
    # Initialize Core Google Cloud Services
    from services.gcp_services import gcp_aux
    gcp_aux.initialize_integrations()
    
    # Start AI loop in the background
    simulation_task = asyncio.create_task(ai_engine.run_simulation())
    
    logger.info("Startup complete. System status: Operational.")
    yield
    
    # Clean up on shutdown
    simulation_task.cancel()
    try:
        await simulation_task
    except asyncio.CancelledError:
        pass
    logger.info("System shutdown complete.")


# Initialize FastAPI with metadata
app = FastAPI(
    title="Smart Stadium OS",
    description="Next-generation crowd management and AI-enhanced navigation system.",
    version="2.1.0",
    lifespan=lifespan
)

# ---------------------------------------------------------------------------
# Middleware Configuration
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Security: Elite Headers Middleware
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Security: Rate Limiting
app.add_middleware(RateLimiterMiddleware)

# Security: Hardened CORS (Configurable via ENV for Production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# ---------------------------------------------------------------------------
# API Routing
# ---------------------------------------------------------------------------

app.include_router(security.router, prefix="/api/security", tags=["Auth"])
app.include_router(routing.router, prefix="/api/nav", tags=["Navigation"])
app.include_router(alerts.router, prefix="/api/safety", tags=["Safety"])
app.include_router(health.router, prefix="/api/ops", tags=["Ops"])


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    Handles real-time data streaming to connected Digital Twin clients.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; ignore individual client text in favor of broadcast
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        manager.disconnect(websocket)


# ---------------------------------------------------------------------------
# Static SPA Serving (Cloud Run Optimized)
# ---------------------------------------------------------------------------

if os.path.exists("./static"):
    # Serve assets folder
    app.mount("/assets", StaticFiles(directory="./static/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa_catchall(request: Request, full_path: str):
        """
        Catch-all route to serve the SPA (React).
        Ensures internal API routes are protected.
        """
        # Protect internal API routes — these should be handled by include_router above
        if full_path.startswith("api/"):
            return None 

        index_path = os.path.join("./static", "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return {"error": "Frontend artifacts missing"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
