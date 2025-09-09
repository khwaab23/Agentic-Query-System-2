# 🚨 URGENT: Remove .env from GitHub Repository

The `.env` file with your API key is still visible on GitHub. Here's how to remove it:

## Option 1: Quick Fix (Recommended)

### Step 1: Clone/Pull the repository locally
```bash
git clone https://github.com/khwaab23/Agentic-Query-System-2.git
cd Agentic-Query-System-2
```

### Step 2: Remove .env from git tracking
```bash
git rm .env
```

### Step 3: Commit and push the removal
```bash
git commit -m "Remove .env file containing API key for security"
git push origin main
```

## Option 2: Complete History Cleanup (More Secure)

If you want to remove the API key from all Git history:

### Step 1: Remove from all history using git filter-branch
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

### Step 2: Force push to overwrite history
```bash
git push origin --force --all
```

## Option 3: GitHub Web Interface

1. Go to https://github.com/khwaab23/Agentic-Query-System-2
2. Navigate to the .env file
3. Click the trash icon to delete it
4. Commit the deletion directly on GitHub

## ⚠️ CRITICAL: After Removing from GitHub

1. **Immediately rotate your API key**:
   - Go to https://platform.openai.com/api-keys
   - Delete the exposed key
   - Generate a new one
   - Update your local .env file

2. **The exposed key was**:
   ```
   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
   ```

## After Cleanup

1. ✅ .gitignore is already set up to prevent future .env commits
2. ✅ SECURITY.md provides ongoing guidance
3. ✅ .env.example shows the proper template
4. ✅ Update your local .env with the new API key

**Do this immediately to secure your OpenAI account!**
