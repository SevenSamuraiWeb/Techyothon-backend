"""
Test script for the Smart Problem Resolver API
Run this after setting up the server to test all endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("\n🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_submit_complaint():
    """Test complaint submission"""
    print("\n🔍 Testing Complaint Submission...")
    
    data = {
        "title": "Large pothole on MG Road",
        "description": "Dangerous pothole near the traffic signal causing accidents",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "address": "MG Road, Bangalore",
        "user_id": "test_user_123"
    }
    
    response = requests.post(f"{BASE_URL}/api/complaints/submit", data=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if response.status_code == 200:
        complaint_id = result.get("complaint_id")
        print(f"\n✅ Complaint created with ID: {complaint_id}")
        return complaint_id
    return None

def test_get_complaint(complaint_id):
    """Test getting complaint details"""
    print(f"\n🔍 Testing Get Complaint Details for ID: {complaint_id}...")
    
    response = requests.get(f"{BASE_URL}/api/complaints/{complaint_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Title: {result.get('title')}")
        print(f"Category: {result.get('category')}")
        print(f"Priority: {result.get('priority')}")
        print(f"Status: {result.get('status')}")
        return True
    return False

def test_get_user_complaints(user_id):
    """Test getting user complaints"""
    print(f"\n🔍 Testing Get User Complaints for user: {user_id}...")
    
    response = requests.get(f"{BASE_URL}/api/complaints/user/{user_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Total complaints: {result.get('total_complaints')}")
        return True
    return False

def test_update_status(complaint_id):
    """Test updating complaint status"""
    print(f"\n🔍 Testing Status Update for complaint: {complaint_id}...")
    
    data = {
        "status": "Assigned",
        "updated_by": "admin",
        "comment": "Assigned to Roads Department"
    }
    
    response = requests.patch(
        f"{BASE_URL}/api/complaints/{complaint_id}/status",
        json=data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return True
    return False

def test_get_map_complaints():
    """Test getting complaints for map"""
    print("\n🔍 Testing Get Map Complaints (GeoJSON)...")
    
    response = requests.get(f"{BASE_URL}/api/map/complaints")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Type: {result.get('type')}")
        print(f"Features count: {len(result.get('features', []))}")
        return True
    return False

def test_get_nearby_complaints():
    """Test getting nearby complaints"""
    print("\n🔍 Testing Get Nearby Complaints...")
    
    params = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "radius_km": 5.0
    }
    
    response = requests.get(f"{BASE_URL}/api/map/nearby", params=params)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Total found: {result.get('total_found')}")
        return True
    return False

def test_get_dashboard_analytics():
    """Test analytics dashboard"""
    print("\n🔍 Testing Analytics Dashboard...")
    
    response = requests.get(f"{BASE_URL}/api/analytics/dashboard")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        overview = result.get('overview', {})
        print(f"Total complaints: {overview.get('total_complaints')}")
        print(f"Categories: {list(result.get('by_category', {}).keys())}")
        return True
    return False

def test_department_complaints():
    """Test getting department complaints"""
    print("\n🔍 Testing Department Complaints...")
    
    dept_name = "Roads Department"
    response = requests.get(f"{BASE_URL}/api/departments/{dept_name}/complaints")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Department: {result.get('department')}")
        print(f"Total complaints: {result.get('total_complaints')}")
        return True
    return False

def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("🚀 Smart Problem Resolver API Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Health check
    results['health_check'] = test_health_check()
    
    # Test 2: Submit complaint
    complaint_id = test_submit_complaint()
    results['submit_complaint'] = complaint_id is not None
    
    if complaint_id:
        # Test 3: Get complaint
        results['get_complaint'] = test_get_complaint(complaint_id)
        
        # Test 4: Update status
        results['update_status'] = test_update_status(complaint_id)
        
        # Test 5: Get user complaints
        results['get_user_complaints'] = test_get_user_complaints("test_user_123")
    
    # Test 6: Map complaints
    results['map_complaints'] = test_get_map_complaints()
    
    # Test 7: Nearby complaints
    results['nearby_complaints'] = test_get_nearby_complaints()
    
    # Test 8: Analytics
    results['analytics'] = test_get_dashboard_analytics()
    
    # Test 9: Department complaints
    results['department'] = test_department_complaints()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server")
        print("Make sure the server is running at http://localhost:8000")
        print("Run: python app.py")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)

