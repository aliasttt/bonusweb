# Environment Variables Guide

## Required Variables

### Django Settings
- `DJANGO_SECRET_KEY`: Your Django secret key (required)
- `ALLOWED_HOSTS`: Your app domain, comma-separated (e.g., `your-app-name.scalingo.io`)
- `DJANGO_DEBUG`: Set to `0` for production, `1` for development

### Database
- `DATABASE_URL`: Automatically set by Scalingo (PostgreSQL connection string)

## Media Storage Configuration

### Problem: File Loss on Scalingo
Scalingo uses an **ephemeral filesystem**, which means uploaded files (media) are **deleted** after each deployment or restart. This causes 404 errors for images.

### Solution: Use Cloudinary (Recommended)

Cloudinary provides free cloud storage for media files. Follow these steps:

1. **Sign up for Cloudinary** (free tier available):
   - Go to https://cloudinary.com/users/register/free
   - Create an account

2. **Get your credentials**:
   - Go to https://cloudinary.com/console
   - Copy your:
     - Cloud Name
     - API Key
     - API Secret

3. **Set environment variables in Scalingo**:
   ```bash
   scalingo env-set USE_CLOUDINARY=1
   scalingo env-set CLOUDINARY_CLOUD_NAME=your-cloud-name
   scalingo env-set CLOUDINARY_API_KEY=your-api-key
   scalingo env-set CLOUDINARY_API_SECRET=your-api-secret
   ```

4. **Deploy**:
   - After setting these variables, deploy your app
   - All new uploads will be stored in Cloudinary
   - Old files that were lost need to be re-uploaded

### Environment Variables for Cloudinary

```bash
USE_CLOUDINARY=1
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

**Note**: If `USE_CLOUDINARY=0` or credentials are missing, the app will use local file storage (which gets deleted on Scalingo).

## Optional Variables

- `STRIPE_SECRET_KEY`: For payment processing
- `FIREBASE_CREDENTIALS_FILE`: For Firebase integration
- `AUDIT_LOGGING_ENABLED`: Set to `1` to enable audit logging (default: `1`)

## Checking Media Files

To check if media files exist in your database and storage:

```bash
python manage.py shell < check_media_files.py
```

Or run it directly:
```bash
python check_media_files.py
```

This script will:
- List all products and sliders with images
- Check if files exist in storage
- Report missing files
- Provide recommendations

## Troubleshooting

### Images showing 404 errors

1. **Check if Cloudinary is enabled**:
   ```bash
   scalingo env | grep CLOUDINARY
   ```

2. **Verify credentials are correct**:
   - Check Cloudinary dashboard
   - Ensure all three variables are set

3. **Check existing files**:
   ```bash
   python check_media_files.py
   ```

4. **Re-upload missing images**:
   - Files uploaded before enabling Cloudinary are lost
   - Re-upload them through the admin panel or API

### Files not uploading

1. Check `USE_CLOUDINARY=1` is set
2. Verify Cloudinary credentials are correct
3. Check Django logs for errors
4. Ensure `django-storages` and `cloudinary` are in `requirements.txt`

