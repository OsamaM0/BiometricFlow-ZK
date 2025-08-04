#!/usr/bin/env python3
"""
Frontend Startup Script
Starts the frontend with proper environment loading
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print(f"💻 Starting Frontend from: {script_dir}")
    
    # Check if environment file exists
    env_file = script_dir / "frontend.env"
    if not env_file.exists():
        print(f"❌ Environment file not found: {env_file}")
        print("Please run: python generate_keys.py")
        sys.exit(1)
    
    print(f"✅ Using environment file: {env_file}")
    
    # Set the frontend file path
    frontend_file = script_dir / "src" / "biometric_flow" / "frontend" / "app.py"
    
    if not frontend_file.exists():
        print(f"❌ Frontend file not found: {frontend_file}")
        sys.exit(1)
    
    print(f"📄 Frontend file: {frontend_file}")
    print(f"🔗 Backend URL: http://localhost:9000")
    print(f"🌐 Frontend URL: http://localhost:8501")
    
    try:
        # Start streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(frontend_file),
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Frontend shutdown requested")
    except Exception as e:
        print(f"❌ Frontend startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
