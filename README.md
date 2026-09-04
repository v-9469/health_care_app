# Healthcare Backend System (Django & DRF) 

A clean-architecture Django foundation for a healthcare application built with **Django 5**, **Django REST Framework (DRF)**, **PostgreSQL 16**, **JWT Authentication** (`djangorestframework-simplejwt`), **Dependency Injection (DI)**, **Docker containerization**, and a **Centralized Pytest Harness with In-Memory DB Mocks**.

---

## 📁 Project Structure (Phase 0 Only)

```
health_care_app/
│
├── core/                                # Core Project Infrastructure
│   ├── __init__.py
│   ├── asgi.py                          # ASGI interface
│   ├── container.py                     # Central Dependency Injection Container
│   ├── exceptions.py                    # Standardized error response envelope
│   ├── permissions.py                   # Custom permission classes
│   ├── settings.py                      # PostgreSQL, Connection Pooling & JWT settings
│   ├── urls.py                          # Master URL routing & Swagger/Redoc docs
│   └── wsgi.py                          # WSGI interface
│
├── tests/                               # Centralized Pytest Test Suite
│   ├── __init__.py
│   ├── conftest.py                      # Global fixtures & DI Container auto-mocking
│   ├── mocks.py                         # In-memory mock repositories (User, Patient, Doctor, Mapping)
│   └── test_init_setup.py               # Phase 0 smoke tests
│
├── .dockerignore                        # Docker build ignore rules
├── .env.example                         # PostgreSQL & JWT environment template
├── .env                                 # Local environment configuration
├── .gitignore                           # Git ignore rules
├── Dockerfile                           # Django backend container definition
├── docker-compose.yml                   # Multi-container orchestration (web + db)
├── pytest.ini                           # Pytest configuration
├── requirements.txt                     # Project dependencies
├── manage.py                            # Django management CLI
└── README.md                            # Comprehensive project documentation
```

---

## 🚀 Getting Started with Docker

### 1. Environment Variables
```powershell
cp .env.example .env
```

### 2. Build and Start Full Stack (Django + PostgreSQL)
```powershell
docker compose up -d --build
```

### 3. Check Service Logs
```powershell
docker compose logs -f
```

### 4. Run Pytest Suite Inside Docker Container
```powershell
docker compose exec web pytest
```

### 5. Stop Containers
```powershell
docker compose down
```

---

## 🔒 Standardized Error Format

All error responses return a uniform JSON envelope:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed for one or more fields.",
    "details": {}
  }
}
```

---

## 📖 API Documentation (Interactive Swagger)

When the stack is running (`http://127.0.0.1:8000`), open your browser at:
* **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
* **Redoc**: `http://127.0.0.1:8000/api/redoc/`
* **Raw Schema**: `http://127.0.0.1:8000/api/schema/`
