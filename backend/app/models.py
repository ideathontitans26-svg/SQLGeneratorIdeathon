"""SQLAlchemy database models for query tracking and analytics."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    """User account for email login."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())  # plain DateTime for SQLite compatibility


class DatabaseConnection(Base):
    """Stored database connection metadata (schema info only - data privacy)."""
    __tablename__ = "database_connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    connection_type = Column(String(50))  # postgresql, mysql, sqlite, etc.
    schema_info = Column(Text)  # JSON string of tables/columns - no actual data
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class QueryRecord(Base):
    """Track all user-generated queries for analytics."""
    __tablename__ = "query_records"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    generated_sql = Column(Text)
    model_used = Column(String(50), nullable=False)
    success = Column(Boolean, default=True)
    execution_time_ms = Column(Float)
    error_message = Column(Text, nullable=True)
    connection_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StoredPrompt(Base):
    """Store prompts and generated queries for future use."""
    __tablename__ = "stored_prompts"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    generated_sql = Column(Text)
    model_used = Column(String(50))
    tags = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
