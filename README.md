<<<<<<< HEAD
# 🏠 AI Home Service Platform

An AI-powered home service provider platform built with Django, featuring a **RAG (Retrieval-Augmented Generation) AI assistant** that understands home problems and recommends the right professional.

---

## 🚀 Quick Start

```bash
# 1. Activate virtual environment
venv\Scripts\activate

# 2. Run migrations
python manage.py migrate

# 3. Seed database (categories + sample providers + admin user)
python manage.py seed_data

# 4. Start development server
python manage.py runserver

# 5. Open browser
# http://127.0.0.1:8000/
```

---

## 🔑 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Provider | `ahmed_plumbing` | `provider123` |
| Provider | `ali_electric` | `provider123` |
| Provider | `cool_tech_ac` | `provider123` |
| *(all providers)* | see seed_data | `provider123` |

---

## 🏗️ Project Structure

```
AI_House_Serrvice/
├── config/                # Django settings, URLs, WSGI
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── accounts/          # User auth (Customer / Provider / Admin)
│   ├── providers/         # Provider profiles, skills, service areas
│   ├── services/          # Service requests lifecycle
│   ├── reviews/           # Customer reviews & ratings
│   ├── ai_assistant/      # 🤖 AI Chat + RAG pipeline
│   │   ├── rag_service.py    # Core RAG engine
│   │   ├── prompts.py        # LLM prompt templates
│   │   └── management/
│   │       └── commands/
│   │           └── ingest_knowledge.py  # ChromaDB indexer
│   ├── recommendations/   # Provider scoring & history
│   └── core/              # Home page, dashboard routing
│       └── management/
│           └── commands/
│               └── seed_data.py  # Initial data seeder
├── templates/             # Bootstrap 5 HTML templates
├── knowledge_base/        # AI knowledge documents
│   ├── home_services_guide.txt
│   └── common_problems.json
├── vector_store/          # ChromaDB persisted vectors
├── static/                # CSS, JS, images
├── media/                 # User uploaded files
└── manage.py
```

---

## 🤖 AI Features

### RAG Pipeline (`ai_assistant/rag_service.py`)

The AI recommendation pipeline works as follows:

1. **User describes problem** → "My kitchen sink is leaking"
2. **Safety check** → Detects dangerous keywords (gas leak, fire, sparks)
3. **Category detection** → Keyword matching (plumber, electrician, AC, etc.)
4. **RAG retrieval** → Searches ChromaDB for relevant knowledge chunks
5. **Provider retrieval** → Queries database for verified providers
6. **Hybrid scoring** → Ranks providers using weighted formula:
   - Service Category Match: **40%**
   - Location Match: **20%**
   - Skills Match: **15%**
   - Customer Rating: **10%**
   - Experience Years: **10%**
   - Availability: **5%**
7. **LLM generation** → OpenAI/compatible LLM explains recommendations
8. **Fallback mode** → Works without API key using keyword-based responses

### Setting up the Knowledge Base

```bash
# Index all knowledge_base/ documents + provider profiles into ChromaDB
python manage.py ingest_knowledge

# Rebuild from scratch
python manage.py ingest_knowledge --rebuild
```

### Configuring OpenAI API

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
```

The app works in **fallback mode** without an API key — it still detects the category and recommends providers, but without the AI-generated explanation.

---

## 📡 REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/recommend/` | POST | Main AI recommendation endpoint |
| `/api/ai/chat/` | POST | Authenticated chat endpoint |
| `/api/providers/` | GET | List all providers |
| `/api/providers/<id>/` | GET | Provider detail |
| `/api/services/` | GET/POST | Service requests |
| `/api/auth/token/` | POST | JWT login |
| `/api/auth/register/customer/` | POST | Customer registration |
| `/api/auth/register/provider/` | POST | Provider registration |

### AI Recommendation API Example

```bash
curl -X POST http://127.0.0.1:8000/api/ai/recommend/ \
  -H "Content-Type: application/json" \
  -d '{"problem": "My kitchen sink is leaking", "location": "Bahria Town"}'
```

---

## 👤 User Roles

| Role | Capabilities |
|------|-------------|
| **Customer** | Register, use AI chat, browse providers, create service requests, submit reviews |
| **Provider** | Register, complete profile, manage service areas, accept/reject requests |
| **Admin** | Full access, verify providers, view AI conversations, manage all data |

---

## 🌐 Key URLs

| URL | Description |
|-----|-------------|
| `/` | Home page with AI search |
| `/ai/` | AI Assistant chat |
| `/providers/` | Browse providers |
| `/services/` | Service requests |
| `/admin/` | Django admin panel |
| `/accounts/login/` | Login |
| `/accounts/register/customer/` | Customer registration |
| `/accounts/register/provider/` | Provider registration |

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.14, Django 6.1 |
| **REST API** | Django REST Framework 3.18 |
| **Authentication** | JWT (djangorestframework-simplejwt) |
| **AI/LLM** | OpenAI API (configurable) |
| **Embeddings** | Sentence-Transformers (all-MiniLM-L6-v2) |
| **Vector DB** | ChromaDB (persistent) |
| **Database** | SQLite (dev) / PostgreSQL-ready |
| **Frontend** | Bootstrap 5, Vanilla JS |
| **Document parsing** | pypdf |

---

## ⚠️ Safety Features

The AI assistant automatically detects dangerous situations and provides immediate warnings:

- **Gas leaks** → Evacuate, call SNGPL 1199
- **Electrical sparks/fire** → Cut main power, call emergency services
- **Structural damage** → Evacuation advice
- All AI responses include: *"This is an AI assessment, not a professional inspection"*

---

## 🔧 Development Notes

- **No compiler required** — all packages use pre-built binary wheels
- **Works offline** — RAG and fallback mode work without internet
- **Provider verification** — Admin must mark providers as verified before they appear in AI recommendations
- **Seed data** — 8 service categories, 75+ skills, 8 sample verified providers in Rawalpindi/Islamabad area
=======
# AI_House_Services
>>>>>>> f7515dfd2b970de58d0e2fa2cf89a3167b86afbc
