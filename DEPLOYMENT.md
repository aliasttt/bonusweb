# Deployment Guide for Scalingo

## Environment Variables

Set these environment variables in your Scalingo dashboard. See `ENV_VARIABLES.md` for detailed instructions.

### Required Variables:
- `DJANGO_SECRET_KEY`: Your Django secret key
- `ALLOWED_HOSTS`: Your app domain (e.g., `your-app-name.scalingo.io`)

### Media Storage (IMPORTANT - Prevents File Loss):
**⚠️ CRITICAL**: Scalingo uses an ephemeral filesystem. Uploaded files are **deleted** after each deployment.

**Solution**: Use Cloudinary for media storage:
- `USE_CLOUDINARY=1`: Enable Cloudinary storage
- `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name
- `CLOUDINARY_API_KEY`: Your Cloudinary API key
- `CLOUDINARY_API_SECRET`: Your Cloudinary API secret

Get free Cloudinary account at: https://cloudinary.com/users/register/free

### Optional Variables:
- `DJANGO_DEBUG`: Set to `0` for production
- `STRIPE_SECRET_KEY`: For payment processing
- `FIREBASE_CREDENTIALS_FILE`: For Firebase integration
- `AUDIT_LOGGING_ENABLED`: Set to `1` to enable audit logging

## Database

The app automatically uses PostgreSQL when `DATABASE_URL` is set (which Scalingo does automatically).

## Static Files

Static files are handled by WhiteNoise and collected during deployment.

## Media Files

**IMPORTANT**: Media files (uploaded images) are stored in Cloudinary when configured, preventing file loss on Scalingo's ephemeral filesystem.

- **Without Cloudinary**: Files are stored locally and **will be deleted** on deployment/restart
- **With Cloudinary**: Files are stored permanently in the cloud

See `ENV_VARIABLES.md` for setup instructions.

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

## Troubleshooting Media Files

If you see 404 errors for images:

1. Check if Cloudinary is configured: `scalingo env | grep CLOUDINARY`
2. Run the media check script: `python check_media_files.py`
3. Re-upload missing images (files uploaded before Cloudinary setup are lost)
4. See `ENV_VARIABLES.md` for detailed troubleshooting