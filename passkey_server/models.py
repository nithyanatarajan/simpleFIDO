from pydantic import BaseModel
from typing import Optional

# Schemas
class RegisterBeginRequest(BaseModel):
    username: str
    account: str
    org_id: str


class RegisterCompleteRequest(BaseModel):
    attestation: dict
    challenge_token: str


class AuthBeginRequest(BaseModel):
    username: Optional[str] = None
    org_id: str


class AuthCompleteRequest(BaseModel):
    assertion: dict
    challenge_token: str
    account_token: str
