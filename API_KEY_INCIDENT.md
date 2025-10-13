# API Key Exposure Incident - Action Required

## Summary

On October 13, 2025, Google Cloud Platform detected a publicly accessible API key associated with this repository:

- **Project**: RAG Chatbot (id: famous-cogency-461014-e2)
- **Exposed Key**: AIzaSyBQPSOrRrrV13s8xfcQc_ijpIRNBky5lrw
- **Location**: Previously exposed in `.env.backup` file in git history
- **Status**: Key location has been removed from current codebase

## Immediate Actions Required

### 1. Revoke the Exposed API Key (CRITICAL)

**You MUST revoke the exposed key immediately**, even though it's no longer in the current code:

1. Visit [Google AI Studio API Keys](https://makersuite.google.com/app/apikey)
2. Sign in with the Google account associated with project ID `famous-cogency-461014-e2`
3. Find and **DELETE** the key: `AIzaSyBQPSOrRrrV13s8xfcQc_ijpIRNBky5lrw`
4. Generate a new API key
5. Update your local `.env` file with the new key

**Why this is critical**: Once an API key is exposed publicly, it should be considered compromised. Bad actors may have already copied it and could use it to:
- Consume your API quota
- Incur charges on your account
- Access your Google Cloud resources

### 2. Update Your Local Repository

If you have a clone of this repository:

```bash
cd Research-Assistant
git pull origin main
```

This will update your `.gitignore` to properly exclude `.env.backup` and all `.env.*` files.

### 3. Check Your Own Repositories

If you forked this repository or copied code from it:

1. Check your `.gitignore` includes:
   ```
   .env
   .env.*
   ```

2. Search for any `.env.backup` files:
   ```bash
   find . -name ".env.backup" -o -name ".env.*"
   ```

3. If you find any, DELETE them and ensure they're gitignored:
   ```bash
   rm .env.backup .env.*
   git rm --cached .env.backup .env.* 2>/dev/null || true
   git commit -m "security: remove env backup files"
   ```

### 4. Verify No Sensitive Files in Git History

Check your repository for any sensitive files in git history:

```bash
git log --all --full-history -- .env.backup
git log --all --full-history -- .env
```

If you find any, you need to remove them from git history. **Warning**: This rewrites history and requires force push.

For small repositories, you can use git filter-branch:
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env.backup .env .env.*" \
  --prune-empty --tag-name-filter cat -- --all
```

Then force push:
```bash
git push origin --force --all
```

**Note**: Only do this if you're the sole owner of the repository or have coordinated with all collaborators.

## What Changed in This Fix

### Changes Made

1. **Updated `.gitignore`**: Now excludes all `.env.*` files including backups
   ```diff
   # Environments
   .env
   +.env.*
   .envrc
   ```

2. **Removed backup creation**: The `api_key_manager.py` no longer creates `.env.backup` files in the project directory
   - Previous behavior: Created `.env.backup` when saving new keys
   - New behavior: No automatic backups (users should use git or external backup tools)

3. **Added security documentation**:
   - Created `SECURITY.md` with comprehensive security guidelines
   - Created this incident response document

### Why This Happened

The original code created backup files (`.env.backup`) when saving API keys, but these files were not included in `.gitignore`. This meant:

1. A `.env.backup` file was created locally
2. It could be accidentally committed to git
3. Once committed, even if later removed, it remains in git history
4. GitHub's URL to that historical commit exposes the file contents

### Prevention Going Forward

- ✅ `.gitignore` now blocks all `.env*` files
- ✅ No automatic backup files are created
- ✅ Clear documentation on API key security
- ✅ Security policy in place

## FAQ

### Q: Is the key still in the repository?

No, the key is not in the current repository code. However, it may still exist in git history, which is why it must be revoked.

### Q: Do I need to change my API key if I just cloned the repo?

If you created your own API key and stored it in your local `.env` file, your key was never exposed. However, if you somehow used the key from the example or a backup file, you should create your own key.

### Q: The exposed key wasn't mine, do I need to do anything?

Update your repository to get the security fixes:
```bash
git pull origin main
```

And ensure your `.env` file is never committed.

### Q: How do I know if my key was exposed?

Check your git history:
```bash
git log --all --full-history --diff-filter=A -- .env .env.backup
```

If you see any commits, your key may have been exposed. Revoke and regenerate it immediately.

### Q: Can I still create backups of my .env file?

Yes, but store them outside the repository directory:
```bash
# Good - backup outside repo
cp .env ~/backups/research-assistant-env-backup-$(date +%Y%m%d)

# Bad - backup in repo directory (may be accidentally committed)
cp .env .env.backup
```

### Q: I'm getting "Invalid API key" errors after updating

You need to revoke the old key and create a new one, then update your `.env` file. See "Immediate Actions Required" above.

## Support

If you need help with this security incident:

1. For key revocation issues: Contact Google Cloud Support
2. For repository issues: Open a discussion on GitHub (NOT an issue, to avoid exposing details)
3. For urgent security concerns: Use GitHub Security Advisories

## Timeline

- **Unknown Date**: `.env.backup` file was created and committed
- **Unknown Date**: Commit was pushed to GitHub
- **October 13, 2025**: Google detected exposed key and sent notification
- **October 13, 2025**: Security fixes implemented and deployed

## Additional Resources

- [Google API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)
- [GitHub: Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [OWASP: API Security Top 10](https://owasp.org/www-project-api-security/)

---

**Remember**: When in doubt, revoke and regenerate. It's always safer to create a new API key than to risk using a potentially compromised one.
