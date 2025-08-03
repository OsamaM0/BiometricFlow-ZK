"""
Unified Backend Gateway - Aggregates data from all device backends
Acts as a single API gateway that combines all backend endpoints
Enhanced with comprehensive security features and multi-place support
"""
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import aiohttp
import json
import os
import uvicorn
from pathlib import Path
import logging
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the core module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from security import (
    validate_api_key, security_middleware, get_cors_origins, 
    log_security_event, create_secure_response, create_error_response,
    generate_secure_session, create_jwt_token, verify_jwt_token
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🔒 Secure Unified Fingerprint Attendance Backend Gateway",
    description="Enhanced secure unified API gateway that aggregates data from all place backends with powerful security",
    version="3.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
    openapi_url="/openapi.json" if os.getenv("ENVIRONMENT") != "production" else None
)

# Add security middleware
app.middleware("http")(security_middleware)

# Secure CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Configuration
class UnifiedConfig:
    def __init__(self):
        # Load backend configurations
        self.backends = self._load_backend_configs()
        self.gateway_port = int(os.getenv("GATEWAY_PORT", "9000"))
        self.frontend_backend_port = int(os.getenv("FRONTEND_BACKEND_PORT", "9001"))
        
    def _load_backend_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load backend configurations from environment or config file"""
        # Try to load from config file first
        config_file = Path("backend/unified_backends_config.json")
        if not config_file.exists():
            config_file = Path("unified_backends_config.json")  # Try current directory
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    logger.info(f"Loaded {len(config_data)} places from config file: {config_file}")
                    return config_data
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        
        # Fallback to environment variables
        backends = {}
        
        # Load from environment variables
        for i in range(10):  # Support up to 10 backends
            if i == 0:
                name = os.getenv("BACKEND_NAME", "Place_1_BackOffice")
                url = os.getenv("BACKEND_URL", "http://localhost:8000")
                location = os.getenv("BACKEND_LOCATION", "Default Location")
            else:
                name = os.getenv(f"BACKEND_{i}_NAME")
                url = os.getenv(f"BACKEND_{i}_URL")
                location = os.getenv(f"BACKEND_{i}_LOCATION", f"Location {i}")
            
            if name and url:
                backends[name] = {
                    "name": name,
                    "url": url,
                    "location": location,
                    "timeout": 30,
                    "devices": [],
                    "description": f"Backend at {location}"
                }
        
        logger.info(f"Loaded {len(backends)} places from environment variables")
        return backends

config = UnifiedConfig()

# Response Models
class UnifiedDeviceInfo(BaseModel):
    device_name: str
    device_ip: str
    device_port: int
    backend_name: str
    backend_url: str
    place_location: str
    is_connected: bool
    last_sync: Optional[str]

class UnifiedAttendanceRecord(BaseModel):
    user_name: str
    date: str
    day_name: str
    check_in: str
    check_out: str
    working_time: str
    working_hours: float
    working_hours_progress: Optional[float] = 0.0
    status: str
    device_name: str
    backend_name: str
    place_location: str
    expected_hours: Optional[float] = 8.0

class UnifiedResponse(BaseModel):
    success: bool
    data: List[Any]
    total_records: int
    backend_sources: List[str]
    places: List[str]
    message: str

class PlaceSummary(BaseModel):
    place_name: str
    location: str
    backend_url: str
    devices: List[str]
    total_users: int
    total_attendance_records: int
    is_healthy: bool

# Helper Functions
async def call_backend(session: aiohttp.ClientSession, backend_name: str, endpoint: str, params: Dict = None) -> Dict:
    """Enhanced secure backend communication with improved authentication"""
    if backend_name not in config.backends:
        log_security_event("BACKEND_NOT_FOUND", f"Backend '{backend_name}' not found", "gateway")
        raise HTTPException(status_code=404, detail=f"Backend '{backend_name}' not found")
    
    backend_config = config.backends[backend_name]
    url = f"{backend_config['url']}{endpoint}"
    
    # Enhanced authentication headers
    headers = {
        "User-Agent": "BiometricFlow-Gateway/3.0",
        "X-Gateway-Request": "true",
        "Content-Type": "application/json"
    }
    
    # Multiple authentication methods
    backend_api_key = os.getenv("BACKEND_API_KEY")
    main_api_key = os.getenv("MAIN_API_KEY")
    
    if backend_api_key:
        headers["Authorization"] = f"Bearer {backend_api_key}"
    elif main_api_key:
        headers["Authorization"] = f"Bearer {main_api_key}"
    else:
        logger.warning("No API key configured for backend communication")
    
    # Add JWT token for enhanced security if available
    try:
        jwt_payload = {"gateway": True, "backend": backend_name}
        jwt_token = create_jwt_token(jwt_payload)
        headers["X-Gateway-Token"] = jwt_token
    except Exception as e:
        logger.debug(f"JWT token creation failed: {e}")
    
    try:
        timeout = aiohttp.ClientTimeout(total=backend_config.get('timeout', 15))  # Reduced timeout for NGROK
        async with session.get(url, params=params, headers=headers, timeout=timeout, ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                # Add backend metadata to response
                if isinstance(data, dict):
                    data['_backend_name'] = backend_name
                    data['_backend_url'] = backend_config['url']
                    data['_place_location'] = backend_config.get('location', 'Unknown')
                    data['_response_time'] = response.headers.get('X-Process-Time', 'unknown')
                return data
            elif response.status == 401:
                log_security_event("BACKEND_AUTH_FAILED", f"Authentication failed for backend {backend_name}", "gateway")
                return {
                    "success": False,
                    "error": f"Authentication failed for backend {backend_name}",
                    "error_code": "AUTH_FAILED",
                    "_backend_name": backend_name,
                    "_backend_url": backend_config['url'],
                    "_place_location": backend_config.get('location', 'Unknown')
                }
            elif response.status == 403:
                log_security_event("BACKEND_ACCESS_DENIED", f"Access denied for backend {backend_name}", "gateway")
                return {
                    "success": False,
                    "error": f"Access denied for backend {backend_name}",
                    "error_code": "ACCESS_DENIED",
                    "_backend_name": backend_name,
                    "_backend_url": backend_config['url'],
                    "_place_location": backend_config.get('location', 'Unknown')
                }
            elif response.status >= 500:
                log_security_event("BACKEND_SERVER_ERROR", f"Backend {backend_name} server error: {response.status}", "gateway")
                return {
                    "success": False,
                    "error": f"Backend {backend_name} server error",
                    "error_code": "SERVER_ERROR",
                    "_backend_name": backend_name,
                    "_backend_url": backend_config['url'],
                    "_place_location": backend_config.get('location', 'Unknown')
                }
            else:
                return {
                    "success": False,
                    "error": f"Backend {backend_name} returned status {response.status}",
                    "error_code": "HTTP_ERROR",
                    "_backend_name": backend_name,
                    "_backend_url": backend_config['url'],
                    "_place_location": backend_config.get('location', 'Unknown')
                }
    except asyncio.TimeoutError:
        log_security_event("BACKEND_TIMEOUT", f"Timeout calling backend {backend_name}", "gateway")
        return {
            "success": False,
            "error": f"Backend {backend_name} timeout",
            "error_code": "TIMEOUT",
            "_backend_name": backend_name,
            "_backend_url": backend_config['url'],
            "_place_location": backend_config.get('location', 'Unknown')
        }
    except Exception as e:
        log_security_event("BACKEND_ERROR", f"Error calling backend {backend_name}: {str(e)}", "gateway")
        return {
            "success": False,
            "error": f"Backend communication error: {str(e)}",
            "error_code": "CONNECTION_ERROR",
            "_backend_name": backend_name,
            "_backend_url": backend_config['url'],
            "_place_location": backend_config.get('location', 'Unknown')
        }

async def call_all_backends(endpoint: str, params: Dict = None) -> List[Dict]:
    """Call an endpoint on all backends simultaneously"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for backend_name in config.backends:
            task = call_backend(session, backend_name, endpoint, params)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and failed calls
        valid_results = []
        for result in results:
            if isinstance(result, dict) and not isinstance(result, Exception):
                valid_results.append(result)
        
        return valid_results

async def call_specific_place_backend(backend_name: str, endpoint: str, params: Dict = None) -> Dict:
    """Call a specific place backend"""
    async with aiohttp.ClientSession() as session:
        return await call_backend(session, backend_name, endpoint, params)

# Unified API Endpoints

@app.get("/", response_model=dict)
async def root(request: Request, _: bool = Depends(validate_api_key)):
    """Root endpoint with unified gateway information"""
    client_ip = request.client.host if request.client else "unknown"
    log_security_event("API_ACCESS", "Root endpoint accessed", client_ip)
    
    places_info = []
    for backend_name, backend_config in config.backends.items():
        places_info.append({
            "name": backend_name,
            "location": backend_config.get('location', 'Unknown'),
            "url": backend_config['url'],
            "devices": backend_config.get('devices', [])
        })
    
    return create_secure_response({
        "service": "🔒 Secure Unified Fingerprint Attendance Gateway",
        "version": "3.0.0",
        "total_places": len(config.backends),
        "places": places_info,
        "gateway_port": config.gateway_port,
        "frontend_backend_port": config.frontend_backend_port,
        "status": "running",
        "security_enabled": True,
        "endpoints": {
            "unified_all": [
                "/devices/all",
                "/attendance/all",
                "/users/all",
                "/summary/all",
                "/health/all"
            ],
            "place_specific": [
                "/place/{place_name}/devices",
                "/place/{place_name}/attendance",
                "/place/{place_name}/users",
                "/place/{place_name}/summary"
            ],
            "device_specific": [
                "/device/{device_name}/attendance",
                "/device/{device_name}/info"
            ]
        }
    })

@app.get("/health", response_model=dict)
async def health_check():
    """Health check for the unified gateway"""
    backend_health = {}
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for backend_name in config.backends:
            task = call_backend(session, backend_name, "/health")
            tasks.append((backend_name, task))
        
        for backend_name, task in tasks:
            try:
                result = await task
                backend_health[backend_name] = {
                    "status": "healthy" if result.get("status", False) == "healthy" else "unhealthy",
                    "location": config.backends[backend_name].get('location', 'Unknown'),
                    "url": config.backends[backend_name]['url'],
                    "response": result
                }
            except Exception as e:
                backend_health[backend_name] = {
                    "status": "unhealthy",
                    "location": config.backends[backend_name].get('location', 'Unknown'),
                    "url": config.backends[backend_name]['url'],
                    "error": str(e)
                }
    
    healthy_backends = sum(1 for h in backend_health.values() if h["status"] == "healthy")
    
    return {
        "service": "Unified Gateway",
        "status": "healthy" if healthy_backends > 0 else "unhealthy",
        "total_places": len(config.backends),
        "healthy_places": healthy_backends,
        "place_health": backend_health
    }

@app.get("/holidays", response_model=dict)
async def get_holidays():
    """Get all holidays information"""
    holidays = []
    for backend_name, backend_config in config.backends.items():
        holidays.extend(backend_config.get('holidays', []))
    return {
        "success": True,
        "holidays": holidays,
        "total_holidays": len(holidays),
        "message": f"Retrieved {len(holidays)} holidays"
    }

@app.get("/holidays/{year}", response_model=dict)
async def get_holidays_by_year(year: int):
    """Get holidays for a specific year"""
    holidays = []
    for backend_name, backend_config in config.backends.items():
        holidays.extend(backend_config.get('holidays', []))
    
    # Filter holidays by year if they have date information
    filtered_holidays = []
    for holiday in holidays:
        if isinstance(holiday, dict) and 'date' in holiday:
            try:
                holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d')
                if holiday_date.year == year:
                    filtered_holidays.append(holiday)
            except:
                # If date parsing fails, include the holiday anyway
                filtered_holidays.append(holiday)
        else:
            # If no date info, include all holidays
            filtered_holidays.append(holiday)
    
    return {
        "success": True,
        "holidays": filtered_holidays,
        "total_holidays": len(filtered_holidays),
        "year": year,
        "message": f"Retrieved {len(filtered_holidays)} holidays for year {year}"
    }

@app.get("/places", response_model=dict)
async def get_places():
    """Get all places information"""
    places = []
    for backend_name, backend_config in config.backends.items():
        places.append({
            "name": backend_name,
            "location": backend_config.get('location', 'Unknown'),
            "url": backend_config['url'],
            "devices": backend_config.get('devices', []),
            "description": backend_config.get('description', '')
        })
    
    return {
        "success": True,
        "places": places,
        "total_places": len(places),
        "message": f"Retrieved {len(places)} places"
    }

@app.get("/devices/all", response_model=dict)
async def get_all_devices_unified():
    """Get all devices from all places unified"""
    results = await call_all_backends("/devices")
    
    all_devices = []
    backend_sources = []
    places = []
    
    for result in results:
        if result.get("success") and "devices" in result:
            backend_name = result.get("_backend_name", "Unknown")
            place_location = result.get("_place_location", "Unknown")
            backend_sources.append(backend_name)
            if place_location not in places:
                places.append(place_location)
            
            for device in result["devices"]:
                # Enhance device info with place information
                device["backend_name"] = backend_name
                device["place_location"] = place_location
                all_devices.append(device)
    
    return {
        "success": True,
        "devices": all_devices,
        "total_devices": len(all_devices),
        "backend_sources": backend_sources,
        "places": places,
        "message": f"Retrieved {len(all_devices)} devices from {len(backend_sources)} places"
    }

@app.get("/attendance/all", response_model=dict)
async def get_all_attendance_unified(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    user_name: Optional[str] = Query(None, description="Filter by specific user name"),
    additional_holidays: Optional[str] = Query(None, description="Comma-separated list of additional holidays")
):
    """Get attendance data from all places unified"""
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    if user_name:
        params["user_name"] = user_name
    if additional_holidays:
        params["additional_holidays"] = additional_holidays
    
    results = await call_all_backends("/attendance/all", params)
    
    all_records = []
    backend_sources = []
    places = []
    
    for result in results:
        if result.get("success") and "data" in result:
            backend_name = result.get("_backend_name", "Unknown")
            place_location = result.get("_place_location", "Unknown")
            backend_sources.append(backend_name)
            if place_location not in places:
                places.append(place_location)
            
            for record in result["data"]:
                # Enhance record with place information
                record["backend_name"] = backend_name
                record["place_location"] = place_location
                all_records.append(record)
    
    return {
        "success": True,
        "data": all_records,
        "total_records": len(all_records),
        "backend_sources": backend_sources,
        "places": places,
        "message": f"Retrieved {len(all_records)} records from {len(backend_sources)} places"
    }

@app.get("/users/all", response_model=dict)
async def get_all_users_unified():
    """Get all users from all places unified"""
    results = await call_all_backends("/users/all")
    
    all_users = []
    backend_sources = []
    places = []
    user_set = set()  # To avoid duplicates
    
    for result in results:
        if result.get("success") and "users" in result:
            backend_name = result.get("_backend_name", "Unknown")
            place_location = result.get("_place_location", "Unknown")
            backend_sources.append(backend_name)
            if place_location not in places:
                places.append(place_location)
            
            for user in result["users"]:
                # Create unique user identifier
                user_key = f"{user.get('name', '')}-{user.get('userid', '')}"
                if user_key not in user_set:
                    user_set.add(user_key)
                    # Enhance user info with place information
                    user["backend_name"] = backend_name
                    user["place_location"] = place_location
                    all_users.append(user)
    
    return {
        "success": True,
        "users": all_users,
        "total_users": len(all_users),
        "backend_sources": backend_sources,
        "places": places,
        "message": f"Retrieved {len(all_users)} unique users from {len(backend_sources)} places"
    }

@app.get("/summary/all", response_model=dict)
async def get_all_summary_unified(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    additional_holidays: Optional[str] = Query(None, description="Comma-separated list of additional holidays")
):
    """Get attendance summary from all places unified"""
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    if additional_holidays:
        params["additional_holidays"] = additional_holidays
    
    results = await call_all_backends("/attendance/summary/all", params)
    
    all_summaries = []
    backend_sources = []
    places = []
    
    for result in results:
        if result.get("success"):
            backend_name = result.get("_backend_name", "Unknown")
            place_location = result.get("_place_location", "Unknown")
            backend_sources.append(backend_name)
            if place_location not in places:
                places.append(place_location)
            
            # Add place information to summary
            summary = result.copy()
            summary["backend_name"] = backend_name
            summary["place_location"] = place_location
            all_summaries.append(summary)
    
    return {
        "success": True,
        "summaries": all_summaries,
        "total_places": len(all_summaries),
        "backend_sources": backend_sources,
        "places": places,
        "message": f"Retrieved summaries from {len(backend_sources)} places"
    }

# Place-specific endpoints
@app.get("/place/{place_name}/devices", response_model=dict)
async def get_place_devices(place_name: str):
    """Get devices from a specific place"""
    result = await call_specific_place_backend(place_name, "/devices")
    
    if result.get("success"):
        # Enhance devices with place information
        for device in result.get("devices", []):
            device["backend_name"] = place_name
            device["place_location"] = config.backends[place_name].get('location', 'Unknown')
    
    return result

@app.get("/place/{place_name}/attendance", response_model=dict)
async def get_place_attendance(
    place_name: str,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    device_name: Optional[str] = Query(None, description="Filter by device name"),
    user_name: Optional[str] = Query(None, description="Filter by user name"),
    additional_holidays: Optional[str] = Query(None, description="Comma-separated list of additional holidays")
):
    """Get attendance data from a specific place"""
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    if device_name:
        params["device_name"] = device_name
    if user_name:
        params["user_name"] = user_name
    if additional_holidays:
        params["additional_holidays"] = additional_holidays
    
    result = await call_specific_place_backend(place_name, "/attendance/all", params)
    
    if result.get("success") and "data" in result:
        # Enhance records with place information
        place_location = config.backends[place_name].get('location', 'Unknown')
        for record in result["data"]:
            record["backend_name"] = place_name
            record["place_location"] = place_location
    
    return result

@app.get("/place/{place_name}/users", response_model=dict)
async def get_place_users(place_name: str):
    """Get users from a specific place"""
    result = await call_specific_place_backend(place_name, "/users/all")
    
    if result.get("success") and "users" in result:
        # Enhance users with place information
        place_location = config.backends[place_name].get('location', 'Unknown')
        for user in result["users"]:
            user["backend_name"] = place_name
            user["place_location"] = place_location
    
    return result

@app.get("/place/{place_name}/summary", response_model=dict)
async def get_place_summary(
    place_name: str,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    additional_holidays: Optional[str] = Query(None, description="Comma-separated list of additional holidays")
):
    """Get attendance summary from a specific place"""
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    if additional_holidays:
        params["additional_holidays"] = additional_holidays
    
    result = await call_specific_place_backend(place_name, "/attendance/summary/all", params)
    
    if result.get("success"):
        # Add place information to summary
        result["backend_name"] = place_name
        result["place_location"] = config.backends[place_name].get('location', 'Unknown')
    
    return result

# Device-specific endpoints (across all places)
@app.get("/device/{device_name}/info", response_model=dict)
async def get_device_info(device_name: str):
    """Get device information from any place"""
    results = await call_all_backends(f"/device/info?device_name={device_name}")
    
    for result in results:
        if result.get("success") and result.get("device_name") == device_name:
            # Enhance with place information
            result["backend_name"] = result.get("_backend_name", "Unknown")
            result["place_location"] = result.get("_place_location", "Unknown")
            return result
    
    raise HTTPException(status_code=404, detail=f"Device '{device_name}' not found in any place")

@app.get("/device/{device_name}/attendance", response_model=dict)
async def get_device_attendance(
    device_name: str,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    user_name: Optional[str] = Query(None, description="Filter by user name"),
    additional_holidays: Optional[str] = Query(None, description="Comma-separated list of additional holidays")
):
    """Get attendance data from a specific device across all places"""
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "device_name": device_name
    }
    if user_name:
        params["user_name"] = user_name
    if additional_holidays:
        params["additional_holidays"] = additional_holidays
    
    results = await call_all_backends("/attendance", params)
    
    for result in results:
        if result.get("success") and "data" in result:
            # Check if this result has data for our device
            device_data = [record for record in result["data"] if record.get("device_name") == device_name]
            if device_data:
                # Enhance with place information
                place_location = result.get("_place_location", "Unknown")
                backend_name = result.get("_backend_name", "Unknown")
                for record in device_data:
                    record["backend_name"] = backend_name
                    record["place_location"] = place_location
                
                return {
                    "success": True,
                    "data": device_data,
                    "total_records": len(device_data),
                    "device_name": device_name,
                    "backend_name": backend_name,
                    "place_location": place_location,
                    "message": f"Retrieved {len(device_data)} records for device {device_name}"
                }
    
    raise HTTPException(status_code=404, detail=f"No attendance data found for device '{device_name}'")

# Backend management endpoints
@app.get("/backends/list", response_model=dict)
async def list_backends():
    """List all available backends/places"""
    backends_info = []
    for backend_name, backend_config in config.backends.items():
        backends_info.append({
            "name": backend_name,
            "location": backend_config.get('location', 'Unknown'),
            "url": backend_config['url'],
            "devices": backend_config.get('devices', []),
            "description": backend_config.get('description', ''),
            "timeout": backend_config.get('timeout', 30)
        })
    
    return {
        "success": True,
        "backends": backends_info,
        "total_backends": len(backends_info),
        "message": f"Retrieved {len(backends_info)} backend configurations"
    }

if __name__ == "__main__":
    print(f"Starting Unified Fingerprint Attendance Gateway")
    print(f"Gateway Port: {config.gateway_port}")
    print(f"Frontend Backend Port: {config.frontend_backend_port}")
    print(f"Total Place Sources: {len(config.backends)}")
    print(f"Place Sources: {list(config.backends.keys())}")
    
    # Display place information
    print("\nPlace Configuration:")
    for place_name, place_config in config.backends.items():
        print(f"  - {place_name}: {place_config.get('location', 'Unknown')} ({place_config['url']})")
        devices = place_config.get('devices', [])
        if devices:
            print(f"    Devices: {', '.join(devices)}")
    
    uvicorn.run(app, host="0.0.0.0", port=config.gateway_port)
