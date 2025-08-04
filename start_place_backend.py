#!/usr/bin/env python3
"""
Place Backend Startup Script
Starts the place backend with proper environment loading
"""
import os
import sys
import uvicorn
from pathlib import Path

def main():
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print(f"🚀 Starting Place Backend from: {script_dir}")
    
    # Check if environment file exists
    env_file = script_dir / "place_backend.env"
    if not env_file.exists():
        print(f"❌ Environment file not found: {env_file}")
        print("Please run: python generate_keys.py")
        sys.exit(1)
    
    print(f"✅ Using environment file: {env_file}")
    
    # Add the src directory to Python path
    src_path = script_dir / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Import the backend module
        from biometric_flow.backend.place_backend import app
        
        # Load config to show info
        from dotenv import load_dotenv
        load_dotenv(dotenv_path='place_backend.env')
        
        place_name = os.getenv("PLACE_NAME", "Unknown Place")
        place_location = os.getenv("PLACE_LOCATION", "Unknown Location")
        backend_port = int(os.getenv("SERVICE_PORT", "8000"))
        backend_host = os.getenv("SERVICE_HOST", "0.0.0.0")
        
        print(f"🏢 Place: {place_name}")
        print(f"📍 Location: {place_location}")
        print(f"🔌 Port: {backend_port}")
        print(f"� Host: {backend_host}")
        
        # Start the server
        uvicorn.run(
            app,
            host=backend_host,
            port=backend_port,
            reload=False,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
