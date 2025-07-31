from pydantic import BaseModel


class AuthenticateRequest(BaseModel):
    username: str
    account: str

class ExtensionRequest(BaseModel):
    account_token: str

