from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, chat

app = FastAPI(title="AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

app.include_router(health.router, prefix="/api")
app.include_router(chat.router,  prefix="/api") 