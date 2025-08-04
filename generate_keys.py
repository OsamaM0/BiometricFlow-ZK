#!/usr/bin/env python3
"""
Generate secure API keys for BiometricFlow-ZK services
"""
import secrets
import os
from pathlib import Path

def generate_secure_key(length=32):
    """Generate a secure API key"""
    return secrets.token_urlsafe(length)

def main():
    print("🔐 Generating secure API keys for BiometricFlow-ZK services...")
    print("=" * 60)
    
    # Generate keys for each service
    keys = {
        'MAIN_API_KEY': generate_secure_key(32),
        'UNIFIED_GATEWAY_API_KEY': generate_secure_key(32),
        'PLACE_BACKEND_API_KEY': generate_secure_key(32),
        'FRONTEND_API_KEY': generate_secure_key(32),
        'JWT_SECRET': generate_secure_key(32),
        'UNIFIED_JWT_SECRET': generate_secure_key(32),
        'PLACE_JWT_SECRET': generate_secure_key(32),
        'FRONTEND_JWT_SECRET': generate_secure_key(32),
    }
    
    print("Generated keys:")
    for key_name, key_value in keys.items():
        print(f"{key_name}={key_value}")
    
    print("\n" + "=" * 60)
    print("🔧 Key Assignment for Each Service:")
    print("=" * 60)
    
    print("\n📍 Place Backend (.env):")
    print(f"MAIN_API_KEY={keys['PLACE_BACKEND_API_KEY']}")
    print(f"JWT_SECRET={keys['PLACE_JWT_SECRET']}")
    print(f"UNIFIED_GATEWAY_API_KEY={keys['UNIFIED_GATEWAY_API_KEY']}")
    
    print("\n🌐 Unified Gateway (.env):")
    print(f"MAIN_API_KEY={keys['UNIFIED_GATEWAY_API_KEY']}")
    print(f"JWT_SECRET={keys['UNIFIED_JWT_SECRET']}")
    print(f"PLACE_BACKEND_API_KEY={keys['PLACE_BACKEND_API_KEY']}")
    print(f"FRONTEND_API_KEY={keys['FRONTEND_API_KEY']}")
    
    print("\n💻 Frontend (.env):")
    print(f"MAIN_API_KEY={keys['FRONTEND_API_KEY']}")
    print(f"JWT_SECRET={keys['FRONTEND_JWT_SECRET']}")
    print(f"UNIFIED_GATEWAY_API_KEY={keys['UNIFIED_GATEWAY_API_KEY']}")
    
    # Create updated environment files
    create_env_files(keys)
    
    print("\n✅ Environment files created/updated!")
    print("🚀 You can now start the services in order:")
    print("   1. Place Backend: python src/biometric_flow/backend/place_backend.py")
    print("   2. Unified Gateway: python src/biometric_flow/backend/unified_gateway.py")
    print("   3. Frontend: streamlit run src/biometric_flow/frontend/app.py")

def create_env_files(keys):
    """Create environment files for each service"""
    
    # Place Backend Environment
    place_env_content = f"""# Place Backend Environment Configuration
# Generated automatically with secure keys
# =====================================

# Service Configuration
SERVICE_NAME=place_backend
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
ENVIRONMENT=production

# Place Information
PLACE_NAME=Main Office
PLACE_LOCATION=Building A, Floor 1
PLACE_ID=place_001

# Security Configuration - UNIQUE FOR THIS PLACE
JWT_SECRET={keys['PLACE_JWT_SECRET']}
JWT_EXPIRE_HOURS=24
MAIN_API_KEY={keys['PLACE_BACKEND_API_KEY']}
BACKEND_API_KEY={keys['PLACE_BACKEND_API_KEY']}

# Unified Gateway Communication
UNIFIED_GATEWAY_API_KEY={keys['UNIFIED_GATEWAY_API_KEY']}
UNIFIED_GATEWAY_URL=http://localhost:9000

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:9000,https://localhost:9000
NGROK_ENABLED=false

# Device Configuration
DEVICES_CONFIG_FILE=devices_config.json
DEFAULT_DEVICE_IP=192.168.1.201
DEFAULT_DEVICE_PORT=4370
DEFAULT_DEVICE_PASSWORD=0

# Working Hours Configuration
EXPECTED_WORKING_HOURS=8
LATE_THRESHOLD_MINUTES=15
EARLY_LEAVE_THRESHOLD_MINUTES=30

# Auto-registration with Unified Gateway
AUTO_REGISTER_WITH_UNIFIED=true
REGISTRATION_RETRY_INTERVAL=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=place_backend.log
"""

    # Unified Gateway Environment
    gateway_env_content = f"""# Unified Gateway Environment Configuration
# Generated automatically with secure keys
# =========================================

# Service Configuration
SERVICE_NAME=unified_gateway
SERVICE_PORT=9000
SERVICE_HOST=0.0.0.0
ENVIRONMENT=production

# Security Configuration - UNIQUE FOR GATEWAY
JWT_SECRET={keys['UNIFIED_JWT_SECRET']}
JWT_EXPIRE_HOURS=24
MAIN_API_KEY={keys['UNIFIED_GATEWAY_API_KEY']}
BACKEND_API_KEY={keys['UNIFIED_GATEWAY_API_KEY']}

# Place Backend Communication
PLACE_BACKEND_API_KEY={keys['PLACE_BACKEND_API_KEY']}

# Frontend Communication
FRONTEND_API_KEY={keys['FRONTEND_API_KEY']}
FRONTEND_JWT_EXPIRE_HOURS=8

# Rate Limiting
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW=60

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:8501,https://localhost:8501
NGROK_ENABLED=false

# Backend Places Configuration
BACKEND_PLACES_CONFIG_FILE=backend_places_config.json
AUTO_DISCOVER_PLACES=true
PLACE_HEALTH_CHECK_INTERVAL=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=unified_gateway.log

# Data Aggregation Settings
CACHE_TTL=300
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
"""

    # Frontend Environment
    frontend_env_content = f"""# Frontend Environment Configuration
# Generated automatically with secure keys
# =================================

# Service Configuration
SERVICE_NAME=frontend_app
SERVICE_PORT=8501
SERVICE_HOST=0.0.0.0
ENVIRONMENT=production

# Security Configuration - UNIQUE FOR FRONTEND
JWT_SECRET={keys['FRONTEND_JWT_SECRET']}
FRONTEND_API_KEY={keys['FRONTEND_API_KEY']}
SESSION_TIMEOUT=3600
MAX_REQUEST_SIZE=5242880

# Unified Gateway Communication
UNIFIED_GATEWAY_API_KEY={keys['UNIFIED_GATEWAY_API_KEY']}
BACKEND_URL=http://localhost:9000
REQUEST_TIMEOUT=30

# CORS and Security Headers
ALLOWED_BACKEND_URLS=http://localhost:9000,https://localhost:9000
NGROK_ENABLED=false

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# Data Refresh Settings
DATA_CACHE_TTL=300
AUTO_REFRESH_INTERVAL=60

# UI Configuration
MAX_DEVICES_PER_PAGE=50
DEFAULT_DATE_RANGE_DAYS=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=frontend_app.log
"""

    # Backend places config
    backend_places_config = f"""{{
  "places": {{
    "place_001": {{
      "name": "Main Office",
      "location": "Building A, Floor 1",
      "url": "http://localhost:8000",
      "api_key": "{keys['PLACE_BACKEND_API_KEY']}",
      "enabled": true,
      "health_check_endpoint": "/health",
      "timeout": 30
    }},
    "place_002": {{
      "name": "Branch Office",
      "location": "Building B, Floor 2", 
      "url": "http://localhost:8001",
      "api_key": "{keys['PLACE_BACKEND_API_KEY']}",
      "enabled": false,
      "health_check_endpoint": "/health",
      "timeout": 30
    }}
  }},
  "discovery_settings": {{
    "auto_register": true,
    "health_check_interval": 60,
    "max_retries": 3,
    "retry_delay": 10
  }}
}}"""

    # Write files
    with open('place_backend.env', 'w') as f:
        f.write(place_env_content)
    
    with open('unified_gateway.env', 'w') as f:
        f.write(gateway_env_content)
        
    with open('frontend.env', 'w') as f:
        f.write(frontend_env_content)
        
    with open('backend_places_config.json', 'w') as f:
        f.write(backend_places_config)

if __name__ == "__main__":
    main()
