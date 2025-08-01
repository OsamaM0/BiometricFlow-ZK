import requests
import json
from datetime import datetime, timedelta
import sys

def test_unified_system():
    """Test the complete unified multi-place fingerprint attendance system"""
    print("🔧 Testing Unified Multi-Place Fingerprint Attendance System")
    print("=" * 70)
    
    # Test configurations
    unified_gateway_url = "http://localhost:9000"
    place_backends = {
        "Place_1_BackOffice": "http://localhost:8000",
        "Place_2_ShowRoom": "http://localhost:8001", 
        "Place_3_Warehouse": "http://localhost:8002"
    }
    frontend_url = "http://localhost:8501"
    
    # Test 1: Unified Gateway Health
    print("\n1️⃣ Testing Unified Gateway Health...")
    try:
        response = requests.get(f"{unified_gateway_url}/health", timeout=15)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Gateway Status: {health_data.get('status', 'unknown')}")
            print(f"   📍 Total Places: {health_data.get('total_places', 0)}")
            print(f"   🟢 Healthy Places: {health_data.get('healthy_places', 0)}")
            
            for place, health in health_data.get('place_health', {}).items():
                status_icon = "✅" if health['status'] == 'healthy' else "❌"
                print(f"   {status_icon} {place}: {health['status']} ({health.get('location', 'Unknown')})")
        else:
            print(f"   ❌ Gateway Health Check Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Gateway Health Check Error: {e}")
        return False
    
    # Test 2: Places Endpoint
    print("\n2️⃣ Testing Places Discovery...")
    try:
        response = requests.get(f"{unified_gateway_url}/places", timeout=5)
        if response.status_code == 200:
            places_data = response.json()
            print(f"   ✅ Places Retrieved: {places_data.get('total_places', 0)}")
            for place in places_data.get('places', []):
                print(f"   📍 {place['name']}: {place['location']} - Devices: {len(place.get('devices', []))}")
        else:
            print(f"   ❌ Places Discovery Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Places Discovery Error: {e}")
    
    # Test 3: Unified Devices
    print("\n3️⃣ Testing Unified Device Discovery...")
    try:
        response = requests.get(f"{unified_gateway_url}/devices/all", timeout=10)
        if response.status_code == 200:
            devices_data = response.json()
            print(f"   ✅ Total Devices: {devices_data.get('total_devices', 0)}")
            print(f"   🏢 Backend Sources: {len(devices_data.get('backend_sources', []))}")
            print(f"   📍 Places: {devices_data.get('places', [])}")
            
            for device in devices_data.get('devices', []):
                status_icon = "✅" if device.get('is_connected') else "❌"
                print(f"   {status_icon} {device.get('device_name', 'Unknown')} @ {device.get('place_location', 'Unknown')}")
        else:
            print(f"   ❌ Device Discovery Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Device Discovery Error: {e}")
    
    # Test 4: Individual Place Backends
    print("\n4️⃣ Testing Individual Place Backends...")
    for place_name, place_url in place_backends.items():
        try:
            response = requests.get(f"{place_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {place_name}: Running on {place_url}")
                
                # Test devices endpoint for this place
                devices_response = requests.get(f"{place_url}/devices", timeout=5)
                if devices_response.status_code == 200:
                    devices_data = devices_response.json()
                    device_count = len(devices_data.get('devices', []))
                    print(f"      📱 Devices: {device_count}")
            else:
                print(f"   ❌ {place_name}: Failed (HTTP {response.status_code})")
        except Exception as e:
            print(f"   ⚠️ {place_name}: Not reachable ({e})")
    
    # Test 5: Place-Specific Endpoints
    print("\n5️⃣ Testing Place-Specific Endpoints...")
    for place_name in ["Place_1_BackOffice", "Place_2_ShowRoom", "Place_3_Warehouse"]:
        try:
            response = requests.get(f"{unified_gateway_url}/place/{place_name}/devices", timeout=5)
            if response.status_code == 200:
                data = response.json()
                device_count = len(data.get('devices', []))
                print(f"   ✅ {place_name}: {device_count} devices")
            else:
                print(f"   ❌ {place_name}: Failed (HTTP {response.status_code})")
        except Exception as e:
            print(f"   ⚠️ {place_name}: Error ({e})")
    
    # Test 6: Frontend Accessibility
    print("\n6️⃣ Testing Frontend Accessibility...")
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Frontend accessible at {frontend_url}")
        else:
            print(f"   ❌ Frontend Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Frontend: {e}")
    
    # Test 7: Sample Attendance Query
    print("\n7️⃣ Testing Sample Attendance Query...")
    try:
        # Test with date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        response = requests.get(f"{unified_gateway_url}/attendance/all", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Attendance Query Successful")
            print(f"   📊 Records: {data.get('total_records', 0)}")
            print(f"   🏢 Sources: {len(data.get('backend_sources', []))}")
        else:
            print(f"   ❌ Attendance Query Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Attendance Query Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ System Test Complete!")
    print("\n🌐 Access Points:")
    print(f"   • Unified Gateway: {unified_gateway_url}")
    print(f"   • Frontend UI: {frontend_url}")
    print(f"   • Place 1 Backend: {place_backends['Place_1_BackOffice']}")
    print(f"   • Place 2 Backend: {place_backends['Place_2_ShowRoom']}")
    print(f"   • Place 3 Backend: {place_backends['Place_3_Warehouse']}")
    
    return True

if __name__ == "__main__":
    test_unified_system()
