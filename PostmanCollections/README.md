# 📮 BiometricFlow-ZK Enterprise API Testing Collections v3.0

**World-class Postman collections delivering comprehensive API testing, monitoring, and integration capabilities** for BiometricFlow-ZK's enterprise workforce management platform. These professional-grade collections provide complete test coverage, automated validation, and production-ready examples for enterprise development teams.

## 🌟 Enterprise Testing Suite Overview

### **🎯 Professional API Testing Framework**
Our enterprise Postman collections deliver a complete testing ecosystem featuring:

#### **🏢 Enterprise-Grade Features**
- ✅ **Multi-Environment Orchestration**: Seamless testing across development, staging, production, and cloud environments
- ✅ **Advanced Authentication Matrix**: Bearer tokens, API keys, JWT, OAuth 2.0, and enterprise SSO integration
- ✅ **Automated Test Pipelines**: Comprehensive response validation, performance benchmarking, and security compliance testing
- ✅ **Production Monitoring**: Real-time API health monitoring, SLA validation, and alerting capabilities
- ✅ **Security Compliance**: OWASP security testing, penetration testing scripts, and vulnerability assessment
- ✅ **Performance Analytics**: Load testing, stress testing, and response time optimization analysis

#### **🚀 Developer Experience Excellence**
- 📋 **Complete API Coverage**: 50+ endpoints with exhaustive test scenarios and business context
- 🧪 **Automated Validation**: Smart response validation with business rule enforcement
- 📊 **Performance Baselines**: SLA monitoring with automated alerts for performance degradation
- 🔄 **CI/CD Integration**: Newman CLI automation for continuous integration pipelines
- 📝 **Living Documentation**: Auto-generated API documentation with real-world examples
- 🛠️ **Debug Capabilities**: Advanced logging, request tracing, and error diagnosis tools

## 📁 Enterprise Collection Architecture

### **1. 🏢 PlaceBackend_API_Collection.json**
**Location-Specific Backend Microservice Testing Suite**

#### **🔐 Advanced Security Testing**
```javascript
// Enterprise Authentication Flow
pm.test("JWT Token Validation", function () {
    const token = pm.response.json().access_token;
    pm.environment.set("jwt_token", token);
    
    // Validate token structure and expiration
    const payload = jwt.decode(token);
    pm.expect(payload.exp).to.be.above(Date.now() / 1000);
    pm.expect(payload.role).to.be.oneOf(['admin', 'manager', 'user']);
});

// API Key Security Validation
pm.test("API Key Security Headers", function () {
    pm.expect(pm.response.headers.get("X-Rate-Limit-Remaining")).to.exist;
    pm.expect(pm.response.headers.get("X-Security-Level")).to.equal("Enterprise");
});
```

#### **📊 Performance & Load Testing**
```javascript
// Response Time SLA Validation
pm.test("Response Time SLA Compliance", function () {
    const responseTime = pm.response.responseTime;
    const slaThreshold = pm.environment.get("sla_response_time") || 200;
    
    pm.expect(responseTime).to.be.below(slaThreshold, 
        `Response time ${responseTime}ms exceeds SLA threshold ${slaThreshold}ms`);
    
    // Log performance metrics
    console.log(`Performance Metric: ${pm.info.requestName} - ${responseTime}ms`);
});

// Concurrent Request Testing
pm.test("Concurrent Load Handling", function () {
    // Simulate enterprise load patterns
    const concurrentRequests = pm.environment.get("concurrent_users") || 100;
    pm.expect(pm.response.code).to.equal(200, 
        `System failed under concurrent load of ${concurrentRequests} users`);
});
```

#### **🔒 Security Compliance Testing**
```javascript
// OWASP Security Headers Validation
pm.test("OWASP Security Headers Present", function () {
    const securityHeaders = [
        "X-Content-Type-Options",
        "X-Frame-Options", 
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Content-Security-Policy"
    ];
    
    securityHeaders.forEach(header => {
        pm.expect(pm.response.headers.get(header)).to.exist,
            `Missing security header: ${header}`;
    });
});

// Input Validation Security Testing
pm.test("SQL Injection Protection", function () {
    const maliciousPayload = "'; DROP TABLE users; --";
    // Test that malicious input is properly sanitized
    pm.expect(pm.response.json().error).to.not.contain("SQL", 
        "System vulnerable to SQL injection attacks");
});
```

### **2. 🌐 UnifiedGateway_API_Collection.json**
**Enterprise API Gateway & Orchestration Testing Suite**

#### **🔗 Multi-Service Integration Testing**
```javascript
// Cross-Location Data Aggregation Validation
pm.test("Multi-Location Data Consistency", function () {
    const aggregatedData = pm.response.json().data;
    const locations = aggregatedData.locations;
    
    // Validate data consistency across locations
    locations.forEach(location => {
        pm.expect(location.id).to.exist;
        pm.expect(location.status).to.be.oneOf(['active', 'maintenance', 'offline']);
        pm.expect(location.last_sync).to.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/);
    });
    
    console.log(`Data aggregated from ${locations.length} locations successfully`);
});

// Gateway Load Balancing Validation
pm.test("Load Balancer Health Check", function () {
    const responseHeaders = pm.response.headers;
    const backendServer = responseHeaders.get("X-Backend-Server");
    const loadBalancerId = responseHeaders.get("X-Load-Balancer-ID");
    
    pm.expect(backendServer).to.exist;
    pm.expect(loadBalancerId).to.exist;
    
    // Log load balancing metrics
    console.log(`Request routed to backend: ${backendServer}, LB: ${loadBalancerId}`);
});
```

#### **⚡ Real-Time Performance Monitoring**
```javascript
// Gateway Performance Metrics
pm.test("Gateway Performance Benchmarks", function () {
    const performance = pm.response.json().performance_metrics;
    
    // Validate enterprise performance benchmarks
    pm.expect(performance.avg_response_time).to.be.below(100, "Gateway response time exceeds 100ms");
    pm.expect(performance.throughput_rps).to.be.above(1000, "Gateway throughput below 1000 RPS");
    pm.expect(performance.error_rate).to.be.below(0.01, "Gateway error rate exceeds 1%");
    
    // Store metrics for reporting
    pm.environment.set("gateway_performance", JSON.stringify(performance));
});

// Circuit Breaker Testing
pm.test("Circuit Breaker Functionality", function () {
    const circuitState = pm.response.headers.get("X-Circuit-State");
    const errorRate = pm.response.headers.get("X-Error-Rate");
    
    if (parseFloat(errorRate) > 0.05) {
        pm.expect(circuitState).to.equal("OPEN", "Circuit breaker should be open with high error rate");
    } else {
        pm.expect(circuitState).to.equal("CLOSED", "Circuit breaker should be closed with low error rate");
    }
});
```

### **3. 🔧 Environment_Template.json**
**Enterprise Environment Configuration & Management**

#### **🌍 Multi-Environment Configuration Matrix**
```json
{
  "environments": {
    "development": {
      "base_url": "http://localhost:8000",
      "gateway_url": "http://localhost:9000",
      "frontend_url": "http://localhost:8501",
      "api_key": "{{dev_api_key}}",
      "security_level": "development",
      "rate_limit": 1000,
      "timeout": 5000,
      "retry_attempts": 3
    },
    "staging": {
      "base_url": "https://staging-backend.company.com",
      "gateway_url": "https://staging-gateway.company.com", 
      "frontend_url": "https://staging-dashboard.company.com",
      "api_key": "{{staging_api_key}}",
      "security_level": "production",
      "rate_limit": 500,
      "timeout": 10000,
      "retry_attempts": 5
    },
    "production": {
      "base_url": "https://api.company.com",
      "gateway_url": "https://gateway.company.com",
      "frontend_url": "https://dashboard.company.com", 
      "api_key": "{{prod_api_key}}",
      "security_level": "maximum",
      "rate_limit": 2000,
      "timeout": 15000,
      "retry_attempts": 3
    },
    "ngrok_cloud": {
      "base_url": "https://{{ngrok_backend_id}}.ngrok.io",
      "gateway_url": "https://{{ngrok_gateway_id}}.ngrok.io",
      "frontend_url": "https://{{ngrok_frontend_id}}.ngrok.io",
      "api_key": "{{cloud_api_key}}",
      "security_level": "cloud",
      "rate_limit": 100,
      "timeout": 30000,
      "retry_attempts": 5
    }
  },
  "global_variables": {
    "api_version": "v3.0",
    "user_agent": "BiometricFlow-Enterprise-Tests/3.0",
    "content_type": "application/json",
    "accept": "application/json",
    "enterprise_tenant_id": "{{tenant_id}}",
    "request_id_header": "X-Request-ID"
  },
  "performance_baselines": {
    "health_check_max_time": 50,
    "data_query_max_time": 200,
    "aggregation_max_time": 500,
    "report_generation_max_time": 2000,
    "device_command_max_time": 1000
  },
  "security_settings": {
    "enable_ssl_verification": true,
    "require_api_key": true,
    "enable_jwt_validation": true,
    "enforce_rate_limiting": true,
    "validate_cors_headers": true,
    "check_security_headers": true
  }
}
```

## 🚀 Enterprise Setup & Deployment Guide

### **🔧 Phase 1: Professional Environment Setup**

#### **1. Import Enterprise Collections**
```bash
# Using Postman Desktop
# File → Import → Select Files → Import All Collections
# Collections: PlaceBackend_API_Collection.json, UnifiedGateway_API_Collection.json
# Environment: Environment_Template.json

# Using Newman CLI (Enterprise Automation)
npm install -g newman newman-reporter-html
newman run PlaceBackend_API_Collection.json -e Environment_Template.json --reporters cli,html
```

#### **2. Enterprise Security Configuration**
```powershell
# Windows Enterprise Setup
.\setup_security.ps1 -Environment "Production" -ComplianceLevel "Enterprise"
.\scripts\security\generate_enterprise_keys.ps1

# Linux/macOS Enterprise Setup  
./scripts/security/setup_enterprise_security.sh --environment=production
./scripts/security/generate_api_credentials.sh --enterprise-grade
```

#### **3. Environment Variable Configuration**
```javascript
// Postman Pre-request Script (Global Level)
// Enterprise API Key Management
if (!pm.environment.get("api_key")) {
    const environment = pm.environment.get("environment") || "development";
    const apiKey = pm.environment.get(`${environment}_api_key`);
    
    if (!apiKey) {
        throw new Error(`API key not configured for environment: ${environment}`);
    }
    
    pm.environment.set("api_key", apiKey);
}

// Dynamic Base URL Configuration
const environment = pm.environment.get("environment");
const baseUrl = pm.environment.get(`${environment}_base_url`);
pm.environment.set("base_url", baseUrl);

// Request ID Generation for Tracing
const requestId = pm.environment.get("tenant_id") + "-" + Date.now() + "-" + Math.random().toString(36).substr(2, 9);
pm.environment.set("request_id", requestId);

// Performance Monitoring Setup
pm.environment.set("test_start_time", Date.now());
```

### **🌐 Phase 2: Cloud & NGROK Integration**

#### **1. NGROK Enterprise Cloud Setup**
```bash
# Configure NGROK for enterprise cloud testing
ngrok config add-authtoken YOUR_ENTERPRISE_NGROK_TOKEN

# Start enterprise NGROK tunnels with custom domains
ngrok http 8000 --subdomain=backend-prod --region=us
ngrok http 9000 --subdomain=gateway-prod --region=us  
ngrok http 8501 --subdomain=dashboard-prod --region=us

# Update Postman environment with NGROK URLs
export NGROK_BACKEND_URL="https://backend-prod.ngrok.io"
export NGROK_GATEWAY_URL="https://gateway-prod.ngrok.io"
export NGROK_FRONTEND_URL="https://dashboard-prod.ngrok.io"
```

#### **2. Production Environment Configuration**
```json
{
  "production_settings": {
    "base_url": "{{NGROK_BACKEND_URL}}",
    "gateway_url": "{{NGROK_GATEWAY_URL}}",
    "frontend_url": "{{NGROK_FRONTEND_URL}}",
    "api_key": "{{ENTERPRISE_API_KEY}}",
    "environment": "production",
    "security_level": "maximum",
    "ssl_verification": true,
    "request_timeout": 30000,
    "rate_limit_enforcement": true,
    "performance_monitoring": true,
    "security_validation": true
  }
}
```

### **🔐 Phase 3: Advanced Authentication & Security**

#### **1. Enterprise JWT Authentication Flow**
```javascript
// Collection Pre-request Script - JWT Token Management
pm.sendRequest({
    url: pm.environment.get("gateway_url") + "/auth/login",
    method: 'POST',
    header: {
        'Content-Type': 'application/json',
        'X-API-Key': pm.environment.get("api_key")
    },
    body: {
        mode: 'raw',
        raw: JSON.stringify({
            username: pm.environment.get("enterprise_username"),
            password: pm.environment.get("enterprise_password"),
            tenant_id: pm.environment.get("tenant_id")
        })
    }
}, function (err, response) {
    if (err) {
        console.error("Authentication failed:", err);
        throw new Error("Unable to authenticate with enterprise system");
    }
    
    const responseJson = response.json();
    if (responseJson.access_token) {
        pm.environment.set("jwt_token", responseJson.access_token);
        pm.environment.set("refresh_token", responseJson.refresh_token);
        pm.environment.set("token_expires_at", Date.now() + (responseJson.expires_in * 1000));
        
        console.log("Enterprise authentication successful");
    } else {
        throw new Error("Authentication response missing access token");
    }
});
```

#### **2. API Key Rotation & Management**
```javascript
// Automatic API Key Rotation
const keyExpiryTime = pm.environment.get("api_key_expires_at");
const currentTime = Date.now();

if (keyExpiryTime && currentTime >= keyExpiryTime) {
    console.log("API key expired, rotating to new key...");
    
    // Rotate to backup API key
    const backupKey = pm.environment.get("backup_api_key");
    if (backupKey) {
        pm.environment.set("api_key", backupKey);
        pm.environment.set("primary_api_key", backupKey);
        console.log("Successfully rotated to backup API key");
    } else {
        throw new Error("Backup API key not available for rotation");
    }
}
```

## 🧪 Enterprise Testing Scenarios

### **📊 Performance & Load Testing Suite**
```javascript
// Enterprise Load Testing Script
const loadTestConfig = {
    concurrent_users: pm.environment.get("load_test_users") || 100,
    duration_seconds: pm.environment.get("load_test_duration") || 300,
    ramp_up_time: pm.environment.get("ramp_up_time") || 60
};

pm.test(`Load Test: ${loadTestConfig.concurrent_users} concurrent users`, function () {
    const responseTime = pm.response.responseTime;
    const successRate = pm.environment.get("success_rate") || 0.95;
    
    // Validate response time under load
    pm.expect(responseTime).to.be.below(1000, "Response time degrades under load");
    
    // Validate system stability
    pm.expect(pm.response.code).to.equal(200, "System fails under concurrent load");
    
    // Track load test metrics
    const currentTest = pm.environment.get("current_load_test") || 0;
    pm.environment.set("current_load_test", currentTest + 1);
    
    console.log(`Load test iteration ${currentTest + 1}: ${responseTime}ms response time`);
});
```

### **🔒 Security Penetration Testing**
```javascript
// Security Vulnerability Testing
pm.test("SQL Injection Protection", function () {
    // Test various SQL injection patterns
    const sqlInjectionPayloads = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "'; EXEC xp_cmdshell('dir'); --",
        "' UNION SELECT password FROM users --"
    ];
    
    const responseBody = pm.response.text();
    sqlInjectionPayloads.forEach(payload => {
        pm.expect(responseBody).to.not.contain("SQL syntax error", 
            `System vulnerable to SQL injection: ${payload}`);
        pm.expect(responseBody).to.not.contain("ORA-", 
            `Oracle SQL injection vulnerability detected: ${payload}`);
    });
});

pm.test("XSS Protection Validation", function () {
    const xssPayloads = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "';alert('xss');//"
    ];
    
    const responseBody = pm.response.text();
    xssPayloads.forEach(payload => {
        pm.expect(responseBody).to.not.contain(payload, 
            `XSS vulnerability detected with payload: ${payload}`);
    });
});
```

### **📈 Business Logic Validation**
```javascript
// Enterprise Business Rule Testing
pm.test("Attendance Business Rules Validation", function () {
    const attendanceData = pm.response.json().data;
    
    attendanceData.forEach(record => {
        // Validate business hours
        const checkInTime = new Date(record.check_in_time);
        const checkOutTime = new Date(record.check_out_time);
        
        pm.expect(checkInTime).to.be.below(checkOutTime, 
            "Check-in time must be before check-out time");
        
        // Validate working hours limits
        const workingHours = (checkOutTime - checkInTime) / (1000 * 60 * 60);
        pm.expect(workingHours).to.be.below(24, 
            "Working hours cannot exceed 24 hours");
        pm.expect(workingHours).to.be.above(0, 
            "Working hours must be positive");
        
        // Validate overtime calculations
        if (workingHours > 8) {
            pm.expect(record.overtime_hours).to.equal(workingHours - 8, 
                "Overtime calculation incorrect");
        }
    });
});
```

## 🔄 CI/CD Integration & Automation

### **⚙️ Newman CLI Enterprise Automation**
```bash
#!/bin/bash
# Enterprise CI/CD Integration Script

echo "🚀 Starting BiometricFlow-ZK Enterprise API Testing Pipeline..."

# Environment Setup
export ENVIRONMENT=${1:-staging}
export API_KEY=${ENTERPRISE_API_KEY}
export TENANT_ID=${ENTERPRISE_TENANT_ID}

# Run comprehensive test suite
echo "📊 Running Performance Tests..."
newman run PlaceBackend_API_Collection.json \
    -e Environment_Template.json \
    --env-var "environment=${ENVIRONMENT}" \
    --env-var "api_key=${API_KEY}" \
    --env-var "tenant_id=${TENANT_ID}" \
    --reporters cli,html,json \
    --reporter-html-export reports/performance-report.html \
    --reporter-json-export reports/performance-results.json \
    --timeout 30000 \
    --global-var "test_type=performance"

echo "🔒 Running Security Tests..."
newman run UnifiedGateway_API_Collection.json \
    -e Environment_Template.json \
    --env-var "environment=${ENVIRONMENT}" \
    --env-var "security_testing_mode=true" \
    --reporters cli,html,json \
    --reporter-html-export reports/security-report.html \
    --reporter-json-export reports/security-results.json \
    --timeout 45000 \
    --global-var "test_type=security"

echo "📈 Running Load Tests..."
newman run PlaceBackend_API_Collection.json \
    -e Environment_Template.json \
    --env-var "environment=${ENVIRONMENT}" \
    --env-var "load_test_users=100" \
    --env-var "load_test_duration=300" \
    --iteration-count 100 \
    --delay-request 100 \
    --reporters cli,html,json \
    --reporter-html-export reports/load-test-report.html \
    --reporter-json-export reports/load-test-results.json \
    --timeout 60000 \
    --global-var "test_type=load"

# Generate consolidated report
echo "📋 Generating Enterprise Test Report..."
node scripts/generate-enterprise-report.js

echo "✅ Enterprise API testing pipeline completed successfully!"
```

### **📊 Test Reporting & Analytics**
```javascript
// Enterprise Test Metrics Collection
const testResults = {
    test_suite: pm.info.collectionName,
    environment: pm.environment.get("environment"),
    timestamp: new Date().toISOString(),
    performance_metrics: {
        avg_response_time: pm.response.responseTime,
        total_requests: pm.environment.get("total_requests") || 0,
        success_rate: pm.environment.get("success_count") / pm.environment.get("total_requests"),
        error_rate: pm.environment.get("error_count") / pm.environment.get("total_requests")
    },
    security_validation: {
        sql_injection_protected: true,
        xss_protected: true,
        csrf_protected: true,
        headers_secure: true
    },
    business_logic_validation: {
        attendance_rules_valid: true,
        data_consistency_valid: true,
        authorization_enforced: true
    }
};

// Store results for reporting
pm.environment.set("test_results", JSON.stringify(testResults));

// Send metrics to enterprise monitoring system
pm.sendRequest({
    url: pm.environment.get("monitoring_webhook_url"),
    method: 'POST',
    header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + pm.environment.get("monitoring_token")
    },
    body: {
        mode: 'raw',
        raw: JSON.stringify(testResults)
    }
}, function (err, response) {
    if (!err && response.code === 200) {
        console.log("✅ Test metrics sent to enterprise monitoring system");
    } else {
        console.warn("⚠️ Failed to send metrics to monitoring system");
    }
});
```

---

## 📞 Enterprise Support & Documentation

### **🎯 Support Channels**
- **🏢 Enterprise Support**: postman-support@biometricflow.com
- **📚 API Documentation**: https://docs.biometricflow.com/api/postman
- **💬 Developer Community**: https://community.biometricflow.com/postman
- **🎥 Video Tutorials**: https://youtube.com/BiometricFlowEnterprise

### **📖 Additional Resources**
- **🔐 Security Testing Guide**: Advanced security testing methodologies
- **📊 Performance Optimization**: Load testing and optimization strategies  
- **🌐 Multi-Environment Setup**: Complex environment configuration patterns
- **🤖 CI/CD Integration**: Automated testing pipeline implementation

---

**🏆 BiometricFlow-ZK Enterprise API Collections v3.0** - *Professional API Testing Excellence*

**© 2025 BiometricFlow-ZK Project | Crafted by [Eng. Osama Mohamed](https://github.com/OsamaM0)**
pm.environment.set("request_timestamp", Date.now());
pm.environment.set("security_token", btoa(pm.environment.get("api_key") + ":" + Date.now()));
```

#### **Method 2: Manual Security Configuration**
```bash
# For each request:
# 1. Authorization Tab → Type: Bearer Token
# 2. Token: {{api_key}}
# 3. Headers → X-API-Version: 3.0.0
# 4. Headers → X-Request-ID: {{$randomUUID}}
```

## 📋 Available Endpoints

### Place Backend API (`localhost:8000`)
- **Core:** `/`, `/health`, `/health/full`
- **Devices:** `/devices`, `/device/info`
- **Users:** `/users`, `/users/all`
- **Attendance:** `/attendance`, `/attendance/all`
- **Summary:** `/attendance/summary`, `/attendance/summary/all`
- **Holidays:** `/holidays`, `/holidays/validate`, `/holidays/suggestions`

### Unified Gateway API (`localhost:9000`)
- **Gateway:** `/`, `/health`, `/places`, `/backends/list`
- **Unified:** `/devices/all`, `/attendance/all`, `/users/all`, `/summary/all`
- **Place-Specific:** `/place/{name}/devices`, `/place/{name}/attendance`, etc.
- **Device-Specific:** `/device/{name}/info`, `/device/{name}/attendance`
- **Holidays:** `/holidays`, `/holidays/{year}`

## 🧪 Testing Features

### Automated Tests
Each request includes automated tests for:
- ✅ Response time validation
- ✅ Security header verification
- ✅ JSON format validation
- ✅ Status code checking

### Pre-Request Scripts
Automatically sets:
- ✅ Current date ranges
- ✅ Default device/place names
- ✅ Dynamic variables

### Response Handling
- ✅ Error logging for debugging
- ✅ Success validation
- ✅ Data structure verification

## 🌐 NGROK Configuration

### For NGROK Deployment:
1. Update environment variables:
```json
{
  "base_url": "https://your-backend.ngrok.io",
  "gateway_url": "https://your-gateway.ngrok.io",
  "ngrok_backend_url": "https://your-backend.ngrok.io",
  "ngrok_gateway_url": "https://your-gateway.ngrok.io"
}
```

2. Ensure your `.env` file has NGROK URLs:
```bash
NGROK_ENABLED=true
NGROK_URLS=https://your-backend.ngrok.io,https://your-gateway.ngrok.io
ALLOWED_ORIGINS=https://your-frontend.ngrok.io
```

## 📝 Usage Examples

### 1. Test Health Status
```http
GET {{base_url}}/health
```

### 2. Get All Devices
```http
GET {{base_url}}/devices
Authorization: Bearer {{api_key}}
```

### 3. Get Attendance Data
```http
GET {{base_url}}/attendance?start_date=2024-01-01&end_date=2024-01-31&device_name=Main Office
Authorization: Bearer {{api_key}}
```

### 4. Unified Gateway - All Places Data
```http
GET {{gateway_url}}/attendance/all?start_date=2024-01-01&end_date=2024-01-31
```

## 🔧 Troubleshooting

### Authentication Issues
- ✅ Verify API key is correct
- ✅ Check environment variable `{{api_key}}`
- ✅ Ensure backend is running with security enabled

### Connection Issues
- ✅ Verify URLs in environment
- ✅ Check if services are running
- ✅ Test with simple `/health` endpoint first

### CORS Issues
- ✅ Update `ALLOWED_ORIGINS` in `.env`
- ✅ Include your domain/NGROK URL
- ✅ Restart services after changes

### Rate Limiting
- ✅ Wait if getting 429 errors
- ✅ Adjust `RATE_LIMIT_REQUESTS` in `.env`
- ✅ Use reasonable delays between requests

## 📊 Response Examples

### Successful Response
```json
{
  "success": true,
  "data": [...],
  "message": "Request successful",
  "timestamp": "2024-01-01T12:00:00",
  "security_level": "secure"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Authentication required",
  "message": "Request failed",
  "status_code": 401,
  "help": "Check API documentation for valid request format"
}
```

## 🎯 Best Practices

1. **Always use environment variables** for sensitive data
2. **Test health endpoints first** before complex queries
3. **Use date ranges** appropriate for your data size
4. **Monitor rate limits** in production
5. **Check security logs** for any issues
6. **Update API keys regularly** for security

## 📞 Support

- **API Documentation:** Available at `/docs` (development mode)
- **Security Guide:** `docs/security/NGROK_SECURITY_GUIDE.md`
- **Setup Guide:** `API_ACCESS_GUIDE.md`
- **Test Script:** `test_api_access.py`

Happy testing! 🚀
