"""FastAPI application with CRUD endpoints for moderation dashboard."""
import structlog
from typing import List

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend import database
from backend.ai_service import ai_service
from backend.config import get_settings
from backend.middleware import SecurityHeadersMiddleware, LoggingMiddleware
from backend.monitoring import router as monitoring_router
from backend.models import (
    FlaggedItemCreate,
    FlaggedItemResponse,
    FlaggedItemUpdate,
    StatsResponse,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
settings = get_settings()

# Initialize database (non-blocking - will retry on first use)
try:
    database.init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.warning("Database initialization failed, will retry on first use", error=str(e))
    # Don't raise - allow app to start even if DB is temporarily unavailable

# Create FastAPI app
app = FastAPI(
    title="AI Moderation Dashboard API",
    description="Production-ready moderation dashboard API",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting if enabled
if settings.rate_limit_enabled:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("Rate limiting enabled", limit_per_minute=settings.rate_limit_per_minute)
else:
    # Create a no-op limiter for when rate limiting is disabled
    class NoOpLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    limiter = NoOpLimiter()

# Include monitoring routes
app.include_router(monitoring_router)

# Serve static files from frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def root():
    """Serve the main dashboard page."""
    return FileResponse("frontend/index.html")


def _row_to_response(row: dict) -> FlaggedItemResponse:
    """Helper function to convert database row to response model."""
    return FlaggedItemResponse(
        id=row["id"],
        content_type=row["content_type"],
        content=row["content"],
        priority=row["priority"],
        status=row["status"],
        ai_summary=row["ai_summary"],
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


@app.get("/api/flags", response_model=List[FlaggedItemResponse])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_flags(request: Request):
    """Get all flagged items."""
    
    try:
        rows = database.get_all_flags()
        return [_row_to_response(row) for row in rows]
    except Exception as e:
        logger.error("Error fetching flags", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching flagged items"
        )


@app.get("/api/flags/{flag_id}", response_model=FlaggedItemResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_flag(flag_id: int, request: Request):
    """Get a single flagged item by ID."""
    
    try:
        row = database.get_flag_by_id(flag_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flagged item {flag_id} not found",
            )
        return _row_to_response(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching flag", flag_id=flag_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching flagged item"
        )


@app.post("/api/flags", response_model=FlaggedItemResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def create_flag(item: FlaggedItemCreate, request: Request):
    """Create a new flagged item."""
    
    try:
        priority = ai_service.calculate_priority(item.content)
        ai_summary = ai_service.generate_summary(item.content, item.content_type)
        
        flag_id = database.create_flag(
            content_type=item.content_type,
            content=item.content,
            priority=priority,
            ai_summary=ai_summary,
        )
        
        row = database.get_flag_by_id(flag_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created flagged item"
            )
        
        logger.info("Flag created", flag_id=flag_id, priority=priority)
        return _row_to_response(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating flag", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating flagged item"
        )


@app.patch("/api/flags/{flag_id}", response_model=FlaggedItemResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def update_flag(flag_id: int, update: FlaggedItemUpdate, request: Request):
    """Update the status of a flagged item."""
    
    try:
        updated = database.update_flag_status(flag_id, update.status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flagged item {flag_id} not found",
            )
        
        row = database.get_flag_by_id(flag_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated flagged item"
            )
        
        logger.info("Flag updated", flag_id=flag_id, status=update.status)
        return _row_to_response(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating flag", flag_id=flag_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating flagged item"
        )


@app.delete("/api/flags/{flag_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def delete_flag(flag_id: int, request: Request):
    """Delete a flagged item."""
    
    try:
        deleted = database.delete_flag(flag_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flagged item {flag_id} not found",
            )
        
        logger.info("Flag deleted", flag_id=flag_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting flag", flag_id=flag_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting flagged item"
        )


@app.get("/api/stats", response_model=StatsResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_stats(request: Request):
    """Get dashboard statistics using optimized SQL aggregation."""
    
    try:
        stats_dict = database.get_stats()
        return StatsResponse(**stats_dict)
    except Exception as e:
        logger.error("Error fetching stats", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching statistics"
        )
