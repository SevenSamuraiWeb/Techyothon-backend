# Quick Setup Guide

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
# Make sure you're in the project directory
cd Techyothon-backend

# Activate virtual environment
venv\Scripts\activate

# Install all required packages
pip install -r requirements.txt
```

### 2. Create .env File

Create a new file named `.env` in the root directory with the following content:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://admin:Test%23123@cluster0.a2ypqny.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=smart_problem_resolver

# Cloudinary Configuration (Get these from cloudinary.com)
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here

# Gemini AI Configuration (Get from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
APP_NAME=Smart Problem Resolver
APP_VERSION=1.0.0
```

**Note**: The MongoDB URI already has the password URL-encoded (`#` as `%23`)

### 3. Get Required API Keys

#### Cloudinary (for image/audio storage)

1. Go to https://cloudinary.com/
2. Sign up for a free account
3. After login, go to Dashboard
4. Copy these values:
   - Cloud Name
   - API Key
   - API Secret
5. Paste them in your `.env` file

#### Google Gemini AI (for categorization)

1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the API key
4. Paste it in your `.env` file as `GEMINI_API_KEY`

### 4. Run the Server

```bash
# Run with auto-reload (development)
python app.py

# Or using uvicorn
uvicorn app:app --reload
```

You should see:
```
🚀 Starting Smart Problem Resolver API...
✓ Successfully connected to MongoDB!
✓ Application ready!
```

### 5. Test the API

Open your browser and go to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

### 6. Test Complaint Submission

You can test using the Swagger UI at http://localhost:8000/docs

Or use this test script:

```python
import requests

# Test complaint submission
url = "http://localhost:8000/api/complaints/submit"

data = {
    "title": "Large pothole on Main Street",
    "description": "Dangerous pothole near the traffic signal",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "address": "Main Street, Bangalore",
    "user_id": "test_user_123"
}

response = requests.post(url, data=data)
print(response.json())
```

## Common Issues

### Issue 1: Import errors for pymongo or motor

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue 2: MongoDB connection failed

**Solution**: 
- Check if `.env` file exists
- Verify MongoDB URI is correct
- Ensure password special characters are URL-encoded

### Issue 3: Cloudinary upload fails

**Solution**:
- Verify you've added Cloudinary credentials to `.env`
- Check if credentials are correct (no extra spaces)

### Issue 4: Gemini API errors

**Solution**:
- Ensure you have a valid Gemini API key
- Check if you're within the API quota
- Try regenerating the API key

## Next Steps

1. **Test all endpoints** using Swagger UI at http://localhost:8000/docs
2. **Connect with frontend** - Share the base URL with your frontend team
3. **Test file uploads** - Try uploading images through the complaint submission
4. **Check analytics** - View the dashboard at `/api/analytics/dashboard`
5. **Test map features** - Get GeoJSON data at `/api/map/complaints`

## API Testing with Frontend

Your Next.js frontend should make requests to:

```javascript
const API_BASE_URL = "http://localhost:8000";

// Submit complaint
const submitComplaint = async (formData) => {
  const response = await fetch(`${API_BASE_URL}/api/complaints/submit`, {
    method: 'POST',
    body: formData // FormData with title, description, latitude, longitude, image
  });
  return response.json();
};

// Get all complaints for map
const getMapComplaints = async () => {
  const response = await fetch(`${API_BASE_URL}/api/map/complaints`);
  return response.json();
};

// Get user complaints
const getUserComplaints = async (userId) => {
  const response = await fetch(`${API_BASE_URL}/api/complaints/user/${userId}`);
  return response.json();
};
```

## CORS Configuration

The backend is configured to accept requests from any origin (for development).

For production, update `middleware/cors.py`:

```python
allow_origins=["http://localhost:3000", "https://yourfrontend.com"]
```

## File Upload Size Limits

Default limits:
- Images: Up to 10MB
- Audio: Up to 10MB

To change, configure in your deployment environment.

## Database Indexes

The system automatically creates a geospatial index on the `location` field for efficient nearby queries.

## Need Help?

1. Check `/docs` for API documentation
2. Check `/health` to verify server is running
3. Look at console logs for error messages
4. Verify all environment variables are set correctly

