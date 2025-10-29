# Deployment Guide for Scalingo

## Environment Variables

Set these environment variables in your Scalingo dashboard:

### Required Variables:
- `DJANGO_SECRET_KEY`: Your Django secret key
- `ALLOWED_HOSTS`: Your app domain (e.g., `your-app-name.scalingo.io`)

### Optional Variables:
- `DJANGO_DEBUG`: Set to `0` for production
- `STRIPE_SECRET_KEY`: For payment processing
- `FIREBASE_CREDENTIALS_FILE`: For Firebase integration
- `AUDIT_LOGGING_ENABLED`: Set to `1` to enable audit logging

## Database

The app automatically uses PostgreSQL when `DATABASE_URL` is set (which Scalingo does automatically).

## Static Files

Static files are handled by WhiteNoise and collected during deployment.

## Build Process

The build process:
1. Installs dependencies from `requirements.txt`
2. Collects static files
3. Runs database migrations

## Files Included

- `Procfile`: Defines how to start the app
- `runtime.txt`: Specifies Python version
- `scalingo.json`: Scalingo configuration
- `build.sh`: Build script
- `requirements.txt`: Python dependencies