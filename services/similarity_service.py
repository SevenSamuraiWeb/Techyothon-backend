from typing import List, Dict
from datetime import datetime, timedelta
from models import Complaint, ComplaintCategory
from database import get_database
import math


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in meters using Haversine formula
    """
    R = 6371000  # Earth's radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Simple text similarity using word overlap (Jaccard similarity)
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


async def find_similar_complaints(
    complaint_id: str,
    title: str,
    description: str,
    category: ComplaintCategory,
    latitude: float,
    longitude: float,
    max_distance_meters: float = 50.0,
    days_back: int = 7,
    similarity_threshold: float = 0.3
) -> List[Dict]:
    """
    Find similar complaints based on:
    1. Same category
    2. Nearby location (within max_distance_meters)
    3. Recent time window (within days_back)
    4. Text similarity
    """
    
    db = await get_database()
    complaints_collection = db["complaints"]
    
    # Calculate time threshold
    time_threshold = datetime.utcnow() - timedelta(days=days_back)
    
    # Query for nearby complaints in same category
    query = {
        "_id": {"$ne": complaint_id},  # Exclude current complaint
        "category": category,
        "created_at": {"$gte": time_threshold}
    }
    
    similar_complaints = []
    
    # Find potential matches
    cursor = complaints_collection.find(query)
    
    async for complaint_doc in cursor:
        # Calculate geographic distance
        complaint_coords = complaint_doc["location"]["coordinates"]
        complaint_lon, complaint_lat = complaint_coords
        
        distance = calculate_distance(latitude, longitude, complaint_lat, complaint_lon)
        
        # Check if within distance threshold
        if distance <= max_distance_meters:
            # Calculate text similarity
            text_similarity = calculate_text_similarity(
                f"{title} {description}",
                f"{complaint_doc.get('title', '')} {complaint_doc.get('description', '')}"
            )
            
            # Calculate overall similarity score
            # Weight: 60% location, 40% text
            location_score = 1 - (distance / max_distance_meters)
            overall_similarity = (0.6 * location_score) + (0.4 * text_similarity)
            
            if overall_similarity >= similarity_threshold:
                similar_complaints.append({
                    "complaint_id": str(complaint_doc["_id"]),
                    "title": complaint_doc.get("title"),
                    "status": complaint_doc.get("status"),
                    "distance_meters": round(distance, 2),
                    "text_similarity": round(text_similarity, 2),
                    "overall_similarity": round(overall_similarity, 2),
                    "created_at": complaint_doc.get("created_at")
                })
    
    # Sort by similarity score (highest first)
    similar_complaints.sort(key=lambda x: x["overall_similarity"], reverse=True)
    
    return similar_complaints


async def check_duplicate(
    title: str,
    description: str,
    category: ComplaintCategory,
    latitude: float,
    longitude: float,
    duplicate_threshold: float = 0.8
) -> Dict:
    """
    Check if a complaint is likely a duplicate
    Returns: {"is_duplicate": bool, "similar_complaints": List}
    """
    
    similar = await find_similar_complaints(
        complaint_id="",  # Empty for new complaints
        title=title,
        description=description,
        category=category,
        latitude=latitude,
        longitude=longitude,
        max_distance_meters=50.0,
        days_back=7,
        similarity_threshold=0.5
    )
    
    # Check if any complaint exceeds duplicate threshold
    is_duplicate = any(c["overall_similarity"] >= duplicate_threshold for c in similar)
    
    return {
        "is_duplicate": is_duplicate,
        "similar_complaints": similar[:5]  # Return top 5 similar complaints
    }

