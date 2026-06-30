import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend root
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

# Gemini
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# OpenRouter (free tier available — https://openrouter.ai/keys)
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

# Poppler (Windows: set POPPLER_PATH in .env; Linux/Mac: leave blank)
POPPLER_PATH: str | None = os.getenv("POPPLER_PATH") or None

# Upload limits
MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024)))  # 50 MB
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
ALLOWED_EXTENSIONS: tuple = (".pdf", ".jpg", ".jpeg", ".png")
ALLOWED_MIME_MAGIC: dict = {
    b"%PDF": "pdf",
    b"\xff\xd8\xff": "jpeg",
    b"\x89PNG": "png",
}

# CORS
CORS_ORIGINS: list[str] = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175",
    ).split(",")
    if o.strip()
]

# Allows Vercel preview/prod URLs (can be overridden in environment)
CORS_ORIGIN_REGEX: str = os.getenv("CORS_ORIGIN_REGEX", r"^https://.*\.vercel\.app$")

# Vector DB
VECTOR_DB: str = os.getenv("VECTOR_DB", "vectorstore")
EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
