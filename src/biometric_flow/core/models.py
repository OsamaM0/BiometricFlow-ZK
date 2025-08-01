"""
Core Models for BiometricFlow

Data models and business entities used throughout the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class DeviceStatus(Enum):
    """Device status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    UNKNOWN = "unknown"


class AttendanceType(Enum):
    """Attendance type enumeration"""
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    BREAK_START = "break_start"
    BREAK_END = "break_end"


@dataclass
class Device:
    """Fingerprint device model"""
    name: str
    ip: str
    port: int
    place: str
    status: DeviceStatus = DeviceStatus.UNKNOWN
    last_seen: Optional[datetime] = None
    firmware_version: Optional[str] = None
    user_count: int = 0
    attendance_count: int = 0
    
    @property
    def connection_string(self) -> str:
        """Return device connection string"""
        return f"{self.ip}:{self.port}"


@dataclass
class User:
    """User model"""
    user_id: int
    name: str
    user_sn: Optional[str] = None
    privilege: int = 0
    password: Optional[str] = None
    group_id: Optional[str] = None
    card: Optional[int] = None


@dataclass
class AttendanceRecord:
    """Attendance record model"""
    user_id: int
    timestamp: datetime
    device_name: str
    place: str
    punch: int
    attendance_type: AttendanceType = AttendanceType.CHECK_IN
    
    @property
    def formatted_time(self) -> str:
        """Return formatted timestamp"""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class PlaceConfig:
    """Place configuration model"""
    name: str
    location: str
    backend_port: int
    devices: List[Device] = field(default_factory=list)
    
    def add_device(self, device: Device):
        """Add a device to this place"""
        device.place = self.name
        self.devices.append(device)


@dataclass
class SystemHealth:
    """System health status model"""
    unified_gateway_status: bool
    places: Dict[str, bool] = field(default_factory=dict)
    devices: Dict[str, DeviceStatus] = field(default_factory=dict)
    total_places: int = 0
    total_devices: int = 0
    healthy_devices: int = 0
    
    @property
    def overall_health(self) -> float:
        """Calculate overall system health percentage"""
        if self.total_devices == 0:
            return 0.0
        return (self.healthy_devices / self.total_devices) * 100


@dataclass
class ApiResponse:
    """Standard API response model"""
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
