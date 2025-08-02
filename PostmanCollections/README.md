# 📮 BiometricFlow-ZK Postman Collections

This directory contains comprehensive Postman collections for testing and interacting with the BiometricFlow-ZK APIs.

## 📁 Files Included

### 1. **PlaceBackend_API_Collection.json**
Complete Postman collection for the Place Backend API with:
- ✅ All endpoints with proper authentication
- ✅ Pre-configured environment variables
- ✅ Request examples and descriptions
- ✅ Automated tests for responses
- ✅ Security header validation

### 2. **UnifiedGateway_API_Collection.json** 
Complete Postman collection for the Unified Gateway API with:
- ✅ Multi-place aggregation endpoints
- ✅ Place-specific endpoints
- ✅ Device-specific endpoints
- ✅ Cross-place data retrieval
- ✅ Enhanced error handling

### 3. **Environment_Template.json**
Pre-configured environment template with:
- ✅ Default URLs (localhost and NGROK)
- ✅ API key placeholders
- ✅ Common variables for testing
- ✅ Date range presets

## 🚀 Quick Setup

### Step 1: Import Collections
1. Open Postman
2. Click **Import** → **Files**
3. Select all `.json` files from this directory
4. Click **Import**

### Step 2: Setup Environment
1. Import `Environment_Template.json`
2. Set your **API key** (generate using `setup_security.ps1`)
3. Update URLs if needed (NGROK, different ports, etc.)

### Step 3: Generate API Key
```powershell
# Run this to generate secure API keys
.\setup_security.ps1
```

### Step 4: Update Environment Variables
```json
{
  "api_key": "your_generated_api_key_here",
  "base_url": "http://localhost:8000",
  "gateway_url": "http://localhost:9000"
}
```

## 🔐 Authentication Setup

### Method 1: Environment Variables
1. Set `api_key` in your Postman environment
2. Collections automatically use `{{api_key}}` variable

### Method 2: Manual Setup
1. Go to any request → **Authorization** tab
2. Type: **Bearer Token**
3. Token: `your_api_key_here`

## 📋 Available Endpoints

### Place Backend API (`localhost:8000`)
- **Core:** `/`, `/health`, `/health/full`
- **Devices:** `/devices`, `/device/info`
- **Users:** `/users`, `/users/all`
- **Attendance:** `/attendance`, `/attendance/all`
- **Summary:** `/attendance/summary`, `/attendance/summary/all`
- **Holidays:** `/holidays`, `/holidays/validate`, `/holidays/suggestions`

### Unified Gateway API (`localhost:9000`)
- **Gateway:** `/`, `/health`, `/places`, `/backends/list`
- **Unified:** `/devices/all`, `/attendance/all`, `/users/all`, `/summary/all`
- **Place-Specific:** `/place/{name}/devices`, `/place/{name}/attendance`, etc.
- **Device-Specific:** `/device/{name}/info`, `/device/{name}/attendance`
- **Holidays:** `/holidays`, `/holidays/{year}`

## 🧪 Testing Features

### Automated Tests
Each request includes automated tests for:
- ✅ Response time validation
- ✅ Security header verification
- ✅ JSON format validation
- ✅ Status code checking

### Pre-Request Scripts
Automatically sets:
- ✅ Current date ranges
- ✅ Default device/place names
- ✅ Dynamic variables

### Response Handling
- ✅ Error logging for debugging
- ✅ Success validation
- ✅ Data structure verification

## 🌐 NGROK Configuration

### For NGROK Deployment:
1. Update environment variables:
```json
{
  "base_url": "https://your-backend.ngrok.io",
  "gateway_url": "https://your-gateway.ngrok.io",
  "ngrok_backend_url": "https://your-backend.ngrok.io",
  "ngrok_gateway_url": "https://your-gateway.ngrok.io"
}
```

2. Ensure your `.env` file has NGROK URLs:
```bash
NGROK_ENABLED=true
NGROK_URLS=https://your-backend.ngrok.io,https://your-gateway.ngrok.io
ALLOWED_ORIGINS=https://your-frontend.ngrok.io
```

## 📝 Usage Examples

### 1. Test Health Status
```http
GET {{base_url}}/health
```

### 2. Get All Devices
```http
GET {{base_url}}/devices
Authorization: Bearer {{api_key}}
```

### 3. Get Attendance Data
```http
GET {{base_url}}/attendance?start_date=2024-01-01&end_date=2024-01-31&device_name=Main Office
Authorization: Bearer {{api_key}}
```

### 4. Unified Gateway - All Places Data
```http
GET {{gateway_url}}/attendance/all?start_date=2024-01-01&end_date=2024-01-31
```

## 🔧 Troubleshooting

### Authentication Issues
- ✅ Verify API key is correct
- ✅ Check environment variable `{{api_key}}`
- ✅ Ensure backend is running with security enabled

### Connection Issues
- ✅ Verify URLs in environment
- ✅ Check if services are running
- ✅ Test with simple `/health` endpoint first

### CORS Issues
- ✅ Update `ALLOWED_ORIGINS` in `.env`
- ✅ Include your domain/NGROK URL
- ✅ Restart services after changes

### Rate Limiting
- ✅ Wait if getting 429 errors
- ✅ Adjust `RATE_LIMIT_REQUESTS` in `.env`
- ✅ Use reasonable delays between requests

## 📊 Response Examples

### Successful Response
```json
{
  "success": true,
  "data": [...],
  "message": "Request successful",
  "timestamp": "2024-01-01T12:00:00",
  "security_level": "secure"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Authentication required",
  "message": "Request failed",
  "status_code": 401,
  "help": "Check API documentation for valid request format"
}
```

## 🎯 Best Practices

1. **Always use environment variables** for sensitive data
2. **Test health endpoints first** before complex queries
3. **Use date ranges** appropriate for your data size
4. **Monitor rate limits** in production
5. **Check security logs** for any issues
6. **Update API keys regularly** for security

## 📞 Support

- **API Documentation:** Available at `/docs` (development mode)
- **Security Guide:** `docs/security/NGROK_SECURITY_GUIDE.md`
- **Setup Guide:** `API_ACCESS_GUIDE.md`
- **Test Script:** `test_api_access.py`

Happy testing! 🚀
