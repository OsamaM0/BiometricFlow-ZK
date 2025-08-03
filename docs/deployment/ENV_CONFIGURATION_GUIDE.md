# Environment Configuration Guide

## Overview
All deployment scripts now support loading environment variables from a `.env` file located in the project root directory. This allows for centralized configuration management across all services.

## Setup Instructions

1. **Copy the template file:**
   ```bash
   cp .env.template .env
   ```

2. **Edit the `.env` file:**
   - Customize the values according to your environment
   - Uncomment variables you want to override
   - Add any additional environment variables as needed

3. **Environment Variable Loading:**
   - Windows batch scripts (`.bat`) automatically parse and load the `.env` file
   - Linux/Mac shell scripts (`.sh`) use the `source` command to load variables
   - Variables from `.env` are loaded before service-specific variables
   - Service-specific variables will override `.env` values if both are set

## How It Works

### Windows Scripts (.bat)
```batch
REM === Load .env from root project directory ===
if exist "%PROJECT_DIR%\.env" (
    echo 🔄 Loading environment variables from .env...
    for /f "usebackq tokens=* delims=" %%a in ("%PROJECT_DIR%\.env") do (
        set "line=%%a"
        REM Skip empty lines and comments
        if not "!line!"=="" if "!line:~0,1!" neq "#" (
            for /f "tokens=1,* delims==" %%b in ("!line!") do (
                set "%%b=%%c"
            )
        )
    )
) else (
    echo ⚠️  .env file not found in %PROJECT_DIR%
)
```

### Linux/Mac Scripts (.sh)
```bash
# === Load .env from root project directory ===
if [ -f "$PROJECT_DIR/.env" ]; then
    echo "🔄 Loading environment variables from .env..."
    set -a
    source "$PROJECT_DIR/.env"
    set +a
else
    echo "⚠️  .env file not found in $PROJECT_DIR"
fi
```

## Variable Precedence

Variables are loaded in the following order (later values override earlier ones):

1. System environment variables
2. Variables from `.env` file
3. Service-specific variables set in individual scripts

## Benefits

- **Centralized Configuration:** All environment settings in one place
- **Environment-Specific Settings:** Different `.env` files for dev/test/prod
- **Security:** Keep sensitive data out of scripts and version control
- **Flexibility:** Override any setting without modifying scripts
- **Consistency:** Same configuration approach across all services

## Example Usage

### Database Configuration
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/biometric_flow
DATABASE_POOL_SIZE=20
```

### Service Ports
```env
BACKEND_PORT=8000
GATEWAY_PORT=9000
STREAMLIT_SERVER_PORT=8501
```

### Development vs Production
```env
# Development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

## Security Considerations

- Add `.env` to your `.gitignore` file to prevent committing sensitive data
- Use `.env.template` for sharing configuration structure without sensitive values
- Ensure proper file permissions on production servers (600 or 644)
- Consider using encrypted secrets for highly sensitive data

## Troubleshooting

### Common Issues

1. **Variables not loading:**
   - Check file path and name (must be `.env` in project root)
   - Ensure proper syntax: `KEY=value` (no spaces around =)
   - Check for special characters that need escaping

2. **Comments not working:**
   - Use `#` at the beginning of the line
   - Inline comments are not supported

3. **Windows-specific issues:**
   - Avoid special characters in paths
   - Use double quotes for values with spaces
   - Check that enabledelayedexpansion is set

## Updated Scripts

All the following scripts now support `.env` loading:

### Windows (.bat)
- `start_place1_backend.bat`
- `start_place2_backend.bat`
- `start_unified_backend.bat`
- `start_frontend.bat`
- `start_all_services.bat`

### Linux/Mac (.sh)
- `start_place1_backend.sh`
- `start_place2_backend.sh`
- `start_unified_backend.sh`
- `start_frontend.sh`
- `start_all_services.sh`
