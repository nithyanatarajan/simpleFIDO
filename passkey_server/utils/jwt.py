import jwt
from config import Config


def encode_challenge_token(token: str) -> str:
    return jwt.encode(token, Config.JWT_SECRET, algorithm="HS256")


def decode_challenge_token(token: str) -> dict:
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
