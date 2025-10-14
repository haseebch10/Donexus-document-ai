# DoNexus Document AI - Backend

FastAPI backend for AI-powered lease agreement extraction.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
```
OPENAI_API_KEY=your_actual_openai_api_key
ANTHROPIC_API_KEY=your_actual_anthropic_api_key
```

### 4. Run the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Or use the main.py directly
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & middleware
│   ├── config.py            # Configuration settings
│   ├── schemas.py           # Pydantic models
│   ├── storage.py           # File-based storage
│   ├── logging_config.py    # Logging setup
│   ├── api/                 # API routes (coming next)
│   ├── services/            # Business logic (coming next)
│   └── utils/               # Utilities (coming next)
├── tests/                   # Tests
├── uploads/                 # Uploaded PDFs (auto-created)
├── data/                    # JSON storage (auto-created)
├── logs/                    # Application logs (auto-created)
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

### Current Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check

### Coming Soon

- `POST /api/upload` - Upload PDF
- `GET /api/extractions` - List extractions
- `GET /api/extractions/{id}` - Get extraction
- `POST /api/export` - Export data

## Development

### Code Formatting

```bash
# Format code
black app/

# Lint code
ruff check app/
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app
```

## Storage

Currently using **file-based storage** (JSON file) for simplicity:
- Extractions saved to `data/extractions.json`
- PDFs saved to `uploads/`

Easy to migrate to PostgreSQL/MongoDB later if needed.

## Logging

Logs are written to:
- **Console**: Colored output with Loguru
- **File**: `logs/app.log` (rotating, 7-day retention)

## Next Steps

1. Add PDF processing service
2. Add AI extraction service
3. Add API endpoints for upload/extraction
4. Add export functionality
