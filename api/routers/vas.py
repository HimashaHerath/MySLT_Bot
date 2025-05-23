from fastapi import APIRouter, Depends, HTTPException
from myslt.api import SLTAPI
from config.config import SUBSCRIBER_ID
from api.app import get_slt_api
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

router = APIRouter(prefix="/vas", tags=["VAS"])

class VASBundleDetail(BaseModel):
    name: str
    used: Optional[str] = None
    expiry_date: Optional[str] = None
    description: Optional[str] = None
    raw_data: Dict[str, Any]

class VASBundlesResponse(BaseModel):
    bundles: List[VASBundleDetail]

@router.get("/bundles", response_model=VASBundlesResponse)
async def get_vas_bundles(slt_api: SLTAPI = Depends(get_slt_api)):
    """
    Get VAS (Value-Added Services) bundles information
    """
    try:
        vas_bundles = slt_api.get_vas_bundles(SUBSCRIBER_ID)
        
        if not vas_bundles.get("isSuccess", False):
            raise HTTPException(status_code=400, detail="Failed to retrieve VAS bundles information")
        
        data_bundle = vas_bundles.get("dataBundle", {})
        usage_details = data_bundle.get("usageDetails", [])
        
        bundles = []
        for detail in usage_details:
            bundles.append({
                "name": detail.get("name", "Unknown"),
                "used": detail.get("used"),
                "expiry_date": detail.get("expiry_date"),
                "description": detail.get("description"),
                "raw_data": detail
            })
        
        return {"bundles": bundles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving VAS bundles information: {str(e)}")

@router.get("/extra-gb", response_model=Dict[str, Any])
async def get_extra_gb(slt_api: SLTAPI = Depends(get_slt_api)):
    """
    Get Extra GB information
    """
    try:
        extra_gb = slt_api.get_extra_gb(SUBSCRIBER_ID)
        
        if not extra_gb.get("isSuccess", False):
            raise HTTPException(status_code=400, detail="Failed to retrieve Extra GB information")
        
        return extra_gb.get("dataBundle", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Extra GB information: {str(e)}") 