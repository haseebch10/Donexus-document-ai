from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import uuid

from app.config import settings
from app.logging_config import logger
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Upload directory: {settings.upload_dir}")
    logger.info(f"Data directory: {settings.data_dir}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered lease agreement extraction system for property managers",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} | ID: {request.state.request_id}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Log response
    logger.info(
        f"Response: {request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Duration: {duration_ms:.2f}ms | "
        f"ID: {request.state.request_id}"
    )
    
    return response


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "request_id": request.state.request_id
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "request_id": request.state.request_id
        }
    )


# Health Check Endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint
    
    Returns application status and version information
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version
    )


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


# Import routers (will add these next)
# from app.api import upload, extraction, export
# app.include_router(upload.router, prefix="/api", tags=["Upload"])
# app.include_router(extraction.router, prefix="/api", tags=["Extraction"])
# app.include_router(export.router, prefix="/api", tags=["Export"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
