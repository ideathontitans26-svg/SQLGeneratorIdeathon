"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GenerateSQLRequest(BaseModel):
    prompt: str
    model: str = "openai-gpt4"
    schema_info: Optional[str] = None


class GenerateSQLResponse(BaseModel):
    sql: str
    model_used: str
    success: bool = True
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class QueryRecordCreate(BaseModel):
    prompt: str
    generated_sql: Optional[str] = None
    model_used: str
    success: bool = True
    execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    connection_id: Optional[int] = None


class QueryRecordResponse(BaseModel):
    id: int
    prompt: str
    generated_sql: Optional[str]
    model_used: str
    success: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_queries: int
    success_rate: float
    queries_by_model: dict
    queries_today: int
    avg_execution_time_ms: Optional[float]
    recent_queries: list


class StoredPromptCreate(BaseModel):
    prompt: str
    generated_sql: Optional[str] = None
    model_used: Optional[str] = None
    tags: Optional[str] = None


class ConnectionRequest(BaseModel):
    connection_string: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    email: str
    token: str
