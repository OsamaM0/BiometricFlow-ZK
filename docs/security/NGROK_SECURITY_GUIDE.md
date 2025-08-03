# 🔒 NGROK Security Deployment Guide

This guide covers the enhanced security features implemented for safe NGROK deployment of BiometricFlow-ZK.

## ⚡ Quick Start Security Setup

### 1. Generate API Keys
```bash
# Generate secure API keys
python -c "import secrets; print('MAIN_API_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('BACKEND_API_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('FRONTEND_API_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your generated keys and NGROK URLs
nano .env
```

### 3. Start Services Securely
```bash
# Start backend with security
ENVIRONMENT=production python src/biometric_flow/backend/place_backend.py

# Start unified gateway with security
ENVIRONMENT=production python src/biometric_flow/backend/unified_gateway.py

# Start frontend with security
ENVIRONMENT=production streamlit run src/biometric_flow/frontend/app.py
```

## 🛡️ Security Features Implemented

### 1. Enhanced Authentication
- **API Key Authentication**: Secure Bearer token authentication
- **JWT Token Support**: Stateless authentication with expiration
- **Multiple Key Support**: Different keys for different services
- **Header Validation**: Multiple authentication methods

### 2. Rate Limiting & DDoS Protection
- **IP-based Rate Limiting**: Configurable requests per minute
- **Automatic IP Blocking**: Temporary blocks for rate limit violations
- **Request Size Limits**: Protection against large payload attacks
- **Connection Timeouts**: Prevents resource exhaustion

### 3. Input Validation & Sanitization
- **Malicious Pattern Detection**: Blocks common attack patterns
- **Content Validation**: Validates POST/PUT request content
- **URL Validation**: Validates allowed backend URLs
- **Parameter Sanitization**: Cleans input parameters

### 4. CORS & Origin Security
- **NGROK Origin Support**: Automatic NGROK URL detection
- **Strict Origin Validation**: Configurable allowed origins
- **Header Security**: Security headers for browser protection
- **Environment-based Configuration**: Different rules for dev/prod

### 5. IP Allowlisting
- **CIDR Range Support**: Allow IP ranges or individual IPs
- **NGROK IP Detection**: Handles NGROK forwarded headers
- **Localhost Support**: Automatic local development support
- **Flexible Configuration**: Environment-based IP rules

### 6. Logging & Monitoring
- **Security Event Logging**: Comprehensive security audit logs
- **Attack Detection**: Logs suspicious activities
- **Performance Monitoring**: Request timing and metrics
- **Error Tracking**: Detailed error logging

## 🚀 NGROK Deployment Steps

### 1. Install NGROK
```bash
# Download and install NGROK
# Visit: https://ngrok.com/download
```

### 2. Setup NGROK Tunnels
```bash
# Backend tunnel (adjust port as needed)
ngrok http 8000 --region us --hostname your-backend.ngrok.io

# Gateway tunnel
ngrok http 9000 --region us --hostname your-gateway.ngrok.io

# Frontend tunnel
ngrok http 8501 --region us --hostname your-frontend.ngrok.io
```

### 3. Configure Environment Variables
```bash
# Update .env file with NGROK URLs
NGROK_ENABLED=true
NGROK_URLS=https://your-backend.ngrok.io,https://your-gateway.ngrok.io,https://your-frontend.ngrok.io
BACKEND_URL=https://your-gateway.ngrok.io
ALLOWED_ORIGINS=https://your-frontend.ngrok.io
ALLOWED_BACKEND_URLS=https://your-gateway.ngrok.io
```

### 4. Start Services with Security
```bash
# Set production environment
export ENVIRONMENT=production

# Start backend
python src/biometric_flow/backend/place_backend.py

# Start gateway  
python src/biometric_flow/backend/unified_gateway.py

# Start frontend
streamlit run src/biometric_flow/frontend/app.py
```

## 🔧 Security Configuration Options

### Rate Limiting
```bash
RATE_LIMIT_REQUESTS=60      # Requests per window
RATE_LIMIT_WINDOW=60        # Window in seconds
MAX_REQUEST_SIZE=5242880    # 5MB max request size
```

### Authentication
```bash
MAIN_API_KEY=your_secure_key
BACKEND_API_KEY=your_backend_key
JWT_SECRET=your_jwt_secret
JWT_EXPIRE_HOURS=24
```

### IP Security
```bash
ALLOWED_IPS=127.0.0.1,192.168.1.0/24  # Comma-separated IPs/ranges
```

### CORS Security
```bash
ALLOWED_ORIGINS=https://your-domain.com,https://your-ngrok.io
```

## 🚨 Security Best Practices

### 1. API Key Management
- Use different keys for each environment
- Rotate keys regularly (monthly recommended)
- Never commit keys to version control
- Use environment variables only

### 2. NGROK Security
- Use NGROK auth tokens for paid accounts
- Restrict NGROK access to known IPs when possible
- Monitor NGROK logs for suspicious activity
- Use custom domains with NGROK Pro

### 3. Monitoring
- Check security logs regularly: `tail -f logs/security.log`
- Monitor rate limit violations
- Watch for authentication failures
- Track unusual IP access patterns

### 4. Network Security
- Use HTTPS-only in production
- Configure firewall rules appropriately
- Limit network access to required ports only
- Use VPN when possible

## 📊 Security Monitoring

### Log Files
```bash
# Security events log
logs/security.log

# Application logs
console output

# NGROK access logs
ngrok web interface (http://localhost:4040)
```

### Security Events to Monitor
- `RATE_LIMIT_EXCEEDED`: Potential DDoS attempts
- `INVALID_AUTH`: Authentication failures
- `MALICIOUS_REQUEST`: Attack pattern detection
- `IP_BLOCKED`: Blocked IP attempts
- `BACKEND_AUTH_FAILED`: Backend communication issues

### Health Check Endpoints
```bash
# Check backend health
curl -H "Authorization: Bearer YOUR_API_KEY" https://your-backend.ngrok.io/health

# Check gateway health  
curl -H "Authorization: Bearer YOUR_API_KEY" https://your-gateway.ngrok.io/health
```

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API keys are set correctly
   - Check Authorization header format
   - Ensure keys match between services

2. **Rate Limit Issues**
   - Increase `RATE_LIMIT_REQUESTS` if needed
   - Check for multiple clients using same IP
   - Monitor for legitimate high-traffic periods

3. **CORS Errors**
   - Add your NGROK URLs to `ALLOWED_ORIGINS`
   - Verify frontend is using correct backend URL
   - Check browser console for CORS details

4. **IP Blocking**
   - Add your IP to `ALLOWED_IPS`
   - Check security logs for blocking reason
   - Clear rate limit cache if needed

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Disable security for testing (development only)
export ENVIRONMENT=development
export ALLOW_NO_AUTH=true
```

## 📞 Security Support

If you encounter security issues:

1. Check the security logs first
2. Review environment configuration
3. Test with debug mode enabled
4. Document the exact error messages
5. Include relevant log snippets

Remember: Security is a process, not a destination. Regularly review and update your security configuration as your deployment evolves.
