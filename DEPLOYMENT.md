# Deployment Guide for Scalingo

## Prerequisites
- Scalingo account
- Git repository with your code

## Environment Variables
Set these environment variables in your Scalingo dashboard:

```
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=0
ALLOWED_HOSTS=your-app.scalingo.io
STRIPE_SECRET_KEY=your-stripe-secret-key
FIREBASE_CREDENTIALS_FILE=path/to/firebase-credentials.json
AUDIT_LOGGING_ENABLED=1
```

## Database
The app will automatically use PostgreSQL addon if available, otherwise it will use SQLite.

## Static Files
Static files are handled by WhiteNoise and will be automatically collected during deployment.

## Deployment Steps

1. **Connect to Scalingo:**
   ```bash
   scalingo login
   ```

2. **Create a new app:**
   ```bash
   scalingo create your-app-name
   ```

3. **Add PostgreSQL addon:**
   ```bash
   scalingo addons-add postgresql:postgresql-sandbox
   ```

4. **Set environment variables:**
   ```bash
   scalingo env-set DJANGO_SECRET_KEY=your-secret-key
   scalingo env-set DJANGO_DEBUG=0
   scalingo env-set ALLOWED_HOSTS=your-app.scalingo.io
   ```

5. **Deploy:**
   ```bash
   git push scalingo main
   ```

## Troubleshooting

### Static Files Error
If you get static files error, make sure:
- `static/` directory exists
- `whitenoise` is in INSTALLED_APPS
- `whitenoise.middleware.WhiteNoiseMiddleware` is in MIDDLEWARE

### Database Error
If you get database error:
- Check if PostgreSQL addon is installed
- Verify DATABASE_URL environment variable

### Build Error
If build fails:
- Check Python version in runtime.txt
- Verify all dependencies in requirements.txt
- Check for any syntax errors in settings.py
