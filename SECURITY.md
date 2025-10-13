# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:

1. **DO NOT** open a public issue
2. Contact the maintainers privately via GitHub Security Advisories
3. Or email the project maintainers directly

We take all security reports seriously and will respond promptly.

## API Key Security

### Important: Protecting Your API Keys

This project requires API keys for Google Gemini and other services. **Never commit API keys to version control.**

### Best Practices

1. **Use .env files**: Store your API keys in a `.env` file (already gitignored)
2. **Never commit sensitive files**: The following files are automatically ignored:
   - `.env`
   - `.env.*` (includes `.env.backup`, `.env.local`, etc.)
   - Any file matching pattern `.env*`

3. **Check before committing**: Always review your changes before committing:
   ```bash
   git status
   git diff
   ```

4. **Use .env.example as template**: Copy `.env.example` to `.env` and fill in your keys
   ```bash
   cp .env.example .env
   # Edit .env with your actual keys
   ```

### If You Accidentally Commit an API Key

If you accidentally commit an API key, follow these steps immediately:

1. **Revoke the exposed key**:
   - Google Gemini API: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) and delete the key
   - SerpAPI: Visit [SerpAPI Dashboard](https://serpapi.com/manage-api-key) and revoke the key
   - OpenAI: Visit [OpenAI API Keys](https://platform.openai.com/api-keys) and revoke the key

2. **Generate a new key** from the same dashboard

3. **Remove the key from git history**:
   - If the commit hasn't been pushed yet: `git reset --soft HEAD~1`
   - If already pushed: Contact a maintainer immediately or use tools like `git filter-branch` or `BFG Repo-Cleaner` (advanced users only)

4. **Update your local .env file** with the new key

### What This Project Does to Protect Your Keys

- ✅ `.gitignore` configured to exclude all `.env*` files
- ✅ `.env.example` provided as a safe template (no real keys)
- ✅ No backup files created in the repository directory
- ✅ API keys loaded only from environment variables or `.env` files
- ✅ Keys never logged or displayed in output

### Security Notice - October 2025

**IMPORTANT**: If you obtained this code before October 13, 2025, please verify your `.gitignore` includes:

```
.env
.env.*
```

Previous versions may not have protected `.env.backup` files. Please update your `.gitignore` and check that no sensitive files were committed.

### Revoke Exposed Keys

If you received a notification that your API key was exposed:

1. **Immediately revoke the key** using the provider's dashboard
2. **Generate a new key**
3. **Update your `.env` file** with the new key
4. **Never reuse exposed keys**

### Additional Security Recommendations

1. **Regularly rotate API keys**: Change your keys periodically
2. **Use API key restrictions**: Where possible, restrict keys by:
   - IP address
   - Referrer URL
   - Specific API endpoints
3. **Monitor API usage**: Check your provider dashboards for unusual activity
4. **Use environment-specific keys**: Different keys for development, testing, and production

## Responsible Disclosure

We follow responsible disclosure practices:

- We acknowledge receipt of vulnerability reports within 48 hours
- We aim to provide fixes within 30 days for critical vulnerabilities
- We will credit researchers who report vulnerabilities (if desired)

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2) and announced via:

- GitHub Security Advisories
- Release notes
- README updates

## Questions?

If you have questions about security practices in this project, please open a discussion on GitHub Discussions (not Issues).
