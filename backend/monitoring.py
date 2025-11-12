"""Monitoring and metrics endpoints."""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from backend import database
from backend.config import get_settings

settings = get_settings()

# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

database_connections = Gauge(
    'database_connections_active',
    'Active database connections'
)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint - lightweight check without database."""
    # Simple health check that doesn't require database
    # Railway uses this to verify the service is up
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "service": "moderation-dashboard",
            "environment": settings.environment
        }
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Check database connectivity
        with database.get_db_connection() as conn:
            conn.cursor().execute("SELECT 1")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ready"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "error": str(e)}
        )


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    if not settings.prometheus_enabled:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Metrics disabled"}
        )
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

