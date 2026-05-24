# ====================================================================================================
# server/main.py — FINAL with keep-alive
# ====================================================================================================
"""
HDM AI — Main Application Entry Point
FastAPI Server | Port 5002 | Production Ready
7 Services | 128 Endpoints | MongoDB + Redis
"""

import sys
import os
import asyncio as _asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from config import settings
from db.session import init_db, close_db

# ================================================================================================
# LOGGING
# ================================================================================================

os.makedirs(settings.LOG_DIR, exist_ok=True)

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)
logger.add(
    f"{settings.LOG_DIR}/hdm_ai_{{time:YYYY-MM-DD}}.log",
    rotation="10 MB",
    retention=f"{settings.LOG_RETENTION_DAYS} days",
    level="INFO",
)
logger.add(
    f"{settings.LOG_DIR}/errors_{{time:YYYY-MM-DD}}.log",
    rotation="10 MB",
    retention="30 days",
    level="ERROR",
)

# ================================================================================================
# LIFESPAN
# ================================================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    logger.info(f"╔══════════════════════════════════════════════╗")
    logger.info(f"║  {settings.APP_NAME} v{settings.VERSION}                         ║")
    logger.info(f"║  Environment: {settings.ENVIRONMENT.ljust(31)}║")
    logger.info(f"║  Port: {str(settings.PORT).ljust(36)}║")
    logger.info(f"╚══════════════════════════════════════════════╝")

    # MongoDB
    try:
        await init_db()
    except Exception as e:
        logger.error(f"MongoDB: FAILED — {e}")
        logger.warning("Running without database — auth, chat, and persistence disabled")

    # Redis
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        logger.info("Redis: CONNECTED")
    except Exception:
        logger.warning("Redis: UNAVAILABLE — rate limiting disabled")

    # AI Providers
    if settings.GROQ_API_KEY:
        logger.info("Groq: CONFIGURED")
    else:
        logger.warning("Groq: MISSING — AI chat disabled")

    if settings.GEMINI_API_KEY:
        logger.info("Gemini: CONFIGURED")
    else:
        logger.warning("Gemini: MISSING — image/vision disabled")

    # ================================================================================================
    # KEEP-ALIVE (Prevent Render free tier sleep)
    # ================================================================================================
    if settings.ENVIRONMENT == "production":
        try:
            from keep_alive import keep_alive as _keep_alive_loop
            _asyncio.create_task(_keep_alive_loop())
            logger.info("Keep-alive: ENABLED (self-ping every 9 minutes)")
        except Exception as e:
            logger.warning(f"Keep-alive: FAILED — {e}")

    yield

    # Shutdown
    try:
        await close_db()
    except:
        pass
    logger.info(f"{settings.APP_NAME} shut down")


# ================================================================================================
# APP
# ================================================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Central Intelligence Platform — 7 AI Services, 128 Endpoints",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred" if settings.ENVIRONMENT == "production" else str(exc),
            },
        },
    )

# ================================================================================================
# ROUTES
# ================================================================================================

route_registry = [
    ("auth", "Authentication"),
    ("api_keys", "API Keys"),
    ("admin", "Admin"),
    ("general", "General AI"),
    ("smartpos", "SmartPOS AI"),
    ("spark", "Spark Messenger AI"),
    ("vibe", "Vibe Social AI"),
    ("vault", "HDM Vault AI"),
    ("erp", "ERP AI Gateway"),
    ("widget", "Widget AI"),
]

loaded = 0
for module_name, label in route_registry:
    try:
        module = __import__(f"routes.{module_name}", fromlist=["router"])
        app.include_router(module.router, prefix="/api/v1")
        loaded += 1
    except Exception as e:
        logger.warning(f"{label}: SKIPPED — {e}")

logger.info(f"Routes loaded: {loaded}/{len(route_registry)}")

# ================================================================================================
# ROOT
# ================================================================================================

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "services": loaded,
        "docs": "/docs" if settings.DEBUG else None,
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }


# ================================================================================================
# ENTRY POINT
# ================================================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )