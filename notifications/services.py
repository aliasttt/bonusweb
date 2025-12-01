from __future__ import annotations

import base64
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
except Exception:  # pragma: no cover - optional dependency
    firebase_admin = None
    credentials = None
    messaging = None


_initialized = False


def _load_credentials_from_env():
    """
    Load Firebase service-account credentials from settings.

    Priority:
    1. FIREBASE_CREDENTIALS_FILE path
    2. FIREBASE_CREDENTIALS_JSON raw JSON string
    3. FIREBASE_CREDENTIALS_BASE64 base64 encoded JSON
    """
    if settings.FIREBASE_CREDENTIALS_FILE:
        return credentials.Certificate(settings.FIREBASE_CREDENTIALS_FILE)

    if settings.FIREBASE_CREDENTIALS_JSON:
        data = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
        return credentials.Certificate(data)

    if settings.FIREBASE_CREDENTIALS_BASE64:
        decoded = base64.b64decode(settings.FIREBASE_CREDENTIALS_BASE64).decode("utf-8")
        data = json.loads(decoded)
        return credentials.Certificate(data)

    return None


def _ensure_init() -> None:
    global _initialized
    if _initialized or not firebase_admin:
        return

    cred = _load_credentials_from_env()
    if not cred:
        return

    firebase_admin.initialize_app(cred)
    _initialized = True


def send_push_to_tokens(tokens: Iterable[str], title: str, body: str, data: dict | None = None) -> None:
    if not firebase_admin:
        return
    _ensure_init()
    if not tokens:
        return
    message = messaging.MulticastMessage(
        tokens=list(tokens),
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in (data or {}).items()},
    )
    messaging.send_multicast(message)


def send_push_notification(device_token: str, title: str, body: str, data: dict | None = None):
    """
    Send a push notification using Firebase FCM legacy HTTP API.
    Uses FCM_SERVER_KEY from environment/settings.
    """
    if not requests:
        raise RuntimeError("The 'requests' library is required to send FCM HTTP notifications")

    server_key = getattr(settings, "FCM_SERVER_KEY", "") or os.environ.get("FCM_SERVER_KEY", "")
    if not server_key:
        raise RuntimeError("FCM_SERVER_KEY is not configured")

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
