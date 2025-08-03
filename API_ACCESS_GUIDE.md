# 🔐 API Access Guide for BiometricFlow-ZK

This guide explains how to properly access the secure API endpoints in your BiometricFlow-ZK system.

## 🚨 Current Security Issue

Your system has **strong security enabled** which requires proper authentication for all API endpoints. Here's how to resolve access issues:

## 📋 Quick Solution Steps

### 1. Generate API Keys
First, generate secure API keys by running these commands:

```bash
# Generate Main API Key
python -c "import secrets; print('MAIN_API_KEY=' + secrets.token_urlsafe(32))"

# Generate Backend API Key  
python -c "import secrets; print('BACKEND_API_KEY=' + secrets.token_urlsafe(32))"

# Generate Frontend API Key
python -c "import secrets; print('FRONTEND_API_KEY=' + secrets.token_urlsafe(32))"

# Generate JWT Secret
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"
```

### 2. Create Environment Configuration
Create a `.env` file in your project root with the generated keys:

```bash
# Security Configuration
MAIN_API_KEY=your_generated_main_key_here
BACKEND_API_KEY=your_generated_backend_key_here  
FRONTEND_API_KEY=your_generated_frontend_key_here
JWT_SECRET=your_generated_jwt_secret_here

# Environment Settings
ENVIRONMENT=production
NGROK_ENABLED=false

# For local development, you can temporarily disable some security
# ALLOW_NO_AUTH=true  # Only for testing!
```

### 3. Test API Access
Test your API endpoints with proper authentication:

```bash
# Test health endpoint
curl -H "Authorization: Bearer YOUR_MAIN_API_KEY" http://localhost:8000/health

# Test with actual key (replace with your generated key)
curl -H "Authorization: Bearer AbCdEf123456..." http://localhost:8000/health
```

## 🛠️ Available API Endpoints

### Core Endpoints
- `GET /` - Root endpoint (basic info)
- `GET /health` - Simple health check
- `GET /health/full` - Detailed health information

### Device Management
- `GET /devices` - List all configured devices
- `GET /device/info` - Get device information

### User Management  
- `GET /users` - Get users from device
- `GET /users/all` - Get all users from all devices

### Attendance Data
- `GET /attendance` - Get attendance records
- `GET /attendance/all` - Get all attendance records
- `GET /attendance/summary` - Get attendance summary
- `GET /attendance/summary/all` - Get complete attendance summary

### Holiday Management
- `GET /holidays` - Get holiday information
- `POST /holidays/validate` - Validate holiday dates
- `GET /holidays/suggestions` - Get holiday suggestions

## 🔒 Authentication Methods

### Method 1: Bearer Token (Recommended)
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/endpoint
```

### Method 2: API Key Header
```bash
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/endpoint
```

### Method 3: Python Requests
```python
import requests

# Your API key
api_key = "your_generated_api_key_here"

# Headers
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Make request
response = requests.get("http://localhost:8000/health", headers=headers)
print(response.json())
```

### Method 4: JavaScript/Fetch
```javascript
const apiKey = 'your_generated_api_key_here';

fetch('http://localhost:8000/health', {
    headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🔧 Troubleshooting Access Issues

### Issue 1: "401 Unauthorized" or "Authentication Required"
**Solution:**
1. Generate API keys using the commands above
2. Create `.env` file with the keys
3. Restart your backend service
4. Include `Authorization: Bearer YOUR_KEY` in requests

### Issue 2: "403 Forbidden" or "Invalid API Key"
**Solution:**
1. Verify your API key is correct
2. Check that the key is at least 32 characters
3. Ensure no extra spaces in the key
4. Try regenerating the key

### Issue 3: CORS Errors (from browser)
**Solution:**
Add to your `.env` file:
```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501,http://127.0.0.1:8501
```

### Issue 4: Connection Refused
**Solution:**
1. Ensure backend is running: `python src/biometric_flow/backend/place_backend.py`
2. Check the correct port (default: 8000)
3. Verify no firewall blocking

## 🚀 Quick Test Script

Create this test script (`test_api.py`) to verify your setup:

```python
#!/usr/bin/env python3
import requests
import os
import sys

# Load your API key
API_KEY = "YOUR_GENERATED_API_KEY_HERE"  # Replace with actual key
BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET"):
    """Test an API endpoint"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers)
            
        print(f"✅ {method} {endpoint}: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ {method} {endpoint}: Connection failed - {e}")

if __name__ == "__main__":
    print("🔍 Testing BiometricFlow-ZK API Endpoints...")
    print(f"📡 Base URL: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY[:8]}...")
    print("-" * 50)
    
    # Test endpoints
    test_endpoint("/")
    test_endpoint("/health")
    test_endpoint("/health/full")
    test_endpoint("/devices")
    test_endpoint("/users")
    test_endpoint("/attendance")
    
    print("-" * 50)
    print("✨ Testing complete!")
```

## 🔄 Alternative: Temporary Security Bypass (Development Only)

**⚠️ ONLY for local development/testing:**

Add to your `.env` file:
```bash
ENVIRONMENT=development
ALLOW_NO_AUTH=true
```

This will temporarily disable authentication. **Never use this in production!**

## 📞 Need Help?

1. **Check logs**: Look at console output when starting the backend
2. **Security logs**: Check `logs/security.log` for auth failures  
3. **Environment**: Ensure `.env` file is in the correct location
4. **Keys**: Verify API keys are properly generated and formatted

## 🎯 Next Steps

1. Generate your API keys using the commands above
2. Create your `.env` file
3. Restart the backend service
4. Test with the provided examples
5. Start using the endpoints with proper authentication!

Remember: Security is important, but it shouldn't block your development. Follow these steps and you'll have secure, working API access in minutes! 🚀
