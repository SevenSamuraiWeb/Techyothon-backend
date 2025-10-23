from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from bson import ObjectId

from models import StatusUpdate, VerificationRequest, ComplaintStatus
from database import get_database

router = APIRouter(prefix="/api/complaints", tags=["status"])


@router.patch("/{complaint_id}/status")
async def update_complaint_status(complaint_id: str, status_update: StatusUpdate):
    """
    Update the status of a complaint
    Used by authorities/departments to track progress
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    try:
        complaint = await complaints_collection.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID format")
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Create new status history entry
    new_status_entry = {
        "status": status_update.status.value,
        "timestamp": datetime.utcnow(),
        "updated_by": status_update.updated_by,
        "comment": status_update.comment
    }
    
    # Update fields
    update_data = {
        "$set": {
            "status": status_update.status.value,
            "updated_at": datetime.utcnow()
        },
        "$push": {
            "status_history": new_status_entry
        }
    }
    
    # If status is resolved, set resolved_at timestamp
    if status_update.status == ComplaintStatus.RESOLVED:
        update_data["$set"]["resolved_at"] = datetime.utcnow()
    
    await complaints_collection.update_one(
        {"_id": ObjectId(complaint_id)},
        update_data
    )
    
    return {
        "complaint_id": complaint_id,
        "status": status_update.status.value,
        "message": "Status updated successfully"
    }


@router.post("/{complaint_id}/verify")
async def verify_resolution(complaint_id: str, verification: VerificationRequest):
    """
    Allow citizens to verify that their complaint has been resolved
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    try:
        complaint = await complaints_collection.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID format")
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Check if complaint belongs to user
    if complaint.get("user_id") != verification.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to verify this complaint")
    
    # Check if complaint is marked as resolved
    if complaint.get("status") != ComplaintStatus.RESOLVED.value:
        raise HTTPException(status_code=400, detail="Complaint is not yet marked as resolved")
    
    # Update verification status
    await complaints_collection.update_one(
        {"_id": ObjectId(complaint_id)},
        {
            "$set": {
                "verified_by_citizen": verification.verified,
                "verification_feedback": verification.feedback,
                "verified_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Add to status history
    status_entry = {
        "status": ComplaintStatus.RESOLVED.value,
        "timestamp": datetime.utcnow(),
        "updated_by": verification.user_id,
        "comment": f"Citizen verification: {'Confirmed' if verification.verified else 'Not confirmed'}. {verification.feedback or ''}"
    }
    
    await complaints_collection.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$push": {"status_history": status_entry}}
    )
    
    return {
        "complaint_id": complaint_id,
        "verified": verification.verified,
        "message": "Verification recorded successfully"
    }


@router.get("/{complaint_id}/history")
async def get_status_history(complaint_id: str):
    """
    Get the complete status history of a complaint
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    try:
        complaint = await complaints_collection.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID format")
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return {
        "complaint_id": complaint_id,
        "current_status": complaint.get("status"),
        "status_history": complaint.get("status_history", [])
    }

