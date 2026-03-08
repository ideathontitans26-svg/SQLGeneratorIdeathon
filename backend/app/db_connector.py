"""Secure database connectivity - schema extraction only (Data Privacy)."""
import json
from typing import Optional, Tuple
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError


def extract_schema(connection_string: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract schema metadata (tables, columns) only - NO actual data.
    Returns (schema_json, error_message). On success: (schema, None). On failure: (None, error).
    """
    if not (connection_string or "").strip():
        return None, "Connection string is empty"
    try:
        # SQLite: ensure URL format - allow path-only to be interpreted as sqlite
        conn = connection_string.strip()
        if conn and not conn.startswith("sqlite") and not conn.startswith("postgresql") and not conn.startswith("mysql"):
            if "://" not in conn:
                conn = "sqlite:///" + conn.replace("\\", "/")
        engine = create_engine(
            conn,
            connect_args={"check_same_thread": False} if "sqlite" in conn else {},
        )
        inspector = inspect(engine)
        schema = {}
        for table in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"])
                })
            schema[table] = columns
        return (json.dumps(schema, indent=2) if schema else "{}", None)
    except SQLAlchemyError as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)


def validate_connection(connection_string: str) -> tuple[bool, Optional[str]]:
    """Test if connection works without exposing data."""
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        return False, str(e)
