# Admin Quick Reference

## 🚀 Quick Commands

### Launch with existing keys
```bash
./admin_launch.sh
```

### Restore keys from backup
```bash
./admin_launch.sh restore
```

### Test API config screen (remove .env)
```bash
./admin_launch.sh clean
python main.py
```

### Launch with environment variables
```bash
export GEMINI_API_KEY="your-key"
export SERPAPI_KEY="your-key"
export ADMIN_MODE=true
python main.py
```

---

## 📁 File Locations

- **Your API Keys**: `.env` (auto-created after first config)
- **Backups**: `.env.backup.*` (timestamped)
- **Admin Script**: `admin_launch.sh`
- **Documentation**: 
  - `docs/ADMIN_MODE.md` - Full admin docs
  - `docs/PRODUCTION_CHECKLIST.md` - Pre-deployment checklist

---

## 🔄 Common Workflows

### Daily Development
```bash
./admin_launch.sh          # Start with your keys
# Work on features...
# Ctrl+C to stop
```

### Test API Config UI
```bash
./admin_launch.sh clean    # Remove .env
python main.py             # See API config screen
# Enter keys...
# Test...
# Ctrl+C
./admin_launch.sh restore  # Get keys back
```

### Switch Projects
```bash
# Backup current keys
cp .env .env.project1

# Use different keys
cp .env.project2 .env
./admin_launch.sh
```

---

## ⚠️ Remember

- Admin features are **temporary** (for development only)
- Delete before production:
  - `admin_launch.sh`
  - `docs/ADMIN_MODE.md`
  - Admin code in `src/utils/api_key_manager.py`
- See `docs/PRODUCTION_CHECKLIST.md` for removal guide

---

## 🎯 Current Status

Your setup:
- ✅ `.env` file exists with your keys
- ✅ Admin script ready to use
- ✅ Application running at: https://b4507cac03d6fdb550.gradio.live
- ✅ Main interface visible (keys loaded)

To test API config screen:
```bash
./admin_launch.sh clean
python main.py
# You'll see the API key configuration screen
```

---

*Quick reference - See `docs/ADMIN_MODE.md` for full documentation*
