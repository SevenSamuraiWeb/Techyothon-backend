from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from datetime import datetime
from bson import ObjectId

from models import (
    ComplaintResponse, ComplaintStatus, Location, 
    StatusHistory, CATEGORY_DEPARTMENT_MAP
)
from database import get_database
from services.cloudinary_service import upload_image, upload_audio
from services.gemini_service import categorize_complaint
from services.similarity_service import check_duplicate

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("/submit", response_model=ComplaintResponse)
async def submit_complaint(
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None)
):
    """
    Submit a new complaint with multimodal input
    Accepts: title, description, location, image (optional), audio (optional)
    """
    
    db = await get_database()
    complaints_collection = db["complaints"]
    
    # Upload files to Cloudinary
    image_url = None
    audio_url = None
    
    if image:
        image_url = await upload_image(image)
    
    if audio:
        audio_url = await upload_audio(audio)
    
    # Use Gemini AI to categorize the complaint
    category, priority = await categorize_complaint(title, description, image_url)
    
    # Auto-assign to department based on category
    assigned_department = CATEGORY_DEPARTMENT_MAP.get(category)
    
    # Create location object
    location = Location(
        type="Point",
        coordinates=[longitude, latitude]
    )
    
    # Check for duplicates
    duplicate_check = await check_duplicate(
        title=title,
        description=description,
        category=category,
        latitude=latitude,
        longitude=longitude
    )
    
    # Create initial status history
    status_history = [
        StatusHistory(
            status=ComplaintStatus.SUBMITTED,
            timestamp=datetime.utcnow(),
            updated_by=user_id,
            comment="Complaint submitted"
        ).dict()
    ]
    
    # Prepare complaint document
    complaint_data = {
        "title": title,
        "description": description,
        "category": category.value,
        "priority": priority.value,
        "status": ComplaintStatus.SUBMITTED.value,
        "location": location.dict(),
        "address": address,
        "image_url": image_url,
        "audio_url": audio_url,
        "user_id": user_id,
        "assigned_department": assigned_department.value if assigned_department else None,
        "status_history": status_history,
        "verified_by_citizen": False,
        "related_complaints": [c["complaint_id"] for c in duplicate_check["similar_complaints"]],
        "is_duplicate": duplicate_check["is_duplicate"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "resolved_at": None
    }
    
    # Insert into database
    result = await complaints_collection.insert_one(complaint_data)
    complaint_id = str(result.inserted_id)
    
    return ComplaintResponse(
        complaint_id=complaint_id,
        status=ComplaintStatus.SUBMITTED,
        category=category,
        priority=priority,
        message="Complaint registered successfully"
    )


@router.get("/{complaint_id}")
async def get_complaint(complaint_id: str):
    """
    Get details of a specific complaint
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    try:
        complaint = await complaints_collection.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID format")
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Convert ObjectId to string
    complaint["_id"] = str(complaint["_id"])
    
    return complaint


@router.get("/user/{user_id}")
async def get_user_complaints(user_id: str, status: Optional[str] = None):
    """
    Get all complaints submitted by a user
    Optional filter by status
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    query = {"user_id": user_id}
    if status:
        query["status"] = status
    
    complaints = []
    cursor = complaints_collection.find(query).sort("created_at", -1)
    
    async for complaint in cursor:
        complaint["_id"] = str(complaint["_id"])
        complaints.append(complaint)
    
    return {
        "user_id": user_id,
        "total_complaints": len(complaints),
        "complaints": complaints
    }


@router.get("/{complaint_id}/similar")
async def get_similar_complaints(complaint_id: str):
    """
    Find similar complaints to help identify duplicates
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    try:
        complaint = await complaints_collection.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID format")
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    from services.similarity_service import find_similar_complaints
    
    coords = complaint["location"]["coordinates"]
    similar = await find_similar_complaints(
        complaint_id=complaint_id,
        title=complaint["title"],
        description=complaint["description"],
        category=complaint["category"],
        latitude=coords[1],
        longitude=coords[0]
    )
    
    return {
        "complaint_id": complaint_id,
        "similar_complaints": similar
    }

