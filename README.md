# SQL Generator Tool - Hackathon Project

A user-friendly tool that generates SQL queries from natural language using multiple LLM models, with secure database connectivity, query tracking, and analytics dashboard.

## Features

- **User-friendly Frontend**: Modern React interface for natural language to SQL conversion
- **Multiple LLM Models**: OpenAI GPT-4 and Anthropic Claude integration
- **Secure Database Connectivity**: Schema-aware SQL generation (metadata only - no data transfer for privacy)
- **Query & Prompt Storage**: Persist prompts and generated queries for future use
- **Query Tracking**: Track all user-generated queries with timestamps and metadata
- **Analytics Dashboard**: Monitor query generation performance, model usage, success rates

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   React         │────▶│  FastAPI         │────▶│  SQLite         │
│   Frontend      │     │  Backend         │     │  (Storage)      │
│   (Vite)        │     │  - LLM Service   │     │  - Queries      │
│                 │     │  - DB Connector  │     │  - Analytics    │
└─────────────────┘     │  - Analytics     │     └─────────────────┘
                        └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │  LLM APIs        │
                        │  OpenAI/Anthropic│
                        └──────────────────┘
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- API Keys: OpenAI and/or Anthropic (add to `.env`)

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env  # macOS/Linux

# Edit .env and add your OPENAI_API_KEY and/or ANTHROPIC_API_KEY
python run.py
```

Backend runs at **http://localhost:8000**

### 2. Frontend Setup

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

### 3. Host & Run (Production – single command)

Build the frontend and serve everything from one server:

```powershell
# Windows - from project root
.\build_and_run.bat
```

Or manually:

```powershell
cd frontend
npm run build
cd ..\backend
python run.py
```

Then open **http://localhost:8000** – the app (frontend + API) runs on one port.

## Environment Variables

Create `backend/.env`:

```
# Ollama (local - no API key needed, runs at http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Optional: cloud LLMs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

DATABASE_URL=sqlite:///./sql_generator.db
```

**Using Ollama (no API keys):** Install [Ollama](https://ollama.ai), run `ollama pull llama3.2`, start Ollama, then select **Ollama (Local)** in the app.

## Project Structure

```
SQLGeneratorIdeathon/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── llm_service.py  # Multi-LLM integration
│   │   ├── db_connector.py # Secure DB connectivity
│   │   └── analytics.py    # Query tracking & analytics
│   ├── requirements.txt
│   └── run.py
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # SQL Generator, Dashboard
│   │   └── api/            # API client
│   └── package.json
└── README.md
```

## Mandatory Requirements Met

✅ **Query Tracking**: All user-generated queries stored with model, timestamp, success status  
✅ **Analytics Dashboard**: Performance metrics, model comparison, usage trends
