#!/usr/bin/env python3
"""
Test the authentication flow between services
"""
import requests
import json
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv(dotenv_path='place_backend.env')
    place_api_key = os.getenv('MAIN_API_KEY')
    
    load_dotenv(dotenv_path='unified_gateway.env')
    gateway_api_key = os.getenv('MAIN_API_KEY')
    frontend_api_key = os.getenv('FRONTEND_API_KEY')
    
    load_dotenv(dotenv_path='frontend.env')
    frontend_key = os.getenv('FRONTEND_API_KEY')
    
    print("🔐 Testing BiometricFlow-ZK Authentication Flow")
    print("=" * 50)
    
    # Test 1: Place Backend Health Check
    print("\n1️⃣ Testing Place Backend health check...")
    try:
        response = requests.get(
            "http://localhost:8000/health",
            headers={"Authorization": f"Bearer {place_api_key}"},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Place Backend is healthy and accepting requests")
        else:
            print(f"❌ Place Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Place Backend connection failed: {e}")
        return False
    
    # Test 2: Unified Gateway Health Check
    print("\n2️⃣ Testing Unified Gateway health check...")
    try:
        response = requests.get(
            "http://localhost:9000/health",
            headers={"Authorization": f"Bearer {gateway_api_key}"},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Unified Gateway is healthy and accepting requests")
        else:
            print(f"❌ Unified Gateway health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Unified Gateway connection failed: {e}")
        return False
    
    # Test 3: Frontend Token Request
    print("\n3️⃣ Testing Frontend token request from Gateway...")
    try:
        response = requests.post(
            "http://localhost:9000/auth/frontend/token",
            headers={"Authorization": f"Bearer {frontend_api_key}"},
            timeout=5
        )
        
        if response.status_code == 200:
            token_data = response.json()
            if token_data.get("success", False):
                frontend_token = token_data["data"]["access_token"]
                print("✅ Frontend successfully obtained access token from Gateway")
                
                # Test 4: Use Frontend token to access Gateway data
                print("\n4️⃣ Testing Frontend token usage for data access...")
                
                response = requests.get(
                    "http://localhost:9000/devices/all",
                    headers={"Authorization": f"Bearer {frontend_token}"},
                    timeout=5
                )
                
                if response.status_code == 200:
                    devices_data = response.json()
                    print("✅ Frontend token successfully accesses Gateway data")
                    print(f"   Found {len(devices_data.get('data', []))} devices")
                    return True
                else:
                    print(f"❌ Frontend token access failed: {response.status_code}")
            else:
                print(f"❌ Token request failed: {token_data}")
        else:
            print(f"❌ Frontend authentication failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend authentication test failed: {e}")
    
    return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Authentication Flow Test: PASSED")
        print("✅ All services are working with proper token authentication")
        print("🚀 Ready to start the frontend!")
    else:
        print("\n❌ Authentication Flow Test: FAILED")
        print("🔧 Please check the service logs and configuration")
    
    print("\n🔗 Service URLs:")
    print("   Place Backend:     http://localhost:8000")
    print("   Unified Gateway:   http://localhost:9000")
    print("   Frontend (when started): http://localhost:8501")
