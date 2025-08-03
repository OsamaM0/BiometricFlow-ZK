# 📮 Postman Import Guide for BiometricFlow-ZK

## 🚀 Quick Import Steps

### Step 1: Open Postman
1. Launch Postman application
2. Sign in or continue as guest

### Step 2: Import Collections
1. Click **Import** button (top left)
2. Select **Files** tab
3. Click **Choose Files** or drag & drop
4. Select these files:
   - `PlaceBackend_API_Collection.json`
   - `UnifiedGateway_API_Collection.json`
   - `Environment_Template.json`
5. Click **Import**

### Step 3: Setup Environment
1. Click **Environments** (left sidebar)
2. Select **BiometricFlow-ZK Environment**
3. Update these variables:

```json
{
  "api_key": "your_generated_api_key_here",
  "base_url": "http://localhost:8000",
  "gateway_url": "http://localhost:9000",
  "device_name": "Main Office",
  "place_name": "Place_1_BackOffice"
}
```

### Step 4: Generate API Key
```powershell
# Windows
.\setup_security.ps1

# Or manually generate
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Test Connection
1. Select **BiometricFlow-ZK Environment** (top right)
2. Open **Place Backend** collection
3. Run **Health Check - Fast** request
4. Should return `200 OK` with health status

## ✅ Verification Checklist

- [ ] Collections imported successfully
- [ ] Environment imported and selected
- [ ] API key generated and set
- [ ] Backend service running on port 8000
- [ ] Gateway service running on port 9000
- [ ] Health check returns 200 OK
- [ ] Authentication test passes

## 🔧 Common Issues

### Issue: 401 Unauthorized
**Solution:** Check your API key
- Generate new key with `setup_security.ps1`
- Update environment variable `api_key`
- Ensure no extra spaces in the key

### Issue: Connection Refused
**Solution:** Start the services
```bash
# Start backend
python src/biometric_flow/backend/place_backend.py

# Start gateway  
python src/biometric_flow/backend/unified_gateway.py
```

### Issue: CORS Errors
**Solution:** Update CORS settings
```bash
# Add to .env file
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:9000
```

## 🌐 For NGROK Users

### Update Environment for NGROK:
```json
{
  "base_url": "https://your-backend.ngrok.io",
  "gateway_url": "https://your-gateway.ngrok.io",
  "api_key": "your_api_key_here"
}
```

### Update .env for NGROK:
```bash
NGROK_ENABLED=true
NGROK_URLS=https://your-backend.ngrok.io,https://your-gateway.ngrok.io
ALLOWED_ORIGINS=https://your-frontend.ngrok.io
```

## 📋 Test Sequence

### 1. Basic Tests
- [ ] Health Check (both APIs)
- [ ] Root endpoint (with auth)
- [ ] Get devices list

### 2. Data Tests  
- [ ] Get users
- [ ] Get attendance data
- [ ] Get summary statistics

### 3. Advanced Tests
- [ ] Multi-place unified data
- [ ] Holiday management
- [ ] Error handling

## 💡 Pro Tips

1. **Use Folders:** Organize requests in logical folders
2. **Save Examples:** Save successful responses as examples
3. **Use Tests:** Enable automated testing in requests
4. **Environment Switching:** Create separate environments for dev/prod
5. **Documentation:** Add descriptions to your custom requests

## 📞 Need Help?

1. **Check Logs:** Look at console output from backend services
2. **Test Script:** Run `python test_api_access.py`
3. **Security Guide:** Read `API_ACCESS_GUIDE.md`
4. **Environment:** Verify `.env` file configuration

You're all set! 🎉
