from pydantic import BaseModel


class ExtensionRegistrationRequest(BaseModel):
    username: str


class ExtensionRegistrationResponse(BaseModel):
    status: str
    user: str
    account_id: str
    challenge: str
    issued_at: int  # Unix timestamp
    registered: bool = None


class ExtensionValidationRequest(BaseModel):
    username: str
    credential: dict


class ExtensionValidationResponse(BaseModel):
    status: str
    user: str
    account_id: str
    authenticated: bool = None
