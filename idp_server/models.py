from pydantic import BaseModel


class TokenRequest(BaseModel):
    username: str
    password: str
    account_id: str


class TokenResponse(BaseModel):
    token_rp: str
    token_extn: str
