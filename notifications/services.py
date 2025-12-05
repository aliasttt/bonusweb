from __future__ import annotations

import base64
import binascii
import json
from typing import Iterable

from django.conf import settings
import os

try:
    import requests  # HTTP-based FCM (legacy) sender
except Exception:  # pragma: no cover - optional dependency
    requests = None

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    from firebase_admin import exceptions as firebase_exceptions
except Exception:  # pragma: no cover - optional dependency
    firebase_admin = None
    credentials = None
    messaging = None
    firebase_exceptions = None


_initialized = False


def _load_credentials_from_env():
    """
    Load Firebase service-account credentials from settings.
    
    IMPORTANT: Base64 is prioritized because it's the recommended method for production.
    Legacy FCM_SERVER_KEY is not available in new Firebase projects (2024+).

    Priority:
    1. FIREBASE_CREDENTIALS_BASE64 (base64 encoded JSON) - RECOMMENDED
    2. FIREBASE_CREDENTIALS_JSON (raw JSON string)
    3. FIREBASE_CREDENTIALS_FILE (only if file exists and is not a placeholder)
    """
    if not credentials:
        print("DEBUG: Firebase credentials module not available")
        return None
    
    # Priority 1: Base64 (RECOMMENDED for production)
    if settings.FIREBASE_CREDENTIALS_BASE64:
        try:
            print(f"DEBUG: Attempting to load from FIREBASE_CREDENTIALS_BASE64 (length: {len(settings.FIREBASE_CREDENTIALS_BASE64)})")
            decoded = base64.b64decode(settings.FIREBASE_CREDENTIALS_BASE64).decode("utf-8")
            data = json.loads(decoded)
            print("DEBUG: Successfully decoded Base64 and parsed JSON")
            
            # Log project info for debugging
            project_id = data.get("project_id", "NOT FOUND")
            client_email = data.get("client_email", "NOT FOUND")
            print(f"DEBUG: Project ID from credentials: {project_id}")
            print(f"DEBUG: Service account email: {client_email}")
            
            print("DEBUG: Creating Firebase credentials Certificate...")
            cred_obj = credentials.Certificate(data)
            print("DEBUG: Firebase credentials Certificate created successfully")
            return cred_obj
        except binascii.Error as e:
            print(f"DEBUG: Invalid Base64 encoding: {e}")
            import traceback
            print(traceback.format_exc())
        except json.JSONDecodeError as e:
            print(f"DEBUG: Invalid JSON after Base64 decode: {e}")
            print(f"DEBUG: Decoded string (first 200 chars): {decoded[:200] if 'decoded' in locals() else 'N/A'}")
            import traceback
            print(traceback.format_exc())
        except Exception as e:
            print(f"DEBUG: Failed to decode/parse FIREBASE_CREDENTIALS_BASE64: {e}")
            import traceback
            print(traceback.format_exc())

    # Priority 2: JSON string
    if settings.FIREBASE_CREDENTIALS_JSON:
        try:
            data = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
            print("DEBUG: Loading Firebase credentials from FIREBASE_CREDENTIALS_JSON")
            return credentials.Certificate(data)
        except Exception as e:
            print(f"DEBUG: Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")

    # Priority 3: File path (only if not a placeholder and file exists)
    if settings.FIREBASE_CREDENTIALS_FILE:
        file_path = settings.FIREBASE_CREDENTIALS_FILE.strip()
        # Skip placeholder paths like "/path/to/service-account.json"
        is_placeholder = (
            "/path/to/" in file_path.lower() or 
            file_path == "/path/to/service-account.json" or
            not file_path or
            file_path.startswith("/path/")
        )
        
        if is_placeholder:
            print(f"DEBUG: Skipping FIREBASE_CREDENTIALS_FILE (detected placeholder): {file_path}")
        elif not os.path.exists(file_path):
            print(f"DEBUG: Skipping FIREBASE_CREDENTIALS_FILE (file not found): {file_path}")
        else:
            try:
                print(f"DEBUG: Loading Firebase credentials from file: {file_path}")
                return credentials.Certificate(file_path)
            except FileNotFoundError as e:
                print(f"DEBUG: File not found when loading credentials from {file_path}: {e}")
            except Exception as e:
                print(f"DEBUG: Failed to load credentials from file {file_path}: {e}")

    return None


def _ensure_init() -> None:
    global _initialized
    if _initialized:
        print("DEBUG: Firebase already initialized")
        return
    
    if not firebase_admin:
        print("DEBUG: Firebase Admin SDK not installed (firebase-admin package missing)")
        return
    
    if not credentials:
        print("DEBUG: Firebase credentials module not available")
        return
    
    cred = _load_credentials_from_env()
    if not cred:
        print("DEBUG: Firebase credentials not found. Check FIREBASE_CREDENTIALS_FILE, FIREBASE_CREDENTIALS_JSON, or FIREBASE_CREDENTIALS_BASE64")
        print(f"DEBUG: FIREBASE_CREDENTIALS_FILE = {settings.FIREBASE_CREDENTIALS_FILE}")
        print(f"DEBUG: FIREBASE_CREDENTIALS_JSON = {'SET' if settings.FIREBASE_CREDENTIALS_JSON else 'NOT SET'}")
        print(f"DEBUG: FIREBASE_CREDENTIALS_BASE64 = {'SET' if settings.FIREBASE_CREDENTIALS_BASE64 else 'NOT SET'}")
        return
    
    try:
        # Check if Firebase is already initialized to avoid duplicate initialization errors
        if firebase_admin._apps:
            print("DEBUG: Firebase Admin SDK already initialized (found existing apps)")
            _initialized = True
            return
        
        firebase_admin.initialize_app(cred)
        _initialized = True
        print("DEBUG: Firebase Admin SDK initialized successfully")
    except ValueError as e:
        # ValueError can occur if Firebase is already initialized
        if "already initialized" in str(e).lower() or firebase_admin._apps:
            print("DEBUG: Firebase Admin SDK already initialized")
            _initialized = True
        else:
            print(f"DEBUG: Failed to initialize Firebase Admin SDK: {e}")
    except Exception as e:
        print(f"DEBUG: Failed to initialize Firebase Admin SDK: {e}")
        import traceback
        print(traceback.format_exc())
        # Don't raise - allow the app to continue without Firebase


def send_push_to_tokens(tokens: Iterable[str], title: str, body: str, data: dict | None = None):
    """
    Send push notifications to multiple tokens using Firebase Admin SDK.
    Returns BatchResponse with success/failure details.
    """
    if not firebase_admin:
        print("DEBUG: Firebase Admin SDK not available (firebase-admin package not installed)")
        return None
    
    _ensure_init()
    
    # Check if initialization was successful
    if not _initialized:
        print("DEBUG: Firebase Admin SDK not initialized, cannot send notifications")
        return None
    
    if not tokens:
        print("DEBUG: No tokens provided")
        return None
    
    token_list = list(tokens)
    print(f"DEBUG: Sending to {len(token_list)} tokens via Firebase")
    
    message = messaging.MulticastMessage(
        tokens=token_list,
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in (data or {}).items()},
    )
    
    try:
        response = messaging.send_multicast(message)
        print(f"DEBUG: Firebase BatchResponse - Success: {response.success_count}, Failure: {response.failure_count}")
        
        # Log details for each response
        for idx, resp in enumerate(response.responses):
            if resp.success:
                print(f"DEBUG: Token {idx} ({token_list[idx][:20]}...): ✅ Success - Message ID: {resp.message_id}")
            else:
                print(f"DEBUG: Token {idx} ({token_list[idx][:20]}...): ❌ Failed - {resp.exception}")
        
        return response
    except Exception as e:
        if firebase_exceptions and isinstance(e, firebase_exceptions.NotFoundError):
            error_msg = (
                "Firebase Cloud Messaging API is not enabled or not accessible. "
                "Please enable 'Firebase Cloud Messaging API (V1)' in Google Cloud Console: "
                "https://console.cloud.google.com/apis/library/fcm.googleapis.com"
            )
            print(f"ERROR: {error_msg}")
            print(f"ERROR: Original error: {e}")
            import traceback
            print(traceback.format_exc())
            raise RuntimeError(error_msg) from e
        elif firebase_exceptions and isinstance(e, firebase_exceptions.PermissionDeniedError):
            error_msg = (
                "Firebase service account does not have permission to send messages. "
                "Please check service account permissions in Google Cloud Console."
            )
            print(f"ERROR: {error_msg}")
            print(f"ERROR: Original error: {e}")
            import traceback
            print(traceback.format_exc())
            raise RuntimeError(error_msg) from e
        else:
            print(f"DEBUG: Firebase send_multicast error: {e}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            import traceback
            print(traceback.format_exc())
            raise


def send_push_notification(device_token: str, title: str, body: str, data: dict | None = None):
    """
    Send a push notification using Firebase FCM legacy HTTP API.
    
    NOTE: Legacy FCM Server Key is no longer available in Firebase projects (2024+).
    This method will only work if FCM_SERVER_KEY is explicitly set (rare).
    For new projects, use Firebase Admin SDK (send_push_to_tokens) instead.
    """
    if not requests:
        print("ERROR: The 'requests' library is required to send FCM HTTP notifications")
        raise RuntimeError("The 'requests' library is required to send FCM HTTP notifications")

    server_key = getattr(settings, "FCM_SERVER_KEY", "") or os.environ.get("FCM_SERVER_KEY", "")
    if not server_key:
        error_msg = (
            "FCM_SERVER_KEY is not configured. "
            "Legacy FCM Server Key is no longer available in Firebase projects (2024+). "
            "Please use Firebase Admin SDK instead by setting FIREBASE_CREDENTIALS_BASE64. "
            "If you need Legacy API, enable 'Cloud Messaging API (Legacy)' in Firebase Console."
        )
        print(f"ERROR: {error_msg}")
        raise RuntimeError(error_msg)

    url = getattr(settings, "FCM_HTTP_API_URL", "https://fcm.googleapis.com/fcm/send")
    payload = {
        "to": device_token,
        "notification": {
            "title": title,
            "body": body,
        },
        "data": {k: (str(v) if v is not None else "") for k, v in (data or {}).items()},
    }
    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp
