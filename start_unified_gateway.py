#!/usr/bin/env python3
"""
Unified Gateway Startup Script
Starts the unified gateway with proper environment loading
"""
import os
import sys
import uvicorn
from pathlib import Path

def main():
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print(f"🌐 Starting Unified Gateway from: {script_dir}")
    
    # Check if environment file exists
    env_file = script_dir / "unified_gateway.env"
    if not env_file.exists():
        print(f"❌ Environment file not found: {env_file}")
        print("Please run: python generate_keys.py")
        sys.exit(1)
    
    print(f"✅ Using environment file: {env_file}")
    
    # Add the src directory to Python path
    src_path = script_dir / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Import the gateway module
        from biometric_flow.backend.unified_gateway import app
        
        # Load config to show info
        from dotenv import load_dotenv
        load_dotenv(dotenv_path='unified_gateway.env')
        
        gateway_port = int(os.getenv("SERVICE_PORT", "9000"))
        gateway_host = os.getenv("SERVICE_HOST", "0.0.0.0")
        
        print(f"🔗 Gateway Port: {gateway_port}")
        print(f"🌐 Host: {gateway_host}")
        
        # Start the server
        uvicorn.run(
            app,
            host=gateway_host,
            port=gateway_port,
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
