#!/usr/bin/env python3
"""
API Access Test Script for BiometricFlow-ZK
Tests all available endpoints with proper authentication
"""

import requests
import os
import sys
import json
from datetime import datetime

# Configuration
API_KEY = None  # Will be loaded from environment or user input
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def load_api_key():
    """Load API key from environment or prompt user"""
    global API_KEY
    
    # Try to load from environment
    API_KEY = os.getenv("MAIN_API_KEY")
    
    if not API_KEY:
        print("🔑 No MAIN_API_KEY found in environment.")
        print("You can either:")
        print("1. Set environment variable: set MAIN_API_KEY=your_key_here")
        print("2. Enter the API key now")
        print()
        
        # Generate a key for user
        try:
            import secrets
            suggested_key = secrets.token_urlsafe(32)
            print(f"💡 Suggested secure API key: {suggested_key}")
            print()
        except:
            pass
            
        API_KEY = input("Enter your API key: ").strip()
        
    if not API_KEY or len(API_KEY) < 16:
        print("❌ Invalid API key. Must be at least 16 characters.")
        sys.exit(1)
        
    print(f"✅ Using API key: {API_KEY[:8]}...{API_KEY[-4:]}")

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test an API endpoint with proper error handling"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "BiometricFlow-Test-Client/1.0"
    }
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print(f"📡 Testing: {method} {endpoint}")
        if description:
            print(f"   📝 {description}")
            
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
            
        # Check response
        if response.status_code == 200:
            print(f"   ✅ Success: {response.status_code}")
            try:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    # Pretty print first few keys
                    preview = {k: v for i, (k, v) in enumerate(data.items()) if i < 3}
                    print(f"   📄 Data preview: {json.dumps(preview, indent=2)[:100]}...")
                elif isinstance(data, list) and len(data) > 0:
                    print(f"   📄 List with {len(data)} items, first item: {str(data[0])[:50]}...")
                else:
                    print(f"   📄 Response: {str(data)[:100]}...")
            except:
                print(f"   📄 Response: {response.text[:100]}...")
        elif response.status_code == 401:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   💡 Check your API key is correct")
        elif response.status_code == 403:
            print(f"   ❌ Forbidden: {response.status_code}")
            print(f"   💡 API key may be invalid or insufficient permissions")
        elif response.status_code == 429:
            print(f"   ⚠️  Rate limited: {response.status_code}")
            print(f"   💡 Too many requests, wait a moment")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            print(f"   📄 Response: {response.text[:100]}...")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - Backend not running?")
        print(f"   💡 Start backend: python src/biometric_flow/backend/place_backend.py")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timeout after {TIMEOUT}s")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_all_endpoints():
    """Test all available API endpoints"""
    
    print("🔍 Testing BiometricFlow-ZK API Endpoints")
    print(f"📡 Base URL: {BASE_URL}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    endpoints = [
        # Core endpoints
        ("/", "GET", None, "Root endpoint - basic system info"),
        ("/health", "GET", None, "Health check - system status"),
        ("/health/full", "GET", None, "Detailed health information"),
        
        # Device management
        ("/devices", "GET", None, "List all configured devices"),
        ("/device/info", "GET", None, "Get device information"),
        
        # User management
        ("/users", "GET", None, "Get users from device"),
        ("/users/all", "GET", None, "Get all users from all devices"),
        
        # Attendance data
        ("/attendance", "GET", None, "Get attendance records"),
        ("/attendance/all", "GET", None, "Get all attendance records"),
        ("/attendance/summary", "GET", None, "Get attendance summary"),
        ("/attendance/summary/all", "GET", None, "Get complete attendance summary"),
        
        # Holiday management
        ("/holidays", "GET", None, "Get holiday information"),
        ("/holidays/suggestions", "GET", None, "Get holiday suggestions"),
    ]
    
    successful = 0
    total = len(endpoints)
    
    for endpoint, method, data, description in endpoints:
        print()
        success = test_endpoint(endpoint, method, data, description)
        if success:
            successful += 1
    
    print()
    print("=" * 60)
    print(f"📊 Test Results: {successful}/{total} endpoints accessible")
    
    if successful == total:
        print("🎉 All endpoints working perfectly!")
    elif successful > 0:
        print("⚠️  Some endpoints working - check authentication and backend status")
    else:
        print("❌ No endpoints accessible - check configuration")
        print()
        print("🔧 Troubleshooting steps:")
        print("1. Ensure backend is running: python src/biometric_flow/backend/place_backend.py")
        print("2. Check API key is set correctly")
        print("3. Verify .env file configuration")
        print("4. Check firewall/network settings")
    
    return successful == total

def generate_api_keys():
    """Generate secure API keys for the user"""
    print("🔑 Generating secure API keys...")
    
    try:
        import secrets
        
        main_key = secrets.token_urlsafe(32)
        backend_key = secrets.token_urlsafe(32)
        frontend_key = secrets.token_urlsafe(32)
        jwt_secret = secrets.token_urlsafe(32)
        
        print("\n📋 Copy these to your .env file:")
        print("=" * 50)
        print(f"MAIN_API_KEY={main_key}")
        print(f"BACKEND_API_KEY={backend_key}")
        print(f"FRONTEND_API_KEY={frontend_key}")
        print(f"JWT_SECRET={jwt_secret}")
        print("=" * 50)
        
        return main_key
        
    except ImportError:
        print("❌ Cannot generate keys - 'secrets' module not available")
        return None

def main():
    """Main test function"""
    print("🚀 BiometricFlow-ZK API Access Test")
    print("=" * 40)
    
    # Check if user wants to generate keys
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-keys":
        generated_key = generate_api_keys()
        if generated_key:
            use_generated = input("\nUse the generated MAIN_API_KEY for testing? (y/n): ").lower()
            if use_generated.startswith('y'):
                global API_KEY
                API_KEY = generated_key
                print(f"✅ Using generated key: {API_KEY[:8]}...{API_KEY[-4:]}")
                print()
                test_all_endpoints()
        return
    
    # Load API key
    load_api_key()
    print()
    
    # Run tests
    success = test_all_endpoints()
    
    if not success:
        print("\n🆘 Need help? Run with --generate-keys to create secure API keys:")
        print("python test_api_access.py --generate-keys")

if __name__ == "__main__":
    main()
