import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env


class Config:
    # JWT settings
    JWT_SECRET = os.getenv("JWT_SECRET", "super-secure-token")
    JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY", 60))

    USER_KEY = "user"
    ACCOUNT_ID_KEY = "account_id"
