from fastapi import APIRouter, Query
from typing import Optional, List
from database import get_database

router = APIRouter(prefix="/api/map", tags=["map"])


@router.get("/complaints")
async def get_map_complaints(
    category: Optional[str] = None,
    status: Optional[str] = None,
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lng: Optional[float] = None
):
    """
    Get complaints in GeoJSON format for map display
    Supports filtering by category, status, and bounding box
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    query = {}
    
    if category:
        query["category"] = category
    
    if status:
        query["status"] = status
    
    # Add bounding box filter if coordinates provided
    if all(v is not None for v in [min_lat, max_lat, min_lng, max_lng]):
        query["location.coordinates.0"] = {"$gte": min_lng, "$lte": max_lng}
        query["location.coordinates.1"] = {"$gte": min_lat, "$lte": max_lat}
    
    features = []
    cursor = complaints_collection.find(query)
    
    async for complaint in cursor:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": complaint["location"]["coordinates"]
            },
            "properties": {
                "complaint_id": str(complaint["_id"]),
                "title": complaint.get("title"),
                "category": complaint.get("category"),
                "status": complaint.get("status"),
                "priority": complaint.get("priority"),
                "created_at": complaint.get("created_at").isoformat() if complaint.get("created_at") else None,
                "image_url": complaint.get("image_url")
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/heatmap")
async def get_heatmap_data(
    category: Optional[str] = None,
    days_back: int = 30
):
    """
    Get complaint density data for heatmap visualization
    Returns array of {lat, lng, intensity}
    """
    from datetime import datetime, timedelta
    
    db = await get_database()
    complaints_collection = db["complaints"]
    
    query = {}
    
    if category:
        query["category"] = category
    
    # Filter by time window
    time_threshold = datetime.utcnow() - timedelta(days=days_back)
    query["created_at"] = {"$gte": time_threshold}
    
    heatmap_data = []
    cursor = complaints_collection.find(query)
    
    async for complaint in cursor:
        coords = complaint["location"]["coordinates"]
        heatmap_data.append({
            "lat": coords[1],
            "lng": coords[0],
            "intensity": 1  # Can be weighted by priority later
        })
    
    return {
        "heatmap_data": heatmap_data,
        "total_points": len(heatmap_data)
    }


@router.get("/nearby")
async def get_nearby_complaints(
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location"),
    radius_km: float = Query(1.0, description="Search radius in kilometers"),
    category: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Find complaints near a specific location
    Uses MongoDB geospatial query
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    # Ensure geospatial index exists
    try:
        await complaints_collection.create_index([("location", "2dsphere")])
    except:
        pass  # Index might already exist
    
    # Build query
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": radius_km * 1000  # Convert km to meters
            }
        }
    }
    
    if category:
        query["category"] = category
    
    if status:
        query["status"] = status
    
    nearby_complaints = []
    cursor = complaints_collection.find(query).limit(50)
    
    async for complaint in cursor:
        complaint["_id"] = str(complaint["_id"])
        nearby_complaints.append(complaint)
    
    return {
        "center": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "total_found": len(nearby_complaints),
        "complaints": nearby_complaints
    }


@router.get("/clusters")
async def get_complaint_clusters(
    category: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get complaint clusters/hotspots
    Groups nearby complaints for better visualization
    """
    db = await get_database()
    complaints_collection = db["complaints"]
    
    query = {}
    if category:
        query["category"] = category
    if status:
        query["status"] = status
    
    # Simple clustering by rounding coordinates
    # For production, use more sophisticated clustering algorithms
    clusters = {}
    cursor = complaints_collection.find(query)
    
    async for complaint in cursor:
        coords = complaint["location"]["coordinates"]
        # Round to 3 decimal places (~100m precision)
        cluster_key = f"{round(coords[1], 3)},{round(coords[0], 3)}"
        
        if cluster_key not in clusters:
            clusters[cluster_key] = {
                "lat": round(coords[1], 3),
                "lng": round(coords[0], 3),
                "count": 0,
                "complaints": []
            }
        
        clusters[cluster_key]["count"] += 1
        clusters[cluster_key]["complaints"].append(str(complaint["_id"]))
    
    # Convert to list and sort by count
    cluster_list = list(clusters.values())
    cluster_list.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "total_clusters": len(cluster_list),
        "clusters": cluster_list
    }

