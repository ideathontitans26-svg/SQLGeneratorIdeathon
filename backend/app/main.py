"""FastAPI application - SQL Generator Tool."""
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import get_db, init_db
from .models import QueryRecord, StoredPrompt, User
from .schemas import (
    GenerateSQLRequest,
    GenerateSQLResponse,
    ConnectionRequest,
    LoginRequest,
    RegisterRequest,
    AuthResponse,
)
from .auth import hash_password, verify_password, create_access_token, decode_token
from .llm_service import generate_sql
from .analytics import get_analytics_summary
from .db_connector import extract_schema, validate_connection

app = FastAPI(title="SQL Generator Tool", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API router - all routes under /api
from fastapi import APIRouter
api_router = APIRouter(prefix="/api", tags=["api"])


@app.on_event("startup")
def startup():
    init_db()


@api_router.get("/health")
def health():
    return {"status": "ok"}


def get_current_user_email(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> str | None:
    """Return email if valid Bearer token, else None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "").strip()
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        return None
    email = payload["sub"]
    user = db.query(User).filter(User.email == email).first()
    return email if user else None


@api_router.post("/auth/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email and password."""
    try:
        if db.query(User).filter(User.email == req.email.lower()).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(
            email=req.email.lower().strip(),
            password_hash=hash_password(req.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token(data={"sub": user.email})
        return AuthResponse(email=user.email, token=token)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@api_router.post("/auth/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    try:
        user = db.query(User).filter(User.email == req.email.lower().strip()).first()
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = create_access_token(data={"sub": user.email})
        return AuthResponse(email=user.email, token=token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@api_router.get("/auth/me")
def auth_me(authorization: str | None = Header(None), db: Session = Depends(get_db)):
    """Return current user email if token is valid."""
    email = get_current_user_email(authorization, db)
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"email": email}


@api_router.get("/models")
def list_models():
    """List available LLM models."""
    return {"models": ["ollama", "openai-gpt4", "anthropic-claude", "google-gemini"]}


@api_router.post("/generate", response_model=GenerateSQLResponse)
async def generate_sql_endpoint(req: GenerateSQLRequest, db: Session = Depends(get_db)):
    """Generate SQL from natural language using selected LLM."""
    try:
        sql, model_used, elapsed_ms = await generate_sql(
            req.prompt, req.model, req.schema_info
        )
        
        record = QueryRecord(
            prompt=req.prompt,
            generated_sql=sql,
            model_used=model_used,
            success=True,
            execution_time_ms=elapsed_ms,
        )
        db.add(record)
        db.commit()

        stored = StoredPrompt(
            prompt=req.prompt,
            generated_sql=sql,
            model_used=model_used,
        )
        db.add(stored)
        db.commit()

        return GenerateSQLResponse(
            sql=sql,
            model_used=model_used,
            success=True,
            execution_time_ms=round(elapsed_ms, 1),
        )
    except Exception as e:
        record = QueryRecord(
            prompt=req.prompt,
            model_used=req.model,
            success=False,
            error_message=str(e),
        )
        db.add(record)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/extract-schema")
def extract_schema_endpoint(req: ConnectionRequest):
    """Extract schema only (no data) for schema-aware SQL generation."""
    schema, err = extract_schema(req.connection_string)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"schema": schema or "{}"}


@api_router.post("/validate-connection")
def validate_connection_endpoint(req: ConnectionRequest):
    """Validate database connection without exposing data."""
    ok, err = validate_connection(req.connection_string)
    if not ok:
        raise HTTPException(status_code=400, detail=err)
    return {"valid": True}


@api_router.get("/analytics")
def analytics_endpoint(days: int = 7, db: Session = Depends(get_db)):
    """Analytics dashboard data for query generation performance."""
    return get_analytics_summary(db, days)


@api_router.get("/queries")
def list_queries(limit: int = 50, db: Session = Depends(get_db)):
    """List tracked user-generated queries."""
    records = db.query(QueryRecord).order_by(QueryRecord.created_at.desc()).limit(limit).all()
    return {
        "queries": [
            {
                "id": r.id,
                "prompt": r.prompt,
                "generated_sql": r.generated_sql,
                "model_used": r.model_used,
                "success": r.success,
                "execution_time_ms": r.execution_time_ms,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]
    }


@api_router.get("/stored-prompts")
def list_stored_prompts(limit: int = 50, db: Session = Depends(get_db)):
    """List stored prompts and generated queries."""
    prompts = db.query(StoredPrompt).order_by(StoredPrompt.created_at.desc()).limit(limit).all()
    return {
        "prompts": [
            {
                "id": p.id,
                "prompt": p.prompt,
                "generated_sql": p.generated_sql,
                "model_used": p.model_used,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in prompts
        ]
    }


app.include_router(api_router)

# Serve static frontend (production)
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """Serve index.html for SPA routes; static files for assets."""
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
