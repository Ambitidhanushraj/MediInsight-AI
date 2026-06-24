import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / ".env")

from app.api.report import router as report_router
from app.api.rag import router as rag_router
from app.api.report_chat import router as report_chat_router
from app.config.config import CORS_ORIGINS
from app.services.history_service import init_history_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MediInsight AI"
)

init_history_db()

# CORS — origins loaded from CORS_ORIGINS in .env (dev defaults to localhost ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(report_router)
app.include_router(rag_router)
app.include_router(report_chat_router)

@app.get("/")
def root():
    return {
        "message": "MediInsight AI Backend Running"
    }