from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import logger
from app.database.session import init_db
from app.middleware import setup_cors, RequestTimingLoggerMiddleware, register_exception_handlers
from app.routers import api_v1_router
from app.routers.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan context manager."""
    logger.info(f"Starting {settings.PROJECT_NAME} API v{settings.VERSION} [{settings.ENVIRONMENT}]")
    try:
        await init_db()
    except Exception as exc:
        logger.error(f"Error during database initialization: {exc}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME} API gracefully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Register CORS Middleware
setup_cors(app)

# Register Timing & Request Logging Middleware
app.add_middleware(RequestTimingLoggerMiddleware)

# Register Centralized Exception Handlers
register_exception_handlers(app)

# Mount Health Check Endpoints at root level
app.include_router(health_router)

# Mount API v1 Routers (/api/v1)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
    }
