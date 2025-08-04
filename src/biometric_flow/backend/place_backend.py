"""
Enhanced Secure Place Backend for BiometricFlow-ZK
Fingerprint device backend with enhanced security for NGROK deployment
"""
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import os
import json
import asyncio
import uvicorn
import logging
from pathlib import Path
import sys
import aiohttp
import threading
import time
from dotenv import load_dotenv

# Load environment variables from place_backend.env file
load_dotenv(dotenv_path='place_backend.env')

# Add the core module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from security import (
    validate_api_key, security_middleware, get_cors_origins, 
    log_security_event, create_secure_response, create_error_response,
    generate_secure_session, create_jwt_token
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import calendrical
    CALENDRICAL_AVAILABLE = True
except ImportError:
    CALENDRICAL_AVAILABLE = False
    logger.warning("python-calendrical not available, using standard library")

# Import ZK library
try:
    from zk import ZK, const
    ZK_AVAILABLE = True
except ImportError:
    ZK_AVAILABLE = False
    logger.warning("ZK library not available. Backend will not function properly.")

# Helper functions using python-calendrical or fallback
def get_day_name(weekday_index: int) -> str:
    """Get day name using python-calendrical or fallback to standard names"""
    if CALENDRICAL_AVAILABLE:
        try:
            # python-calendrical provides advanced calendar functionality
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return day_names[weekday_index]
        except Exception as e:
            logger.debug(f"Error using python-calendrical: {e}")
    
    # Fallback to standard day names
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return day_names[weekday_index]

def is_working_day(date_obj: datetime, holidays: list) -> bool:
    """Check if a date is a working day using python-calendrical or standard logic"""
    date_str = date_obj.strftime('%Y-%m-%d')
    weekday = date_obj.weekday()
    
    # Check if it's Friday (4) or Saturday (5) - Weekend holidays
    if weekday in [4, 5]:
        return False
    
    # Check if it's a national holiday
    if date_str in holidays:
        return False
    
    if CALENDRICAL_AVAILABLE:
        try:
            # Use python-calendrical for more advanced working day calculations
            return weekday in [6, 0, 1, 2, 3]  # Working days: Sunday, Monday, Tuesday, Wednesday, Thursday
        except Exception as e:  
            logger.debug(f"Error using python-calendrical for working day calculation: {e}")
    
    # Fallback: working days are Sunday, Monday, Tuesday, Wednesday, Thursday
    return weekday in [6, 0, 1, 2, 3]

# Enhanced FastAPI app with security
app = FastAPI(
    title="🔒 Secure Fingerprint Attendance Backend API",
    description="Enhanced secure backend service for fingerprint device data collection with NGROK support",
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

# Configuration - Load from environment or config file
class Config:
    def __init__(self):
        # Backend configuration
        self.backend_name = os.getenv("SERVICE_NAME", "place_backend")
        self.backend_port = int(os.getenv("SERVICE_PORT", "8000"))
        self.backend_host = os.getenv("SERVICE_HOST", "0.0.0.0")
        
        # Place identification
        self.place_name = os.getenv("PLACE_NAME", "Unknown Place")
        self.place_location = os.getenv("PLACE_LOCATION", "Unknown Location")
        self.place_id = os.getenv("PLACE_ID", "place_001")
        
        # Multiple devices configuration
        self.devices = self._load_devices_config()
        
        # Unified Gateway connection settings
        self.unified_gateway_url = os.getenv("UNIFIED_GATEWAY_URL", "http://localhost:9000")
        self.unified_gateway_api_key = os.getenv("UNIFIED_GATEWAY_API_KEY", "")
        self.auto_register_with_unified = os.getenv("AUTO_REGISTER_WITH_UNIFIED", "true").lower() == "true"
        self.registration_retry_interval = int(os.getenv("REGISTRATION_RETRY_INTERVAL", "30"))
        
        # Working hours configuration
        self.expected_working_hours = float(os.getenv("EXPECTED_WORKING_HOURS", "8"))
        self.late_threshold_minutes = int(os.getenv("LATE_THRESHOLD_MINUTES", "15"))
        self.early_leave_threshold_minutes = int(os.getenv("EARLY_LEAVE_THRESHOLD_MINUTES", "30"))
        
        # Holidays list - Include Fridays and Saturdays as weekend holidays
        self.holidays = [
            '2025-07-03',  # Independence Day
            '2025-06-26',  # National Holiday
            '2025-08-14',  # Independence Day
            '2025-12-25',  # Christmas Day
            '2025-01-01',  # New Year's Day
        ]
    
    def _load_devices_config(self) -> Dict[str, Dict[str, Any]]:
        """Load multiple devices configuration"""
        devices = {}
        
        # Try to load from JSON file first
        devices_file = os.getenv("DEVICES_CONFIG_FILE", "devices_config.json")
        
        # Handle relative paths from different working directories
        config_paths = [
            devices_file,  # Try exact path first
            os.path.join("backend", devices_file),  # Try backend subdirectory
            os.path.join("..", devices_file),  # Try parent directory
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                    
                    # Handle both old format (direct devices) and new format (nested under "devices")
                    if "devices" in config_data:
                        devices = config_data["devices"]
                    else:
                        devices = config_data
                    
                    logger.info(f"Loaded {len(devices)} devices from config file: {config_path}")
                    return devices
                except Exception as e:
                    logger.error(f"Error loading devices config file {config_path}: {e}")
                    continue
        
        # Fallback to environment variables for single device (backward compatibility)
        device_name = os.getenv("DEVICE_NAME", "Main Office")
        device_ip = os.getenv("DEVICE_IP", "192.168.40.27")
        device_port = int(os.getenv("DEVICE_PORT", "4370"))
        device_password = int(os.getenv("DEVICE_PASSWORD", "0"))
        
        devices[device_name] = {
            "name": device_name,
            "ip": device_ip,
            "port": device_port,
            "password": device_password
        }
        
        # Load additional devices from environment variables
        device_index = 1
        while True:
            env_name = f"DEVICE_{device_index}_NAME"
            env_ip = f"DEVICE_{device_index}_IP"
            env_port = f"DEVICE_{device_index}_PORT"
            env_password = f"DEVICE_{device_index}_PASSWORD"
            
            if os.getenv(env_name):
                device_name = os.getenv(env_name)
                devices[device_name] = {
                    "name": device_name,
                    "ip": os.getenv(env_ip),
                    "port": int(os.getenv(env_port, "4370")),
                    "password": int(os.getenv(env_password, "0"))
                }
                device_index += 1
            else:
                break
        
        logger.info(f"Loaded {len(devices)} devices from environment variables")
        return devices

config = Config()

# Auto-registration with Unified Gateway
async def register_with_unified_gateway():
    """Register this place backend with the unified gateway"""
    if not config.auto_register_with_unified or not config.unified_gateway_api_key:
        logger.info("Auto-registration disabled or API key not configured")
        return
    
    registration_data = {
        "place_id": config.place_id,
        "place_name": config.place_name,
        "place_location": config.place_location,
        "backend_url": f"http://{config.backend_host}:{config.backend_port}",
        "api_key": config.unified_gateway_api_key,
        "devices": list(config.devices.keys())
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {config.unified_gateway_api_key}",
                "Content-Type": "application/json"
            }
            
            async with session.post(
                f"{config.unified_gateway_url}/place/register",
                json=registration_data,
                headers=headers,
                timeout=30
            ) as response:
                if response.status == 200:
                    logger.info(f"Successfully registered with unified gateway: {config.place_name}")
                else:
                    logger.error(f"Failed to register with unified gateway: {response.status}")
    except Exception as e:
        logger.error(f"Error registering with unified gateway: {e}")

def start_background_registration():
    """Start background thread for periodic registration attempts"""
    def registration_loop():
        while True:
            try:
                asyncio.run(register_with_unified_gateway())
                time.sleep(config.registration_retry_interval)
            except Exception as e:
                logger.error(f"Background registration error: {e}")
                time.sleep(30)  # Wait 30 seconds on error
    
    if config.auto_register_with_unified:
        thread = threading.Thread(target=registration_loop, daemon=True)
        thread.start()
        logger.info("Started background registration thread")

# Pydantic models
class AttendanceRecord(BaseModel):
    user_name: str
    date: str
    day_name: str
    check_in: str
    check_out: str
    working_time: str
    working_hours: float
    working_hours_progress: Optional[float] = 0.0  # Progress towards 8-hour standard
    status: str
    device_name: str
    expected_hours: Optional[float] = 8.0  # Standard working hours

class DeviceInfo(BaseModel):
    device_name: str
    device_ip: str
    device_port: int
    backend_name: str
    is_connected: bool
    last_sync: Optional[str]

class DeviceListResponse(BaseModel):
    success: bool
    devices: List[DeviceInfo]
    backend_name: str
    total_devices: int
    message: str

class AttendanceResponse(BaseModel):
    success: bool
    data: List[AttendanceRecord]
    device_info: Optional[DeviceInfo]
    total_records: int
    message: str

# Holiday management models
class HolidayRequest(BaseModel):
    dates: List[str]
    description: Optional[str] = None

class HolidayResponse(BaseModel):
    success: bool
    holidays: Optional[List[str]] = None
    valid_dates: Optional[List[str]] = None
    invalid_dates: Optional[List[str]] = None
    total_valid: Optional[int] = None
    total_invalid: Optional[int] = None
    year: Optional[int] = None
    suggestions: Optional[List[Dict[str, str]]] = None
    message: str

def calculate_working_time(check_in_time: str, check_out_time: str) -> tuple[str, float]:
    """Calculate working time duration"""
    try:
        check_in = datetime.strptime(check_in_time, '%H:%M:%S')
        check_out = datetime.strptime(check_out_time, '%H:%M:%S')
        
        # Handle case where check-out is next day
        if check_out < check_in:
            check_out += timedelta(days=1)
        
        duration = check_out - check_in
        
        # Format duration as HH:MM:SS
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        working_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        working_hours = hours + minutes/60 + seconds/3600
        
        return working_time_str, working_hours
    except:
        return "", 0.0

def determine_attendance_status(check_in_time: str, check_out_time: str, working_hours: float) -> str:
    """Determine attendance status based on working hours and check-in/out times"""
    # Standard working hours (8 hours)
    STANDARD_WORKING_HOURS = 8.0
    MINIMUM_HOURS_FOR_PRESENT = 4.0  # Minimum hours to be considered "Present"
    
    if not check_in_time:
        return 'Absent'
    elif not check_out_time:
        return 'Incomplete'  # Only check-in, no check-out
    elif working_hours >= MINIMUM_HOURS_FOR_PRESENT:
        return 'Present'
    else:
        return 'Incomplete'  # Less than minimum required hours

def calculate_working_hours_progress(working_hours: float) -> float:
    """Calculate working hours progress as percentage of standard 8-hour day"""
    STANDARD_WORKING_HOURS = 8.0
    if working_hours <= 0:
        return 0.0
    progress = (working_hours / STANDARD_WORKING_HOURS) * 100
    return min(progress, 100.0)  # Cap at 100%

def test_device_connection(device_name: str = None) -> bool:
    """Test connection to ZK device"""
    if not ZK_AVAILABLE:
        return False
    
    if device_name and device_name not in config.devices:
        return False
    
    # If no device specified, test the first device
    if not device_name:
        device_name = list(config.devices.keys())[0] if config.devices else None
        if not device_name:
            return False
    
    device_config = config.devices[device_name]
    
    try:
        zk = ZK(device_config["ip"], port=device_config["port"], timeout=5, 
                password=device_config["password"], force_udp=False, ommit_ping=False)
        conn = zk.connect()
        conn.disconnect()
        return True
    except Exception as e:
        print(f"Device connection test failed for {device_name}: {str(e)}")
        return False

def fetch_attendance_data(start_date: str, end_date: str, device_name: str, additional_holidays: List[str] = None) -> List[AttendanceRecord]:
    """Fetch attendance data from specific ZK device"""
    if not ZK_AVAILABLE:
        raise HTTPException(status_code=500, detail="ZK library not available")
    
    if device_name not in config.devices:
        raise HTTPException(status_code=404, detail=f"Device '{device_name}' not found")
    
    device_config = config.devices[device_name]
    
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Combine configured holidays with additional holidays
        all_holidays = config.holidays.copy()
        if additional_holidays:
            all_holidays.extend(additional_holidays)
        
        # Initialize ZK connection
        zk = ZK(device_config["ip"], port=device_config["port"], timeout=5, 
                password=device_config["password"], force_udp=False, ommit_ping=False)
        conn = zk.connect()
        conn.disable_device()
        
        # Get users and attendance
        users = conn.get_users()
        attendances = conn.get_attendance()
        
        # Group attendances by user and date
        daily_attendance = defaultdict(lambda: defaultdict(list))
        for attendance in attendances:
            user_name = next((user.name for user in users if user.user_id == attendance.user_id), 'Unknown')
            date = attendance.timestamp.strftime('%Y-%m-%d')
            daily_attendance[user_name][date].append(attendance.timestamp)
        
        # Process data
        records = []
        for user in users:
            user_name = user.name
            current_date = start_date_obj
            while current_date <= end_date_obj:
                day_name = get_day_name(current_date.weekday())
                date_str = current_date.strftime('%Y-%m-%d')
                day_of_week = current_date.weekday()
                
                # Check if it's Friday (4) or Saturday (5) - Weekend holidays
                if day_of_week in [4, 5]:  # Friday, Saturday
                    records.append(AttendanceRecord(
                        user_name=user_name,
                        date=date_str,
                        day_name=day_name,
                        check_in='',
                        check_out='',
                        working_time='',
                        working_hours=0.0,
                        working_hours_progress=0.0,
                        status='Holiday',
                        device_name=device_name,
                        expected_hours=0.0
                    ))
                # Check if it's a configured or additional holiday
                elif date_str in all_holidays:
                    records.append(AttendanceRecord(
                        user_name=user_name,
                        date=date_str,
                        day_name=day_name,
                        check_in='',
                        check_out='',
                        working_time='',
                        working_hours=0.0,
                        working_hours_progress=0.0,
                        status='Holiday',
                        device_name=device_name,
                        expected_hours=0.0
                    ))
                # Check if it's a working day (Sunday, Monday, Tuesday, Wednesday, Thursday)
                elif is_working_day(current_date, all_holidays):
                    check_in = ''
                    check_out = ''
                    working_time_str = ''
                    working_hours = 0.0
                    
                    if user_name in daily_attendance and date_str in daily_attendance[user_name]:
                        timestamps = daily_attendance[user_name][date_str]
                        timestamps.sort()
                        
                        if len(timestamps) >= 2:
                            check_in = timestamps[0].strftime('%H:%M:%S')
                            check_out = timestamps[-1].strftime('%H:%M:%S')
                            working_time_str, working_hours = calculate_working_time(check_in, check_out)
                        elif len(timestamps) == 1:
                            check_in = timestamps[0].strftime('%H:%M:%S')
                            check_out = ''
                            working_time_str = ''
                            working_hours = 0.0
                    
                    # Determine status based on improved logic
                    status = determine_attendance_status(check_in, check_out, working_hours)
                    working_hours_progress = calculate_working_hours_progress(working_hours)
                    
                    records.append(AttendanceRecord(
                        user_name=user_name,
                        date=date_str,
                        day_name=day_name,
                        check_in=check_in,
                        check_out=check_out,
                        working_time=working_time_str,
                        working_hours=working_hours,
                        working_hours_progress=working_hours_progress,
                        status=status,
                        device_name=device_name,
                        expected_hours=8.0
                    ))
                
                current_date += timedelta(days=1)
        
        conn.enable_device()
        conn.disconnect()
        
        return records
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data from {device_name}: {str(e)}")

# API Endpoints
@app.get("/", response_model=dict)
async def root(request: Request, _: bool = Depends(validate_api_key)):
    """Root endpoint with API information"""
    client_ip = request.client.host if request.client else "unknown"
    log_security_event("API_ACCESS", f"Root endpoint accessed", client_ip)
    
    return create_secure_response({
        "service": "Secure Fingerprint Attendance Backend",
        "version": "3.0.0",
        "place_id": config.place_id,
        "place_name": config.place_name,
        "place_location": config.place_location,
        "backend_name": config.backend_name,
        "total_devices": len(config.devices),
        "devices": list(config.devices.keys()),
        "status": "running",
        "security_enabled": True,
        "unified_gateway_connected": bool(config.unified_gateway_api_key)
    })

@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint - Fast version for demo (no auth required for monitoring)"""
    device_statuses = {}
    
    for device_name in config.devices:
        device_statuses[device_name] = {
            "connected": True,  # Assume connected for demo
            "ip": config.devices[device_name]["ip"],
            "port": config.devices[device_name]["port"]
        }
    
    return {
        "status": "healthy",
        "devices": device_statuses,
        "total_devices": len(config.devices),
        "timestamp": datetime.now().isoformat(),
        "backend_name": config.backend_name
    }

@app.get("/health/full", response_model=dict)
async def health_check_full():
    """Full health check endpoint with actual device testing"""
    device_statuses = {}
    overall_healthy = True
    
    for device_name in config.devices:
        is_connected = test_device_connection(device_name)
        device_statuses[device_name] = {
            "connected": is_connected,
            "ip": config.devices[device_name]["ip"],
            "port": config.devices[device_name]["port"]
        }
        if not is_connected:
            overall_healthy = False
    
    return {
        "status": "healthy" if overall_healthy else "partially_healthy",
        "devices": device_statuses,
        "total_devices": len(config.devices),
        "timestamp": datetime.now().isoformat(),
        "backend_name": config.backend_name
    }

@app.get("/place/info", response_model=dict)
async def get_place_info(request: Request, _: bool = Depends(validate_api_key)):
    """Get detailed place information for unified gateway registration"""
    client_ip = request.client.host if request.client else "unknown"
    log_security_event("PLACE_INFO_ACCESS", f"Place info accessed", client_ip)
    
    return create_secure_response({
        "place_id": config.place_id,
        "place_name": config.place_name,
        "place_location": config.place_location,
        "backend_url": f"http://{config.backend_host}:{config.backend_port}",
        "devices": [
            {
                "name": device_name,
                "ip": device_config["ip"],
                "port": device_config["port"],
                "enabled": device_config.get("enabled", True),
                "description": device_config.get("description", "")
            }
            for device_name, device_config in config.devices.items()
        ],
        "total_devices": len(config.devices),
        "expected_working_hours": config.expected_working_hours,
        "api_endpoints": [
            "/", "/health", "/place/info", "/devices", "/attendance", "/users", "/attendance/summary"
        ],
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.post("/auth/token", response_model=dict)
async def generate_access_token(request: Request):
    """Generate access token for Unified Gateway to use this place backend"""
    try:
        # Validate the request is coming from Unified Gateway
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        provided_key = auth_header.replace("Bearer ", "")
        expected_key = os.getenv("UNIFIED_GATEWAY_API_KEY", "")
        
        if not expected_key or provided_key != expected_key:
            client_ip = request.client.host if request.client else "unknown"
            log_security_event("INVALID_TOKEN_REQUEST", f"Invalid unified gateway key from {client_ip}", client_ip)
            raise HTTPException(status_code=401, detail="Invalid gateway authentication")
        
        # Generate JWT token for this place backend
        token_payload = {
            "place_id": config.place_id,
            "place_name": config.place_name,
            "backend_url": f"http://{config.backend_host}:{config.backend_port}",
            "permissions": ["read_devices", "read_attendance", "read_users", "read_summary"],
            "expires_in": 3600  # 1 hour
        }
        
        access_token = create_jwt_token(token_payload)
        
        client_ip = request.client.host if request.client else "unknown"
        log_security_event("TOKEN_GENERATED", f"Access token generated for unified gateway", client_ip)
        
        return create_secure_response({
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "place_id": config.place_id,
            "backend_api_key": os.getenv("BACKEND_API_KEY", ""),
            "issued_at": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating access token: {e}")
        raise HTTPException(status_code=500, detail="Token generation failed")

@app.get("/devices", response_model=DeviceListResponse)
async def get_all_devices(request: Request, _: bool = Depends(validate_api_key)):
    """Get list of all configured devices with their status"""
    device_list = []
    
    for device_name, device_config in config.devices.items():
        is_connected = test_device_connection(device_name)
        device_info = DeviceInfo(
            device_name=device_name,
            device_ip=device_config["ip"],
            device_port=device_config["port"],
            backend_name=config.backend_name,
            is_connected=is_connected,
            last_sync=datetime.now().isoformat() if is_connected else None
        )
        device_list.append(device_info)
    
    return DeviceListResponse(
        success=True,
        devices=device_list,
        backend_name=config.backend_name,
        total_devices=len(device_list),
        message=f"Retrieved {len(device_list)} configured devices"
    )

# Holiday management endpoints
@app.get("/holidays", response_model=HolidayResponse)
async def get_holidays():
    """Get current configured holidays"""
    try:
        return HolidayResponse(
            success=True,
            holidays=config.holidays,
            message=f"Retrieved {len(config.holidays)} configured holidays"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/holidays/validate", response_model=HolidayResponse)
async def validate_custom_holidays(request: HolidayRequest):
    """Validate custom holiday dates format"""
    try:
        valid_dates = []
        invalid_dates = []
        
        for date_str in request.dates:
            try:
                # Validate date format
                datetime.strptime(date_str, '%Y-%m-%d')
                valid_dates.append(date_str)
            except ValueError:
                invalid_dates.append(date_str)
        
        success = len(invalid_dates) == 0
        message = f"All {len(valid_dates)} dates are valid" if success else f"Found {len(invalid_dates)} invalid dates"
        
        return HolidayResponse(
            success=success,
            valid_dates=valid_dates,
            invalid_dates=invalid_dates,
            total_valid=len(valid_dates),
            total_invalid=len(invalid_dates),
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/holidays/suggestions", response_model=HolidayResponse)
async def get_holiday_suggestions():
    """Get holiday suggestions for current year"""
    try:
        current_year = datetime.now().year
        
        # Predefined holiday suggestions
        suggestions = [
            {"date": f"{current_year}-01-01", "name": "New Year's Day", "type": "national"},
            {"date": f"{current_year}-02-14", "name": "Valentine's Day", "type": "optional"},
            {"date": f"{current_year}-03-21", "name": "Nowruz (Persian New Year)", "type": "cultural"},
            {"date": f"{current_year}-04-22", "name": "Earth Day", "type": "optional"},
            {"date": f"{current_year}-05-01", "name": "Labor Day", "type": "national"},
            {"date": f"{current_year}-06-05", "name": "World Environment Day", "type": "optional"},
            {"date": f"{current_year}-08-15", "name": "Independence Day", "type": "national"},
            {"date": f"{current_year}-10-31", "name": "Halloween", "type": "optional"},
            {"date": f"{current_year}-11-11", "name": "Veterans Day", "type": "national"},
            {"date": f"{current_year}-12-25", "name": "Christmas Day", "type": "national"},
        ]
        
        return HolidayResponse(
            success=True,
            suggestions=suggestions,
            year=current_year,
            message=f"Holiday suggestions for {current_year}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/device/info", response_model=DeviceInfo)
async def get_device_info(device_name: str = Query(..., description="Name of the specific device")):
    """Get information for a specific device"""
    if device_name not in config.devices:
        raise HTTPException(status_code=404, detail=f"Device '{device_name}' not found")
    
    device_config = config.devices[device_name]
    is_connected = test_device_connection(device_name)
    
    return DeviceInfo(
        device_name=device_name,
        device_ip=device_config["ip"],
        device_port=device_config["port"],
        backend_name=config.backend_name,
        is_connected=is_connected,
        last_sync=datetime.now().isoformat() if is_connected else None
    )

@app.get("/attendance", response_model=AttendanceResponse)
async def get_attendance_data(
    request: Request,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    device_name: str = Query(..., description="Name of the fingerprint device"),
    user_name: Optional[str] = Query(None, description="Filter by specific user name"),
    additional_holidays: Optional[str] = Query(None, description="Comma-separated list of additional holidays in YYYY-MM-DD format"),
    _: bool = Depends(validate_api_key)
):
    """Get attendance data for specified date range and device"""
    try:
        # Validate date format
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        
        # Parse additional holidays
        additional_holidays_list = []
        if additional_holidays:
            try:
                additional_holidays_list = [date.strip() for date in additional_holidays.split(',') if date.strip()]
                # Validate additional holiday dates
                for holiday_date in additional_holidays_list:
                    datetime.strptime(holiday_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid additional holiday date format. Use YYYY-MM-DD")
        
        # Validate device exists
        if device_name not in config.devices:
            raise HTTPException(status_code=404, detail=f"Device '{device_name}' not found")
        
        records = fetch_attendance_data(start_date, end_date, device_name, additional_holidays_list)
        
        # Filter by user if specified
        if user_name:
            records = [r for r in records if r.user_name.lower() == user_name.lower()]
        
        device_config = config.devices[device_name]
        device_info = DeviceInfo(
            device_name=device_name,
            device_ip=device_config["ip"],
            device_port=device_config["port"],
            backend_name=config.backend_name,
            is_connected=True,
            last_sync=datetime.now().isoformat()
        )
        
        return AttendanceResponse(
            success=True,
            data=records,
            device_info=device_info,
            total_records=len(records),
            message=f"Successfully retrieved {len(records)} attendance records from {device_name}" +
                   (f" (with {len(additional_holidays_list)} additional holidays)" if additional_holidays_list else "")
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/attendance/all", response_model=AttendanceResponse)
async def get_all_attendance_data(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    user_name: Optional[str] = Query(None, description="Filter by specific user name"),
    additional_holidays: Optional[str] = Query(None, description="Comma-separated list of additional holidays in YYYY-MM-DD format")
):
    """Get attendance data from all devices for specified date range"""
    try:
        # Validate date format
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        
        # Parse additional holidays
        additional_holidays_list = []
        if additional_holidays:
            try:
                additional_holidays_list = [date.strip() for date in additional_holidays.split(',') if date.strip()]
                # Validate additional holiday dates
                for holiday_date in additional_holidays_list:
                    datetime.strptime(holiday_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid additional holiday date format. Use YYYY-MM-DD")
        
        all_records = []
        
        # Fetch data from all devices
        for device_name in config.devices:
            try:
                records = fetch_attendance_data(start_date, end_date, device_name, additional_holidays_list)
                all_records.extend(records)
            except Exception as e:
                print(f"Error fetching data from {device_name}: {e}")
                continue
        
        # Filter by user if specified
        if user_name:
            all_records = [r for r in all_records if r.user_name.lower() == user_name.lower()]
        
        return AttendanceResponse(
            success=True,
            data=all_records,
            device_info=None,
            total_records=len(all_records),
            message=f"Successfully retrieved {len(all_records)} attendance records from {len(config.devices)} devices" +
                   (f" (with {len(additional_holidays_list)} additional holidays)" if additional_holidays_list else "")
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users", response_model=dict)
async def get_users(
    request: Request,
    device_name: str = Query(..., description="Name of the fingerprint device"),
    _: bool = Depends(validate_api_key)
):
    """Get list of users from a specific device"""
    if not ZK_AVAILABLE:
        raise HTTPException(status_code=500, detail="ZK library not available")
    
    if device_name not in config.devices:
        raise HTTPException(status_code=404, detail=f"Device '{device_name}' not found")
    
    device_config = config.devices[device_name]
    
    try:
        zk = ZK(device_config["ip"], port=device_config["port"], timeout=5, 
                password=device_config["password"], force_udp=False, ommit_ping=False)
        conn = zk.connect()
        conn.disable_device()
        
        users = conn.get_users()
        user_list = [{"user_id": user.user_id, "name": user.name, "privilege": user.privilege} 
                     for user in users]
        
        conn.enable_device()
        conn.disconnect()
        
        return {
            "success": True,
            "users": user_list,
            "total_users": len(user_list),
            "device_name": device_name
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users from {device_name}: {str(e)}")

@app.get("/users/all", response_model=dict)
async def get_all_users():
    """Get list of users from all devices"""
    if not ZK_AVAILABLE:
        raise HTTPException(status_code=500, detail="ZK library not available")
    
    all_users = {}
    total_users = 0
    
    for device_name, device_config in config.devices.items():
        try:
            zk = ZK(device_config["ip"], port=device_config["port"], timeout=5, 
                    password=device_config["password"], force_udp=False, ommit_ping=False)
            conn = zk.connect()
            conn.disable_device()
            
            users = conn.get_users()
            user_list = [{"user_id": user.user_id, "name": user.name, "privilege": user.privilege} 
                         for user in users]
            
            all_users[device_name] = {
                "users": user_list,
                "total_users": len(user_list),
                "device_ip": device_config["ip"]
            }
            total_users += len(user_list)
            
            conn.enable_device()
            conn.disconnect()
            
        except Exception as e:
            print(f"Error fetching users from {device_name}: {e}")
            all_users[device_name] = {
                "error": str(e),
                "users": [],
                "total_users": 0
            }
    
    return {
        "success": True,
        "devices": all_users,
        "total_devices": len(config.devices),
        "total_users": total_users,
        "backend_name": config.backend_name
    }

@app.get("/attendance/summary", response_model=dict)
async def get_attendance_summary(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    device_name: str = Query(..., description="Name of the fingerprint device"),
    additional_holidays: Optional[str] = Query(None, description="Comma-separated list of additional holidays in YYYY-MM-DD format")
):
    """Get attendance summary statistics for a specific device"""
    try:
        if device_name not in config.devices:
            raise HTTPException(status_code=404, detail=f"Device '{device_name}' not found")
        
        # Parse additional holidays
        additional_holidays_list = []
        if additional_holidays:
            try:
                additional_holidays_list = [date.strip() for date in additional_holidays.split(',') if date.strip()]
                # Validate additional holiday dates
                for holiday_date in additional_holidays_list:
                    datetime.strptime(holiday_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid additional holiday date format. Use YYYY-MM-DD")
        
        records = fetch_attendance_data(start_date, end_date, device_name, additional_holidays_list)
        
        # Separate holidays from working day records
        working_records = [r for r in records if r.status != 'Holiday']
        holiday_records = [r for r in records if r.status == 'Holiday']
        
        total_records = len(records)
        working_days_count = len(working_records)
        holiday_count = len(holiday_records)
        present_count = sum(1 for r in working_records if r.status == 'Present')
        absent_count = sum(1 for r in working_records if r.status == 'Absent')
        incomplete_count = sum(1 for r in working_records if r.status == 'Incomplete')
        
        # Group by user with enhanced statistics (excluding holidays from user stats)
        user_stats = defaultdict(lambda: {
            'present_days': 0, 
            'absent_days': 0, 
            'incomplete_days': 0, 
            'holiday_days': 0,
            'total_working_hours': 0.0,
            'total_expected_hours': 0.0,
            'average_working_hours': 0.0,
            'working_hours_progress': 0.0
        })
        
        for record in records:
            if record.status == 'Holiday':
                user_stats[record.user_name]['holiday_days'] += 1
            else:
                user_stats[record.user_name][record.status.lower() + '_days'] += 1
                user_stats[record.user_name]['total_working_hours'] += record.working_hours
                user_stats[record.user_name]['total_expected_hours'] += record.expected_hours
        
        # Calculate averages and progress for each user
        for user_name, stats in user_stats.items():
            working_days = stats['present_days'] + stats['absent_days'] + stats['incomplete_days']
            if working_days > 0:
                stats['average_working_hours'] = stats['total_working_hours'] / working_days
                stats['working_hours_progress'] = (stats['total_working_hours'] / stats['total_expected_hours'] * 100) if stats['total_expected_hours'] > 0 else 0.0
                stats['attendance_rate'] = f"{(stats['present_days'] / working_days * 100):.1f}%"
            else:
                stats['attendance_rate'] = "0%"
        
        return {
            "success": True,
            "device_name": device_name,
            "date_range": {"start_date": start_date, "end_date": end_date},
            "overall_stats": {
                "total_records": total_records,
                "working_days_count": working_days_count,
                "holiday_count": holiday_count,
                "present_count": present_count,
                "absent_count": absent_count,
                "incomplete_count": incomplete_count,
                "day_based_attendance_rate": f"{(present_count / working_days_count * 100):.1f}%" if working_days_count > 0 else "0%",
                "standard_working_hours": 8.0,
                "total_expected_hours": working_days_count * 8.0,
                "total_actual_hours": sum(r.working_hours for r in working_records),
                "hours_based_progress": f"{(sum(r.working_hours for r in working_records) / (working_days_count * 8.0) * 100):.1f}%" if working_days_count > 0 else "0%"
            },
            "user_stats": dict(user_stats)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/attendance/summary/all", response_model=dict)
async def get_all_attendance_summary(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    additional_holidays: Optional[str] = Query(None, description="Comma-separated list of additional holidays in YYYY-MM-DD format")
):
    """Get attendance summary statistics for all devices"""
    try:
        # Parse additional holidays
        additional_holidays_list = []
        if additional_holidays:
            try:
                additional_holidays_list = [date.strip() for date in additional_holidays.split(',') if date.strip()]
                # Validate additional holiday dates
                for holiday_date in additional_holidays_list:
                    datetime.strptime(holiday_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid additional holiday date format. Use YYYY-MM-DD")
        
        all_stats = {}
        overall_totals = {
            "total_records": 0,
            "working_days_count": 0,
            "holiday_count": 0,
            "present_count": 0,
            "absent_count": 0,
            "incomplete_count": 0
        }
        
        for device_name in config.devices:
            try:
                records = fetch_attendance_data(start_date, end_date, device_name, additional_holidays_list)
                
                # Separate holidays from working day records
                working_records = [r for r in records if r.status != 'Holiday']
                holiday_records = [r for r in records if r.status == 'Holiday']
                
                total_records = len(records)
                working_days_count = len(working_records)
                holiday_count = len(holiday_records)
                present_count = sum(1 for r in working_records if r.status == 'Present')
                absent_count = sum(1 for r in working_records if r.status == 'Absent')
                incomplete_count = sum(1 for r in working_records if r.status == 'Incomplete')
                
                # Update overall totals
                overall_totals["total_records"] += total_records
                overall_totals["working_days_count"] += working_days_count
                overall_totals["holiday_count"] += holiday_count
                overall_totals["present_count"] += present_count
                overall_totals["absent_count"] += absent_count
                overall_totals["incomplete_count"] += incomplete_count
                
                # Group by user for this device (excluding holidays from user stats)
                user_stats = defaultdict(lambda: {'present': 0, 'absent': 0, 'incomplete': 0, 'holiday': 0})
                for record in records:
                    if record.status == 'Holiday':
                        user_stats[record.user_name]['holiday'] += 1
                    else:
                        user_stats[record.user_name][record.status.lower()] += 1
                
                all_stats[device_name] = {
                    "device_stats": {
                        "total_records": total_records,
                        "working_days_count": working_days_count,
                        "holiday_count": holiday_count,
                        "present_count": present_count,
                        "absent_count": absent_count,
                        "incomplete_count": incomplete_count,
                        "attendance_rate": f"{(present_count / working_days_count * 100):.1f}%" if working_days_count > 0 else "0%"
                    },
                    "user_stats": dict(user_stats)
                }
                
            except Exception as e:
                print(f"Error getting summary for {device_name}: {e}")
                all_stats[device_name] = {"error": str(e)}
        
        return {
            "success": True,
            "backend_name": config.backend_name,
            "date_range": {"start_date": start_date, "end_date": end_date},
            "overall_stats": {
                **overall_totals,
                "attendance_rate": f"{(overall_totals['present_count'] / overall_totals['working_days_count'] * 100):.1f}%" if overall_totals['working_days_count'] > 0 else "0%"
            },
            "devices": all_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"Starting Fingerprint Backend Service")
    print(f"Backend Name: {config.backend_name}")
    print(f"API Port: {config.backend_port}")
    print(f"Total Devices: {len(config.devices)}")
    print(f"Calendar Library: {'python-calendrical' if CALENDRICAL_AVAILABLE else 'standard fallback'}")
    
    # Test connection for all devices on startup
    print("\nTesting device connections:")
    for device_name, device_config in config.devices.items():
        print(f"  - {device_name} ({device_config['ip']}:{device_config['port']})", end=" ")
        if test_device_connection(device_name):
            print("✅ Connected")
        else:
            print("❌ Failed")
    
    uvicorn.run(app, host="0.0.0.0", port=config.backend_port)