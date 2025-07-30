from pydantic import BaseModel

# Schemas
class RegisterBeginRequest(BaseModel):
    username: str


class RegisterCompleteRequest(BaseModel):
    attestation: dict
    challenge_token: str


class AuthBeginRequest(BaseModel):
    username: str


class AuthCompleteRequest(BaseModel):
    assertion: dict
    challenge_token: str
    account_token: str
