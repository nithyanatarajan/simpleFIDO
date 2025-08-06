from pydantic import BaseModel


class RegResponse(BaseModel):
    status: str
    user: str
    account_id: str
    org: str = None
    region: str = None
    registered: bool = None


class AuthResponse(BaseModel):
    status: str
    user: str
    account_id: str
    org: str = None
    region: str = None
    authenticated: bool = None
