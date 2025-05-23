from fastapi import APIRouter, Depends, HTTPException, Request
from myslt.api import SLTAPI
from config.config import SUBSCRIBER_ID
from api.app import get_slt_api
from pydantic import BaseModel, Field
from typing import Optional
import logging

# Get logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/usage", tags=["Usage"])

class UsageDetail(BaseModel):
    used: float = Field(..., description="Amount of data used in GB")
    limit: float = Field(..., description="Data limit in GB")
    remaining: float = Field(..., description="Remaining data in GB")
    percentage: float = Field(..., description="Percentage of data used")

class UsageSummaryResponse(BaseModel):
    total_used: float = Field(..., description="Total data used in GB")
    total_limit: float = Field(..., description="Total data limit in GB")
    total_percentage: float = Field(..., description="Total percentage of data used")
    daytime: UsageDetail = Field(..., description="Daytime (Standard) data usage")
    nighttime: UsageDetail = Field(..., description="Nighttime (Free) data usage")
    reported_time: Optional[str] = Field(None, description="Time when usage was reported")

@router.get("/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(request: Request, slt_api: SLTAPI = Depends(get_slt_api)):
    """
    Get the current data usage summary, separated into daytime (Standard) and nighttime (Free) usage
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
        my_package_info = data_bundle.get("my_package_info", {})
        usage_details = my_package_info.get("usageDetails", [])
        reported_time = my_package_info.get("reported_time")
        
        # Get total usage
        total_used = float(my_package_summary.get("used", 0))
        total_limit = float(my_package_summary.get("limit", 1))  # Default to 1 to avoid division by zero
        total_percentage = (total_used / total_limit) * 100 if total_limit > 0 else 0
        
        # Initialize daytime and nighttime usage with default values
        daytime_usage = {
            "used": 0.0,
            "limit": 0.0,
            "remaining": 0.0,
            "percentage": 0.0
        }
        
        nighttime_usage = {
            "used": 0.0,
            "limit": 0.0,
            "remaining": 0.0,
            "percentage": 0.0
        }
        
        # Find standard (daytime) and calculate nighttime usage
        for detail in usage_details:
            if detail.get("name") == "Standard":
                # Standard/daytime data
                daytime_limit = float(detail.get("limit", 0))
                daytime_used = float(detail.get("used", 0))
                daytime_remaining = float(detail.get("remaining", 0))
                daytime_percentage = (daytime_used / daytime_limit) * 100 if daytime_limit > 0 else 0
                
                daytime_usage = {
                    "used": daytime_used,
                    "limit": daytime_limit,
                    "remaining": daytime_remaining,
                    "percentage": daytime_percentage
                }
                
                # Calculate nighttime/free usage (total - standard)
                nighttime_limit = total_limit - daytime_limit
                nighttime_used = max(0, total_used - daytime_used)  # Ensure we don't get negative values
                nighttime_remaining = max(0, nighttime_limit - nighttime_used)
                nighttime_percentage = (nighttime_used / nighttime_limit) * 100 if nighttime_limit > 0 else 0
                
                nighttime_usage = {
                    "used": nighttime_used,
                    "limit": nighttime_limit,
                    "remaining": nighttime_remaining,
                    "percentage": nighttime_percentage
                }
                break
        
        response_data = {
            "total_used": total_used,
            "total_limit": total_limit,
            "total_percentage": total_percentage,
            "daytime": daytime_usage,
            "nighttime": nighttime_usage,
            "reported_time": reported_time
        }
        
        logger.debug(
            "Usage summary data processed successfully", 
            extra={
                'event_type': 'usage_summary_success',
                'request_id': request_id,
                'total_used': total_used,
                'total_limit': total_limit,
                'daytime_used': daytime_usage["used"],
                'nighttime_used': nighttime_usage["used"]
            }
        )
        
        return response_data
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