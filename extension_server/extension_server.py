# extension_server.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from exceptions.handlers import register_exception_handlers
from models import ExtensionRequest
from validations.validate import validate_runtime_token

app = FastAPI()
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/extensions/validate")
async def validate_extension(req: ExtensionRequest):
    user, account_id = await validate_runtime_token(req.account_token)
    return {'status': 'valid', Config.USER_KEY: user, Config.ACCOUNT_ID_KEY: account_id}


if __name__ == "__main__":
    uvicorn.run(app, port=9000, log_level="info")
