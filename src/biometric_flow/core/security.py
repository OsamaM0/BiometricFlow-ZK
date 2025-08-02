"""
Enhanced Security Module for BiometricFlow-ZK
Provides powerful but simple security features for NGROK and production deployment
"""

import os
import secrets
import hashlib
import hmac
import time
import jwt
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Set, Union
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import ipaddress

logger = logging.getLogger(__name__)

# Security Configuration
class SecurityConfig:
    def __init__(self):
        # API Key Authentication
        self.api_keys = self._load_api_keys()
        
        # JWT Configuration
        self.jwt_secret = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
        self.jwt_algorithm = "HS256"
        self.jwt_expire_hours = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
        
        # Rate limiting configuration (enhanced for NGROK)
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))  # Reduced for NGROK
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
        
        # CORS configuration for NGROK
        self.allowed_origins = self._get_allowed_origins()
        
        # Request validation
        self.max_request_size = int(os.getenv("MAX_REQUEST_SIZE", "5242880"))  # 5MB for NGROK
        
        # Enhanced security headers for NGROK
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",  # Less restrictive for embedded usage
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Powered-By": "BiometricFlow-Secure",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        # NGROK specific settings
        self.ngrok_enabled = os.getenv("NGROK_ENABLED", "false").lower() == "true"
        self.ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
        
        # Blocked patterns for security
        self.blocked_patterns = [
            r'(\.\./|\.\.\\)',  # Path traversal
            r'<script.*?>',     # XSS attempts
            r'union.*select',   # SQL injection
            r'drop\s+table',    # SQL injection
            r'exec\(',          # Code execution
        ]
    
        # IP Allowlist for enhanced security
        self.allowed_ips = self._get_allowed_ips()
        
        
    def _load_api_keys(self) -> Set[str]:
        """Load API keys from environment or generate secure defaults"""
        api_keys = set()
        
        # Load from environment
        env_keys = os.getenv("API_KEYS", "").split(",")
        for key in env_keys:
            if key.strip() and len(key.strip()) >= 16:  # Minimum key length
                api_keys.add(key.strip())
        
        # Generate secure default keys if none provided
        if not api_keys:
            # Main API key
            main_key = os.getenv("MAIN_API_KEY")
            if not main_key:
                main_key = secrets.token_urlsafe(32)
                logger.warning(f"Generated MAIN API key: {main_key}")
                logger.warning("Set MAIN_API_KEY environment variable for production")
            api_keys.add(main_key)
            
            # Backend communication key
            backend_key = os.getenv("BACKEND_API_KEY")
            if not backend_key:
                backend_key = secrets.token_urlsafe(32)
                logger.warning(f"Generated BACKEND API key: {backend_key}")
                logger.warning("Set BACKEND_API_KEY environment variable for production")
            api_keys.add(backend_key)
        
        return api_keys
    
    def _get_allowed_origins(self) -> List[str]:
        """Get allowed origins for CORS - enhanced NGROK support"""
        origins = []
        
        # Default local origins
        default_origins = [
            "http://localhost:8501", "https://localhost:8501",
            "http://localhost:9000", "https://localhost:9000",
            "http://127.0.0.1:8501", "https://127.0.0.1:8501",
            "http://127.0.0.1:9000", "https://127.0.0.1:9000"
        ]
        origins.extend(default_origins)
        
        # NGROK origins from environment (multiple support)
        ngrok_urls = os.getenv("NGROK_URLS", "").split(",")
        for ngrok_url in ngrok_urls:
            if ngrok_url.strip():
                url = ngrok_url.strip()
                origins.append(url)
                # Add both http and https versions
                if url.startswith("http://"):
                    origins.append(url.replace("http://", "https://"))
                elif url.startswith("https://"):
                    origins.append(url.replace("https://", "http://"))
        
        # Single NGROK URL (backward compatibility)
        ngrok_url = os.getenv("NGROK_URL")
        if ngrok_url:
            origins.append(ngrok_url)
            if ngrok_url.startswith("http://"):
                origins.append(ngrok_url.replace("http://", "https://"))
            elif ngrok_url.startswith("https://"):
                origins.append(ngrok_url.replace("https://", "http://"))
        
        # Additional custom origins
        custom_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
        for origin in custom_origins:
            if origin.strip():
                origins.append(origin.strip())
        
        # Allow all origins in development mode only
        if os.getenv("ENVIRONMENT") == "development":
            origins.append("*")
        
        return list(set(origins))  # Remove duplicates
    
    def _get_allowed_ips(self) -> List[str]:
        """Get allowed IP addresses/ranges for enhanced security"""
        allowed_ips = []
        
        # Default allowed IPs (local)
        default_ips = ["127.0.0.1", "::1", "localhost"]
        allowed_ips.extend(default_ips)
        
        # Custom allowed IPs from environment
        custom_ips = os.getenv("ALLOWED_IPS", "").split(",")
        for ip in custom_ips:
            if ip.strip():
                allowed_ips.append(ip.strip())
        
        # NGROK IP ranges (if enabled)
        if self.ngrok_enabled:
            # Common NGROK IP ranges (update as needed)
            ngrok_ranges = [
                "3.20.0.0/16", "3.21.0.0/16", "3.22.0.0/16", "3.23.0.0/16",
                "13.59.0.0/16", "18.216.0.0/16", "18.217.0.0/16"
            ]
            allowed_ips.extend(ngrok_ranges)
        
        return allowed_ips

# Global security configuration
security_config = SecurityConfig()

# Rate limiting storage (in-memory for simplicity)
rate_limit_storage: Dict[str, List[float]] = {}

# Blocked requests cache
blocked_ips_cache: Dict[str, float] = {}

# Security bearer scheme
security_bearer = HTTPBearer(auto_error=False)

def create_jwt_token(payload: Dict) -> str:
    """Create JWT token for secure communication"""
    payload.update({
        "exp": datetime.utcnow() + timedelta(hours=security_config.jwt_expire_hours),
        "iat": datetime.utcnow(),
        "iss": "BiometricFlow-ZK"
    })
    return jwt.encode(payload, security_config.jwt_secret, algorithm=security_config.jwt_algorithm)

def verify_jwt_token(token: str) -> Optional[Dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, security_config.jwt_secret, algorithms=[security_config.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
        return None

def is_safe_request(request_data: str) -> bool:
    """Check if request contains malicious patterns"""
    request_lower = request_data.lower()
    for pattern in security_config.blocked_patterns:
        if re.search(pattern, request_lower, re.IGNORECASE):
            return False
    return True

def is_ip_allowed(client_ip: str) -> bool:
    """Check if IP is in allowlist"""
    if not security_config.allowed_ips:
        return True  # No restrictions if no IPs specified
    
    # Check exact matches
    if client_ip in security_config.allowed_ips:
        return True
    
    # Check IP ranges
    try:
        client_addr = ipaddress.ip_address(client_ip)
        for allowed in security_config.allowed_ips:
            try:
                if "/" in allowed:  # CIDR notation
                    network = ipaddress.ip_network(allowed, strict=False)
                    if client_addr in network:
                        return True
                else:  # Single IP
                    if client_addr == ipaddress.ip_address(allowed):
                        return True
            except ValueError:
                continue
    except ValueError:
        # Invalid IP format
        return False
    
    return False

def get_client_ip(request: Request) -> str:
    """Get client IP address, considering NGROK and proxy headers"""
    # Check for NGROK forwarded IP (priority order)
    headers_to_check = [
        "X-Forwarded-For",
        "X-Real-IP", 
        "X-Original-Forwarded-For",
        "CF-Connecting-IP",  # Cloudflare
        "True-Client-IP"     # Akamai
    ]
    
    for header in headers_to_check:
        value = request.headers.get(header)
        if value:
            # Handle comma-separated IPs (take first one)
            ip = value.split(",")[0].strip()
            if ip and ip != "unknown":
                return ip
    
    # Fallback to client host
    return request.client.host if request.client else "unknown"

def check_rate_limit(client_ip: str) -> bool:
    """Enhanced rate limiting with IP blocking"""
    current_time = time.time()
    window_start = current_time - security_config.rate_limit_window
    
    # Check if IP is temporarily blocked
    if client_ip in blocked_ips_cache:
        if current_time < blocked_ips_cache[client_ip]:
            return False
        else:
            del blocked_ips_cache[client_ip]
    
    # Clean old entries
    if client_ip in rate_limit_storage:
        rate_limit_storage[client_ip] = [
            timestamp for timestamp in rate_limit_storage[client_ip]
            if timestamp > window_start
        ]
    else:
        rate_limit_storage[client_ip] = []
    
    # Check if rate limit exceeded
    if len(rate_limit_storage[client_ip]) >= security_config.rate_limit_requests:
        # Block IP for 5 minutes on rate limit exceeded
        blocked_ips_cache[client_ip] = current_time + 300
        log_security_event("RATE_LIMIT_EXCEEDED", f"IP blocked for 5 minutes", client_ip)
        return False
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)
    return True

def validate_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)) -> bool:
    """Enhanced API key validation with JWT support"""
    if not credentials:
        # Check if development mode allows requests without API key
        if os.getenv("ENVIRONMENT") == "development" and os.getenv("ALLOW_NO_AUTH", "false").lower() == "true":
            logger.warning("Request without API key - allowed in development mode")
            return True
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required - API key or JWT token needed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Try JWT validation first
    jwt_payload = verify_jwt_token(token)
    if jwt_payload:
        return True
    
    # Fallback to API key validation
    if token in security_config.api_keys:
        return True
    
    # Invalid credentials
    log_security_event("INVALID_AUTH", f"Invalid API key/token attempt", "unknown")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def security_middleware(request: Request, call_next):
    """Enhanced security middleware for NGROK deployment"""
    start_time = time.time()
    
    # Get client IP
    client_ip = get_client_ip(request)
    
    # Skip security for health check endpoints
    if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
        response = await call_next(request)
        for header, value in security_config.security_headers.items():
            response.headers[header] = value
        return response
    
    # IP allowlist check (if configured)
    if security_config.allowed_ips and not is_ip_allowed(client_ip):
        log_security_event("IP_BLOCKED", f"IP not in allowlist", client_ip)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied from this IP address"
        )
    
    # Rate limiting
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )
    
    # Request size validation
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > security_config.max_request_size:
        log_security_event("REQUEST_TOO_LARGE", f"Request size: {content_length}", client_ip)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Request payload too large"
        )
    
    # Content validation for POST/PUT requests
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body and not is_safe_request(body.decode('utf-8', errors='ignore')):
                log_security_event("MALICIOUS_REQUEST", "Blocked malicious request pattern", client_ip)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request contains invalid patterns"
                )
        except Exception:
            pass  # Continue if body reading fails
    
    # Process request
    response = await call_next(request)
    
    # Add security headers
    for header, value in security_config.security_headers.items():
        response.headers[header] = value
    
    # Add NGROK-specific headers
    if security_config.ngrok_enabled:
        response.headers["X-NGROK-Secured"] = "true"
    
    # Add processing time header
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 3))
    
    # Log request (minimal logging for performance)
    if response.status_code >= 400:
        logger.warning(f"Request from {client_ip}: {request.method} {request.url.path} - {response.status_code}")
    else:
        logger.info(f"OK: {client_ip} {request.method} {request.url.path}")
    
    return response

def get_cors_origins() -> List[str]:
    """Get CORS origins for the application"""
    return security_config.allowed_origins

def log_security_event(event_type: str, details: str, client_ip: str = "unknown"):
    """Enhanced security event logging"""
    timestamp = datetime.now().isoformat()
    security_log = {
        "timestamp": timestamp,
        "type": event_type,
        "details": details,
        "client_ip": client_ip,
        "severity": "HIGH" if event_type in ["MALICIOUS_REQUEST", "IP_BLOCKED"] else "MEDIUM"
    }
    
    # Log to console with appropriate level
    if security_log["severity"] == "HIGH":
        logger.error(f"SECURITY ALERT: {security_log}")
    else:
        logger.warning(f"SECURITY EVENT: {security_log}")
    
    # Write to security log file
    try:
        log_file = "logs/security.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} - {event_type} - {client_ip} - {details}\n")
    except Exception as e:
        logger.error(f"Failed to write security log: {e}")

def create_secure_response(data: any, message: str = "Success") -> Dict:
    """Create a standardized secure response"""
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "server_time": int(time.time()),
        "security_level": "secure"
    }

def create_error_response(error: str, status_code: int = 400) -> Dict:
    """Create a standardized error response"""
    return {
        "success": False,
        "error": error,
        "message": "Request failed",
        "timestamp": datetime.now().isoformat(),
        "status_code": status_code,
        "help": "Check API documentation for valid request format"
    }

def generate_secure_session() -> Dict[str, str]:
    """Generate secure session tokens for frontend communication"""
    session_token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(16)
    
    return {
        "session_token": session_token,
        "csrf_token": csrf_token,
        "expires_at": (datetime.now() + timedelta(hours=security_config.jwt_expire_hours)).isoformat()
    }

def validate_session_token(token: str) -> bool:
    """Validate session token (placeholder for session management)"""
    # In a production system, this would validate against a session store
    return len(token) >= 32

# Export functions for backward compatibility
__all__ = [
    'validate_api_key', 'security_middleware', 'get_cors_origins',
    'log_security_event', 'create_secure_response', 'create_error_response',
    'generate_secure_session', 'create_jwt_token', 'verify_jwt_token'
]
