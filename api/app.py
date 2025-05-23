from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from typing import Callable
import uuid

from myslt.api import SLTAPI
from config.config import USERNAME, PASSWORD, SUBSCRIBER_ID, TP_NO, ACCOUNT_NO
from logging_config import setup_logging

# Configure enhanced logging for API
logger = setup_logging(
    log_level=logging.INFO, 
    app_name='api_server',
    log_dir='logs',
    json_logs=True
)

# Initialize FastAPI app
app = FastAPI(
    title="MySLT Bot API",
    description="API for accessing SLT data and bot functionality",
    version="1.0.0",
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log the request
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            'event_type': 'request_start',
            'request_id': request_id,
            'method': request.method,
            'path': request.url.path,
            'query_params': str(request.query_params),
            'client_host': request.client.host if request.client else "unknown"
        }
    )
    
    # Process the request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log the response
        logger.info(
            f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}",
            extra={
                'event_type': 'request_complete',
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'duration_ms': round(process_time * 1000, 2)
            }
        )
        
        # Add custom headers to response
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            exc_info=True,
            extra={
                'event_type': 'request_error',
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'error': str(e),
                'duration_ms': round(process_time * 1000, 2)
            }
        )
        raise

# Dependency to get SLT API client
def get_slt_api():
    try:
        api = SLTAPI(USERNAME, PASSWORD)
        return api
    except Exception as e:
        logger.error(
            f"Failed to initialize SLTAPI",
            exc_info=True,
            extra={
                'event_type': 'slt_api_init_failed',
                'error': str(e)
            }
        )
        raise HTTPException(status_code=500, detail="SLT API client initialization failed")

# Health check endpoint
@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint called", extra={'event_type': 'health_check'})
    return {"status": "ok", "service": "MySLT Bot API"}

# Error handler for application exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception in request: {request.method} {request.url.path}",
        exc_info=True,
        extra={
            'event_type': 'unhandled_exception',
            'method': request.method,
            'path': request.url.path,
            'error': str(exc),
            'error_type': type(exc).__name__
        }
    )
    return {"detail": "Internal Server Error", "type": type(exc).__name__}

# Application startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info(
        "API server starting up",
        extra={
            'event_type': 'server_startup'
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(
        "API server shutting down",
        extra={
            'event_type': 'server_shutdown'
        }
    )

# Include routers from other modules
from api.routers import usage, profile, bills, vas

app.include_router(usage.router)
app.include_router(profile.router)
app.include_router(bills.router)
app.include_router(vas.router) 