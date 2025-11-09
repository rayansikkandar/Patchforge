# Security Guidelines

## API Keys and Secrets

**⚠️ IMPORTANT: Never commit real API keys to git!**

### Setup Instructions

1. **Copy the template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your real keys:**
   ```bash
   # Edit .env with your actual credentials
   NVIDIA_API_KEY=your_actual_nvidia_key_here
   GITHUB_TOKEN=your_actual_github_token_here
   NVD_API_KEY=your_actual_nvd_key_here  # Optional
   ```

3. **Verify `.env` is ignored:**
   ```bash
   git check-ignore .env
   # Should output: .env
   ```

### Alternative: Shell Environment Variables

Instead of using `.env`, you can export keys in your shell profile:

**For zsh (~/.zshrc):**
```bash
export NVIDIA_API_KEY="your_actual_key"
export GITHUB_TOKEN="your_actual_token"
export NVD_API_KEY="your_actual_key"  # Optional
```

**For bash (~/.bashrc):**
```bash
export NVIDIA_API_KEY="your_actual_key"
export GITHUB_TOKEN="your_actual_token"
export NVD_API_KEY="your_actual_key"  # Optional
```

Then reload your shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Production/CI Environments

For shared or production environments, use your platform's secrets manager:

- **GitHub Actions**: Use repository secrets
- **AWS**: Use AWS Secrets Manager
- **macOS**: Use Keychain Access
- **Docker**: Use Docker secrets
- **Kubernetes**: Use Kubernetes secrets

Inject them as environment variables before running PatchForge.

### If You Accidentally Committed Secrets

If you accidentally committed real API keys:

1. **Rotate the keys immediately** in the respective services
2. **Remove from git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (if already pushed):
   ```bash
   git push origin --force --all
   ```
4. **Update `.gitignore`** to ensure `.env` is ignored

### Best Practices

- ✅ Keep `.env.example` with placeholder values only
- ✅ Add `.env` to `.gitignore` (already done)
- ✅ Use environment variables or secrets managers in production
- ✅ Rotate keys regularly
- ✅ Never share keys in chat, email, or documentation
- ✅ Use different keys for development and production

