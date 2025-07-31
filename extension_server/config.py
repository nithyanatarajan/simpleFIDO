import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env


class Config:
    # JWT settings
    JWT_ISSUER = os.getenv("JWT_ISSUER", "identify-provider")
    JWT_SECRET = os.getenv("JWT_SECRET", "super-secure-token")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY", 60))
    JWT_LEEWAY_SECONDS = 30

    USER_KEY = "user"
    ACCOUNT_ID_KEY = "account_id"
    ISSUER_KEY = "iss"
