# بررسی Deploy در Scalingo

## وضعیت فعلی

- ✅ کد commit شده (commit: e55618e)
- ✅ کد push شده
- ❓ اما در لاگ‌ها Project ID را نمی‌بینیم

## بررسی‌های لازم

### 1. بررسی که Scalingo deploy کرده

در Scalingo Dashboard:
- به بخش "Deployments" بروید
- بررسی کنید که آخرین commit `e55618e` deploy شده باشد
- اگر deploy نشده، manual deploy کنید

### 2. بررسی که کد جدید در Scalingo است

بعد از deploy، یک notification تست بفرستید و این لاگ‌ها را ببینید:

```powershell
scalingo --app mywebsite logs --follow | Select-String "DEBUG.*Project ID|DEBUG.*Service account|DEBUG.*Firebase"
```

**باید ببینید:**
```
✅ DEBUG: Attempting to load from FIREBASE_CREDENTIALS_BASE64
✅ DEBUG: Successfully decoded Base64 and parsed JSON
✅ DEBUG: Project ID from credentials: bonusapp-1146e
✅ DEBUG: Service account email: firebase-adminsdk-...@bonusapp-1146e.iam.gserviceaccount.com
✅ DEBUG: Firebase Admin SDK initialized successfully
```

**اگر نمی‌بینید:**
- کد جدید deploy نشده
- باید manual deploy کنید

### 3. Manual Deploy (اگر لازم است)

```powershell
# اگر Scalingo auto-deploy نمی‌کند:
scalingo --app mywebsite deploy
```

یا از Scalingo Dashboard:
- Deployments → New deployment → Select commit `e55618e`

## مشکل اصلی: Service Account Permissions

حتی اگر کد deploy شود، اگر Service Account role `Firebase Cloud Messaging Admin` را نداشته باشد، هنوز خطای 404 می‌آید.

### راه حل: اضافه کردن Role

1. به Google Cloud Console بروید:
   ```
   https://console.cloud.google.com/iam-admin/iam?project=bonusapp-1146e
   ```

2. Service Account جدید را پیدا کنید:
   - Email: `firebase-adminsdk-fbsvc@bonusapp-1146e.iam.gserviceaccount.com`
   - یا با `private_key_id`: `5883daf59c95051a63a845dc3a6190d6bbc4a5c4`

3. Edit → Add Another Role → `Firebase Cloud Messaging Admin`

4. Save

5. 5-10 دقیقه صبر کنید

6. یک notification تست بفرستید

## مراحل بعدی

1. ✅ کد commit شده
2. ⏳ بررسی کنید Scalingo deploy کرده
3. ⏳ Service Account role را اضافه کنید
4. ⏳ یک notification تست بفرستید
5. ⏳ لاگ‌ها را بررسی کنید

