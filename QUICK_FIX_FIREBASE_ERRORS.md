# Quick Fix for Firebase Errors

## Current Issues

Based on your logs, you have two problems:

1. **`FIREBASE_CREDENTIALS_FILE` is set to `/path/to/service-account.json`** (placeholder value)
2. **`FCM_SERVER_KEY` is not configured**

## Immediate Fix Commands

### Step 1: Remove the Placeholder Environment Variable

```powershell
scalingo --app mywebsite env-unset FIREBASE_CREDENTIALS_FILE
```

### Step 2: Set Firebase Credentials (Choose ONE method)

#### Option A: Using Base64 (Recommended)

1. Get your Firebase service account JSON file:
   - Go to https://console.firebase.google.com
   - Select your project → Settings → Service Accounts
   - Click "Generate new private key"
   - Download the JSON file

2. Convert to Base64:
   ```powershell
   $json = Get-Content "service-account.json" -Raw
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
   $base64 = [System.Convert]::ToBase64String($bytes)
   Write-Host $base64
   ```

3. Set in Scalingo:
   ```powershell
   scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_BASE64=<PASTE_BASE64_HERE>"
   ```

#### Option B: Using JSON String (Alternative)

```powershell
# Read JSON file and escape quotes
$json = Get-Content "service-account.json" -Raw
$jsonEscaped = $json -replace '"', '\"'
scalingo --app mywebsite env-set "FIREBASE_CREDENTIALS_JSON=$jsonEscaped"
```

### Step 3: Set FCM Server Key

1. Get your FCM Server Key:
   - Go to https://console.firebase.google.com
   - Select your project → Settings → Cloud Messaging
   - Find "Server key" or "Legacy server key"
   - Copy the key

2. Set in Scalingo:
   ```powershell
   scalingo --app mywebsite env-set "FCM_SERVER_KEY=<YOUR_SERVER_KEY>"
   ```

### Step 4: Restart Your App

```powershell
scalingo --app mywebsite restart
```

### Step 5: Verify

```powershell
scalingo --app mywebsite logs --follow
```

Look for:
- ✅ `DEBUG: Firebase Admin SDK initialized successfully`
- ❌ No more `FileNotFoundError` or `FCM_SERVER_KEY is not configured` errors

## Automated Fix Script

You can also run the automated script:

```powershell
.\fix_scalingo_firebase_env.ps1
```

## What Was Fixed in the Code

The code has been updated to:
1. ✅ Better detect and skip placeholder paths like `/path/to/service-account.json`
2. ✅ Handle missing credentials gracefully without crashing
3. ✅ Provide better error messages
4. ✅ Prevent duplicate Firebase initialization errors

## Environment Variables Priority

Firebase credentials are loaded in this order:
1. `FIREBASE_CREDENTIALS_FILE` (only if file exists and is not a placeholder)
2. `FIREBASE_CREDENTIALS_JSON` (raw JSON string)
3. `FIREBASE_CREDENTIALS_BASE64` (base64 encoded JSON) ← **Recommended**

## Notes

- **Never commit** `service-account.json` to git (already in `.gitignore`)
- Use environment variables for all secrets
- Base64 encoding is recommended for complex JSON strings
- `FCM_SERVER_KEY` is used as a fallback when Firebase Admin SDK is unavailable

