# Frontend Integration Guide

Guide for integrating the Smart Problem Resolver backend with your Next.js frontend.

## API Configuration

### 1. Create API Client (Next.js)

Create `lib/api.js`:

```javascript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  baseURL: API_BASE_URL,
  
  // Helper function for fetch requests
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }
    
    return response.json();
  }
};
```

---

## Core Features Implementation

### 1. Multi-Modal Complaint Submission

```javascript
// components/ComplaintForm.jsx
import { useState } from 'react';
import { api } from '@/lib/api';

export default function ComplaintForm() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    latitude: null,
    longitude: null,
    address: '',
  });
  const [image, setImage] = useState(null);
  const [audio, setAudio] = useState(null);
  const [loading, setLoading] = useState(false);

  // Get user's location
  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        setFormData(prev => ({
          ...prev,
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        }));
        
        // Optionally, reverse geocode to get address
        reverseGeocode(position.coords.latitude, position.coords.longitude);
      });
    }
  };

  const reverseGeocode = async (lat, lng) => {
    // Use a geocoding service to get address from coordinates
    // Example with OpenStreetMap Nominatim
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`
      );
      const data = await response.json();
      setFormData(prev => ({
        ...prev,
        address: data.display_name
      }));
    } catch (error) {
      console.error('Geocoding error:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Create FormData object
      const data = new FormData();
      data.append('title', formData.title);
      data.append('description', formData.description);
      data.append('latitude', formData.latitude);
      data.append('longitude', formData.longitude);
      
      if (formData.address) {
        data.append('address', formData.address);
      }
      
      // Add user ID from your auth system
      const userId = localStorage.getItem('userId') || 'anonymous';
      data.append('user_id', userId);
      
      // Add files if present
      if (image) {
        data.append('image', image);
      }
      
      if (audio) {
        data.append('audio', audio);
      }

      // Submit complaint
      const response = await fetch(`${api.baseURL}/api/complaints/submit`, {
        method: 'POST',
        body: data
      });

      const result = await response.json();
      
      if (response.ok) {
        alert(`Complaint submitted! ID: ${result.complaint_id}`);
        // Reset form or redirect
      } else {
        throw new Error(result.detail);
      }
    } catch (error) {
      console.error('Error submitting complaint:', error);
      alert('Failed to submit complaint: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label>Title</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          required
          className="w-full border p-2 rounded"
        />
      </div>

      <div>
        <label>Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          required
          className="w-full border p-2 rounded"
          rows="4"
        />
      </div>

      <div>
        <label>Location</label>
        <button
          type="button"
          onClick={getCurrentLocation}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          📍 Use Current Location
        </button>
        {formData.latitude && (
          <p className="text-sm text-gray-600 mt-2">
            Location: {formData.latitude.toFixed(4)}, {formData.longitude.toFixed(4)}
          </p>
        )}
      </div>

      <div>
        <label>Upload Image (Optional)</label>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImage(e.target.files[0])}
          className="w-full border p-2 rounded"
        />
      </div>

      <div>
        <label>Upload Audio (Optional)</label>
        <input
          type="file"
          accept="audio/*"
          onChange={(e) => setAudio(e.target.files[0])}
          className="w-full border p-2 rounded"
        />
      </div>

      <button
        type="submit"
        disabled={loading || !formData.latitude}
        className="w-full bg-green-500 text-white py-3 rounded disabled:bg-gray-300"
      >
        {loading ? 'Submitting...' : 'Submit Complaint'}
      </button>
    </form>
  );
}
```

---

### 2. Leaflet.js Map Integration

```javascript
// components/ComplaintsMap.jsx
import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { api } from '@/lib/api';

export default function ComplaintsMap() {
  const [geojsonData, setGeojsonData] = useState(null);
  const [filters, setFilters] = useState({
    category: '',
    status: ''
  });

  useEffect(() => {
    fetchComplaints();
  }, [filters]);

  const fetchComplaints = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.category) params.append('category', filters.category);
      if (filters.status) params.append('status', filters.status);
      
      const data = await api.request(`/api/map/complaints?${params}`);
      setGeojsonData(data);
    } catch (error) {
      console.error('Error fetching complaints:', error);
    }
  };

  const onEachFeature = (feature, layer) => {
    const props = feature.properties;
    layer.bindPopup(`
      <div>
        <h3><strong>${props.title}</strong></h3>
        <p>Category: ${props.category}</p>
        <p>Status: ${props.status}</p>
        <p>Priority: ${props.priority}</p>
        ${props.image_url ? `<img src="${props.image_url}" width="200"/>` : ''}
      </div>
    `);
  };

  const getCategoryIcon = (category) => {
    const icons = {
      pothole: '🕳️',
      garbage: '🗑️',
      streetlight: '💡',
      drainage: '🚰',
      water_leakage: '💧',
      power_outage: '⚡',
      other: '❓'
    };
    return icons[category] || '📍';
  };

  return (
    <div>
      {/* Filters */}
      <div className="mb-4 flex gap-4">
        <select
          value={filters.category}
          onChange={(e) => setFilters({...filters, category: e.target.value})}
          className="border p-2 rounded"
        >
          <option value="">All Categories</option>
          <option value="pothole">Potholes</option>
          <option value="garbage">Garbage</option>
          <option value="streetlight">Street Lights</option>
          <option value="drainage">Drainage</option>
          <option value="water_leakage">Water Leakage</option>
          <option value="power_outage">Power Outage</option>
        </select>

        <select
          value={filters.status}
          onChange={(e) => setFilters({...filters, status: e.target.value})}
          className="border p-2 rounded"
        >
          <option value="">All Statuses</option>
          <option value="Submitted">Submitted</option>
          <option value="Assigned">Assigned</option>
          <option value="In Progress">In Progress</option>
          <option value="Resolved">Resolved</option>
        </select>
      </div>

      {/* Map */}
      <MapContainer
        center={[12.9716, 77.5946]}
        zoom={12}
        style={{ height: '600px', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        
        {geojsonData && (
          <GeoJSON
            data={geojsonData}
            onEachFeature={onEachFeature}
            pointToLayer={(feature, latlng) => {
              const icon = getCategoryIcon(feature.properties.category);
              return L.marker(latlng, {
                icon: L.divIcon({
                  html: `<div style="font-size: 24px;">${icon}</div>`,
                  className: 'custom-marker'
                })
              });
            }}
          />
        )}
      </MapContainer>
    </div>
  );
}
```

---

### 3. Complaint Status Tracking

```javascript
// components/ComplaintTracker.jsx
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function ComplaintTracker({ userId }) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserComplaints();
  }, [userId]);

  const fetchUserComplaints = async () => {
    try {
      const data = await api.request(`/api/complaints/user/${userId}`);
      setComplaints(data.complaints);
    } catch (error) {
      console.error('Error fetching complaints:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Submitted': 'bg-blue-100 text-blue-800',
      'Assigned': 'bg-yellow-100 text-yellow-800',
      'In Progress': 'bg-orange-100 text-orange-800',
      'Resolved': 'bg-green-100 text-green-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusStep = (status) => {
    const steps = ['Submitted', 'Assigned', 'In Progress', 'Resolved'];
    return steps.indexOf(status) + 1;
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">My Complaints</h2>
      
      {complaints.map((complaint) => (
        <div key={complaint._id} className="border rounded-lg p-4 shadow">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-bold text-lg">{complaint.title}</h3>
              <p className="text-gray-600 text-sm">{complaint.description}</p>
              <p className="text-gray-500 text-xs mt-2">
                {new Date(complaint.created_at).toLocaleDateString()}
              </p>
            </div>
            
            <span className={`px-3 py-1 rounded-full text-sm ${getStatusColor(complaint.status)}`}>
              {complaint.status}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between mb-2">
              {['Submitted', 'Assigned', 'In Progress', 'Resolved'].map((step, idx) => (
                <div key={step} className="text-xs text-center flex-1">
                  <div className={`w-8 h-8 mx-auto rounded-full flex items-center justify-center ${
                    getStatusStep(complaint.status) > idx ? 'bg-green-500 text-white' : 'bg-gray-300'
                  }`}>
                    {idx + 1}
                  </div>
                  <div className="mt-1">{step}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Image Preview */}
          {complaint.image_url && (
            <img
              src={complaint.image_url}
              alt="Complaint"
              className="mt-4 w-full h-48 object-cover rounded"
            />
          )}
        </div>
      ))}
    </div>
  );
}
```

---

### 4. Department Dashboard

```javascript
// components/DepartmentDashboard.jsx
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function DepartmentDashboard({ department }) {
  const [stats, setStats] = useState(null);
  const [complaints, setComplaints] = useState([]);

  useEffect(() => {
    fetchDepartmentData();
  }, [department]);

  const fetchDepartmentData = async () => {
    try {
      const [statsData, complaintsData] = await Promise.all([
        api.request(`/api/departments/${department}/stats`),
        api.request(`/api/departments/${department}/complaints/pending`)
      ]);
      
      setStats(statsData);
      setComplaints(complaintsData.complaints);
    } catch (error) {
      console.error('Error fetching department data:', error);
    }
  };

  const updateStatus = async (complaintId, newStatus) => {
    try {
      await api.request(`/api/complaints/${complaintId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          updated_by: 'department_admin',
          comment: `Status updated to ${newStatus}`
        })
      });
      
      // Refresh data
      fetchDepartmentData();
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">{department}</h1>
      
      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-100 p-4 rounded">
            <div className="text-2xl font-bold">{stats.total_complaints}</div>
            <div className="text-sm">Total Complaints</div>
          </div>
          
          <div className="bg-yellow-100 p-4 rounded">
            <div className="text-2xl font-bold">{stats.by_status['Submitted'] || 0}</div>
            <div className="text-sm">Submitted</div>
          </div>
          
          <div className="bg-orange-100 p-4 rounded">
            <div className="text-2xl font-bold">{stats.by_status['In Progress'] || 0}</div>
            <div className="text-sm">In Progress</div>
          </div>
          
          <div className="bg-green-100 p-4 rounded">
            <div className="text-2xl font-bold">{stats.by_status['Resolved'] || 0}</div>
            <div className="text-sm">Resolved</div>
          </div>
        </div>
      )}

      {/* Pending Complaints */}
      <h2 className="text-xl font-bold mb-4">Pending Complaints</h2>
      <div className="space-y-4">
        {complaints.map((complaint) => (
          <div key={complaint._id} className="border p-4 rounded">
            <h3 className="font-bold">{complaint.title}</h3>
            <p className="text-sm text-gray-600">{complaint.description}</p>
            <p className="text-xs text-gray-500 mt-2">
              Priority: {complaint.priority} | Status: {complaint.status}
            </p>
            
            <div className="mt-3 flex gap-2">
              <button
                onClick={() => updateStatus(complaint._id, 'Assigned')}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm"
              >
                Assign
              </button>
              <button
                onClick={() => updateStatus(complaint._id, 'In Progress')}
                className="px-3 py-1 bg-orange-500 text-white rounded text-sm"
              >
                Start Work
              </button>
              <button
                onClick={() => updateStatus(complaint._id, 'Resolved')}
                className="px-3 py-1 bg-green-500 text-white rounded text-sm"
              >
                Mark Resolved
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### 5. Analytics Dashboard

```javascript
// components/AnalyticsDashboard.jsx
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const data = await api.request('/api/analytics/dashboard');
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  if (!analytics) return <div>Loading...</div>;

  const categoryData = Object.entries(analytics.by_category).map(([name, count]) => ({
    name,
    count
  }));

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Analytics Dashboard</h1>
      
      {/* Overview Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-100 p-6 rounded">
          <div className="text-3xl font-bold">{analytics.overview.total_complaints}</div>
          <div>Total Complaints</div>
        </div>
        
        <div className="bg-green-100 p-6 rounded">
          <div className="text-3xl font-bold">
            {analytics.resolution_metrics.avg_resolution_time_hours}h
          </div>
          <div>Avg Resolution Time</div>
        </div>
        
        <div className="bg-purple-100 p-6 rounded">
          <div className="text-3xl font-bold">
            {analytics.resolution_metrics.verification_rate}%
          </div>
          <div>Verification Rate</div>
        </div>
      </div>

      {/* Category Chart */}
      <div className="bg-white p-6 rounded shadow">
        <h2 className="text-xl font-bold mb-4">Complaints by Category</h2>
        <BarChart width={600} height={300} data={categoryData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </div>
    </div>
  );
}
```

---

## Environment Variables

Create `.env.local` in your Next.js project:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

---

## Important Notes

1. **CORS**: Backend is configured to allow all origins during development
2. **File Uploads**: Use FormData for multipart uploads
3. **Location**: Use browser's Geolocation API
4. **Real-time Updates**: Consider using WebSockets or polling for live updates
5. **Authentication**: Add JWT tokens when implementing user authentication
6. **Error Handling**: Always handle API errors gracefully

---

## Testing Checklist

- [ ] Complaint submission works with all fields
- [ ] Image upload to Cloudinary successful
- [ ] Map displays complaints correctly
- [ ] Status tracking shows progress
- [ ] Department filtering works
- [ ] Analytics data displays properly
- [ ] Mobile responsive design

