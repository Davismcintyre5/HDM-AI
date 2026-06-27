# ====================================================================================================
# HDM AI Engine — main.py
# Stateless AI Server | 7 Modules | Production Ready
# ====================================================================================================

import sys
import os
import time
import asyncio as _asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from config import settings

_start_time = time.time()

# ================================================================================================
# LOGGING
# ================================================================================================

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
)

# ================================================================================================
# LIFESPAN
# ================================================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 50)
    logger.info(f"  {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"  Environment: {settings.ENVIRONMENT}")
    logger.info(f"  Port: {settings.PORT}")
    logger.info("=" * 50)

    if settings.REDIS_ENABLED:
        try:
            import redis.asyncio as redis
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await r.ping()
            await r.aclose()
            logger.info("Redis: CONNECTED")
        except Exception as e:
            logger.warning(f"Redis: FAILED — {e}")
    else:
        logger.info("Redis: DISABLED")

    if settings.GROQ_API_KEY:
        logger.info("Groq: CONFIGURED (fallback)")
    else:
        logger.warning("Groq: MISSING — will rely on MERN for keys")

    if settings.GEMINI_API_KEY:
        logger.info("Gemini: CONFIGURED (fallback)")
    else:
        logger.warning("Gemini: MISSING — will rely on MERN for keys")

    logger.info(f"MERN: {settings.MERN_INTERNAL_URL}")

    try:
        from services.key_resolver import key_resolver
        await key_resolver.fetch_from_mern()
    except Exception as e:
        logger.warning(f"MERN key fetch skipped: {e}")

    if settings.APP_URL:
        try:
            from keep_alive import keep_alive as _keep_alive_loop
            _asyncio.create_task(_keep_alive_loop())
            logger.info(f"Keep-alive: ENABLED ({settings.APP_URL}/health every 9 min)")
        except Exception as e:
            logger.warning(f"Keep-alive: FAILED — {e}")

    yield
    logger.info(f"{settings.APP_NAME} shut down")


# ================================================================================================
# APP
# ================================================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="HDM AI Engine — Stateless AI Inference Server",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}},
    )


# ================================================================================================
# ROUTES
# ================================================================================================

route_registry = [
    ("general", "General AI"),
    ("erp", "ERP AI Gateway"),
    ("widget", "Widget AI"),
    ("smartpos", "SmartPOS AI"),
    ("vault", "HDM Vault AI"),
    ("spark", "Spark Messenger AI"),
    ("vibe", "Vibe Social AI"),
]

loaded = 0
for module_name, label in route_registry:
    try:
        module = __import__(f"routes.{module_name}", fromlist=["router"])
        app.include_router(module.router, prefix="/api/v1")
        loaded += 1
        logger.info(f"  ✓ {label}")
    except Exception as e:
        logger.warning(f"  ✗ {label}: {e}")

logger.info(f"Routes: {loaded}/{len(route_registry)} loaded")


# ================================================================================================
# ROOT & HEALTH
# ================================================================================================

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "services": loaded,
        "redis": "enabled" if settings.REDIS_ENABLED else "disabled",
        "docs": "/docs" if settings.DEBUG else None,
        "health": "/health",
        "uptime": int(time.time() - _start_time),
        "mern": settings.MERN_INTERNAL_URL,
    }


@app.get("/health")
async def health_check():
    from datetime import datetime
    uptime = int(time.time() - _start_time)
    try:
        import psutil
        mem = psutil.Process().memory_info()
        memory = {"rss": round(mem.rss / 1024 / 1024, 1)}
    except ImportError:
        memory = {"rss": 0}

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime": uptime,
        "memory": memory,
        "redis": "enabled" if settings.REDIS_ENABLED else "disabled",
        "modules": loaded,
        "timestamp": datetime.utcnow().isoformat(),
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