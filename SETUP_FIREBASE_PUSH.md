## Firebase Web Push Setup

### 1. Encode service-account JSON (local shell)

```powershell
Get-Content firebase-service-account.json -Raw | `
  python - <<'PY'
import base64, sys
print(base64.b64encode(sys.stdin.read().encode()).decode())
PY
```

Save the output to use as `FIREBASE_CREDENTIALS_BASE64`.

### 2. Set environment variables (Scalingo example)

```powershell
scalingo --app mywebsite env-set `
  FIREBASE_CREDENTIALS_BASE64="...base64..." `
  VAPID_PUBLIC_KEY="BN46F80CdmxtQtJxgV7Wfc6NXlfSh74q4UdOnAaY-2V4XkWrny0al4bojY_zvZwERirc52upAT0pXSSeIs_qKls" `
  FIREBASE_WEB_API_KEY="AIzaSyBuZrl2zjPrpOFD_2pZKJTDe1AiRUArviA" `
  FIREBASE_WEB_AUTH_DOMAIN="bonusapp-1146e.firebaseapp.com" `
  FIREBASE_WEB_PROJECT_ID="bonusapp-1146e" `
  FIREBASE_WEB_STORAGE_BUCKET="bonusapp-1146e.firebasestorage.app" `
  FIREBASE_WEB_SENDER_ID="127439540218" `
  FIREBASE_WEB_APP_ID="1:127439540218:web:c504c60bc6db03c2181e43" `
  FIREBASE_WEB_MEASUREMENT_ID="G-3BF4XCB9VZ"
```

Restart app after setting env vars:

```powershell
scalingo --app mywebsite restart
```

For local development, add the same keys to `.env`:

```
FIREBASE_CREDENTIALS_BASE64=...
VAPID_PUBLIC_KEY=BN46...
FIREBASE_WEB_API_KEY=...
```

### 3. Verify

1. Run `python manage.py runserver`
2. Login to `/partners/`
3. Browser should prompt for notification permission
4. Service worker `firebase-messaging-sw.js` should be registered (check DevTools → Application → Service Workers)
5. Click "Send Test Notification" (if implemented) or call `POST /api/notifications/send-test/`

