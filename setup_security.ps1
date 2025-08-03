# BiometricFlow-ZK Quick Setup Script
# This script helps you quickly generate API keys and test endpoint access

Write-Host "BiometricFlow-ZK Security Setup" -ForegroundColor Green
Write-Host "=" * 40

# Function to generate secure API key
function Generate-ApiKey {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
    return [System.Convert]::ToBase64String($bytes) -replace '/', '_' -replace '\+', '-'
}

# Check if .env file exists
$envFile = ".\.env"
if (Test-Path $envFile) {
    Write-Host ".env file already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Exiting without changes" -ForegroundColor Red
        exit
    }
}

Write-Host "Generating secure API keys..." -ForegroundColor Cyan

# Generate API keys
$mainApiKey = Generate-ApiKey
$backendApiKey = Generate-ApiKey  
$frontendApiKey = Generate-ApiKey
$jwtSecret = Generate-ApiKey

Write-Host "Keys generated successfully!" -ForegroundColor Green

# Create .env file content
$envContent = @"
# BiometricFlow-ZK Security Configuration
# Generated on $(Get-Date)

# =================================
# SECURITY CONFIGURATION
# =================================

# Main API Key for backend authentication
MAIN_API_KEY=$mainApiKey

# Backend API Key for internal communication between services
BACKEND_API_KEY=$backendApiKey

# Frontend API Key for frontend-backend communication
FRONTEND_API_KEY=$frontendApiKey

# JWT Secret for token generation
JWT_SECRET=$jwtSecret

# JWT Token expiration in hours
JWT_EXPIRE_HOURS=24

# =================================
# ENVIRONMENT CONFIGURATION
# =================================

# Environment mode: development, production
ENVIRONMENT=production

# Session timeout in seconds (1 hour)
SESSION_TIMEOUT=3600

# Request timeout in seconds
REQUEST_TIMEOUT=30

# Allow requests without authentication in development mode
ALLOW_NO_AUTH=false

# =================================
# RATE LIMITING CONFIGURATION
# =================================

# Maximum requests per window
RATE_LIMIT_REQUESTS=60

# Rate limit window in seconds
RATE_LIMIT_WINDOW=60

# Maximum request size in bytes (5MB)
MAX_REQUEST_SIZE=5242880

# =================================
# CORS AND ORIGIN CONFIGURATION
# =================================

# Allowed origins for CORS (add your frontend URLs)
ALLOWED_ORIGINS=http://localhost:8501,http://localhost:3000,http://127.0.0.1:8501

# Backend URL for frontend to connect to
BACKEND_URL=http://localhost:9000

# Allowed backend URLs for frontend security
ALLOWED_BACKEND_URLS=http://localhost:9000,http://localhost:8000

# =================================
# BACKEND CONFIGURATION
# =================================

# Backend name identifier
BACKEND_NAME=Place_1

# Backend port
BACKEND_PORT=8000

# Gateway port
GATEWAY_PORT=9000

# Device configuration file path
DEVICES_CONFIG_FILE=config/devices_config.json

# =================================
# IP SECURITY CONFIGURATION
# =================================

# Allowed IP addresses/ranges (leave empty to allow all for local development)
# ALLOWED_IPS=127.0.0.1,::1,192.168.1.0/24

"@

# Write .env file
try {
    $envContent | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host ".env file created successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Failed to create .env file: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Your API Keys:" -ForegroundColor Yellow
Write-Host "=" * 30
Write-Host "Main API Key:     $($mainApiKey.Substring(0,8))...$($mainApiKey.Substring($mainApiKey.Length-4))" -ForegroundColor White
Write-Host "Backend API Key:  $($backendApiKey.Substring(0,8))...$($backendApiKey.Substring($backendApiKey.Length-4))" -ForegroundColor White
Write-Host "Frontend API Key: $($frontendApiKey.Substring(0,8))...$($frontendApiKey.Substring($frontendApiKey.Length-4))" -ForegroundColor White
Write-Host "JWT Secret:       $($jwtSecret.Substring(0,8))...$($jwtSecret.Substring($jwtSecret.Length-4))" -ForegroundColor White

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host "1. Start the backend:  python src/biometric_flow/backend/place_backend.py" -ForegroundColor White
Write-Host "2. Test API access:    python test_api_access.py" -ForegroundColor White
Write-Host "3. Start frontend:     streamlit run src/biometric_flow/frontend/app.py" -ForegroundColor White

Write-Host ""
Write-Host "Testing API Access:" -ForegroundColor Cyan
$testNow = Read-Host "Do you want to test API access now? (y/n)"

if ($testNow -eq "y") {
    Write-Host "Testing API endpoints..." -ForegroundColor Cyan
    
    # Set environment variable for this session
    $env:MAIN_API_KEY = $mainApiKey
    
    # Test if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Python found: $pythonVersion" -ForegroundColor Green
        
        # Run the test script
        Write-Host "Running API tests..." -ForegroundColor Cyan
        python test_api_access.py
    }
    catch {
        Write-Host "Python not found or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python or add it to your PATH" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Setup complete! Your BiometricFlow-ZK system is now configured with secure API access." -ForegroundColor Green
Write-Host ""
Write-Host "For more details, see:" -ForegroundColor Yellow
Write-Host "   - API_ACCESS_GUIDE.md" -ForegroundColor White
Write-Host "   - docs/security/NGROK_SECURITY_GUIDE.md" -ForegroundColor White