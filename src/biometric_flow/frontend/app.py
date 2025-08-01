import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import warnings
warnings.filterwarnings('ignore')
from collections import defaultdict
import io
import numpy as np
import requests
import json
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp

# Set page config
st.set_page_config(
    page_title="Multi-Device Attendance Management System",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend Configuration - Updated for Unified Gateway
BACKEND_CONFIG = {
    "url": "http://localhost:9000",  # Unified Gateway URL
    "name": "Unified Gateway Backend"
}

# Enhanced table styling functions
def create_enhanced_table_style():
    """Create enhanced styling for all tables with better visibility"""
    return {
        'headers': {
            'background-color': '#2c3e50',
            'color': 'white',
            'font-weight': 'bold',
            'text-align': 'center',
            'border': '1px solid #34495e'
        },
        'data': {
            'background-color': '#ecf0f1',
            'color': '#2c3e50',
            'border': '1px solid #bdc3c7',
            'text-align': 'center'
        },
        'alternate_rows': {
            'background-color': '#f8f9fa',
            'color': '#2c3e50',
            'border': '1px solid #bdc3c7',
            'text-align': 'center'
        }
    }

def style_attendance_summary_table(df):
    """Style summary tables with enhanced visibility"""
    def style_attendance_rates(val):
        if isinstance(val, str) and '%' in val:
            rate = float(val.replace('%', ''))
            if rate >= 95:
                return 'background-color: #d4edda; color: #155724; font-weight: bold'
            elif rate >= 80:
                return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            else:
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
        return 'background-color: #f8f9fa; color: #2c3e50'
    
    def style_hours_progress(val):
        if isinstance(val, str) and '%' in val:
            rate = float(val.replace('%', ''))
            if rate >= 90:
                return 'background-color: #d4edda; color: #155724; font-weight: bold'
            elif rate >= 70:
                return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            else:
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
        return 'background-color: #f8f9fa; color: #2c3e50'
    
    # Apply styling to specific columns
    styled_df = df.style
    
    # Style attendance rate columns
    if 'Attendance_Rate' in df.columns:
        styled_df = styled_df.applymap(lambda x: style_attendance_rates(x) if pd.notna(x) else '', subset=['Attendance_Rate'])
    if 'Attendance Rate' in df.columns:
        styled_df = styled_df.applymap(lambda x: style_attendance_rates(x) if pd.notna(x) else '', subset=['Attendance Rate'])
    
    # Style hours progress columns
    if 'Hours_Progress' in df.columns:
        styled_df = styled_df.applymap(lambda x: style_hours_progress(x) if pd.notna(x) else '', subset=['Hours_Progress'])
    if 'Hours Progress' in df.columns:
        styled_df = styled_df.applymap(lambda x: style_hours_progress(x) if pd.notna(x) else '', subset=['Hours Progress'])
    
    # Apply general table styling
    styled_df = styled_df.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', '#2c3e50'), 
                                          ('color', 'white'), 
                                          ('font-weight', 'bold'),
                                          ('text-align', 'center'),
                                          ('border', '1px solid #34495e')]},
        {'selector': 'tbody td', 'props': [('border', '1px solid #bdc3c7'),
                                          ('text-align', 'center'),
                                          ('padding', '8px')]},
        {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f8f9fa')]},
        {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', '#ffffff')]}
    ])
    
    return styled_df

def style_device_summary_table(df):
    """Style device summary tables with device-specific enhancements"""
    def highlight_device_metrics(row):
        styles = []
        for i, val in enumerate(row):
            if 'Attendance_Rate' in df.columns and df.columns[i] == 'Attendance_Rate':
                if isinstance(val, (int, float)) and val >= 95:
                    styles.append('background-color: #d4edda; color: #155724; font-weight: bold')
                elif isinstance(val, (int, float)) and val >= 80:
                    styles.append('background-color: #fff3cd; color: #856404; font-weight: bold')
                elif isinstance(val, (int, float)) and val < 80:
                    styles.append('background-color: #f8d7da; color: #721c24; font-weight: bold')
                else:
                    styles.append('background-color: #f8f9fa; color: #2c3e50')
            elif 'Hours_Progress' in df.columns and df.columns[i] == 'Hours_Progress':
                if isinstance(val, (int, float)) and val >= 90:
                    styles.append('background-color: #d4edda; color: #155724; font-weight: bold')
                elif isinstance(val, (int, float)) and val >= 70:
                    styles.append('background-color: #fff3cd; color: #856404; font-weight: bold')
                elif isinstance(val, (int, float)) and val < 70:
                    styles.append('background-color: #f8d7da; color: #721c24; font-weight: bold')
                else:
                    styles.append('background-color: #f8f9fa; color: #2c3e50')
            else:
                styles.append('background-color: #f8f9fa; color: #2c3e50; padding: 8px')
        return styles
    
    styled_df = df.style.apply(highlight_device_metrics, axis=1)
    styled_df = styled_df.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', '#34495e'), 
                                          ('color', 'white'), 
                                          ('font-weight', 'bold'),
                                          ('text-align', 'center'),
                                          ('border', '1px solid #2c3e50')]},
        {'selector': 'tbody td', 'props': [('border', '1px solid #bdc3c7'),
                                          ('text-align', 'center'),
                                          ('padding', '8px')]}
    ])
    
    return styled_df

def style_trends_table(df):
    """Style trends tables with date-based formatting"""
    def highlight_trends(row):
        styles = []
        for i, val in enumerate(row):
            if 'attendance_rate' in df.columns and df.columns[i] == 'attendance_rate':
                # Remove % sign if present and convert to float
                if isinstance(val, str) and '%' in val:
                    rate = float(val.replace('%', ''))
                elif isinstance(val, (int, float)):
                    rate = val
                else:
                    rate = 0
                
                if rate >= 95:
                    styles.append('background-color: #d4edda; color: #155724; font-weight: bold')
                elif rate >= 80:
                    styles.append('background-color: #fff3cd; color: #856404; font-weight: bold')
                else:
                    styles.append('background-color: #f8d7da; color: #721c24; font-weight: bold')
            else:
                styles.append('background-color: #f8f9fa; color: #2c3e50; padding: 8px')
        return styles
    
    styled_df = df.style.apply(highlight_trends, axis=1)
    styled_df = styled_df.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', '#17a2b8'), 
                                          ('color', 'white'), 
                                          ('font-weight', 'bold'),
                                          ('text-align', 'center'),
                                          ('border', '1px solid #138496')]},
        {'selector': 'tbody td', 'props': [('border', '1px solid #bdc3c7'),
                                          ('text-align', 'center'),
                                          ('padding', '8px')]},
        {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f8f9fa')]},
        {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', '#ffffff')]}
    ])
    
    return styled_df

class BackendClient:
    """Client to interact with unified multi-place backend API"""
    
    def __init__(self, backend_url: str, timeout: int = 30):
        self.base_url = backend_url.rstrip('/')
        self.timeout = timeout
    
    def health_check(self) -> Dict[str, Any]:
        """Check if unified gateway is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}
    
    def get_places(self) -> Dict[str, Any]:
        """Get list of all places"""
        try:
            response = requests.get(f"{self.base_url}/places", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_devices(self) -> Dict[str, Any]:
        """Get list of all devices from all places"""
        try:
            response = requests.get(f"{self.base_url}/devices/all", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_place_devices(self, place_name: str) -> Dict[str, Any]:
        """Get devices from a specific place"""
        try:
            response = requests.get(f"{self.base_url}/place/{place_name}/devices", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_device_info(self, device_name: str) -> Dict[str, Any]:
        """Get information for a specific device"""
        try:
            response = requests.get(f"{self.base_url}/device/{device_name}/info", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_attendance_data(self, device_name: str, start_date: str, end_date: str, user_name: str = None, additional_holidays: str = None) -> Dict[str, Any]:
        """Get attendance data from specific device"""
        try:
            params = {
                "start_date": start_date, 
                "end_date": end_date
            }
            if user_name:
                params["user_name"] = user_name
            if additional_holidays:
                params["additional_holidays"] = additional_holidays
            
            response = requests.get(f"{self.base_url}/device/{device_name}/attendance", params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_all_attendance_data(self, start_date: str, end_date: str, user_name: str = None, additional_holidays: str = None) -> Dict[str, Any]:
        """Get attendance data from all places"""
        try:
            params = {
                "start_date": start_date, 
                "end_date": end_date
            }
            if user_name:
                params["user_name"] = user_name
            if additional_holidays:
                params["additional_holidays"] = additional_holidays
            
            response = requests.get(f"{self.base_url}/attendance/all", params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_place_attendance_data(self, place_name: str, start_date: str, end_date: str, device_name: str = None, user_name: str = None, additional_holidays: str = None) -> Dict[str, Any]:
        """Get attendance data from specific place"""
        try:
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
            
            response = requests.get(f"{self.base_url}/place/{place_name}/attendance", params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_all_users(self) -> Dict[str, Any]:
        """Get all users from all places"""
        try:
            response = requests.get(f"{self.base_url}/users/all", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_place_users(self, place_name: str) -> Dict[str, Any]:
        """Get users from specific place"""
        try:
            response = requests.get(f"{self.base_url}/place/{place_name}/users", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_all_attendance_summary(self, start_date: str, end_date: str, additional_holidays: str = None) -> Dict[str, Any]:
        """Get attendance summary from all places"""
        try:
            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            if additional_holidays:
                params["additional_holidays"] = additional_holidays
            
            response = requests.get(f"{self.base_url}/summary/all", params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_place_summary(self, place_name: str, start_date: str, end_date: str, additional_holidays: str = None) -> Dict[str, Any]:
        """Get attendance summary from specific place"""
        try:
            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            if additional_holidays:
                params["additional_holidays"] = additional_holidays
            
            response = requests.get(f"{self.base_url}/place/{place_name}/summary", params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    def get_holidays(self) -> Dict[str, Any]:
        """Get holidays for all years"""
        try:
            response = requests.get(f"{self.base_url}/holidays", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate_custom_holidays(self, holiday_dates: List[str]) -> Dict[str, Any]:
        """Validate custom holiday dates"""
        valid_dates = []
        invalid_dates = []
        
        for date_str in holiday_dates:
            try:
                # Validate date format
                datetime.strptime(date_str, '%Y-%m-%d')
                valid_dates.append(date_str)
            except ValueError:
                invalid_dates.append(date_str)
        
        return {
            "success": True,
            "valid_dates": valid_dates,
            "invalid_dates": invalid_dates,
            "message": f"Validated {len(valid_dates)} valid dates, {len(invalid_dates)} invalid dates"
        }
    
    def get_holiday_suggestions(self) -> Dict[str, Any]:
        """Get holiday suggestions for current year"""
        current_year = datetime.now().year
        
        # Basic holiday suggestions
        suggestions = [
            {"date": f"{current_year}-01-01", "name": "New Year's Day", "type": "National"},
            {"date": f"{current_year}-07-04", "name": "Independence Day", "type": "National"},
            {"date": f"{current_year}-12-25", "name": "Christmas Day", "type": "National"},
            {"date": f"{current_year}-11-28", "name": "Thanksgiving", "type": "National"},
        ]
        
        return {
            "success": True,
            "year": current_year,
            "suggestions": suggestions,
            "message": f"Holiday suggestions for {current_year}"
        }


@st.cache_data(ttl=300)  # Cache for 5 minutes
def check_backend_status():
    """Check status of backend and get available devices"""
    client = BackendClient(BACKEND_CONFIG["url"])
    
    # Check backend health
    health_status = client.health_check()
    
    # Get available devices
    devices_response = client.get_devices()
    
    backend_status = {
        "backend_healthy": health_status.get("status") in ["healthy", "partially_healthy"],
        "backend_url": BACKEND_CONFIG["url"],
        "backend_name": BACKEND_CONFIG["name"],
        "devices": []
    }
    
    if devices_response.get("success", False):
        backend_status["devices"] = devices_response["devices"]
        backend_status["total_devices"] = devices_response["total_devices"]
    else:
        backend_status["devices"] = []
        backend_status["total_devices"] = 0
        backend_status["error"] = devices_response.get("error", "Unknown error")
    
    return backend_status

def fetch_multi_device_data(start_date: str, end_date: str, selected_devices: List[str] = None, additional_holidays: List[str] = None) -> pd.DataFrame:
    """Fetch data from selected devices with optional custom holidays"""
    client = BackendClient(BACKEND_CONFIG["url"])
    all_data = []
    errors = []
    
    # Convert additional holidays list to comma-separated string for API
    additional_holidays_str = ",".join(additional_holidays) if additional_holidays else None
    
    if not selected_devices or "All Devices" in selected_devices:
        # Fetch from all devices
        with st.spinner("Fetching data from all devices..."):
            # Use the existing get_all_attendance_data method, but we need to enhance it for holidays
            if additional_holidays_str:
                # Use direct API call with custom holidays for all devices
                params = {
                    "start_date": start_date, 
                    "end_date": end_date,
                    "additional_holidays": additional_holidays_str
                }
                try:
                    response = requests.get(f"{BACKEND_CONFIG['url']}/attendance/all", params=params, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success", False):
                            for record in result["data"]:
                                record_dict = dict(record)
                                all_data.append(record_dict)
                            st.success(f"✅ All Devices: {len(result['data'])} records" + 
                                     (f" (with {len(additional_holidays)} custom holidays)" if additional_holidays else ""))
                        else:
                            error_msg = result.get("error", "Unknown error")
                            errors.append(f"All Devices: {error_msg}")
                            st.error(f"❌ All Devices: {error_msg}")
                    else:
                        error_msg = f"HTTP {response.status_code}"
                        errors.append(f"All Devices: {error_msg}")
                        st.error(f"❌ All Devices: {error_msg}")
                except Exception as e:
                    error_msg = str(e)
                    errors.append(f"All Devices: {error_msg}")
                    st.error(f"❌ All Devices: {error_msg}")
            else:
                # Use existing method without custom holidays
                result = client.get_all_attendance_data(start_date, end_date)
                if result.get("success", False):
                    for record in result["data"]:
                        record_dict = dict(record)
                        all_data.append(record_dict)
                    st.success(f"✅ All Devices: {len(result['data'])} records")
                else:
                    error_msg = result.get("error", "Unknown error")
                    errors.append(f"All Devices: {error_msg}")
                    st.error(f"❌ All Devices: {error_msg}")
    else:
        # Fetch from specific devices
        for device_name in selected_devices:
            with st.spinner(f"Fetching data from {device_name}..."):
                if additional_holidays_str:
                    # Use direct API call with custom holidays for specific device
                    params = {
                        "device_name": device_name,
                        "start_date": start_date, 
                        "end_date": end_date,
                        "additional_holidays": additional_holidays_str
                    }
                    try:
                        response = requests.get(f"{BACKEND_CONFIG['url']}/attendance", params=params, timeout=30)
                        if response.status_code == 200:
                            result = response.json()
                            if result.get("success", False):
                                for record in result["data"]:
                                    record_dict = dict(record)
                                    all_data.append(record_dict)
                                st.success(f"✅ {device_name}: {len(result['data'])} records" + 
                                         (f" (with {len(additional_holidays)} custom holidays)" if additional_holidays else ""))
                            else:
                                error_msg = result.get("error", "Unknown error")
                                errors.append(f"{device_name}: {error_msg}")
                                st.error(f"❌ {device_name}: {error_msg}")
                        else:
                            error_msg = f"HTTP {response.status_code}"
                            errors.append(f"{device_name}: {error_msg}")
                            st.error(f"❌ {device_name}: {error_msg}")
                    except Exception as e:
                        error_msg = str(e)
                        errors.append(f"{device_name}: {error_msg}")
                        st.error(f"❌ {device_name}: {error_msg}")
                else:
                    # Use existing method without custom holidays
                    result = client.get_attendance_data(device_name, start_date, end_date)
                    if result.get("success", False):
                        for record in result["data"]:
                            record_dict = dict(record)
                            all_data.append(record_dict)
                        st.success(f"✅ {device_name}: {len(result['data'])} records")
                    else:
                        error_msg = result.get("error", "Unknown error")
                        errors.append(f"{device_name}: {error_msg}")
                        st.error(f"❌ {device_name}: {error_msg}")
    
    if errors:
        st.warning(f"Some devices had errors: {'; '.join(errors)}")
    
    return pd.DataFrame(all_data)

def create_multi_device_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Create summary statistics for multi-device data with enhanced working hours metrics"""
    if df.empty:
        return {}
    
    # Overall summary (excluding holidays from attendance rate calculation)
    working_records = df[df['status'] != 'Holiday']  # Exclude holidays from analysis
    total_records = len(df)
    working_days_count = len(working_records)
    holiday_count = len(df[df['status'] == 'Holiday'])
    present_count = len(working_records[working_records['status'] == 'Present'])
    absent_count = len(working_records[working_records['status'] == 'Absent'])
    incomplete_count = len(working_records[working_records['status'] == 'Incomplete'])
    
    # Working hours calculations
    total_working_hours = working_records['working_hours'].sum()
    total_expected_hours = working_days_count * 8.0  # 8 hours standard per working day
    hours_progress = (total_working_hours / total_expected_hours * 100) if total_expected_hours > 0 else 0
    avg_hours_per_day = total_working_hours / working_days_count if working_days_count > 0 else 0
    
    # By device summary (excluding holidays from attendance rate calculation)
    device_summary = working_records.groupby('device_name').agg({
        'status': ['count', lambda x: (x == 'Present').sum(), 
                  lambda x: (x == 'Absent').sum(), 
                  lambda x: (x == 'Incomplete').sum()],
        'working_hours': ['sum', 'mean']
    }).round(2)
    
    # Flatten column names
    device_summary.columns = ['Working_Days', 'Present', 'Absent', 'Incomplete', 'Total_Hours', 'Avg_Hours']
    device_summary['Attendance_Rate'] = (device_summary['Present'] / device_summary['Working_Days'] * 100).round(1)
    device_summary['Expected_Hours'] = device_summary['Working_Days'] * 8.0
    device_summary['Hours_Progress'] = (device_summary['Total_Hours'] / device_summary['Expected_Hours'] * 100).round(1)
    
    # Add holiday counts by device
    holiday_by_device = df[df['status'] == 'Holiday'].groupby('device_name').size().to_dict()
    device_summary['Holiday_Count'] = device_summary.index.map(lambda x: holiday_by_device.get(x, 0))
    
    # By user summary (excluding holidays from attendance rate calculation)
    user_summary = working_records.groupby('user_name').agg({
        'status': ['count', lambda x: (x == 'Present').sum()],
        'working_hours': ['sum', 'mean']
    }).round(2)
    user_summary.columns = ['Working_Days', 'Present', 'Total_Hours', 'Avg_Hours']
    user_summary['Attendance_Rate'] = (user_summary['Present'] / user_summary['Working_Days'] * 100).round(1)
    user_summary['Expected_Hours'] = user_summary['Working_Days'] * 8.0
    user_summary['Hours_Progress'] = (user_summary['Total_Hours'] / user_summary['Expected_Hours'] * 100).round(1)
    
    return {
        'overall': {
            'total_records': total_records,
            'working_days_count': working_days_count,
            'holiday_count': holiday_count,
            'present_count': present_count,
            'absent_count': absent_count,
            'incomplete_count': incomplete_count,
            'attendance_rate': f"{(present_count / working_days_count * 100):.1f}%" if working_days_count > 0 else "0%",
            'total_working_hours': total_working_hours,
            'total_expected_hours': total_expected_hours,
            'hours_progress': f"{hours_progress:.1f}%",
            'avg_hours_per_day': f"{avg_hours_per_day:.1f}h",
            'total_devices': df['device_name'].nunique(),
            'total_users': df['user_name'].nunique()
        },
        'by_device': device_summary.to_dict('index'),
        'by_user': user_summary.to_dict('index')
    }

def create_device_checklist_analysis(df: pd.DataFrame, selected_device: str = None):
    """Create checklist analysis by fingerprint device"""
    if df.empty:
        return None
    
    # Filter by device if selected
    if selected_device:
        device_data = df[df['device_name'] == selected_device].copy()
        st.subheader(f"📋 Checklist Analysis - {selected_device}")
    else:
        device_data = df.copy()
        st.subheader("📋 Overall Checklist Analysis")
    
    if device_data.empty:
        st.warning(f"No data found for {selected_device}")
        return None
    
    # Create checklist metrics (excluding holidays from attendance rate calculation)
    working_records = device_data[device_data['status'] != 'Holiday']
    holiday_records = device_data[device_data['status'] == 'Holiday']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_expected = len(device_data)
    working_days = len(working_records)
    holiday_days = len(holiday_records)
    present_count = len(working_records[working_records['status'] == 'Present'])
    absent_count = len(working_records[working_records['status'] == 'Absent'])
    incomplete_count = len(working_records[working_records['status'] == 'Incomplete'])
    
    with col1:
        st.metric("✅ Present", present_count, 
                 delta=f"{present_count/working_days*100:.1f}%" if working_days > 0 else "0%")
    with col2:
        st.metric("❌ Absent", absent_count,
                 delta=f"{absent_count/working_days*100:.1f}%" if working_days > 0 else "0%")
    with col3:
        st.metric("⚠️ Incomplete", incomplete_count,
                 delta=f"{incomplete_count/working_days*100:.1f}%" if working_days > 0 else "0%")
    with col4:
        st.metric("🏖️ Holidays", holiday_days,
                 delta=f"{holiday_days/total_expected*100:.1f}%" if total_expected > 0 else "0%")
    with col5:
        st.metric("📋 Working Days", working_days)
    
    # Daily checklist table
    st.subheader("📅 Daily Checklist")
    
    # Group by date and create checklist
    daily_checklist = device_data.groupby(['date', 'user_name'])['status'].first().reset_index()
    checklist_pivot = daily_checklist.pivot(index='date', columns='user_name', values='status')
    
    # Style the dataframe
    def style_status(val):
        if val == 'Present':
            return 'background-color: #d4edda; color: #155724'
        elif val == 'Absent':
            return 'background-color: #f8d7da; color: #721c24'
        elif val == 'Incomplete':
            return 'background-color: #fff3cd; color: #856404'
        else:
            return ''
    
    styled_checklist = checklist_pivot.style.applymap(style_status)
    st.dataframe(styled_checklist, use_container_width=True)
    
    # Employee status summary for this device - Fixed to exclude holidays from attendance rate
    st.subheader("👥 Employee Summary")
    
    # Calculate metrics excluding holidays
    working_data = device_data[device_data['status'] != 'Holiday']
    holiday_data = device_data[device_data['status'] == 'Holiday']
    
    # Employee summary with working days and holidays separated
    emp_summary = device_data.groupby('user_name').agg({
        'status': ['count', 
                  lambda x: (x == 'Present').sum(), 
                  lambda x: (x == 'Absent').sum(), 
                  lambda x: (x == 'Incomplete').sum(),
                  lambda x: (x == 'Holiday').sum()]
    }).round(2)
    emp_summary.columns = ['Total Days', 'Present', 'Absent', 'Incomplete', 'Holidays']
    
    # Calculate working days (total - holidays)
    emp_summary['Working Days'] = emp_summary['Total Days'] - emp_summary['Holidays']
    
    # Calculate attendance rate based on working days only
    emp_summary['Attendance Rate'] = (emp_summary['Present'] / emp_summary['Working Days'] * 100).round(1)
    
    # Calculate working hours metrics for each employee
    working_hours_summary = working_data.groupby('user_name').agg({
        'working_hours': ['sum', 'mean']
    }).round(2)
    working_hours_summary.columns = ['Total Hours', 'Avg Hours/Day']
    
    # Expected hours based on working days (8 hours standard)
    working_hours_summary['Expected Hours'] = emp_summary['Working Days'] * 8.0
    working_hours_summary['Hours Progress'] = (working_hours_summary['Total Hours'] / working_hours_summary['Expected Hours'] * 100).round(1)
    
    # Combine summaries
    final_summary = emp_summary.join(working_hours_summary, how='left')
    
    # Reorder columns for better display
    column_order = ['Total Days', 'Working Days', 'Holidays', 'Present', 'Absent', 'Incomplete', 
                   'Attendance Rate', 'Total Hours', 'Expected Hours', 'Hours Progress', 'Avg Hours/Day']
    final_summary = final_summary[column_order]
    final_summary = final_summary.sort_values('Attendance Rate', ascending=False)
    
    # Display with enhanced formatting and styling
    st.info("📊 **Attendance Rate** is calculated based on working days only (holidays excluded)")
    styled_summary = style_attendance_summary_table(final_summary)
    st.dataframe(styled_summary, use_container_width=True)
    
    return final_summary

def main():
    st.title("🌐 Multi-Device Attendance Management System")
    st.markdown("---")
    
    # Check backend status
    backend_status = check_backend_status()
    
    # Show backend status in sidebar
    with st.sidebar:
        st.header("🔗 Backend Status")
        
        if backend_status["backend_healthy"]:
            st.success(f"✅ {backend_status['backend_name']}")
            st.write(f"**URL:** {backend_status['backend_url']}")
            st.write(f"**Total Devices:** {backend_status['total_devices']}")
        else:
            st.error(f"❌ {backend_status['backend_name']} - Unreachable")
            if 'error' in backend_status:
                st.error(f"Error: {backend_status['error']}")
            return
        
        # Show available devices
        if backend_status["devices"]:
            st.subheader("📱 Available Devices")
            healthy_devices = []
            for device in backend_status["devices"]:
                if device["is_connected"]:
                    st.success(f"✅ {device['device_name']}")
                    healthy_devices.append(device['device_name'])
                else:
                    st.warning(f"⚠️ {device['device_name']} - Disconnected")
                    st.write(f"   IP: {device['device_ip']}:{device['device_port']}")
        else:
            st.error("No devices configured!")
            return
        
        st.markdown("---")
        st.header("📅 Query Settings")
        
        # Device selection
        device_options = ["All Devices"] + [device['device_name'] for device in backend_status["devices"]]
        selected_devices = st.multiselect(
            "Select Devices:",
            options=device_options,
            default=["All Devices"] if device_options else [],
            help="Choose which fingerprint devices to include in the analysis"
        )
        
        if not selected_devices:
            st.warning("Please select at least one device")
            return
        
        # Date inputs
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=7),
                max_value=datetime.now()
            )
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=datetime.now(),
                max_value=datetime.now()
            )
        
        # Validate date range
        if start_date > end_date:
            st.error("Start date must be before end date!")
            return
        
        # Holiday management section
        st.markdown("---")
        st.header("🏖️ Holiday Management")
        
        # Get backend holidays
        client = BackendClient(BACKEND_CONFIG["url"])
        holidays_response = client.get_holidays()
        
        if holidays_response.get("success", False):
            configured_holidays = holidays_response.get("holidays", [])
            if configured_holidays:
                with st.expander("📋 Configured Holidays", expanded=False):
                    st.write(f"**{len(configured_holidays)} holidays configured in backend:**")
                    
                    # Display holidays in columns for better layout
                    if len(configured_holidays) > 0:
                        cols = st.columns(3)
                        for i, holiday in enumerate(configured_holidays):
                            with cols[i % 3]:
                                st.write(f"📅 {holiday}")
        
        # Custom holidays input
        st.subheader("➕ Additional Holidays")
        st.write("Add extra dates to exclude as holidays (one per line, format: YYYY-MM-DD)")
        
        # Custom holidays text area
        custom_holidays_text = st.text_area(
            "Custom Holiday Dates:",
            value="",
            height=100,
            placeholder="2025-01-15\n2025-03-20\n2025-05-10",
            help="Enter additional holiday dates, one per line in YYYY-MM-DD format"
        )
        
        # Parse and validate custom holidays
        additional_holidays = []
        holiday_validation_errors = []
        
        if custom_holidays_text.strip():
            custom_holiday_lines = [line.strip() for line in custom_holidays_text.strip().split('\n') if line.strip()]
            
            if custom_holiday_lines:
                # Validate holidays using backend
                validation_response = client.validate_custom_holidays(custom_holiday_lines)
                
                if validation_response.get("success", False):
                    additional_holidays = validation_response.get("valid_dates", [])
                    if additional_holidays:
                        st.success(f"✅ {len(additional_holidays)} valid custom holidays will be applied")
                        
                        # Display custom holidays in organized columns
                        if len(additional_holidays) <= 6:
                            cols = st.columns(min(3, len(additional_holidays)))
                            for i, holiday in enumerate(additional_holidays):
                                with cols[i % len(cols)]:
                                    st.write(f"🎯 {holiday}")
                        else:
                            # For more holidays, display in a more compact format
                            st.write("**Custom holidays to be applied:**")
                            for i, holiday in enumerate(additional_holidays):
                                if i % 3 == 0:
                                    col1, col2, col3 = st.columns(3)
                                if i % 3 == 0:
                                    col1.write(f"🎯 {holiday}")
                                elif i % 3 == 1:
                                    col2.write(f"🎯 {holiday}")
                                else:
                                    col3.write(f"🎯 {holiday}")
                
                invalid_dates = validation_response.get("invalid_dates", [])
                if invalid_dates:
                    st.error(f"❌ {len(invalid_dates)} invalid dates found:")
                    for invalid_date in invalid_dates:
                        st.write(f"   • {invalid_date}")
                    holiday_validation_errors = invalid_dates
        
        # Holiday suggestions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💡 Get Holiday Suggestions"):
                suggestions_response = client.get_holiday_suggestions()
                if suggestions_response.get("success", False):
                    st.session_state['holiday_suggestions'] = suggestions_response
                    st.rerun()
        
        with col2:
            if st.button("🔄 Clear Custom Holidays"):
                st.session_state['custom_holidays_text'] = ""
                st.rerun()
        
        # Display holiday suggestions if available
        if 'holiday_suggestions' in st.session_state:
            suggestions = st.session_state['holiday_suggestions']
            if suggestions.get("success", False):
                with st.expander(f"💡 Holiday Suggestions for {suggestions.get('year', 'Current Year')}", expanded=True):
                    suggestion_list = suggestions.get("suggestions", [])
                    
                    # Group suggestions by type
                    suggestion_types = {}
                    for suggestion in suggestion_list:
                        stype = suggestion.get("type", "other")
                        if stype not in suggestion_types:
                            suggestion_types[stype] = []
                        suggestion_types[stype].append(suggestion)
                    
                    # Display suggestions by type
                    for stype, holidays in suggestion_types.items():
                        st.write(f"**{stype.title()} Holidays:**")
                        cols = st.columns(2)
                        for i, holiday in enumerate(holidays):
                            with cols[i % 2]:
                                st.write(f"📅 {holiday['date']} - {holiday['name']}")
                        st.write("")
        
        # Check for validation errors before allowing fetch
        if holiday_validation_errors:
            st.warning("⚠️ Please fix invalid holiday dates before fetching data.")
            return
        
        # Fetch data button
        if st.button("🔄 Fetch Multi-Device Data", type="primary"):
            df = fetch_multi_device_data(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                selected_devices,
                additional_holidays
            )
            st.session_state['attendance_data'] = df
            st.session_state['selected_devices'] = selected_devices
        
        # Export options
        st.header("📤 Export Options")
        if 'attendance_data' in st.session_state and not st.session_state['attendance_data'].empty:
            csv = st.session_state['attendance_data'].to_csv(index=False)
            st.download_button(
                label="📄 Download Multi-Device CSV",
                data=csv,
                file_name=f"multi_device_attendance_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
    
    # Main content
    if 'attendance_data' not in st.session_state:
        st.info("👈 Please select devices and click 'Fetch Multi-Device Data' to get started.")
        
        # Show device information
        st.header("📱 Available Fingerprint Devices")
        if backend_status["devices"]:
            for device in backend_status["devices"]:
                with st.expander(f"{device['device_name']} - {device['device_ip']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Status:** {'Connected' if device['is_connected'] else 'Disconnected'}")
                        st.write(f"**IP Address:** {device['device_ip']}")
                        st.write(f"**Port:** {device['device_port']}")
                    with col2:
                        st.write(f"**Backend:** {device['backend_name']}")
                        if device['last_sync']:
                            st.write(f"**Last Sync:** {device['last_sync'][:19]}")
                        connection_status = "🟢 Online" if device['is_connected'] else "🔴 Offline"
                        st.write(f"**Connection:** {connection_status}")
        return
    
    df = st.session_state['attendance_data']
    
    if df.empty:
        st.warning("No attendance data found for the selected devices and date range.")
        return
    
    # Show holiday information if custom holidays were applied
    if 'additional_holidays' in locals() and additional_holidays:
        st.info(f"ℹ️ **Custom Holidays Applied:** {len(additional_holidays)} additional holidays were excluded from calculations: {', '.join(additional_holidays)}")
    
    # Multi-device summary
    summary = create_multi_device_summary(df)
    
    st.header("📈 Multi-Device Overview")
    
    # Enhanced overview metrics - Two rows for better display
    st.subheader("📊 Key Metrics")
    
    overall = summary['overall']
    
    # First row - Basic counts
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📱 Devices", overall['total_devices'])
    with col2:
        st.metric("👥 Users", overall['total_users']) 
    with col3:
        st.metric("📋 Total Records", overall['total_records'])
    with col4:
        st.metric("💼 Working Days", overall['working_days_count'],
                 help="Total working days (holidays excluded)")
    with col5:
        st.metric("🏖️ Holidays", overall['holiday_count'])
    
    # Second row - Attendance and performance metrics  
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("✅ Present", overall['present_count'])
    with col2:
        st.metric("❌ Absent", overall['absent_count'])
    with col3:
        st.metric("⚠️ Incomplete", overall['incomplete_count'])
    with col4:
        st.metric("📊 Attendance Rate", overall['attendance_rate'],
                 help="Percentage of working days present (holidays excluded)")
    with col5:
        st.metric("⏰ Hours Progress", overall['hours_progress'],
                 help="Percentage of expected working hours completed")
    
    # Third row - Working hours details
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🕐 Total Hours", f"{overall['total_working_hours']:.1f}h")
    with col2:
        st.metric("📈 Expected Hours", f"{overall['total_expected_hours']:.1f}h")
    with col3:
        st.metric("📊 Avg Hours/Day", overall['avg_hours_per_day'])
    with col4:
        # Calculate standard working hours compliance
        standard_compliance = (overall['total_working_hours'] / (overall['working_days_count'] * 8.0) * 100) if overall['working_days_count'] > 0 else 0
        st.metric("🎯 8h Standard", f"{standard_compliance:.1f}%",
                 help="Compliance with 8-hour standard working day")
    
    st.markdown("---")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📱 Device Analysis", 
        "� Device Checklist", 
        "👤 Individual Analysis", 
        "📅 Trends", 
        "📊 Raw Data"
    ])
    
    with tab1:
        st.subheader("📱 Device Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Device attendance rates
            if summary['by_device']:
                device_df = pd.DataFrame(summary['by_device']).T
                device_df = device_df.reset_index()
                device_df.columns = ['Device'] + list(device_df.columns[1:])
                
                fig_devices = px.bar(
                    device_df,
                    x='Device',
                    y='Attendance_Rate',
                    title="Attendance Rate by Device",
                    color='Attendance_Rate',
                    color_continuous_scale='RdYlGn'
                )
                fig_devices.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_devices, use_container_width=True)
        
        with col2:
            # Status distribution by device
            device_status = df.groupby(['device_name', 'status']).size().reset_index(name='count')
            fig_status = px.bar(
                device_status,
                x='device_name',
                y='count',
                color='status',
                title="Status Distribution by Device",
                color_discrete_map={
                    'Present': '#2ecc71',
                    'Absent': '#e74c3c', 
                    'Incomplete': '#f39c12',
                    'Holiday': '#95a5a6'
                }
            )
            fig_status.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_status, use_container_width=True)
        
        # Device summary table
        st.subheader("📋 Device Summary")
        if summary['by_device']:
            device_summary_df = pd.DataFrame(summary['by_device']).T
            styled_device_df = style_device_summary_table(device_summary_df)
            st.info("🎯 **Color Coding:** Green (Excellent ≥95%), Yellow (Good ≥80%), Red (Needs Improvement <80%)")
            st.dataframe(styled_device_df, use_container_width=True)
    
    with tab2:
        st.subheader("📱 Device-Specific Checklist Analysis")
        
        # Device selector
        available_devices = df['device_name'].unique()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_device = st.selectbox(
                "Select Fingerprint Device:",
                options=['All Devices'] + list(available_devices),
                help="Choose a specific fingerprint device for detailed checklist analysis"
            )
        
        with col2:
            if st.button("🔄 Refresh Analysis"):
                st.rerun()
        
        # Create checklist analysis
        if selected_device == 'All Devices':
            # Show overview of all devices
            st.subheader("📊 All Devices Overview")
            
            if summary['by_device']:
                device_df = pd.DataFrame(summary['by_device']).T
                device_df = device_df.reset_index()
                device_df.columns = ['Device'] + list(device_df.columns[1:])
                
                # Device comparison chart
                fig_devices = px.bar(
                    device_df,
                    x='Device',
                    y='Attendance_Rate',
                    title="Attendance Rate by Fingerprint Device",
                    color='Attendance_Rate',
                    color_continuous_scale='RdYlGn'
                )
                fig_devices.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_devices, use_container_width=True)
                
                # Device summary table with enhanced styling
                styled_device_comparison = style_device_summary_table(device_df)
                st.info("📊 **Device Comparison Table** - Color-coded performance metrics")
                st.dataframe(styled_device_comparison, use_container_width=True)
        else:
            # Show specific device analysis
            create_device_checklist_analysis(df, selected_device)
    
    with tab3:
        st.subheader("👤 Individual Employee Analysis")
        
        # Employee and device selector
        col1, col2 = st.columns(2)
        with col1:
            selected_employee = st.selectbox("Select Employee:", df['user_name'].unique())
        with col2:
            employee_devices = df[df['user_name'] == selected_employee]['device_name'].unique()
            selected_device = st.selectbox("Select Device:", ['All Devices'] + list(employee_devices))
        
        if selected_employee:
            emp_data = df[df['user_name'] == selected_employee].copy()
            if selected_device != 'All Devices':
                emp_data = emp_data[emp_data['device_name'] == selected_device]
            
            # Employee metrics - Fixed to use working days only for attendance rate
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Separate working days from holidays
            working_records = emp_data[emp_data['status'] != 'Holiday']
            holiday_records = emp_data[emp_data['status'] == 'Holiday']
            
            total_days = len(emp_data)
            working_days = len(working_records)
            holiday_days = len(holiday_records)
            present_days = len(working_records[working_records['status'] == 'Present'])
            absent_days = len(working_records[working_records['status'] == 'Absent'])
            incomplete_days = len(working_records[working_records['status'] == 'Incomplete'])
            
            with col1:
                st.metric("📅 Total Days", total_days, 
                         help="Total days in the selected period")
            with col2:
                st.metric("💼 Working Days", working_days,
                         help="Working days (excluding holidays)")
            with col3:
                st.metric("✅ Present Days", present_days)
            with col4:
                st.metric("❌ Absent Days", absent_days)
            with col5:
                st.metric("⚠️ Incomplete Days", incomplete_days)
            
            # Additional metrics row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🏖️ Holiday Days", holiday_days)
            with col2:
                st.metric("📊 Attendance Rate", 
                         f"{present_days/working_days*100:.1f}%" if working_days > 0 else "0%",
                         help="Percentage of working days present (holidays excluded)")
            with col3:
                # Calculate working hours metrics
                total_working_hours = emp_data['working_hours'].sum()
                total_expected_hours = working_days * 8.0  # 8 hours standard working day
                st.metric("⏰ Total Hours", f"{total_working_hours:.1f}h")
            with col4:
                st.metric("📈 Hours Progress", 
                         f"{total_working_hours/total_expected_hours*100:.1f}%" if total_expected_hours > 0 else "0%",
                         help="Percentage of expected working hours completed")
            
            # Employee timeline
            emp_data['date'] = pd.to_datetime(emp_data['date'])
            fig_timeline = px.scatter(
                emp_data,
                x='date',
                y='device_name',
                color='status',
                title=f"Attendance Timeline - {selected_employee}",
                color_discrete_map={
                    'Present': '#2ecc71',
                    'Absent': '#e74c3c',
                    'Incomplete': '#f39c12',
                    'Holiday': '#95a5a6'
                },
                hover_data=['day_name', 'working_hours', 'check_in', 'check_out']
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Detailed records with enhanced display
            st.subheader(f"📋 Detailed Records - {selected_employee}")
            
            # Add summary information
            st.info(f"📊 **Summary**: {present_days} present, {absent_days} absent, {incomplete_days} incomplete out of {working_days} working days ({holiday_days} holidays excluded)")
            
            display_columns = ['date', 'day_name', 'device_name', 'check_in', 'check_out', 'working_time', 'working_hours', 'status']
            
            # Style the dataframe based on status with better contrast
            def style_status_row(row):
                if row['status'] == 'Present':
                    return ['background-color: #d4edda; color: #155724; font-weight: normal'] * len(row)
                elif row['status'] == 'Absent':
                    return ['background-color: #f8d7da; color: #721c24; font-weight: normal'] * len(row)
                elif row['status'] == 'Incomplete':
                    return ['background-color: #fff3cd; color: #856404; font-weight: normal'] * len(row)
                elif row['status'] == 'Holiday':
                    return ['background-color: #e2e3e5; color: #6c757d; font-weight: normal'] * len(row)
                else:
                    return ['background-color: #ffffff; color: #2c3e50'] * len(row)
            
            styled_emp_data = emp_data[display_columns].style.apply(style_status_row, axis=1)
            st.dataframe(styled_emp_data, use_container_width=True)
    
    with tab4:
        st.subheader("📅 Multi-Device Trends")
        
        # Daily trends by device (exclude holidays from attendance rate calculation)
        working_df = df[df['status'] != 'Holiday']
        daily_trends = working_df.groupby(['date', 'device_name']).agg({
            'status': lambda x: (x == 'Present').sum(),
            'user_name': 'nunique'
        }).reset_index()
        daily_trends.columns = ['date', 'device_name', 'present_count', 'total_employees']
        daily_trends['attendance_rate'] = (daily_trends['present_count'] / daily_trends['total_employees'] * 100)
        daily_trends['date'] = pd.to_datetime(daily_trends['date'])
        
        # Show holiday information
        holiday_data = df[df['status'] == 'Holiday']
        if not holiday_data.empty:
            st.info(f"🏖️ **Holiday Days Excluded from Trends**: {len(holiday_data['date'].unique())} days")
            holiday_dates = sorted(holiday_data['date'].unique())
            st.write("**Holiday Dates:** " + ", ".join(holiday_dates))
        
        # Multi-line chart
        fig_trends = px.line(
            daily_trends,
            x='date',
            y='attendance_rate',
            color='device_name',
            title="Daily Attendance Rate Trends by Device (Excluding Holidays)",
            labels={'attendance_rate': 'Attendance Rate (%)'}
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
        # Trends table with enhanced styling
        st.subheader("📈 Daily Trends Data (Working Days Only)")
        trends_display = daily_trends.copy()
        trends_display['date'] = trends_display['date'].dt.strftime('%Y-%m-%d')
        trends_display['attendance_rate'] = trends_display['attendance_rate'].round(1).astype(str) + '%'
        styled_trends = style_trends_table(trends_display)
        st.info("📅 **Daily Trends** - Track attendance patterns across devices over time")
        st.dataframe(styled_trends, use_container_width=True)
    
    with tab5:
        st.subheader("📊 Raw Multi-Device Data")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            device_filter = st.multiselect("Filter by Device:", df['device_name'].unique())
        with col2:
            user_filter = st.multiselect("Filter by User:", df['user_name'].unique())
        with col3:
            status_filter = st.multiselect("Filter by Status:", df['status'].unique())
        
        # Apply filters
        filtered_df = df.copy()
        if device_filter:
            filtered_df = filtered_df[filtered_df['device_name'].isin(device_filter)]
        if user_filter:
            filtered_df = filtered_df[filtered_df['user_name'].isin(user_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        
        # Style the dataframe to highlight different statuses with enhanced formatting
        def highlight_status(row):
            if row['status'] == 'Present':
                return ['background-color: #d4edda; color: #155724; font-weight: bold'] * len(row)
            elif row['status'] == 'Absent':
                return ['background-color: #f8d7da; color: #721c24; font-weight: bold'] * len(row)
            elif row['status'] == 'Incomplete':
                return ['background-color: #fff3cd; color: #856404; font-weight: bold'] * len(row)
            elif row['status'] == 'Holiday':
                return ['background-color: #e2e3e5; color: #6c757d; font-weight: bold'] * len(row)
            else:
                return ['background-color: #f8f9fa; color: #2c3e50'] * len(row)
        
        styled_df = filtered_df.style.apply(highlight_status, axis=1)
        
        # Enhanced table styling with better headers
        styled_df = styled_df.set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', '#495057'), 
                                              ('color', 'white'), 
                                              ('font-weight', 'bold'),
                                              ('text-align', 'center'),
                                              ('border', '1px solid #343a40')]},
            {'selector': 'tbody td', 'props': [('border', '1px solid #dee2e6'),
                                              ('text-align', 'center'),
                                              ('padding', '8px')]},
        ])
        
        st.info("🎨 **Color Legend:** 🟢 Present | 🔴 Absent | 🟡 Incomplete | ⚪ Holiday")
        st.dataframe(styled_df, use_container_width=True)
        
        # Filtered data download
        if not filtered_df.equals(df):
            csv_filtered = filtered_df.to_csv(index=False)
            st.download_button(
                label="📄 Download Filtered Data",
                data=csv_filtered,
                file_name=f"filtered_attendance_data.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
