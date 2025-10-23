from fastapi import APIRouter
from datetime import datetime, timedelta
from database import get_database
from typing import Optional

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard_analytics(days_back: int = 30):
    """
    Get comprehensive analytics for the dashboard
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    # Time threshold
    time_threshold = datetime.utcnow() - timedelta(days=days_back)
    
    # Total complaints
    total_complaints = await complaints_collection.count_documents({})
    recent_complaints = await complaints_collection.count_documents({
        "created_at": {"$gte": time_threshold}
    })
    
    # Complaints by category
    category_pipeline = [
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    complaints_by_category = {}
    async for doc in complaints_collection.aggregate(category_pipeline):
        complaints_by_category[doc["_id"]] = doc["count"]
    
    # Complaints by status
    status_pipeline = [
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    
    complaints_by_status = {}
    async for doc in complaints_collection.aggregate(status_pipeline):
        complaints_by_status[doc["_id"]] = doc["count"]
    
    # Complaints by priority
    priority_pipeline = [
        {"$group": {
            "_id": "$priority",
            "count": {"$sum": 1}
        }}
    ]
    
    complaints_by_priority = {}
    async for doc in complaints_collection.aggregate(priority_pipeline):
        complaints_by_priority[doc["_id"]] = doc["count"]
    
    # Average resolution time (for resolved complaints)
    resolution_pipeline = [
        {
            "$match": {
                "status": "Resolved",
                "resolved_at": {"$exists": True}
            }
        },
        {
            "$project": {
                "resolution_time": {
                    "$subtract": ["$resolved_at", "$created_at"]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "avg_resolution_time_ms": {"$avg": "$resolution_time"}
            }
        }
    ]
    
    avg_resolution_time_hours = None
    async for doc in complaints_collection.aggregate(resolution_pipeline):
        if doc.get("avg_resolution_time_ms"):
            avg_resolution_time_hours = round(doc["avg_resolution_time_ms"] / (1000 * 60 * 60), 2)
    
    # Top complaint locations (by address)
    location_pipeline = [
        {"$match": {"address": {"$ne": None}}},
        {"$group": {
            "_id": "$address",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    top_locations = []
    async for doc in complaints_collection.aggregate(location_pipeline):
        top_locations.append({
            "address": doc["_id"],
            "count": doc["count"]
        })
    
    # Recent trends (complaints per day for last 7 days)
    daily_pipeline = [
        {
            "$match": {
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    daily_trends = []
    async for doc in complaints_collection.aggregate(daily_pipeline):
        daily_trends.append({
            "date": doc["_id"],
            "count": doc["count"]
        })
    
    # Verification rate
    total_resolved = await complaints_collection.count_documents({"status": "Resolved"})
    verified_count = await complaints_collection.count_documents({
        "status": "Resolved",
        "verified_by_citizen": True
    })
    
    verification_rate = round((verified_count / total_resolved * 100), 2) if total_resolved > 0 else 0
    
    return {
        "overview": {
            "total_complaints": total_complaints,
            "recent_complaints": recent_complaints,
            "days_analyzed": days_back
        },
        "by_category": complaints_by_category,
        "by_status": complaints_by_status,
        "by_priority": complaints_by_priority,
        "resolution_metrics": {
            "avg_resolution_time_hours": avg_resolution_time_hours,
            "total_resolved": total_resolved,
            "verification_rate": verification_rate
        },
        "top_locations": top_locations,
        "daily_trends": daily_trends
    }


@router.get("/category/{category}")
async def get_category_analytics(category: str, days_back: int = 30):
    """
    Get detailed analytics for a specific category
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    time_threshold = datetime.utcnow() - timedelta(days=days_back)
    
    query = {"category": category}
    recent_query = {
        "category": category,
        "created_at": {"$gte": time_threshold}
    }
    
    total = await complaints_collection.count_documents(query)
    recent = await complaints_collection.count_documents(recent_query)
    
    # Status distribution
    status_pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    
    status_dist = {}
    async for doc in complaints_collection.aggregate(status_pipeline):
        status_dist[doc["_id"]] = doc["count"]
    
    # Department handling
    dept_pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$assigned_department",
            "count": {"$sum": 1}
        }}
    ]
    
    dept_dist = {}
    async for doc in complaints_collection.aggregate(dept_pipeline):
        dept_dist[doc["_id"]] = doc["count"]
    
    return {
        "category": category,
        "total_complaints": total,
        "recent_complaints": recent,
        "by_status": status_dist,
        "by_department": dept_dist
    }


@router.get("/department/{department}")
async def get_department_analytics(department: str, days_back: int = 30):
    """
    Get analytics for a specific department
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    time_threshold = datetime.utcnow() - timedelta(days=days_back)
    
    query = {"assigned_department": department}
    
    total = await complaints_collection.count_documents(query)
    pending = await complaints_collection.count_documents({
        "assigned_department": department,
        "status": {"$in": ["Submitted", "Assigned", "In Progress"]}
    })
    resolved = await complaints_collection.count_documents({
        "assigned_department": department,
        "status": "Resolved"
    })
    
    # Category breakdown
    category_pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    category_dist = {}
    async for doc in complaints_collection.aggregate(category_pipeline):
        category_dist[doc["_id"]] = doc["count"]
    
    resolution_rate = round((resolved / total * 100), 2) if total > 0 else 0
    
    return {
        "department": department,
        "total_complaints": total,
        "pending_complaints": pending,
        "resolved_complaints": resolved,
        "resolution_rate": resolution_rate,
        "by_category": category_dist
    }

