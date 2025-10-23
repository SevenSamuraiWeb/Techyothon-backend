from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class ComplaintStatus(str, Enum):
    SUBMITTED = "Submitted"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


class ComplaintCategory(str, Enum):
    POTHOLE = "pothole"
    GARBAGE = "garbage"
    STREETLIGHT = "streetlight"
    DRAINAGE = "drainage"
    WATER_LEAKAGE = "water_leakage"
    POWER_OUTAGE = "power_outage"
    OTHER = "other"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Department(str, Enum):
    ROADS = "Roads Department"
    SANITATION = "Sanitation Department"
    ELECTRICITY = "Electricity Department"
    WATER = "Water Department"
    OTHER = "Other"


# Models
class Location(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]


class StatusHistory(BaseModel):
    status: ComplaintStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None
    comment: Optional[str] = None


class Complaint(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str
    description: str
    category: Optional[ComplaintCategory] = None
    priority: Optional[Priority] = None
    status: ComplaintStatus = ComplaintStatus.SUBMITTED
    
    # Location data
    location: Location
    address: Optional[str] = None
    
    # Media
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    
    # User info
    user_id: Optional[str] = None
    
    # Department assignment
    assigned_department: Optional[Department] = None
    
    # Status tracking
    status_history: List[StatusHistory] = []
    verified_by_citizen: bool = False
    
    # Duplicate detection
    related_complaints: List[str] = []
    is_duplicate: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Large pothole on Main Street",
                "description": "Dangerous pothole causing traffic issues",
                "location": {
                    "type": "Point",
                    "coordinates": [77.5946, 12.9716]
                },
                "address": "Main Street, Bangalore"
            }
        }


class ComplaintCreate(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    user_id: Optional[str] = None


class ComplaintResponse(BaseModel):
    complaint_id: str
    status: ComplaintStatus
    category: Optional[ComplaintCategory] = None
    priority: Optional[Priority] = None
    message: str


class StatusUpdate(BaseModel):
    status: ComplaintStatus
    updated_by: Optional[str] = None
    comment: Optional[str] = None


class VerificationRequest(BaseModel):
    user_id: str
    verified: bool
    feedback: Optional[str] = None


class DepartmentAssignment(BaseModel):
    department: Department
    assigned_by: Optional[str] = None


# Category to Department mapping
CATEGORY_DEPARTMENT_MAP = {
    ComplaintCategory.POTHOLE: Department.ROADS,
    ComplaintCategory.GARBAGE: Department.SANITATION,
    ComplaintCategory.STREETLIGHT: Department.ELECTRICITY,
    ComplaintCategory.POWER_OUTAGE: Department.ELECTRICITY,
    ComplaintCategory.DRAINAGE: Department.WATER,
    ComplaintCategory.WATER_LEAKAGE: Department.WATER,
    ComplaintCategory.OTHER: Department.OTHER,
}

