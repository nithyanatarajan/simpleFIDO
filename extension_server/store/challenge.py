# store/challenge.py
import os
import time
import base64

from config import Config

# In-memory challenge store: { username: (challenge, expiry_time) }
_challenge_store = {}


def generate_challenge(length: int = 32) -> str:
    return base64.urlsafe_b64encode(os.urandom(length)).rstrip(b'=').decode()


def store_challenge(user: str, challenge: str, ttl_seconds: int = Config.CHALLENGE_TTL_SECONDS):
    expires_at = time.time() + ttl_seconds
    _challenge_store[user] = (challenge, expires_at)


def get_stored_challenge(user: str) -> str | None:
    record = _challenge_store.get(user)
    if record is None:
        return None

    challenge, expires_at = record
    if time.time() > expires_at:
        # Optionally: delete expired entry
        del _challenge_store[user]
        return None

    return challenge


def pop_stored_challenge(user: str) -> str | None:
    """
    Pops (retrieves and removes) the stored challenge for a user.
    Returns None if not found or expired.
    """
    record = _challenge_store.pop(user, None)
    if record is None:
        return None

    challenge, expires_at = record
    if time.time() > expires_at:
        return None  # expired

    return challenge
