import jwt
import time
import argparse
from config import Config


def generate_token(user: str | None, account_id: str | None) -> str:
    payload = {
        Config.USER_KEY: user,
        Config.ACCOUNT_ID_KEY: account_id,
        "exp": int(time.time()) + Config.JWT_EXPIRY_SECONDS
    }

    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
    return token


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate signed JWT for extension testing.")
    parser.add_argument("--user", required=False, help="User email (e.g., user1@example.com)")
    parser.add_argument("--account", required=False, help="Account ID (e.g., acc002)")

    args = parser.parse_args()
    token = generate_token(args.user, args.account)
    print(token)
