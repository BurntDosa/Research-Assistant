# Production Deployment Checklist

This checklist ensures all development-only features are removed before deploying to production.

## ⚠️ CRITICAL: Remove Admin Features

### Files to Delete

- [ ] `admin_launch.sh` - Admin convenience script
- [ ] `docs/ADMIN_MODE.md` - Admin feature documentation
- [ ] `docs/PRODUCTION_CHECKLIST.md` - This file
- [ ] `.env.backup.*` - All backup .env files

```bash
# Command to remove files
rm -f admin_launch.sh
rm -f docs/ADMIN_MODE.md
rm -f docs/PRODUCTION_CHECKLIST.md
rm -f .env.backup.*
```

### Code Changes Required

#### 1. `src/utils/api_key_manager.py`

**Remove these sections:**

```python
# DELETE THIS:
# ========== ADMIN OVERRIDE FOR TESTING ==========
# TODO: Remove this before production deployment
# This allows developers to bypass API key configuration during development
ADMIN_MODE = os.environ.get('ADMIN_MODE', 'false').lower() == 'true'
```

```python
# DELETE THIS from __init__:
# Admin override: Load keys from environment variables if ADMIN_MODE is enabled
if self.ADMIN_MODE and not self.keys:
    self._load_from_environment()
    logger.warning("🔧 ADMIN MODE: Loading API keys from environment variables")
```

```python
# DELETE THIS ENTIRE METHOD:
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

**After removal, `__init__` should look like:**

```python
def __init__(self, config_file: str = ".env"):
    """Initialize API Key Manager"""
    self.config_file = Path(config_file)
    self.keys = {}
    self.load_keys()
```

---

## Security Review

### API Keys
- [ ] No hardcoded API keys in code
- [ ] `.env` file is in `.gitignore`
- [ ] `.env.example` contains only placeholders
- [ ] All API keys use environment variables or `.env` file
- [ ] No API keys in git history (check: `git log -p | grep -i "api.*key"`)

### Admin Features
- [ ] `ADMIN_MODE` environment variable removed
- [ ] `_load_from_environment()` method removed
- [ ] Admin launch script deleted
- [ ] Admin documentation deleted
- [ ] No "TODO: Remove before production" comments remaining

### Sensitive Data
- [ ] No database credentials hardcoded
- [ ] No user data in repository
- [ ] No test API keys committed
- [ ] No backup files committed (`.env.backup.*`)

---

## Functionality Testing

### API Key Configuration
- [ ] Launch with no `.env` file shows configuration screen
- [ ] All required API key fields present
- [ ] Links to get API keys work
- [ ] Key validation works (format checking)
- [ ] Keys save correctly to `.env`
- [ ] Success message shows after saving
- [ ] UI switches to main app after configuration
- [ ] Error messages clear and helpful

### API Key Loading
- [ ] Restart with `.env` file loads keys automatically
- [ ] Application goes directly to main interface
- [ ] All features work with loaded keys
- [ ] Invalid keys show appropriate errors
- [ ] Missing required keys prevent app from starting

### Core Features
- [ ] Literature search works
- [ ] Literature review generation works
- [ ] Research gap analysis works
- [ ] Feasibility assessment works
- [ ] LaTeX writing assistant works
- [ ] PDF upload works
- [ ] All agents initialize correctly

---

## Code Quality

### Search for Development Artifacts
```bash
# Search for TODO comments
grep -r "TODO.*[Rr]emove.*production" .

# Search for admin mode references
grep -r "ADMIN_MODE" .

# Search for admin logging
grep -r "ADMIN.*MODE" .

# Search for backup file patterns
grep -r "\.env\.backup" .
```

### Remove Debug Code
- [ ] No `print()` statements for debugging
- [ ] No excessive logging
- [ ] No commented-out code blocks
- [ ] No development-only imports

### Documentation
- [ ] README.md updated for production
- [ ] API_KEY_SETUP.md reviewed
- [ ] QUICK_START.md reviewed
- [ ] All documentation references admin mode removed

---

## Deployment Configuration

### Environment Variables
Production environment should set:
```bash
# Not needed in production (should be removed):
# ADMIN_MODE=true  ❌ DELETE THIS

# These are fine (users provide via UI):
# GEMINI_API_KEY   ✅ Set by users through UI
# SERPAPI_KEY      ✅ Set by users through UI
```

### Application Settings
- [ ] Debug mode disabled
- [ ] Logging level appropriate (INFO or WARNING)
- [ ] Error handling production-ready
- [ ] Database paths configured correctly

---

## Git Preparation

### Commit Changes
```bash
# Create a production-ready commit
git add -A
git commit -m "Remove admin features for production deployment"
```

### Tag Release
```bash
# Tag the production release
git tag -a v1.0.0-production -m "Production release - admin features removed"
git push origin v1.0.0-production
```

### Verify Clean Repository
```bash
# Check for uncommitted changes
git status

# Check .gitignore is working
git check-ignore .env .env.backup.*

# Verify no sensitive files tracked
git ls-files | grep -E "\.(env|key|pem|crt)"
```

---

## Final Verification

### Pre-Deployment Test
```bash
# 1. Clean install
rm -rf venv_gemini
python -m venv venv_gemini
source venv_gemini/bin/activate
pip install -r requirements.txt

# 2. Remove .env
rm -f .env .env.backup.*

# 3. Test launch
python main.py
# Should show API configuration screen

# 4. Configure with test keys
# Enter keys through UI

# 5. Verify functionality
# Test all major features

# 6. Restart
# Should load keys automatically
python main.py
```

### Security Scan
```bash
# Check for exposed secrets
git secrets --scan

# Check for vulnerable dependencies
pip-audit

# Check for security issues
bandit -r src/
```

---

## Deployment Steps

### 1. Prepare Codebase
- [ ] Complete all checklist items above
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Git repository clean

### 2. Build Deployment Package
```bash
# Create deployment directory
mkdir -p deployment
cp -r src/ deployment/
cp -r docs/ deployment/
cp main.py deployment/
cp requirements.txt deployment/
cp .env.example deployment/
cp README.md deployment/

# Remove development files
rm -f deployment/admin_launch.sh
rm -f deployment/docs/ADMIN_MODE.md
rm -f deployment/docs/PRODUCTION_CHECKLIST.md
```

### 3. Deploy
- [ ] Upload to production server
- [ ] Install dependencies
- [ ] Configure environment
- [ ] Test API key configuration
- [ ] Test core functionality
- [ ] Monitor logs for errors

### 4. Post-Deployment
- [ ] Verify API key screen shows for new users
- [ ] Verify all features work
- [ ] Check error handling
- [ ] Monitor performance
- [ ] Set up error alerting

---

## Rollback Plan

If issues are found after deployment:

1. **Immediate**: Revert to previous version
   ```bash
   git checkout v0.9.0  # Previous stable version
   ```

2. **Fix Issues**: Address problems in development

3. **Re-test**: Complete this checklist again

4. **Re-deploy**: Deploy fixed version

---

## Success Criteria

✅ Deployment is successful when:

1. **No Admin Features**: No admin mode code in production
2. **API Keys Work**: Users can configure their own keys
3. **All Features Work**: Every feature functions correctly
4. **Security**: No hardcoded credentials or sensitive data
5. **Documentation**: User docs are complete and accurate
6. **Performance**: Application runs smoothly
7. **Error Handling**: Errors are handled gracefully
8. **Logging**: Appropriate information logged

---

## Post-Production Maintenance

### Regular Tasks
- Monitor error logs
- Update dependencies
- Review security advisories
- Collect user feedback
- Plan feature updates

### API Key Management
- Monitor API usage/costs
- Update documentation if provider APIs change
- Add new API providers as needed

---

## Contact

For deployment questions:
- Review documentation in `docs/`
- Check issue tracker
- Contact development team

---

*Complete this checklist before every production deployment.*

**Last Updated**: October 2025
