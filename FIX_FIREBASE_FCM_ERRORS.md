# Fix Firebase/FCM Configuration Errors

## Problem

Your Scalingo logs show two errors:
1. `FileNotFoundError: [Errno 2] No such file or directory: '/path/to/service-account.json'`
2. `FCM_SERVER_KEY is not configured`

## Root Cause

1. **Placeholder path**: `FIREBASE_CREDENTIALS_FILE` is set to `/path/to/service-account.json` (a placeholder value)
2. **Missing FCM key**: `FCM_SERVER_KEY` environment variable is not set in Scalingo

## Solution

### Step 1: Fix Firebase Credentials

You have two options:

#### Option A: Use Base64 (Recommended)

1. **Get your Firebase service account JSON**:
   - Go to https://console.firebase.google.com
   - Select your project → Settings → Project settings → Service accounts
   - Click "Generate new private key"
   - Download the JSON file

2. **Convert to Base64** (PowerShell):
   ```powershell
   $json = Get-Content "service-account.json" -Raw
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
   $base64 = [System.Convert]::ToBase64String($bytes)
   Write-Host $base64
   ```

3. **Set in Scalingo**:
   ```powershell
   scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=<PASTE_BASE64_HERE>"
   ```

4. **Remove the placeholder file path**:
   ```powershell
   scalingo --app mywebsite env-unset "FIREBASE_CREDENTIALS_FILE"
   ```

#### Option B: Use JSON String

```powershell
# Read JSON file
$json = Get-Content "service-account.json" -Raw

# Set in Scalingo (escape quotes if needed)
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_JSON=$json"

# Remove placeholder
scalingo --app mywebsite env-unset "FIREBASE_CREDENTIALS_FILE"
```

### Step 2: Configure FCM_SERVER_KEY

1. **Get your FCM Server Key**:
   - Go to https://console.firebase.google.com
   - Select your project → Settings → Project settings → Cloud Messaging
   - Find "Server key" or "Legacy server key"
   - Copy the key

2. **Set in Scalingo**:
   ```powershell
   scalingo --app mywebsite env-set "FCM_SERVER_KEY=<YOUR_SERVER_KEY>"
   ```

### Step 3: Restart Your App

```powershell
scalingo --app mywebsite restart
```

### Step 4: Verify

Check logs to ensure Firebase initializes correctly:

```powershell
scalingo --app mywebsite logs --follow
```

Look for:
- ✅ `DEBUG: Firebase Admin SDK initialized successfully`
- ❌ No more `FileNotFoundError` or `FCM_SERVER_KEY is not configured` errors

## Quick Fix Script

Run the automated script:

```powershell
.\fix_scalingo_firebase_env.ps1
```

This script will:
- Check current environment variables
- Detect placeholder values
- Guide you through configuration

## Code Changes Made

The code has been updated to:
1. ✅ Skip placeholder paths like `/path/to/service-account.json`
2. ✅ Better error messages for missing FCM_SERVER_KEY
3. ✅ Graceful handling of missing configurations

## Environment Variables Priority

Firebase credentials are loaded in this order:
1. `FIREBASE_CREDENTIALS_FILE` (only if file exists and is not a placeholder)
2. `FIREBASE_CREDENTIALS_JSON` (raw JSON string)
3. `FIREBASE_CREDENTIALS_BASE64` (base64 encoded JSON) ← **Recommended**

## Notes

- **Never commit** `service-account.json` to git (already in `.gitignore`)
- Use environment variables for all secrets
- Base64 encoding is recommended for complex JSON strings
- FCM_SERVER_KEY is used as a fallback when Firebase Admin SDK is unavailable



