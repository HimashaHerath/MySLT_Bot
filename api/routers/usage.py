from fastapi import APIRouter, Depends, HTTPException, Request
from myslt.api import SLTAPI
from config.config import SUBSCRIBER_ID
from api.app import get_slt_api
from pydantic import BaseModel
import logging

# Get logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/usage", tags=["Usage"])

class UsageSummaryResponse(BaseModel):
    used: float
    limit: float
    percentage: float

@router.get("/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(request: Request, slt_api: SLTAPI = Depends(get_slt_api)):
    """
    Get the current data usage summary
    """
    request_id = request.headers.get("X-Request-ID", "unknown")
    logger.info(
        "Processing usage summary request",
        extra={
            'event_type': 'usage_summary_request',
            'request_id': request_id,
            'subscriber_id': SUBSCRIBER_ID[:5] + '***' if SUBSCRIBER_ID else None  # Partial logging for privacy
        }
    )
    
    try:
        usage = slt_api.get_usage_summary(SUBSCRIBER_ID)
        
        if not usage.get("isSuccess", False):
            logger.warning(
                "SLT API returned unsuccessful response for usage data",
                extra={
                    'event_type': 'slt_api_unsuccessful',
                    'request_id': request_id,
                    'endpoint': 'usage_summary',
                    'response_status': usage.get("status", "unknown")
                }
            )
            raise HTTPException(status_code=400, detail="Failed to retrieve usage data")
        
        data_bundle = usage.get("dataBundle", {})
        my_package_summary = data_bundle.get("my_package_summary", {})
        
        used = float(my_package_summary.get("used", 0))
        limit = float(my_package_summary.get("limit", 1))  # Default to 1 to avoid division by zero
        
        # Calculate percentage used
        percentage = (used / limit) * 100 if limit > 0 else 0
        
        logger.debug(
            "Usage summary data processed successfully", 
            extra={
                'event_type': 'usage_summary_success',
                'request_id': request_id,
                'used': used,
                'limit': limit,
                'percentage': percentage
            }
        )
        
        return {
            "used": used,
            "limit": limit,
            "percentage": percentage
        }
    except HTTPException:
        # Re-raise HTTP exceptions without wrapping
        raise
    except Exception as e:
        logger.error(
            "Error retrieving usage data", 
            exc_info=True,
            extra={
                'event_type': 'usage_summary_error',
                'request_id': request_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
        )
        raise HTTPException(status_code=500, detail=f"Error retrieving usage data: {str(e)}") 