# DoNexus - AI-Powered Lease Extraction System# DoNexus Document AI 🚀



> Extract structured data from German lease agreements (Mietverträge) using AI> AI-powered lease agreement extraction system for property managers



---[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)

[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://reactjs.org/)

## 🚀 Setup & Run[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

### Prerequisites

- **Python 3.9+**## 📋 Overview

- **Node.js 18+**

- **OpenAI API Key**DoNexus Document AI automates the extraction of structured data from German lease agreements (Mietverträge), eliminating manual data entry and reducing errors.



### Backend Setup**Features:**

- 📄 Drag-and-drop PDF upload

```bash- 🤖 AI-powered field extraction (GPT-4/Claude)

cd backend- ✅ Multi-metric quality scoring

- 👥 Multi-tenant support

# Create virtual environment- 📊 Export to CSV/Excel/JSON

python -m venv venv- 🎯 Real-time validation

source venv/bin/activate  # On Windows: venv\Scripts\activate

## 🏗️ Architecture

# Install dependencies

pip install -r requirements.txt```

┌─────────────────┐

# Configure environment│  React Frontend │ ← Drag & drop UI, results table

cp .env.example .env└────────┬────────┘

# Edit .env and add your OPENAI_API_KEY         │ REST API

┌────────▼────────┐

# Run server│  FastAPI Backend│ ← PDF processing, AI extraction

python -m uvicorn app.main:app --reload└────────┬────────┘

```         │

┌────────▼────────┐

Backend will run on `http://localhost:8000`│ OpenAI/Claude   │ ← Structured data extraction

└─────────────────┘

### Frontend Setup```



```bash## 🚀 Quick Start

cd frontend

### Prerequisites

# Install dependencies- Python 3.11+

npm install- Node.js 18+

- OpenAI API key or Anthropic API key

# Run development server

npm run dev### Backend Setup

```

```bash

Frontend will run on `http://localhost:5173`cd backend



---# Create virtual environment

python3 -m venv venv

## 🏗️ Technology Stacksource venv/bin/activate  # On Windows: venv\Scripts\activate



### Backend# Install dependencies

- **FastAPI** - Modern, fast Python web framework with automatic API documentationpip install -r requirements.txt

- **OpenAI GPT-4** - Large language model for structured data extraction from German text

- **pdfplumber** - Reliable PDF text extraction with fallback to PyPDF2# Configure environment

- **Pydantic v2** - Data validation and schema enforcementcp .env.example .env

# Edit .env and add your API keys

### Frontend

- **React 18** - Component-based UI library# Run server

- **TypeScript** - Type safety and better developer experienceuvicorn app.main:app --reload

- **Vite** - Fast build tool and dev server```

- **Tailwind CSS v3** - Utility-first CSS framework

- **shadcn/ui** - High-quality, accessible component library (Radix UI)Server will be available at:

- **API**: http://localhost:8000

### Why These Choices?- **Docs**: http://localhost:8000/docs



- **OpenAI GPT-4**: Best-in-class understanding of German legal documents, structured JSON output, high accuracy on complex nested data### Frontend Setup (Coming Soon)

- **FastAPI**: Async support for concurrent uploads, automatic OpenAPI docs, built-in validation with Pydantic

- **React + TypeScript**: Type-safe components, excellent ecosystem, fast development with Vite hot reload```bash

- **Tailwind + shadcn/ui**: Rapid UI development with consistent design, accessible components out of the boxcd frontend

npm install

---npm run dev

```

## 📊 Quality Scoring System

## 📊 Extracted Fields

Every extraction is scored using 4 metrics (0-100 scale):

### Required Fields

### 1. **Confidence Score** (30% weight)- **Tenant Information**: Name(s), surname(s), birth dates

- AI's confidence in each extracted field- **Address**: Street, house number, ZIP code, city, unit

- Based on model certainty and field clarity- **Rent**: Cold rent, warm rent, utilities, parking

- **Calculation**: Average confidence across required fields- **Contract**: Start date, end date, active status

- **Rent Increase**: Type and schedule

### 2. **Completeness Score** (25% weight)

- Percentage of required vs. optional fields filled### Bonus Fields

- **Calculation**: `(Required fields × 0.7) + (Bonus fields × 0.3)`- Landlord information

- **Required**: Tenants, address, rent, dates, rent increase type- Security deposit

- **Bonus**: Landlord info, deposit, notice period, parking, utilities- Notice period

- Special clauses

### 3. **Validation Score** (25% weight)- Property details (rooms, square meters)

- Business rule compliance (rent logic, date validity, value ranges)

- **Checks**:## 🎯 Quality Metrics

  - Warm rent ≥ Cold rent

  - Contract end > Contract startThe system calculates a multi-dimensional **Extraction Quality Score (EQS)**:

  - Rent in reasonable range (€100-€10,000)

  - Deposit typically 2-3 months rent1. **Confidence Score** (30%): AI model's confidence per field

  - Valid postal codes and room counts2. **Completeness Score** (25%): Percentage of required fields extracted

- **Calculation**: `(Rules passed / Total rules) × 100`3. **Validation Score** (25%): Business rule compliance

4. **Consistency Score** (20%): Cross-field logical consistency

### 4. **Consistency Score** (20% weight)

- Cross-field logical consistency**Quality Tiers:**

- **Checks**:- 🟢 Excellent (80-100): High confidence, ready to use

  - Active status matches end date- 🟡 Good (60-79): Minor issues, review recommended

  - Rent increase schedule matches type- 🔴 Poor (0-59): Significant issues, manual review needed

  - Postal code matches city (e.g., Munich 80000-81999)

  - Parking rent < Cold rent## 📁 Project Structure

- **Calculation**: `(Checks passed / Total checks) × 100`

```

### Overall Score (EQS)donexus-document-ai/

```├── backend/

EQS = (Confidence × 0.30) + (Completeness × 0.25) + │   ├── app/

      (Validation × 0.25) + (Consistency × 0.20)│   │   ├── main.py              # FastAPI application

```│   │   ├── config.py            # Configuration

│   │   ├── schemas.py           # Data models

**Quality Levels**:│   │   ├── storage.py           # File-based storage

- **Excellent**: 90-100│   │   ├── services/            # Business logic (coming soon)

- **Good**: 75-89│   │   └── api/                 # API routes (coming soon)

- **Fair**: 60-74│   ├── requirements.txt

- **Poor**: 0-59│   ├── .env.example

│   └── README.md

---│

├── frontend/                    # React app (coming soon)

## 📁 Project Structure├── docs/

│   ├── ARCHITECTURE_PLAN.md     # Detailed architecture

```│   └── SCHEMA_ANALYSIS.md       # Schema design decisions

Donexus/└── README.md                    # This file

├── backend/```

│   ├── app/

│   │   ├── api/          # API endpoints## 🛠️ Technology Stack

│   │   ├── services/     # Business logic (AI, PDF, Quality)

│   │   ├── schemas.py    # Pydantic models| Component | Technology | Why |

│   │   └── main.py       # FastAPI app|-----------|-----------|-----|

│   ├── tests/            # Pytest tests| **Backend** | FastAPI | Async support, auto-docs, type safety |

│   └── requirements.txt| **AI** | OpenAI GPT-4 / Claude | Best German language understanding |

│| **PDF** | pdfplumber | Layout-aware extraction |

├── frontend/| **Frontend** | React + TypeScript | Type-safe, component-rich |

│   ├── src/| **Storage** | File-based (JSON) | Simple, no DB overhead for MVP |

│   │   ├── components/   # React components| **Validation** | Pydantic v2 | Runtime type checking |

│   │   ├── lib/          # API client, utilities

│   │   └── types/        # TypeScript types## 📝 API Endpoints

│   └── package.json

│### Current

└── README.md- `GET /health` - Health check

```- `GET /` - API information



---### Coming Soon

- `POST /api/upload` - Upload PDF

## 🔒 Security Features- `GET /api/extractions` - List extractions

- `GET /api/extractions/{id}` - Get single extraction

- **File size validation**: 10MB limit (client + server)- `POST /api/export` - Export data

- **Filename sanitization**: Path traversal protection

- **Chunked file reading**: Memory-efficient with size enforcement## 🧪 Testing

- **Input validation**: Pydantic schema validation on all data

- **CORS configuration**: Restricted origins for production```bash

# Backend tests

---cd backend

pytest

## 📤 Export Formats

# Frontend tests

- **JSON**: Full structured data with all fieldscd frontend

- **Excel**: Flattened 30+ column spreadsheet with auto-sized columnsnpm test

```

---

## 📄 Example Output

## 🧪 Testing

```json

```bash{

cd backend  "tenants": [

    {"first_name": "Daniela", "last_name": "Rudolph", "birth_date": "1992-02-16"},

# Run all tests    {"first_name": "Hendrik", "last_name": "Weber", "birth_date": "1989-09-11"}

pytest  ],

  "address": {

# Run with coverage    "street": "Zieblandstraße",

pytest --cov=app tests/    "house_number": "25",

    "zip_code": "80798",

# Run specific test file    "city": "München",

pytest tests/test_quality_scorer.py -v    "apartment_unit": "3.OG links"

```  },

  "warm_rent": 1405.00,

**Test Coverage**:  "cold_rent": 1040.00,

- Quality Scorer: 18/18 tests passing  "parking_rent": 75.00,

- PDF Processor: 15/15 tests passing  "contract_start_date": "2020-03-01",

- Real extraction: Integration tests with actual PDFs  "is_active": true,

  "quality": {

---    "overall_score": 92.5,

    "quality_tier": "excellent"

## 📝 API Documentation  }

}

Once the backend is running, visit:```

- **Swagger UI**: http://localhost:8000/docs

- **ReDoc**: http://localhost:8000/redoc## 🗺️ Roadmap



---### Phase 1: Core MVP ✅

- [x] Project structure

## 🎯 Features- [x] FastAPI backend setup

- [x] Data schemas with validation

- **Multi-PDF Upload**: Process up to 3 PDFs simultaneously with browser-style tabs- [x] Multi-tenant support

- **Real-time Processing**: Manual trigger button for user control- [ ] PDF processing service

- **Quality Metrics**: Visual quality indicators with detailed breakdowns- [ ] AI extraction service

- **Export Options**: Download individual or all results as JSON/Excel- [ ] Upload API endpoint

- **Error Handling**: Client and server-side validation with user-friendly messages

- **Responsive Design**: Works on desktop and mobile devices### Phase 2: Frontend & Polish

- [ ] React frontend with drag-and-drop

---- [ ] Results table with sorting/filtering

- [ ] Export functionality

## 📄 License- [ ] Quality score visualization



Proprietary - DoNexus Document AI### Phase 3: Advanced Features

- [ ] OCR for scanned documents

---- [ ] Batch processing

- [ ] PDF highlighting (visual extraction)

Built with ❤️ for property managers- [ ] Database integration

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
