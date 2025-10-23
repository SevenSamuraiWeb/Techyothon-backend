from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from datetime import datetime
from bson import ObjectId

from models import (
    ComplaintResponse, ComplaintStatus, Location, 
    StatusHistory, CATEGORY_DEPARTMENT_MAP
)
from database import get_database
from services.cloudinary_service import upload_image, upload_audio, upload_image_bytes
from services.gemini_service import categorize_complaint, categorize_complaint_with_image_bytes
from services.similarity_service import check_duplicate

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

@router.get("/all")
async def get_all_complaints():
    db = await get_database()
    
    complaints = await db.complaints.find().sort("created_at", -1).to_list(length=100)
    
    if not complaints:
        raise HTTPException(status_code=404, detail="Complaints not found")
    
    # Convert ObjectId to string
    submitted_list = []
    for complaint in complaints:
            submitted_list.append({
                "complaint_id": str(complaint["_id"]),
                "status": complaint.get("status"),
                "category": complaint.get("category"),
                "priority": complaint.get("priority"),
                "title": complaint.get("title"),
                "description": complaint.get("description"),
                "created_at": complaint.get("created_at"),
            })

    if not submitted_list:
        return {"total": 0, "complaints": []}

    return {"total": len(submitted_list), "complaints": submitted_list}




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
    Accepts: title, description, location, image, audio (optional)
    """
    
    db = await get_database()
    complaints_collection = db["complaints"]
    
    # Handle media and AI categorization
    image_url = None
    audio_url = None
    image_bytes = None
    mime_type = "image/jpeg"

    # If image present, read once as bytes (for Gemini) and upload to Cloudinary
    if image:
        image_bytes = await image.read()
        if image.content_type:
            mime_type = image.content_type
        # Categorize using bytes to avoid unsupported external URLs
        category, priority = await categorize_complaint_with_image_bytes(title, description, image_bytes, mime_type)
        # Upload to Cloudinary using the same bytes
        image_url = await upload_image_bytes(image_bytes, mime_type)
    else:
        # No image: categorize using text only
        category, priority = await categorize_complaint(title, description, None)

    # Upload audio if provided
    if audio:
        audio_url = await upload_audio(audio)
    
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


@router.get("/{complaint_id:[0-9a-fA-F]{24}}")
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


@router.get("/{complaint_id:[0-9a-fA-F]{24}}/similar")
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



@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...)
):
    
    db = await get_database()
    complaints_collection = db["user"]
    
    
    user_data = {
        "email": email,
        "password": password,
        "role": role
    }
    
    result = await complaints_collection.find_one({"email": user_data["email"]})
    if result == None:
        return { "verified": False, "type": "user not found" }
    else:
        # print(result["_id"])
        if user_data["password"] == result["password"]:
            return {"verified": True, "userid":str(result["_id"])}
        else: return {"verified": False, "type": "wrong password"}



@router.post("/register")
async def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...)
):
    
    db = await get_database()
    complaints_collection = db["user"]
    
    
    user_data = {
        "name": name,   
        "email": email,
        "password": password,
        "role": role
    }
    
    result = await complaints_collection.find_one({"email": user_data["email"]})
    if result == None:
        succ = await complaints_collection.insert_one(user_data)
        if succ.inserted_id:
            return {"success": True}
        else: return {"success": False, "type": "Opps! Please Try again"}
    else:
        return {"success": False, "type": "User already exists"}