"""Run the FastAPI server."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend folder before app imports
load_dotenv(Path(__file__).resolve().parent / ".env")

import uvicorn

if __name__ == "__main__":
    # Production: no reload, serves built frontend
    # Dev: set RELOAD=1 for hot reload (frontend runs separately)
    reload = os.environ.get("RELOAD", "").lower() in ("1", "true", "yes")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=reload)
