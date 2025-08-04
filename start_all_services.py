#!/usr/bin/env python3
"""
BiometricFlow-ZK Service Orchestrator
Starts all services in the correct order with proper token authentication
"""
import os
import sys
import time
import subprocess
import threading
import requests
from pathlib import Path

class ServiceOrchestrator:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.services = {}
        
    def check_environment_files(self):
        """Check if all environment files exist"""
        required_files = [
            "place_backend.env",
            "unified_gateway.env", 
            "frontend.env",
            "backend_places_config.json"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print("❌ Missing environment files:")
            for file in missing_files:
                print(f"   - {file}")
            print("\n🔧 Run this command to generate them:")
            print("   python generate_keys.py")
            return False
        
        print("✅ All environment files found")
        return True
    
    def start_service(self, service_name, script_name, port, wait_time=10):
        """Start a service and wait for it to be ready"""
        print(f"\n🚀 Starting {service_name}...")
        
        script_path = self.project_root / script_name
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False
        
        try:
            # Start the service in a separate process
            process = subprocess.Popen([
                sys.executable, str(script_path)
            ], cwd=self.project_root)
            
            self.services[service_name] = process
            
            # Wait for service to start
            print(f"⏳ Waiting for {service_name} to start on port {port}...")
            
            for i in range(wait_time):
                try:
                    response = requests.get(f"http://localhost:{port}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ {service_name} is ready!")
                        return True
                except:
                    pass
                time.sleep(1)
                print(f"   Waiting... ({i+1}/{wait_time})")
            
            print(f"⚠️ {service_name} might not be fully ready yet, continuing...")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {service_name}: {e}")
            return False
    
    def test_authentication_flow(self):
        """Test the complete authentication flow"""
        print("\n🔐 Testing Authentication Flow...")
        
        try:
            # Test 1: Frontend getting token from Gateway
            print("1️⃣ Testing Frontend → Gateway authentication...")
            
            # Load the frontend API key
            frontend_env = self.project_root / "frontend.env"
            frontend_api_key = None
            
            with open(frontend_env, 'r') as f:
                for line in f:
                    if line.startswith('FRONTEND_API_KEY='):
                        frontend_api_key = line.split('=', 1)[1].strip()
                        break
            
            if not frontend_api_key:
                print("❌ Frontend API key not found")
                return False
            
            # Request token from gateway
            response = requests.post(
                "http://localhost:9000/auth/frontend/token",
                headers={"Authorization": f"Bearer {frontend_api_key}"},
                timeout=5
            )
            
            if response.status_code == 200:
                token_data = response.json()
                if token_data.get("success"):
                    print("✅ Frontend successfully authenticated with Gateway")
                    frontend_token = token_data["data"]["access_token"]
                    
                    # Test 2: Use frontend token to access gateway data
                    print("2️⃣ Testing Frontend token usage...")
                    
                    response = requests.get(
                        "http://localhost:9000/devices/all",
                        headers={"Authorization": f"Bearer {frontend_token}"},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        print("✅ Frontend token works for accessing Gateway data")
                        return True
                    else:
                        print(f"❌ Frontend token failed: {response.status_code}")
                else:
                    print(f"❌ Token request failed: {token_data}")
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
        
        return False
    
    def show_service_status(self):
        """Show status of all services"""
        print("\n📊 Service Status:")
        print("=" * 50)
        
        services_info = [
            ("Place Backend", "http://localhost:8000/health", "8000"),
            ("Unified Gateway", "http://localhost:9000/health", "9000"),
            ("Frontend", "http://localhost:8501", "8501")
        ]
        
        for name, url, port in services_info:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {name:<15} - Running on port {port}")
                else:
                    print(f"⚠️ {name:<15} - Responding but status {response.status_code}")
            except:
                print(f"❌ {name:<15} - Not responding")
    
    def show_access_urls(self):
        """Show access URLs for all services"""
        print("\n🌐 Access URLs:")
        print("=" * 50)
        print("📍 Place Backend API:     http://localhost:8000")
        print("🌐 Unified Gateway API:   http://localhost:9000")
        print("💻 Frontend Application:  http://localhost:8501")
        print("📖 Gateway Documentation: http://localhost:9000/docs")
        print("📖 Place Documentation:   http://localhost:8000/docs")
    
    def cleanup(self):
        """Stop all services"""
        print("\n🛑 Stopping all services...")
        for service_name, process in self.services.items():
            try:
                process.terminate()
                print(f"   Stopped {service_name}")
            except:
                pass
    
    def run(self):
        """Run the complete service orchestration"""
        print("🚀 BiometricFlow-ZK Service Orchestrator")
        print("=" * 50)
        
        # Check environment files
        if not self.check_environment_files():
            return False
        
        try:
            # Start services in order
            if not self.start_service("Place Backend", "start_place_backend.py", 8000, 15):
                return False
            
            if not self.start_service("Unified Gateway", "start_unified_gateway.py", 9000, 15):
                return False
            
            # Test authentication before starting frontend
            if self.test_authentication_flow():
                print("✅ Authentication flow verified!")
            else:
                print("⚠️ Authentication test failed, but continuing...")
            
            # Start frontend
            print("\n🚀 Starting Frontend...")
            print("📱 The frontend will open in your browser automatically")
            print("🔗 Or visit: http://localhost:8501")
            
            # Start frontend in a separate process
            frontend_script = self.project_root / "start_frontend.py"
            frontend_process = subprocess.Popen([
                sys.executable, str(frontend_script)
            ], cwd=self.project_root)
            
            self.services["Frontend"] = frontend_process
            
            # Show final status
            time.sleep(5)
            self.show_service_status()
            self.show_access_urls()
            
            print("\n✅ All services started successfully!")
            print("🔑 Authentication Flow:")
            print("   1. Frontend requests token from Unified Gateway")
            print("   2. Unified Gateway requests tokens from Place Backends")
            print("   3. All communication is now token-based and secure")
            print("\n🛑 Press Ctrl+C to stop all services")
            
            # Wait for interruption
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested...")
                
        except Exception as e:
            print(f"❌ Orchestration error: {e}")
        finally:
            self.cleanup()
        
        return True

def main():
    orchestrator = ServiceOrchestrator()
    success = orchestrator.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
