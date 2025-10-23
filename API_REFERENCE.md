# API Reference Guide

Complete reference for all API endpoints in the Smart Problem Resolver backend.

## Base URL

```
http://localhost:8000
```

---

## Authentication

Currently, no authentication is required (for hackathon demo). In production, implement JWT or API key authentication.

---

## 1. Complaint Management

### 1.1 Submit Complaint

**Endpoint:** `POST /api/complaints/submit`

**Content-Type:** `multipart/form-data`

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Short title of the complaint |
| description | string | Yes | Detailed description |
| latitude | float | Yes | Location latitude |
| longitude | float | Yes | Location longitude |
| address | string | No | Human-readable address |
| user_id | string | No | User identifier |
| image | file | No | Image file (JPEG/PNG) |
| audio | file | No | Audio file (MP3/WAV) |

**Response:**

```json
{
  "complaint_id": "507f1f77bcf86cd799439011",
  "status": "Submitted",
  "category": "pothole",
  "priority": "high",
  "message": "Complaint registered successfully"
}
```

**Example (JavaScript):**

```javascript
const formData = new FormData();
formData.append('title', 'Large pothole');
formData.append('description', 'Dangerous pothole');
formData.append('latitude', 12.9716);
formData.append('longitude', 77.5946);
formData.append('image', imageFile);

const response = await fetch('http://localhost:8000/api/complaints/submit', {
  method: 'POST',
  body: formData
});

const data = await response.json();
```

---

### 1.2 Get Complaint Details

**Endpoint:** `GET /api/complaints/{complaint_id}`

**Response:**

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "title": "Large pothole on MG Road",
  "description": "...",
  "category": "pothole",
  "priority": "high",
  "status": "Submitted",
  "location": {
    "type": "Point",
    "coordinates": [77.5946, 12.9716]
  },
  "address": "MG Road, Bangalore",
  "image_url": "https://cloudinary.com/...",
  "audio_url": null,
  "user_id": "user123",
  "assigned_department": "Roads Department",
  "status_history": [...],
  "created_at": "2024-10-23T10:30:00Z",
  "updated_at": "2024-10-23T10:30:00Z"
}
```

---

### 1.3 Get User Complaints

**Endpoint:** `GET /api/complaints/user/{user_id}`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by status |

**Response:**

```json
{
  "user_id": "user123",
  "total_complaints": 5,
  "complaints": [...]
}
```

---

### 1.4 Find Similar Complaints

**Endpoint:** `GET /api/complaints/{complaint_id}/similar`

**Response:**

```json
{
  "complaint_id": "507f1f77bcf86cd799439011",
  "similar_complaints": [
    {
      "complaint_id": "507f1f77bcf86cd799439012",
      "title": "Pothole on MG Road",
      "status": "In Progress",
      "distance_meters": 25.5,
      "text_similarity": 0.75,
      "overall_similarity": 0.82,
      "created_at": "2024-10-22T15:20:00Z"
    }
  ]
}
```

---

## 2. Status Tracking

### 2.1 Update Complaint Status

**Endpoint:** `PATCH /api/complaints/{complaint_id}/status`

**Request Body:**

```json
{
  "status": "Assigned",
  "updated_by": "admin_user",
  "comment": "Assigned to Roads Department"
}
```

**Valid Status Values:**
- `Submitted`
- `Assigned`
- `In Progress`
- `Resolved`

**Response:**

```json
{
  "complaint_id": "507f1f77bcf86cd799439011",
  "status": "Assigned",
  "message": "Status updated successfully"
}
```

---

### 2.2 Verify Resolution

**Endpoint:** `POST /api/complaints/{complaint_id}/verify`

**Request Body:**

```json
{
  "user_id": "user123",
  "verified": true,
  "feedback": "Issue resolved satisfactorily"
}
```

**Response:**

```json
{
  "complaint_id": "507f1f77bcf86cd799439011",
  "verified": true,
  "message": "Verification recorded successfully"
}
```

---

### 2.3 Get Status History

**Endpoint:** `GET /api/complaints/{complaint_id}/history`

**Response:**

```json
{
  "complaint_id": "507f1f77bcf86cd799439011",
  "current_status": "Resolved",
  "status_history": [
    {
      "status": "Submitted",
      "timestamp": "2024-10-23T10:30:00Z",
      "updated_by": "user123",
      "comment": "Complaint submitted"
    },
    {
      "status": "Assigned",
      "timestamp": "2024-10-23T11:00:00Z",
      "updated_by": "admin",
      "comment": "Assigned to Roads Department"
    }
  ]
}
```

---

## 3. Department Management

### 3.1 Get Department Complaints

**Endpoint:** `GET /api/departments/{dept_name}/complaints`

**Valid Department Names:**
- `Roads Department`
- `Sanitation Department`
- `Electricity Department`
- `Water Department`
- `Other`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by status |
| limit | int | No | Max results (default: 100) |
| skip | int | No | Skip results (default: 0) |

**Response:**

```json
{
  "department": "Roads Department",
  "total_complaints": 45,
  "returned_count": 10,
  "complaints": [...]
}
```

---

### 3.2 Get Pending Complaints

**Endpoint:** `GET /api/departments/{dept_name}/complaints/pending`

**Response:**

```json
{
  "department": "Roads Department",
  "pending_count": 12,
  "complaints": [...]
}
```

---

### 3.3 Assign Complaint to Department

**Endpoint:** `PATCH /api/departments/assign/{complaint_id}`

**Request Body:**

```json
{
  "department": "Roads Department",
  "assigned_by": "admin_user"
}
```

**Response:**

```json
{
  "complaint_id": "507f1f77bcf86cd799439011",
  "assigned_department": "Roads Department",
  "message": "Complaint assigned successfully"
}
```

---

### 3.4 Department Statistics

**Endpoint:** `GET /api/departments/{dept_name}/stats`

**Response:**

```json
{
  "department": "Roads Department",
  "total_complaints": 45,
  "by_status": {
    "Submitted": 5,
    "Assigned": 10,
    "In Progress": 15,
    "Resolved": 15
  },
  "by_priority": {
    "low": 10,
    "medium": 20,
    "high": 10,
    "critical": 5
  }
}
```

---

## 4. Map & Location

### 4.1 Get Map Complaints (GeoJSON)

**Endpoint:** `GET /api/map/complaints`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category | string | No | Filter by category |
| status | string | No | Filter by status |
| min_lat | float | No | Bounding box min latitude |
| max_lat | float | No | Bounding box max latitude |
| min_lng | float | No | Bounding box min longitude |
| max_lng | float | No | Bounding box max longitude |

**Response (GeoJSON):**

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [77.5946, 12.9716]
      },
      "properties": {
        "complaint_id": "507f1f77bcf86cd799439011",
        "title": "Large pothole",
        "category": "pothole",
        "status": "Submitted",
        "priority": "high",
        "created_at": "2024-10-23T10:30:00Z",
        "image_url": "https://..."
      }
    }
  ]
}
```

**Usage with Leaflet.js:**

```javascript
const response = await fetch('http://localhost:8000/api/map/complaints');
const geojson = await response.json();

L.geoJSON(geojson, {
  pointToLayer: (feature, latlng) => {
    return L.marker(latlng);
  },
  onEachFeature: (feature, layer) => {
    layer.bindPopup(feature.properties.title);
  }
}).addTo(map);
```

---

### 4.2 Get Heatmap Data

**Endpoint:** `GET /api/map/heatmap`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| category | string | No | All | Filter by category |
| days_back | int | No | 30 | Days of data to include |

**Response:**

```json
{
  "heatmap_data": [
    {
      "lat": 12.9716,
      "lng": 77.5946,
      "intensity": 1
    }
  ],
  "total_points": 150
}
```

---

### 4.3 Find Nearby Complaints

**Endpoint:** `GET /api/map/nearby`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| latitude | float | Yes | - | Center latitude |
| longitude | float | Yes | - | Center longitude |
| radius_km | float | No | 1.0 | Search radius in km |
| category | string | No | All | Filter by category |
| status | string | No | All | Filter by status |

**Response:**

```json
{
  "center": {
    "latitude": 12.9716,
    "longitude": 77.5946
  },
  "radius_km": 1.0,
  "total_found": 8,
  "complaints": [...]
}
```

---

### 4.4 Get Complaint Clusters

**Endpoint:** `GET /api/map/clusters`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category | string | No | Filter by category |
| status | string | No | Filter by status |

**Response:**

```json
{
  "total_clusters": 25,
  "clusters": [
    {
      "lat": 12.972,
      "lng": 77.595,
      "count": 15,
      "complaints": ["id1", "id2", ...]
    }
  ]
}
```

---

## 5. Analytics

### 5.1 Dashboard Analytics

**Endpoint:** `GET /api/analytics/dashboard`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| days_back | int | No | 30 | Days of data to analyze |

**Response:**

```json
{
  "overview": {
    "total_complaints": 250,
    "recent_complaints": 45,
    "days_analyzed": 30
  },
  "by_category": {
    "pothole": 80,
    "garbage": 60,
    "streetlight": 40,
    "drainage": 35,
    "water_leakage": 20,
    "power_outage": 10,
    "other": 5
  },
  "by_status": {
    "Submitted": 30,
    "Assigned": 50,
    "In Progress": 70,
    "Resolved": 100
  },
  "by_priority": {
    "low": 50,
    "medium": 100,
    "high": 70,
    "critical": 30
  },
  "resolution_metrics": {
    "avg_resolution_time_hours": 48.5,
    "total_resolved": 100,
    "verification_rate": 85.5
  },
  "top_locations": [
    {"address": "MG Road", "count": 25},
    {"address": "Brigade Road", "count": 20}
  ],
  "daily_trends": [
    {"date": "2024-10-17", "count": 5},
    {"date": "2024-10-18", "count": 8}
  ]
}
```

---

### 5.2 Category Analytics

**Endpoint:** `GET /api/analytics/category/{category}`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| days_back | int | No | 30 | Days of data to analyze |

**Response:**

```json
{
  "category": "pothole",
  "total_complaints": 80,
  "recent_complaints": 15,
  "by_status": {
    "Submitted": 5,
    "Assigned": 10,
    "In Progress": 25,
    "Resolved": 40
  },
  "by_department": {
    "Roads Department": 80
  }
}
```

---

### 5.3 Department Analytics

**Endpoint:** `GET /api/analytics/department/{department}`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| days_back | int | No | 30 | Days of data to analyze |

**Response:**

```json
{
  "department": "Roads Department",
  "total_complaints": 120,
  "pending_complaints": 40,
  "resolved_complaints": 80,
  "resolution_rate": 66.67,
  "by_category": {
    "pothole": 120
  }
}
```

---

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

**Error Response Format:**

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Data Types

### Categories

- `pothole`
- `garbage`
- `streetlight`
- `drainage`
- `water_leakage`
- `power_outage`
- `other`

### Priorities

- `low`
- `medium`
- `high`
- `critical`

### Statuses

- `Submitted`
- `Assigned`
- `In Progress`
- `Resolved`

### Departments

- `Roads Department`
- `Sanitation Department`
- `Electricity Department`
- `Water Department`
- `Other`

---

## Rate Limiting

Currently no rate limiting (for hackathon). In production, implement rate limiting based on IP or API key.

---

## CORS

All origins are allowed for development. Update `middleware/cors.py` for production deployment.

