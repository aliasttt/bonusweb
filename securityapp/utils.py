from __future__ import annotations

import base64
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _get_fernet() -> Optional[Fernet]:
    key = getattr(settings, "FIELD_ENCRYPTION_KEY", None)
    if not key:
        return None
    # Expect base64 32-byte key
    try:
        return Fernet(key)
    except Exception:
        return None


def encrypt_str(value: str) -> str:
    f = _get_fernet()
    if not f:
        return value
    token = f.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_str(value: str) -> str:
    f = _get_fernet()
    if not f:
        return value
    try:
        return f.decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return value
