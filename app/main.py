import logging, uuid
from fastapi import FastAPI, Request

from app.logging import setup_logging, request_id_ctx_var

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(name="prediction market LLM gateway")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    token = request_id_ctx_var.set(request_id)
    try:
        response = await call_next(request)
        return response
    finally:
        request_id_ctx_var.reset(token)

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}