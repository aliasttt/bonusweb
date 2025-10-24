from __future__ import annotations

import json
import time
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse


class AuditLogMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not getattr(settings, "AUDIT_LOGGING_ENABLED", True):
            return self.get_response(request)
        start = time.time()
        response = self.get_response(request)
        duration_ms = int((time.time() - start) * 1000)
        try:
            user_id = request.user.id if getattr(request, "user", None) and request.user.is_authenticated else None
            # Minimal console log; in production send to a logging service
            print(json.dumps({
                "path": request.path,
                "method": request.method,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "user_id": user_id,
            }))
        except Exception:
            pass
        return response
