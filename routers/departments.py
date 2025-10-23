from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
from bson import ObjectId

from models import DepartmentAssignment, Department, CATEGORY_DEPARTMENT_MAP
from database import get_database

router = APIRouter(prefix="/api/departments", tags=["departments"])


@router.get("/{dept_name}/complaints")
async def get_department_complaints(
    dept_name: str,
    status: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
):
    """
    Get all complaints assigned to a specific department
    Optional filter by status
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    # Validate department name
    try:
        department = Department(dept_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid department name. Valid options: {[d.value for d in Department]}")
    
    query = {"assigned_department": department.value}
    if status:
        query["status"] = status
    
    complaints = []
    cursor = complaints_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    
    async for complaint in cursor:
        complaint["_id"] = str(complaint["_id"])
        complaints.append(complaint)
    
    # Get total count
    total = await complaints_collection.count_documents(query)
    
    return {
        "department": department.value,
        "total_complaints": total,
        "returned_count": len(complaints),
        "complaints": complaints
    }


@router.get("/{dept_name}/complaints/pending")
async def get_department_pending_complaints(dept_name: str):
    """
    Get pending complaints for a department (Submitted, Assigned, In Progress)
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    # Validate department name
    try:
        department = Department(dept_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid department name")
    
    query = {
        "assigned_department": department.value,
        "status": {"$in": ["Submitted", "Assigned", "In Progress"]}
    }
    
    complaints = []
    cursor = complaints_collection.find(query).sort("priority", -1).sort("created_at", -1)
    
    async for complaint in cursor:
        complaint["_id"] = str(complaint["_id"])
        complaints.append(complaint)
    
    return {
        "department": department.value,
        "pending_count": len(complaints),
        "complaints": complaints
    }


@router.patch("/assign/{complaint_id}")
async def assign_complaint_to_department(
    complaint_id: str,
    assignment: DepartmentAssignment
):
    """
    Manually assign or reassign a complaint to a department
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    try:
        complaint = await complaints_collection.find_one({"_id": ObjectId(complaint_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid complaint ID format")
    
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Update assignment
    await complaints_collection.update_one(
        {"_id": ObjectId(complaint_id)},
        {
            "$set": {
                "assigned_department": assignment.department.value,
                "updated_at": datetime.utcnow()
            },
            "$push": {
                "status_history": {
                    "status": "Assigned",
                    "timestamp": datetime.utcnow(),
                    "updated_by": assignment.assigned_by,
                    "comment": f"Assigned to {assignment.department.value}"
                }
            }
        }
    )
    
    # Update status to Assigned if it's still Submitted
    if complaint.get("status") == "Submitted":
        await complaints_collection.update_one(
            {"_id": ObjectId(complaint_id)},
            {"$set": {"status": "Assigned"}}
        )
    
    return {
        "complaint_id": complaint_id,
        "assigned_department": assignment.department.value,
        "message": "Complaint assigned successfully"
    }


@router.get("/{dept_name}/stats")
async def get_department_statistics(dept_name: str):
    """
    Get statistics for a department
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    # Validate department name
    try:
        department = Department(dept_name)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid department name")
    
    query = {"assigned_department": department.value}
    
    # Get counts by status
    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    
    status_counts = {}
    async for doc in complaints_collection.aggregate(pipeline):
        status_counts[doc["_id"]] = doc["count"]
    
    # Get counts by priority
    priority_pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$priority",
            "count": {"$sum": 1}
        }}
    ]
    
    priority_counts = {}
    async for doc in complaints_collection.aggregate(priority_pipeline):
        priority_counts[doc["_id"]] = doc["count"]
    
    total = await complaints_collection.count_documents(query)
    
    return {
        "department": department.value,
        "total_complaints": total,
        "by_status": status_counts,
        "by_priority": priority_counts
    }

