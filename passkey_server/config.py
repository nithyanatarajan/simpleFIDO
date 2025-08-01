import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env


class Config:
    # WebAuthn RP config
    RP_ID = os.getenv("RP_ID", "localhost")
    RP_NAME = os.getenv("RP_NAME", "Passkey POC")
    ORIGIN = os.getenv("ORIGIN", "http://localhost:8000")

    # JWT settings
    JWT_ISSUER = os.getenv("JWT_ISSUER", "identify-provider")
    JWT_SECRET = os.getenv("JWT_SECRET", "super-secure-token")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY", 60))
    JWT_LEEWAY_SECONDS = 30

    # CORS (optional)
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # Extension validation URL
    EXT_SERVER_URL = os.getenv("EXTENSION_VALIDATION_URL", "http://localhost:9000/extensions/validate")
    EXT_SERVER_TIMEOUT = 2  # seconds
    EXT_MAX_RETRIES = 3

    USER_KEY = "user"
    ACCOUNT_ID_KEY = "account_id"
    ISSUER_KEY = "iss"
