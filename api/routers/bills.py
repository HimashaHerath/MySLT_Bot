from fastapi import APIRouter, Depends, HTTPException
from myslt.api import SLTAPI
from config.config import TP_NO, ACCOUNT_NO
from api.app import get_slt_api
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter(prefix="/bills", tags=["Bills"])

class BillStatusResponse(BaseModel):
    status: str
    amount: Optional[float] = None
    due_date: Optional[str] = None
    raw_data: Dict[str, Any]

@router.get("/status", response_model=BillStatusResponse)
async def get_bill_status(slt_api: SLTAPI = Depends(get_slt_api)):
    """
    Get the current bill status
    """
    try:
        bill_status = slt_api.get_bill_status(TP_NO, ACCOUNT_NO)
        
        if not bill_status.get("isSuccess", False):
            raise HTTPException(status_code=400, detail="Failed to retrieve bill status")
        
        data_bundle = bill_status.get("dataBundle", {})
        
        return {
            "status": data_bundle.get("bill_code_desc", "Unknown"),
            "amount": data_bundle.get("bill_value"),
            "due_date": data_bundle.get("due_date"),
            "raw_data": data_bundle
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bill status: {str(e)}")

@router.get("/payment", response_model=Dict[str, Any])
async def get_bill_payment_info(slt_api: SLTAPI = Depends(get_slt_api)):
    """
    Get bill payment information
    """
    try:
        payment_info = slt_api.get_bill_payment_request(TP_NO, ACCOUNT_NO)
        
        if not payment_info.get("isSuccess", False):
            raise HTTPException(status_code=400, detail="Failed to retrieve bill payment information")
        
        return payment_info.get("dataBundle", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bill payment information: {str(e)}") 