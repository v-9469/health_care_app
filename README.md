# Healthcare Backend System (Django & DRF) - Phase 1: Doctor Management

A clean-architecture Django backend for a healthcare application built with **Django 5**, **Django REST Framework (DRF)**, **PostgreSQL 16**, **JWT Authentication** (`djangorestframework-simplejwt`), **Dependency Injection (DI)**, **Docker containerization**, and a **Centralized Pytest Harness with In-Memory DB Mocks**.

---

## 📁 Project Structure (Phase 1: Doctor Management)

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
├── apps/
│   └── doctors/                         # Feature 1: Doctor Management Module
│       ├── __init__.py
│       ├── apps.py
│       ├── interfaces.py                # IDoctorRepository abstraction
│       ├── models.py                    # Doctor model with DB indexes
│       ├── repositories.py              # DjangoDoctorRepository (ORM)
│       ├── serializers.py               # Doctor serializers & validation
│       ├── services.py                  # DoctorService (DI)
│       ├── urls.py                      # Doctor URL routing
│       └── views.py                     # Injected APIViews
│
├── tests/                               # Centralized Pytest Test Suite
│   ├── __init__.py
│   ├── conftest.py                      # Global fixtures & DI Container auto-mocking
│   ├── mocks.py                         # In-memory mock repositories
│   ├── test_init_setup.py               # Core smoke tests
│   └── test_doctor_feature.py           # Doctor Management Pytest Feature Suite (16 test cases)
│
├── .dockerignore                        # Docker build ignore rules
├── .env.example                         # PostgreSQL & JWT environment template
├── .env                                 # Local environment configuration
├── .gitattributes                       # Line endings normalization
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

### 1. Build and Start Full Stack (PostgreSQL + Django Web)
```powershell
docker compose up -d --build
```

### 2. Apply Database Migrations
```powershell
docker compose exec web python manage.py migrate
```

### 3. Run Pytest Test Suite Inside Docker
```powershell
docker compose exec web pytest
```

---

## 📋 Doctor Management APIs

| Method | Endpoint | Description | Request Body | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/doctors/` | Create a new doctor | `{"name": "...", "specialization": "...", "contact_number": "...", "email": "...", "experience_years": 10}` | `201 Created` |
| `GET` | `/api/doctors/` | List all doctors (supports `?specialization=...` & `?search=...`) | None | `200 OK` |
| `GET` | `/api/doctors/<id>/` | Get details of a specific doctor | None | `200 OK` |
| `PUT` | `/api/doctors/<id>/` | Full update of doctor record | Full doctor payload | `200 OK` |
| `PATCH`| `/api/doctors/<id>/` | Partial update of doctor record | Partial doctor payload | `200 OK` |
| `DELETE`| `/api/doctors/<id>/` | Delete doctor record | None | `204 No Content` |

---

## 📖 Interactive Swagger & OpenAPI Documentation

When the stack is running (`http://127.0.0.1:8000`), open your browser at:
* **Interactive Swagger UI**: `http://127.0.0.1:8000/api/docs/`
* **Redoc Documentation**: `http://127.0.0.1:8000/api/redoc/`
* **Raw OpenAPI 3 Schema**: `http://127.0.0.1:8000/api/schema/`
