"""
Configuration Management

Handles loading and managing configuration from various sources.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from decouple import config

from .models import Device, PlaceConfig, DeviceStatus


class ConfigManager:
    """Configuration manager for the BiometricFlow system"""
    
    def __init__(self, config_root: Optional[Path] = None):
        """Initialize configuration manager"""
        if config_root is None:
            self.config_root = Path(__file__).parent.parent.parent.parent / "config"
        else:
            self.config_root = Path(config_root)
        
        self.devices_dir = self.config_root / "devices"
        self.environments_dir = self.config_root / "environments"
    
    def load_device_config(self, place_name: str) -> List[Device]:
        """Load device configuration for a specific place"""
        config_file = self.devices_dir / f"{place_name}.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Device config not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        devices = []
        for device_data in config_data.get("devices", []):
            device = Device(
                name=device_data["name"],
                ip=device_data["ip"],
                port=device_data["port"],
                place=place_name,
                status=DeviceStatus.UNKNOWN
            )
            devices.append(device)
        
        return devices
    
    def load_place_config(self, place_name: str) -> PlaceConfig:
        """Load complete place configuration including devices"""
        backends_config = self.load_backends_config()
        place_info = backends_config.get("places", {}).get(place_name)
        
        if not place_info:
            raise ValueError(f"Place not found in configuration: {place_name}")
        
        devices = self.load_device_config(place_name)
        
        place_config = PlaceConfig(
            name=place_name,
            location=place_info.get("location", place_name),
            backend_port=place_info.get("port", 8000),
            devices=devices
        )
        
        return place_config
    
    def load_backends_config(self) -> Dict[str, Any]:
        """Load unified backends configuration"""
        config_file = self.environments_dir / "backends.json"
        
        if not config_file.exists():
            # Fallback to old location
            config_file = self.config_root / "unified_backends_config.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Backends config not found: {config_file}")
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def get_all_places(self) -> List[str]:
        """Get list of all configured places"""
        backends_config = self.load_backends_config()
        return list(backends_config.get("places", {}).keys())
    
    def get_environment_config(self, env: str = "development") -> Dict[str, str]:
        """Load environment-specific configuration"""
        env_file = self.environments_dir / f"{env}.env"
        
        if not env_file.exists():
            # Fallback to .env in config root
            env_file = self.config_root / ".env"
        
        env_vars = {}
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_vars[key] = value.strip('"\'')
        
        return env_vars
    
    def get_database_url(self) -> str:
        """Get database URL from configuration"""
        return config('DATABASE_URL', default='sqlite:///biometric_flow.db')
    
    def get_redis_url(self) -> str:
        """Get Redis URL from configuration"""
        return config('REDIS_URL', default='redis://localhost:6379')
    
    def get_log_level(self) -> str:
        """Get log level from configuration"""
        return config('LOG_LEVEL', default='INFO')


# Global configuration instance
config_manager = ConfigManager()
