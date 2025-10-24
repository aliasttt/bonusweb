from __future__ import annotations

import json
from typing import Iterable

from django.conf import settings

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
except Exception:  # pragma: no cover - optional dependency
    firebase_admin = None
    credentials = None
    messaging = None


_initialized = False


def _ensure_init() -> None:
    global _initialized
    if _initialized or not firebase_admin:
        return
    if settings.FIREBASE_CREDENTIALS_FILE:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_FILE)
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
