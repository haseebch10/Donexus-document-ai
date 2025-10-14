# DoNexus Document AI 🚀

> AI-powered lease agreement extraction system for property managers

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

## 📋 Overview

DoNexus Document AI automates the extraction of structured data from German lease agreements (Mietverträge), eliminating manual data entry and reducing errors.

**Features:**
- 📄 Drag-and-drop PDF upload
- 🤖 AI-powered field extraction (GPT-4/Claude)
- ✅ Multi-metric quality scoring
- 👥 Multi-tenant support
- 📊 Export to CSV/Excel/JSON
- 🎯 Real-time validation

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │ ← Drag & drop UI, results table
└────────┬────────┘
         │ REST API
┌────────▼────────┐
│  FastAPI Backend│ ← PDF processing, AI extraction
└────────┬────────┘
         │
┌────────▼────────┐
│ OpenAI/Claude   │ ← Structured data extraction
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key or Anthropic API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Run server
uvicorn app.main:app --reload
```

Server will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

### Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

## 📊 Extracted Fields

### Required Fields
- **Tenant Information**: Name(s), surname(s), birth dates
- **Address**: Street, house number, ZIP code, city, unit
- **Rent**: Cold rent, warm rent, utilities, parking
- **Contract**: Start date, end date, active status
- **Rent Increase**: Type and schedule

### Bonus Fields
- Landlord information
- Security deposit
- Notice period
- Special clauses
- Property details (rooms, square meters)

## 🎯 Quality Metrics

The system calculates a multi-dimensional **Extraction Quality Score (EQS)**:

1. **Confidence Score** (30%): AI model's confidence per field
2. **Completeness Score** (25%): Percentage of required fields extracted
3. **Validation Score** (25%): Business rule compliance
4. **Consistency Score** (20%): Cross-field logical consistency

**Quality Tiers:**
- 🟢 Excellent (80-100): High confidence, ready to use
- 🟡 Good (60-79): Minor issues, review recommended
- 🔴 Poor (0-59): Significant issues, manual review needed

## 📁 Project Structure

```
donexus-document-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── schemas.py           # Data models
│   │   ├── storage.py           # File-based storage
│   │   ├── services/            # Business logic (coming soon)
│   │   └── api/                 # API routes (coming soon)
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                    # React app (coming soon)
├── docs/
│   ├── ARCHITECTURE_PLAN.md     # Detailed architecture
│   └── SCHEMA_ANALYSIS.md       # Schema design decisions
└── README.md                    # This file
```

## 🛠️ Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Backend** | FastAPI | Async support, auto-docs, type safety |
| **AI** | OpenAI GPT-4 / Claude | Best German language understanding |
| **PDF** | pdfplumber | Layout-aware extraction |
| **Frontend** | React + TypeScript | Type-safe, component-rich |
| **Storage** | File-based (JSON) | Simple, no DB overhead for MVP |
| **Validation** | Pydantic v2 | Runtime type checking |

## 📝 API Endpoints

### Current
- `GET /health` - Health check
- `GET /` - API information

### Coming Soon
- `POST /api/upload` - Upload PDF
- `GET /api/extractions` - List extractions
- `GET /api/extractions/{id}` - Get single extraction
- `POST /api/export` - Export data

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📄 Example Output

```json
{
  "tenants": [
    {"first_name": "Daniela", "last_name": "Rudolph", "birth_date": "1992-02-16"},
    {"first_name": "Hendrik", "last_name": "Weber", "birth_date": "1989-09-11"}
  ],
  "address": {
    "street": "Zieblandstraße",
    "house_number": "25",
    "zip_code": "80798",
    "city": "München",
    "apartment_unit": "3.OG links"
  },
  "warm_rent": 1405.00,
  "cold_rent": 1040.00,
  "parking_rent": 75.00,
  "contract_start_date": "2020-03-01",
  "is_active": true,
  "quality": {
    "overall_score": 92.5,
    "quality_tier": "excellent"
  }
}
```

## 🗺️ Roadmap

### Phase 1: Core MVP ✅
- [x] Project structure
- [x] FastAPI backend setup
- [x] Data schemas with validation
- [x] Multi-tenant support
- [ ] PDF processing service
- [ ] AI extraction service
- [ ] Upload API endpoint

### Phase 2: Frontend & Polish
- [ ] React frontend with drag-and-drop
- [ ] Results table with sorting/filtering
- [ ] Export functionality
- [ ] Quality score visualization

### Phase 3: Advanced Features
- [ ] OCR for scanned documents
- [ ] Batch processing
- [ ] PDF highlighting (visual extraction)
- [ ] Database integration
- [ ] User authentication

## 🤝 Contributing

This is a coding challenge project. For production use, please contact the maintainer.

## 📜 License

MIT License - See LICENSE file for details

## 👤 Author

**Muhammad Haseeb Chaudhry**
- GitHub: [@haseebch10](https://github.com/haseebch10)

## 🙏 Acknowledgments

- DoNexus for the coding challenge
- OpenAI for GPT-4 API
- FastAPI community

---

**Submission Date**: October 18, 2025  
**Time Invested**: ~10 hours  
**Status**: Phase 1 Complete ✅
