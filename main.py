import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager

from app.api.proposal_chat_ws import router as proposal_chat_ws
from app.api.upload_router import router as upload_router
from app.core.container import Container

logger = logging.getLogger("app")
container = Container()

@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        container.wire(modules=[proposal_chat_ws.__module__])
        yield
    finally:
        pass

app = FastAPI(
    title="Proposal Generator",
    version="0.2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, tags=["uploads"])
app.include_router(proposal_chat_ws, tags=["chat-proposal"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)