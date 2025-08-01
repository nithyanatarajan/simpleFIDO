# ext_utils.py

import time

import httpx

from config import Config
from exceptions import ExtensionValidationError


def verify_extension_token_with_retries(extension_token: str):
    """Verifies extension token with retry logic and returns validated payload."""

    for attempt in range(Config.EXT_MAX_RETRIES):
        try:
            response = httpx.post(
                Config.EXT_SERVER_URL,
                json={"account_token": extension_token},
                timeout=Config.EXT_SERVER_TIMEOUT,
            )

            # 🚫 Permanent failure → do not retry
            if 400 <= response.status_code < 500:
                raise ExtensionValidationError(
                    f"Extension validation failed: {response.text}"
                )

            # ✅ Raise for other HTTP issues (e.g., 5xx)
            response.raise_for_status()
            return response.json()

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # Final attempt failed
            if attempt == Config.EXT_MAX_RETRIES - 1:
                raise ExtensionValidationError("Extension server unreachable") from e

            time.sleep(1.0)  # ⏳ Backoff before retry

    return None  # Not expected to reach here
