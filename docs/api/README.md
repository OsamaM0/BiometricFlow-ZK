# BiometricFlow-ZK API Documentation

## Overview

This document provides comprehensive API documentation for the BiometricFlow-ZK multi-place fingerprint attendance system.

## Architecture

The system consists of:

1. **Place Backends** - Individual FastAPI services for each location
2. **Unified Gateway** - Central aggregation service 
3. **Frontend Application** - Streamlit web interface

## API Endpoints

### Unified Gateway API (Port 9000)

#### Health Endpoints
- `GET /` - Gateway information and status
- `GET /health` - Health check for all places

#### Global Data Endpoints
- `GET /places` - List all configured places
- `GET /devices/all` - All devices from all places
- `GET /attendance/all` - All attendance data unified
- `GET /users/all` - All users from all places
- `GET /summary/all` - Summary statistics from all places

#### Place-Specific Endpoints
- `GET /place/{place_name}/devices` - Devices from specific place
- `GET /place/{place_name}/attendance` - Attendance from specific place
- `GET /place/{place_name}/users` - Users from specific place
- `GET /place/{place_name}/summary` - Summary for specific place

#### Device-Specific Endpoints
- `GET /device/{device_name}/info` - Device information
- `GET /device/{device_name}/attendance` - Attendance for specific device

### Place Backend API (Ports 8000+)

#### Device Management
- `GET /devices` - List devices for this place
- `GET /device/{device_name}/info` - Device information
- `GET /device/{device_name}/users` - Users on device
- `GET /device/{device_name}/attendance` - Device attendance records

#### User Management
- `GET /users` - List all users
- `POST /users` - Create new user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

#### Attendance
- `GET /attendance` - Get attendance records
- `GET /attendance/today` - Today's attendance
- `GET /attendance/range` - Attendance in date range

## Response Formats

All API endpoints return JSON responses in the following format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-08-01T14:30:00Z"
}
```

## Error Handling

Errors are returned in the same format with `success: false`:

```json
{
  "success": false,
  "error": "Error description",
  "message": "User-friendly error message",
  "timestamp": "2025-08-01T14:30:00Z"
}
```

## Authentication

Currently, the system uses basic authentication for device access. Future versions will include:

- JWT token authentication
- Role-based access control
- API key management

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- Global endpoints: 100 requests/minute
- Device endpoints: 200 requests/minute
- Health endpoints: Unlimited

## SDK Examples

### Python

```python
import aiohttp
import asyncio

async def get_all_attendance():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:9000/attendance/all') as response:
            data = await response.json()
            return data['data']

# Usage
attendance_data = asyncio.run(get_all_attendance())
```

### JavaScript

```javascript
async function getAllAttendance() {
    const response = await fetch('http://localhost:9000/attendance/all');
    const data = await response.json();
    return data.data;
}

// Usage
getAllAttendance().then(data => console.log(data));
```

## Testing

Use the provided test scripts to verify API functionality:

```bash
python tests/test_api_endpoints.py
python tests/test_unified_system.py
```
