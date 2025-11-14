#!/bin/bash
# Script to set Cloudinary environment variables in Scalingo
# Usage: ./setup_cloudinary_scalingo.sh YOUR_API_SECRET [APP_NAME]
# Or set SCALINGO_APP environment variable

if [ -z "$1" ]; then
    echo "Error: API Secret is required"
    echo "Usage: ./setup_cloudinary_scalingo.sh YOUR_API_SECRET [APP_NAME]"
    exit 1
fi

API_SECRET=$1
APP_NAME=$2

# Try to detect app name from git remote if not provided
if [ -z "$APP_NAME" ]; then
    echo "Trying to detect app name from git remote..."
    GIT_REMOTE=$(git remote get-url scalingo 2>/dev/null)
    if [ ! -z "$GIT_REMOTE" ]; then
        APP_NAME=$(echo "$GIT_REMOTE" | sed -n 's/.*scalingo\.com[:/]\([^/]*\)\.git.*/\1/p')
        if [ ! -z "$APP_NAME" ]; then
            echo "Detected app name: $APP_NAME"
        fi
    fi
fi

# Check if SCALINGO_APP is set
if [ -z "$APP_NAME" ] && [ ! -z "$SCALINGO_APP" ]; then
    APP_NAME=$SCALINGO_APP
fi

if [ -z "$APP_NAME" ]; then
    echo "Error: App name is required!"
    echo "Usage: ./setup_cloudinary_scalingo.sh YOUR_SECRET APP_NAME"
    echo "Or set SCALINGO_APP environment variable"
    exit 1
fi

echo "Setting Cloudinary environment variables in Scalingo for app: $APP_NAME"
echo ""

scalingo --app "$APP_NAME" env-set USE_CLOUDINARY=1
scalingo --app "$APP_NAME" env-set CLOUDINARY_CLOUD_NAME=993373522259225
scalingo --app "$APP_NAME" env-set CLOUDINARY_API_KEY=G0UxjA_EEAJ9T_BMd9LS6WOdnZo
scalingo --app "$APP_NAME" env-set CLOUDINARY_API_SECRET="$API_SECRET"

echo ""
echo "✅ Cloudinary environment variables set successfully!"
echo ""
echo "Verifying settings..."
scalingo --app "$APP_NAME" env | grep CLOUDINARY
echo ""
echo "⚠️  Don't forget to restart your app:"
echo "   scalingo --app $APP_NAME restart"

