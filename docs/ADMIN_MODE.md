# Admin Mode Documentation

## ⚠️ FOR DEVELOPMENT/TESTING ONLY - NOT FOR PRODUCTION

This documentation describes admin-only features that are **temporarily** included for development convenience. These features must be **removed before production deployment**.

---

## Purpose

During development, constantly entering API keys through the configuration UI can be tedious. Admin mode provides shortcuts to:

1. Restore API keys from backup `.env` files
2. Load keys from environment variables
3. Quickly switch between testing with/without API key configuration

---

## Admin Features

### 1. Admin Launch Script (`admin_launch.sh`)

A convenient bash script that handles common development scenarios.

#### Usage

```bash
# Launch with existing .env file (if available)
./admin_launch.sh

# Restore .env from most recent backup
./admin_launch.sh restore

# Remove .env to test API configuration screen
./admin_launch.sh clean
```

#### What It Does

**`./admin_launch.sh` (default)**:
1. Checks for existing `.env` file
2. If found: Launches app with those keys
3. If not found: Offers to restore from backup
4. If no backup: Attempts to use environment variables with ADMIN_MODE

**`./admin_launch.sh restore`**:
1. Finds the most recent `.env.backup.*` file
2. Copies it to `.env`
3. Reports success

**`./admin_launch.sh clean`**:
1. Backs up current `.env` (if exists)
2. Removes `.env` file
3. Next launch will show API configuration screen

---

### 2. Admin Mode Environment Variable

The `ADMIN_MODE` environment variable enables special loading behavior.

#### Usage

```bash
# Set environment variables
export GEMINI_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXX"
export SERPAPI_KEY="your-serpapi-key"
export ADMIN_MODE=true

# Launch application
python main.py
```

#### What It Does

When `ADMIN_MODE=true` and no `.env` file exists:
- Application loads API keys directly from environment variables
- Bypasses API key configuration screen
- Logs warning messages indicating admin mode is active
- Keys are not saved to `.env` file

#### Log Output

```
🔧 ADMIN MODE: Loading API keys from environment variables
⚠️ LOADING KEYS FROM ENVIRONMENT - ADMIN MODE ACTIVE
  ✓ Loaded GEMINI_API_KEY from environment
  ✓ Loaded SERPAPI_KEY from environment
🔧 Admin mode loaded 2 keys from environment variables
```

---

## Development Workflows

### Workflow 1: Testing with Existing Keys

**Goal**: Quickly test features without re-entering API keys

```bash
# Use admin script (finds and uses .env or backup)
./admin_launch.sh
```

or

```bash
# Manual approach
python main.py  # Uses .env if it exists
```

---

### Workflow 2: Testing API Configuration Screen

**Goal**: Test the first-time user experience

```bash
# Option A: Use admin script
./admin_launch.sh clean     # Removes .env
python main.py              # Shows API config screen

# Option B: Manual
mv .env .env.backup.$(date +%s)
python main.py
```

---

### Workflow 3: Switching Between Modes

**Goal**: Test both experiences quickly

```bash
# Test with keys
./admin_launch.sh restore
python main.py

# Stop app (Ctrl+C)

# Test without keys
./admin_launch.sh clean
python main.py

# Stop app (Ctrl+C)

# Restore keys again
./admin_launch.sh restore
```

---

### Workflow 4: Using Environment Variables

**Goal**: Test without creating `.env` file

```bash
# Set keys in environment
export GEMINI_API_KEY="AIzaSy..."
export SERPAPI_KEY="..."
export ADMIN_MODE=true

# Launch
python main.py

# Keys loaded from environment, no .env file created
```

---

## Code Implementation

### In `src/utils/api_key_manager.py`

```python
# ========== ADMIN OVERRIDE FOR TESTING ==========
# TODO: Remove this before production deployment
# This allows developers to bypass API key configuration during development
ADMIN_MODE = os.environ.get('ADMIN_MODE', 'false').lower() == 'true'

def __init__(self, config_file: str = ".env"):
    """Initialize API Key Manager"""
    self.config_file = Path(config_file)
    self.keys = {}
    self.load_keys()
    
    # Admin override: Load keys from environment variables if ADMIN_MODE is enabled
    if self.ADMIN_MODE and not self.keys:
        self._load_from_environment()
        logger.warning("🔧 ADMIN MODE: Loading API keys from environment variables")

def _load_from_environment(self) -> None:
    """
    Load API keys from environment variables (ADMIN MODE ONLY)
    
    TODO: Remove before production deployment
    This is a developer convenience feature for testing
    """
    logger.warning("⚠️ LOADING KEYS FROM ENVIRONMENT - ADMIN MODE ACTIVE")
    
    for key_name in self.REQUIRED_KEYS:
        value = os.environ.get(key_name)
        if value:
            self.keys[key_name] = value
            logger.info(f"  ✓ Loaded {key_name} from environment")
    
    for key_name in self.OPTIONAL_KEYS:
        value = os.environ.get(key_name)
        if value:
            self.keys[key_name] = value
            logger.info(f"  ✓ Loaded {key_name} from environment")
    
    if self.keys:
        logger.warning(f"🔧 Admin mode loaded {len(self.keys)} keys from environment variables")
```

---

## Security Considerations

### Why This Is Development-Only

1. **Environment Variable Exposure**: Loading keys from environment variables can expose them in process listings
2. **No Validation**: Admin mode bypasses format validation
3. **No User Consent**: Keys are loaded without explicit user configuration
4. **Audit Trail**: No record of where keys came from

### Safe Usage

✅ **DO**:
- Use only in local development environment
- Use with your own API keys
- Remove before git commits to production branch
- Document when features are ready for production

❌ **DON'T**:
- Deploy admin features to production
- Share admin scripts with end users
- Use in shared/public environments
- Commit with `ADMIN_MODE=true` in code

---

## Removal Checklist

Before production deployment, remove these items:

### Files to Delete
- [ ] `admin_launch.sh`
- [ ] `docs/ADMIN_MODE.md` (this file)

### Code to Remove

**In `src/utils/api_key_manager.py`**:
- [ ] Remove `ADMIN_MODE` class variable
- [ ] Remove `_load_from_environment()` method
- [ ] Remove admin mode logic in `__init__()`
- [ ] Remove admin mode logging statements

```python
# DELETE THESE LINES:
ADMIN_MODE = os.environ.get('ADMIN_MODE', 'false').lower() == 'true'

if self.ADMIN_MODE and not self.keys:
    self._load_from_environment()
    logger.warning("🔧 ADMIN MODE: Loading API keys from environment variables")

def _load_from_environment(self) -> None:
    # ... entire method
```

### Testing After Removal

1. Delete `.env` file
2. Launch application
3. Verify API configuration screen appears
4. Enter test keys
5. Verify keys save correctly
6. Verify application works with saved keys
7. Restart application
8. Verify keys auto-load from `.env`

---

## Examples

### Example 1: Quick Development Testing

```bash
# Morning: Start working
cd Research-Assistant
./admin_launch.sh              # Restores keys, launches app
# Test features...
# Ctrl+C to stop

# Test API config screen
./admin_launch.sh clean
python main.py
# Enter keys through UI...
# Ctrl+C

# Back to normal testing
./admin_launch.sh restore
python main.py
```

---

### Example 2: Environment Variable Testing

```bash
# Add to your ~/.zshrc or ~/.bashrc
export GEMINI_API_KEY="AIzaSy..."
export SERPAPI_KEY="..."

# Then launch with admin mode when needed
export ADMIN_MODE=true
python main.py

# Or without modifying shell config
ADMIN_MODE=true GEMINI_API_KEY="..." SERPAPI_KEY="..." python main.py
```

---

### Example 3: CI/CD Testing (NOT PRODUCTION)

```yaml
# .github/workflows/test.yml (example - don't use in production)
name: Test Application

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Test with admin mode
        env:
          ADMIN_MODE: true
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          SERPAPI_KEY: ${{ secrets.SERPAPI_KEY }}
        run: |
          python -c "from src.utils.api_key_manager import APIKeyManager; mgr = APIKeyManager(); print('Keys loaded:', mgr.has_all_required_keys())"
```

---

## FAQ

### Q: Can I use admin mode in production?
**A**: No. Admin mode is a development convenience and must be removed before production deployment.

### Q: What if I forget to remove admin features?
**A**: Follow the removal checklist above. The code includes TODO comments to help identify admin-only code.

### Q: Why not just use environment variables for everyone?
**A**: 
- Security: Environment variables can be exposed in process listings
- User Experience: Configuration UI is more user-friendly
- Validation: UI validates keys before accepting them
- Documentation: Built-in help links in the UI

### Q: Can end users accidentally enable admin mode?
**A**: Only if they set `ADMIN_MODE=true` environment variable and restart the app. It's not exposed in the UI.

### Q: How do I know if admin mode is active?
**A**: Check the console logs for warning messages:
```
🔧 ADMIN MODE: Loading API keys from environment variables
⚠️ LOADING KEYS FROM ENVIRONMENT - ADMIN MODE ACTIVE
```

---

## Related Documentation

- **API Key Setup**: See `docs/API_KEY_SETUP.md`
- **Quick Start**: See `docs/QUICK_START.md`
- **Implementation Details**: See `docs/API_KEY_IMPLEMENTATION.md`

---

*This is a development-only feature. Remove before production deployment.*

**TODO Marker**: Search codebase for "TODO: Remove this before production deployment"
