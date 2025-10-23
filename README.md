# Smart Local Problem Resolver - Backend

A FastAPI-based backend for a citizen complaint management platform that leverages AI for automatic categorization and intelligent duplicate detection.

## Features

✅ **Multi-Modal Complaint Submission** - Accept text, images, and audio  
✅ **AI-Powered Categorization** - Automatic categorization using Gemini AI  
✅ **Real-Time Status Tracking** - Track complaints from submission to resolution  
✅ **Department Management** - Role-based access for different municipal departments  
✅ **Interactive Map Integration** - GeoJSON endpoints for Leaflet.js  
✅ **Duplicate Detection** - Smart similarity matching to identify duplicate complaints  
✅ **Analytics Dashboard** - Comprehensive insights for authorities  

## Tech Stack

- **FastAPI** - Modern Python web framework
- **MongoDB** - Database with geospatial capabilities
- **Motor** - Async MongoDB driver
- **Cloudinary** - Cloud storage for images and audio
- **Google Gemini AI** - Multi-modal AI for categorization
- **Pydantic** - Data validation

## Project Structure

```
Techyothon-backend/
├── app.py                      # Main FastAPI application
├── config.py                   # Configuration management
├── database.py                 # MongoDB connection
├── models.py                   # Pydantic models and schemas
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── routers/
│   ├── complaints.py          # Complaint submission & retrieval
│   ├── status.py              # Status tracking endpoints
│   ├── departments.py         # Department management
│   ├── map.py                 # Map & location endpoints
│   └── analytics.py           # Analytics & statistics
├── services/
│   ├── cloudinary_service.py  # File upload service
│   ├── gemini_service.py      # AI categorization
│   └── similarity_service.py  # Duplicate detection
└── middleware/
    └── cors.py                # CORS configuration
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=smart_problem_resolver

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key

# Application Settings
APP_NAME=Smart Problem Resolver
APP_VERSION=1.0.0
```

### 3. Get API Keys

#### MongoDB Atlas
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get your connection string
4. **Important**: URL-encode special characters in password (e.g., `#` becomes `%23`)

#### Cloudinary
1. Go to [Cloudinary](https://cloudinary.com/)
2. Sign up for free account
3. Get Cloud Name, API Key, and API Secret from dashboard

#### Google Gemini AI
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Copy the key to your `.env` file

### 4. Run the Application

```bash
# Development mode with auto-reload
python app.py

# Or using uvicorn directly
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Complaint Management

- `POST /api/complaints/submit` - Submit new complaint (multipart form-data)
- `GET /api/complaints/{complaint_id}` - Get complaint details
- `GET /api/complaints/user/{user_id}` - Get user's complaints
- `GET /api/complaints/{complaint_id}/similar` - Find similar complaints

### Status Tracking

- `PATCH /api/complaints/{complaint_id}/status` - Update complaint status
- `POST /api/complaints/{complaint_id}/verify` - Verify resolution
- `GET /api/complaints/{complaint_id}/history` - Get status history

### Department Management

- `GET /api/departments/{dept_name}/complaints` - Get department complaints
- `GET /api/departments/{dept_name}/complaints/pending` - Get pending complaints
- `PATCH /api/departments/assign/{complaint_id}` - Assign to department
- `GET /api/departments/{dept_name}/stats` - Department statistics

### Map & Location

- `GET /api/map/complaints` - Get complaints in GeoJSON format
- `GET /api/map/heatmap` - Get heatmap data
- `GET /api/map/nearby` - Find nearby complaints
- `GET /api/map/clusters` - Get complaint clusters

### Analytics

- `GET /api/analytics/dashboard` - Overall analytics dashboard
- `GET /api/analytics/category/{category}` - Category-specific analytics
- `GET /api/analytics/department/{department}` - Department analytics

## Complaint Submission Example

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/complaints/submit" \
  -F "title=Pothole on Main Street" \
  -F "description=Large pothole causing traffic issues" \
  -F "latitude=12.9716" \
  -F "longitude=77.5946" \
  -F "address=Main Street, Bangalore" \
  -F "user_id=user123" \
  -F "image=@pothole.jpg"
```

### Using JavaScript/Fetch

```javascript
const formData = new FormData();
formData.append('title', 'Pothole on Main Street');
formData.append('description', 'Large pothole causing traffic issues');
formData.append('latitude', 12.9716);
formData.append('longitude', 77.5946);
formData.append('address', 'Main Street, Bangalore');
formData.append('user_id', 'user123');
formData.append('image', fileInput.files[0]);

const response = await fetch('http://localhost:8000/api/complaints/submit', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);
```

## Categories

- `pothole` - Road potholes
- `garbage` - Garbage overflow/collection issues
- `streetlight` - Street light problems
- `drainage` - Drainage and sewage issues
- `water_leakage` - Water pipe leaks
- `power_outage` - Power supply issues
- `other` - Other civic issues

## Status Flow

1. **Submitted** - Initial complaint submission
2. **Assigned** - Assigned to department
3. **In Progress** - Work in progress
4. **Resolved** - Issue resolved
5. Citizen can verify resolution

## Departments

- **Roads Department** - Handles potholes
- **Sanitation Department** - Handles garbage issues
- **Electricity Department** - Handles streetlights and power outages
- **Water Department** - Handles drainage and water leakage
- **Other** - Handles miscellaneous issues

## Features in Detail

### 1. AI Categorization

Gemini AI analyzes the complaint title, description, and image to:
- Automatically categorize the issue
- Determine priority level (low, medium, high, critical)
- Extract relevant insights

### 2. Duplicate Detection

The system uses:
- **Location-based clustering** - Groups complaints within 50m radius
- **Text similarity** - Compares complaint descriptions
- **Category matching** - Only compares similar issue types
- **Time window** - Checks recent complaints (last 7 days)

### 3. Geospatial Queries

MongoDB's geospatial features enable:
- Finding nearby complaints
- Generating heatmaps
- Creating complaint clusters
- Bounding box queries for map views

### 4. Real-time Analytics

Get insights on:
- Complaint trends over time
- Resolution rates by department
- High-complaint areas
- Category distribution
- Priority breakdown

## Testing the API

### Health Check

```bash
curl http://localhost:8000/health
```

### Submit Test Complaint

```bash
curl -X POST "http://localhost:8000/api/complaints/submit" \
  -F "title=Test Pothole" \
  -F "description=Testing the system" \
  -F "latitude=12.9716" \
  -F "longitude=77.5946"
```

### Get Map Data

```bash
curl "http://localhost:8000/api/map/complaints?category=pothole"
```

## Troubleshooting

### Import Errors

If you see import errors, ensure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### MongoDB Connection Issues

1. Check if MongoDB URI is correct in `.env`
2. Ensure password is URL-encoded (special characters like `#` should be `%23`)
3. Verify network access in MongoDB Atlas (add your IP to whitelist)

### Cloudinary Upload Errors

1. Verify credentials in `.env`
2. Check if file size is within limits
3. Ensure file type is supported (JPEG, PNG for images)

### Gemini API Errors

1. Verify API key is valid
2. Check if you have quota available
3. Ensure image URLs are accessible

## Development

### Run with Auto-reload

```bash
uvicorn app:app --reload
```

### Run on Different Port

```bash
uvicorn app:app --port 8080
```

### Enable Debug Mode

Set `reload=True` in `app.py` or use the `--reload` flag

## Production Deployment

For production deployment:

1. Set proper CORS origins in `middleware/cors.py`
2. Use environment variables for all secrets
3. Enable HTTPS
4. Use a production-ready MongoDB instance
5. Set up proper logging
6. Configure rate limiting
7. Use a reverse proxy (nginx)

## License

MIT License - Built for Techyothon Hackathon 2024

## Support

For issues or questions, please check the API documentation at `/docs` or contact the development team.

