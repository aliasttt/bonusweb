# Deploy Firebase Fix - Step by Step

## Current Situation

Your logs show errors because:
1. ✅ Code has been fixed locally (better error handling)
2. ❌ Code changes haven't been deployed to Scalingo yet
3. ❌ Environment variables still need to be configured

## Step 1: Deploy Code Changes

You need to commit and push the code changes, then deploy to Scalingo.

### Option A: If using Git (Recommended)

```powershell
# Check what files changed
git status

# Add the changed files
git add notifications/services.py QUICK_FIX_FIREBASE_ERRORS.md

# Commit
git commit -m "Fix Firebase credential loading and error handling"

# Push to your repository
git push origin main  # or your branch name

# Deploy to Scalingo (if auto-deploy is enabled, this happens automatically)
# Otherwise, Scalingo will detect the push and redeploy
```

### Option B: Manual Deployment

If you're not using Git, you can manually upload the files via Scalingo dashboard or use their CLI.

## Step 2: Fix Environment Variables (Do This Now)

Even before deploying, you can fix the environment variables. This will help once the code is deployed.

### Remove Placeholder Variable

```powershell
scalingo --app mywebsite env-unset FIREBASE_CREDENTIALS_FILE
```

### Set Firebase Credentials (Base64 Method - Recommended)

1. **Get your Firebase service account JSON:**
   - Go to https://console.firebase.google.com
   - Select your project → Settings → Service Accounts
   - Click "Generate new private key"
   - Download the JSON file

2. **Convert to Base64:**
   ```powershell
   $json = Get-Content "service-account.json" -Raw
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
   $base64 = [System.Convert]::ToBase64String($bytes)
   Write-Host $base64
   ```

3. **Set in Scalingo:**
   ```powershell
   scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=<PASTE_THE_BASE64_STRING_HERE>"
   ```

### Set FCM Server Key

1. **Get your FCM Server Key:**
   - Go to https://console.firebase.google.com
   - Select your project → Settings → Cloud Messaging
   - Find "Server key" or "Legacy server key"
   - Copy the key

2. **Set in Scalingo:**
   ```powershell
   scalingo --app mywebsite env-set "FCM_SERVER_KEY=<YOUR_SERVER_KEY>"
   ```

## Step 3: Restart Your App

```powershell
scalingo --app mywebsite restart
```

## Step 4: Verify

```powershell
scalingo --app mywebsite logs --follow
```

**Look for:**
- ✅ `DEBUG: Skipping FIREBASE_CREDENTIALS_FILE (detected placeholder): /path/to/service-account.json`
- ✅ `DEBUG: Firebase Admin SDK initialized successfully` (if credentials are set)
- ✅ No more `FileNotFoundError` errors
- ✅ No more `FCM_SERVER_KEY is not configured` errors

## Quick Commands Summary

```powershell
# 1. Remove placeholder
scalingo --app mywebsite env-unset FIREBASE_CREDENTIALS_FILE

# 2. Set Firebase credentials (after converting JSON to Base64)
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=<BASE64>"

# 3. Set FCM key
scalingo --app mywebsite env-set "FCM_SERVER_KEY=<KEY>"

# 4. Restart
scalingo --app mywebsite restart

# 5. Check logs
scalingo --app mywebsite logs --follow
```

## What the Code Fix Does

The updated code:
1. ✅ Detects placeholder paths like `/path/to/service-account.json` and skips them
2. ✅ Handles missing credentials gracefully without crashing
3. ✅ Provides better debug messages
4. ✅ Prevents duplicate Firebase initialization errors
5. ✅ Allows the app to continue working even if Firebase isn't configured

## Troubleshooting

### If errors persist after deployment:

1. **Check if code was deployed:**
   ```powershell
   # Check recent deployments
   scalingo --app mywebsite deployments
   ```

2. **Verify environment variables:**
   ```powershell
   scalingo --app mywebsite env | Select-String "FIREBASE|FCM"
   ```

3. **Check for the new debug messages:**
   - If you see `DEBUG: Skipping FIREBASE_CREDENTIALS_FILE (detected placeholder)`, the new code is running
   - If you still see `FileNotFoundError`, the old code is still running

### If FCM_SERVER_KEY errors persist:

- Make sure you set `FCM_SERVER_KEY` (not just Firebase credentials)
- The FCM Server Key is different from the service account JSON
- It's used as a fallback when Firebase Admin SDK isn't available

