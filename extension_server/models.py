from pydantic import BaseModel

class ExtensionRequest(BaseModel):
    account_token: str

