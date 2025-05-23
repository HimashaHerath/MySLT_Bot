from fastapi import APIRouter, Depends, HTTPException
from myslt.api import SLTAPI
from config.config import SUBSCRIBER_ID
from api.app import get_slt_api
from pydantic import BaseModel
from typing import Dict, Optional, Any

router = APIRouter(prefix="/profile", tags=["Profile"])

class ProfileResponse(BaseModel):
    fullname: str
    package: str
    contact_no: Optional[str] = None
    email: Optional[str] = None
    raw_data: Dict[str, Any]  # Include raw data for additional fields

@router.get("/info", response_model=ProfileResponse)
async def get_profile_info(slt_api: SLTAPI = Depends(get_slt_api)):
    """
    Get the user's profile information
    """
    try:
        profile = slt_api.get_profile(SUBSCRIBER_ID)
        
        if not profile.get("isSuccess", False):
            raise HTTPException(status_code=400, detail="Failed to retrieve profile data")
        
        data_bundle = profile.get("dataBundle", {})
        
        return {
            "fullname": data_bundle.get("fullname", "Unknown"),
            "package": data_bundle.get("subscriber_package_display", "Unknown"),
            "contact_no": data_bundle.get("contact_no"),
            "email": data_bundle.get("email"),
            "raw_data": data_bundle  # Include all data for additional fields
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile data: {str(e)}") 