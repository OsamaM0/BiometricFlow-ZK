"""
Utility Functions

Common utility functions used throughout the BiometricFlow system.
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import csv


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def is_working_day(date: datetime, holidays: List[str] = None) -> bool:
    """Check if a given date is a working day"""
    if holidays is None:
        holidays = []
    
    # Check if it's a weekend (Saturday = 5, Sunday = 6)
    if date.weekday() >= 5:
        return False
    
    # Check if it's a holiday
    date_str = date.strftime("%Y-%m-%d")
    if date_str in holidays:
        return False
    
    return True


def calculate_working_hours(
    check_in: datetime, 
    check_out: datetime,
    break_duration: timedelta = timedelta(hours=1)
) -> timedelta:
    """Calculate actual working hours"""
    total_time = check_out - check_in
    return max(timedelta(0), total_time - break_duration)


def format_duration(duration: timedelta) -> str:
    """Format duration in human-readable format"""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}h {minutes}m"


def export_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
    """Export data to CSV file"""
    if not data:
        raise ValueError("No data to export")
    
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    return str(filepath)


def export_to_json(data: List[Dict[str, Any]], filename: str) -> str:
    """Export data to JSON file"""
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, default=str)
    
    return str(filepath)


async def retry_async_operation(
    operation,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0
) -> Any:
    """Retry an async operation with exponential backoff"""
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            last_exception = e
            if attempt == max_retries - 1:
                break
            
            await asyncio.sleep(delay * (backoff_factor ** attempt))
    
    raise last_exception


def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    try:
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    except ValueError:
        return False


def validate_port(port: int) -> bool:
    """Validate port number"""
    return 1 <= port <= 65535


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_time_ranges_for_day(date: datetime) -> Tuple[datetime, datetime]:
    """Get start and end datetime for a given date"""
    start_of_day = datetime.combine(date.date(), time.min)
    end_of_day = datetime.combine(date.date(), time.max)
    return start_of_day, end_of_day


def batch_list(items: List[Any], batch_size: int) -> List[List[Any]]:
    """Split a list into batches of specified size"""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


class HealthChecker:
    """Health check utility for services and devices"""
    
    @staticmethod
    async def check_http_endpoint(url: str, timeout: float = 5.0) -> bool:
        """Check if HTTP endpoint is responding"""
        try:
            import aiohttp
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(url) as response:
                    return response.status < 500
        except Exception:
            return False
    
    @staticmethod
    async def check_tcp_connection(host: str, port: int, timeout: float = 5.0) -> bool:
        """Check if TCP connection can be established"""
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False
