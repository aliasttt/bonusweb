from pathlib import Path
from datetime import timedelta
import os


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-me")
# DEBUG: Set to True by default for development, use DJANGO_DEBUG=0 to disable
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "whitenoise.runserver_nostatic",  # WhiteNoise for static files
    # Local apps
    "marketing",
    "partners",
    "loyalty",
    "accounts",
    "campaigns",
    "qr",
    "rewards",
    "reviews",
    "payments",
    "analytics",
    "securityapp",
    "notifications",
]

# Add Cloudinary apps conditionally (will be enabled if credentials are provided)
# This prevents import errors if cloudinary is not installed
try:
    import cloudinary
    INSTALLED_APPS += ["cloudinary", "cloudinary_storage"]
except ImportError:
    pass


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # WhiteNoise for static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "config.middleware.APIAppendSlashMiddleware",  # Custom middleware to disable APPEND_SLASH for API routes
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "accounts.middleware.UserActivityMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "securityapp.middleware.AuditLogMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.firebase_settings",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# Database configuration
if os.environ.get("DATABASE_URL"):
    # Production database (PostgreSQL for Scalingo)
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL"))
    }
else:
    # Development database (SQLite)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("de", "Deutsch"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media (uploads)
# Use Cloudinary in production (Scalingo) to prevent file loss
# In development, use local file storage
USE_CLOUDINARY = os.environ.get("USE_CLOUDINARY", "0") == "1"
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")

if USE_CLOUDINARY and CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    # Production: Use Cloudinary for media storage
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
        )
        DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
        MEDIA_URL = "/media/"  # URLs will be served by Cloudinary
    except ImportError:
        # Fallback to local storage if cloudinary is not installed
        MEDIA_URL = "/media/"
        MEDIA_ROOT = BASE_DIR / "media"
else:
    # Development: Use local file storage
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Authentication URLs
LOGIN_URL = "/partners/login/"
LOGIN_REDIRECT_URL = "/partners/dashboard/"


CORS_ALLOW_ALL_ORIGINS = True


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",  # Add session auth for web views
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
}


SIMPLE_JWT = {
    # Longer-lived tokens to reduce unexpected logouts in the mobile app
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=180),
}


SPECTACULAR_SETTINGS = {
    "TITLE": "Restaurant–Customer Platform API",
    "DESCRIPTION": "Multi-phase backend API for web admin and mobile app",
    "VERSION": "1.0.0",
}

# Email settings
# In production, set EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@localhost")

if EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    # Fallback to console backend for development if SMTP is not configured
    EMAIL_BACKEND = os.environ.get(
        "EMAIL_BACKEND",
        "django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend",
    )


# External services
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
FIREBASE_CREDENTIALS_FILE = os.environ.get("FIREBASE_CREDENTIALS_FILE", "")
FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON", "")
FIREBASE_CREDENTIALS_BASE64 = os.environ.get("FIREBASE_CREDENTIALS_BASE64", "")
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
FCM_SERVER_KEY = os.environ.get("FCM_SERVER_KEY", "")
FCM_HTTP_API_URL = os.environ.get("FCM_HTTP_API_URL", "https://fcm.googleapis.com/fcm/send")

FIREBASE_CONFIG = {
    "apiKey": os.environ.get("FIREBASE_WEB_API_KEY", "AIzaSyBuZrl2zjPrpOFD_2pZKJTDe1AiRUArviA"),
    "authDomain": os.environ.get("FIREBASE_WEB_AUTH_DOMAIN", "bonusapp-1146e.firebaseapp.com"),
    "projectId": os.environ.get("FIREBASE_WEB_PROJECT_ID", "bonusapp-1146e"),
    "storageBucket": os.environ.get("FIREBASE_WEB_STORAGE_BUCKET", "bonusapp-1146e.firebasestorage.app"),
    "messagingSenderId": os.environ.get("FIREBASE_WEB_SENDER_ID", "127439540218"),
    "appId": os.environ.get("FIREBASE_WEB_APP_ID", "1:127439540218:web:c504c60bc6db03c2181e43"),
    "measurementId": os.environ.get("FIREBASE_WEB_MEASUREMENT_ID", "G-3BF4XCB9VZ"),
}

# Unsplash API
# Use UNSPLASH_ACCESS_TOKEN for OAuth (recommended) or UNSPLASH_ACCESS_KEY for public API
UNSPLASH_ACCESS_TOKEN = os.environ.get("UNSPLASH_ACCESS_TOKEN", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")  # Fallback for public API
UNSPLASH_SECRET_KEY = os.environ.get("UNSPLASH_SECRET_KEY", "")

# Twilio API for SMS OTP
# IMPORTANT: Never commit actual credentials to git!
# Set these via environment variables or .env file
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_VERIFY_SERVICE_SID = os.environ.get("TWILIO_VERIFY_SERVICE_SID", "")


# Audit logging toggle (enabled by default)
AUDIT_LOGGING_ENABLED = os.environ.get("AUDIT_LOGGING_ENABLED", "1") == "1"

