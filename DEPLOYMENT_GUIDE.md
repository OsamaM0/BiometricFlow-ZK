# 🚀 BiometricFlow-ZK Enhanced Token-Based Architecture

## Overview

Your BiometricFlow-ZK system now implements a proper **3-tier token-based authentication architecture** where each service is completely independent and can be deployed on different servers.

## 🏗️ Architecture Overview

```
┌─────────────────┐    Token Request    ┌──────────────────┐    Token Request    ┌─────────────────┐
│   Frontend      │◄──────────────────►│ Unified Gateway  │◄──────────────────►│ Place Backend   │
│   (Port 8501)   │     JWT Auth        │   (Port 9000)    │     API Key Auth    │   (Port 8000)   │
│                 │                     │                  │                     │                 │
│ - Streamlit App │                     │ - API Gateway    │                     │ - Device Access │
│ - User Interface│                     │ - Token Manager  │                     │ - Local Data    │
│ - Data Display  │                     │ - Route Requests │                     │ - Token Generate│
└─────────────────┘                     └──────────────────┘                     └─────────────────┘
```

## 🔐 Authentication Flow

### 1. Place Backend → Unified Gateway
- **Place Backend** generates tokens for **Unified Gateway** to access its services
- Uses place-specific API keys for authentication
- Each place backend is independent and can run on separate servers

### 2. Unified Gateway → Frontend 
- **Unified Gateway** generates JWT tokens for **Frontend** access
- Frontend uses its unique API key to request tokens
- Tokens provide access to aggregated data from all places

### 3. Service Independence
- ✅ Each service loads its own environment file
- ✅ No service can see other service files
- ✅ Communication is purely via HTTP APIs with token authentication
- ✅ Each service can be deployed on different servers/networks

## 📁 Environment Files

### 🏢 Place Backend (`place_backend.env`)
```bash
# Place-specific configuration
PLACE_NAME=Main Office
PLACE_LOCATION=Building A, Floor 1
SERVICE_PORT=8000

# Unique API keys for this place
MAIN_API_KEY=s-ZBBiizyZdy3y1MxxQbvAksAfGMG4anerLDiniwUSY
JWT_SECRET=di3jZzfeSdt0RFOF71SJAeC4_XbGObePWwfo3YBlPEQ
UNIFIED_GATEWAY_API_KEY=nZTueOgEr7vRH8MYtm3MwiEDh1c5tqw1Zw5EALHN4YU
```

### 🌐 Unified Gateway (`unified_gateway.env`)
```bash
# Gateway configuration
SERVICE_PORT=9000

# Unique API keys for gateway
MAIN_API_KEY=nZTueOgEr7vRH8MYtm3MwiEDh1c5tqw1Zw5EALHN4YU
JWT_SECRET=JKbf5DScqPQxlFwz1gTY_hILVNkfOOghFHRd4S1jBN0
PLACE_BACKEND_API_KEY=s-ZBBiizyZdy3y1MxxQbvAksAfGMG4anerLDiniwUSY
FRONTEND_API_KEY=-1NbQM0lLSU7yaEJTHydOv-8QRxxEhZCQXvD7Q70LZg
```

### 💻 Frontend (`frontend.env`)
```bash
# Frontend configuration
SERVICE_PORT=8501
BACKEND_URL=http://localhost:9000

# Unique API keys for frontend
FRONTEND_API_KEY=-1NbQM0lLSU7yaEJTHydOv-8QRxxEhZCQXvD7Q70LZg
JWT_SECRET=MHjI3dHQQGW3N7hE5Zd0YslbKUaZ_HcpDfjU8eK22Xc
UNIFIED_GATEWAY_API_KEY=nZTueOgEr7vRH8MYtm3MwiEDh1c5tqw1Zw5EALHN4YU
```

## 🚀 Startup Workflow

### 1. Generate Security Keys
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Generate all API keys and environment files
python generate_keys.py
```

### 2. Start Services in Order

#### Option A: Start Individual Services
```bash
# Terminal 1: Start Place Backend
python start_place_backend.py

# Terminal 2: Start Unified Gateway  
python start_unified_gateway.py

# Terminal 3: Start Frontend
python start_frontend.py
```

#### Option B: Start All Services with Orchestrator
```bash
# Start all services automatically
python start_all_services.py
```

### 3. Verify Authentication
```bash
# Test the complete authentication flow
python test_auth_flow.py
```

## 🔗 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Place Backend | http://localhost:8000 | Device data and local operations |
| Unified Gateway | http://localhost:9000 | API aggregation and routing |
| Frontend | http://localhost:8501 | User interface and data visualization |

## 🔐 Token Authentication Endpoints

### Place Backend Endpoints
- `POST /auth/token` - Generate token for unified gateway
- `GET /health` - Health check (requires authentication)
- `GET /devices` - Get device information
- `GET /attendance` - Get attendance data

### Unified Gateway Endpoints  
- `POST /auth/frontend/token` - Generate token for frontend
- `POST /auth/place/token` - Get token from place backend
- `GET /devices/all` - Get all devices from all places
- `GET /attendance/all` - Get all attendance data

### Frontend Authentication
- Frontend automatically requests token from Unified Gateway on startup
- Tokens are refreshed automatically before expiration
- All API calls use JWT tokens for authentication

## 🎯 Key Features Implemented

### ✅ Complete Service Isolation
- Each service has its own environment file
- No cross-service file dependencies
- Services communicate only via HTTP APIs

### ✅ Secure Token-Based Authentication
- JWT tokens for frontend communication
- API key authentication between services
- Automatic token refresh and validation

### ✅ Multi-Server Deployment Ready
- Each service can run on different servers
- Environment variables specify connection URLs
- No shared file system requirements

### ✅ Robust Error Handling
- Authentication failures are properly handled
- Service health monitoring
- Automatic retry mechanisms

## 🔧 Configuration for Different Servers

### For Separate Server Deployment:

#### Server 1 (Place Backend):
```bash
# Update place_backend.env
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000
UNIFIED_GATEWAY_URL=http://gateway-server:9000
```

#### Server 2 (Unified Gateway):
```bash
# Update unified_gateway.env  
SERVICE_HOST=0.0.0.0
SERVICE_PORT=9000

# Update backend_places_config.json
{
  "places": {
    "place_001": {
      "url": "http://place-server:8000",
      "api_key": "place_backend_api_key"
    }
  }
}
```

#### Server 3 (Frontend):
```bash
# Update frontend.env
BACKEND_URL=http://gateway-server:9000
```

## 🎉 Success Verification

When everything is working correctly, you should see:

1. **Place Backend**: Device data accessible via API
2. **Unified Gateway**: Aggregating data from all places
3. **Frontend**: Displaying unified dashboard with authentication
4. **Authentication Flow**: All services communicating with proper tokens

The system is now fully token-based, secure, and ready for multi-server deployment! 🚀
