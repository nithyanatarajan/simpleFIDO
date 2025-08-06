import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env


class Config:
    # JWT settings
    JWT_ISSUER = "identity-provider"
    JWT_AUDIENCE_RP = "relying-party-server"
    JWT_AUDIENCE_EXTN = "extension-server"
    JWT_SECRET = os.getenv("JWT_SECRET", "super-secure-token")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY", "60"))  # Default to 60 seconds

    # CORS (optional)
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    USER_KEY = "user"
    ACCOUNT_ID_KEY = "account_id"
