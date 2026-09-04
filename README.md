# Healthcare Backend System (Django & DRF)

A clean-architecture Django backend for a healthcare application built with **Django 5**, **Django REST Framework (DRF)**, **PostgreSQL 16**, **JWT Authentication** (`djangorestframework-simplejwt`), **Dependency Injection (DI)**, **Docker containerization**, and a **Centralized Pytest Harness with In-Memory DB Mocks**.

---

## 📁 Project Structure

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
│   ├── accounts/                        # Authentication & User Management Module
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── interfaces.py                # IUserRepository, ITokenService abstractions
│   │   ├── models.py                    # Custom User model with B-Tree indexes
│   │   ├── repositories.py              # DjangoUserRepository (ORM)
│   │   ├── serializers.py               # Register & Login serializers
│   │   ├── services.py                  # AuthService (DI) & JWTTokenService
│   │   ├── urls.py                      # Auth URL routing
│   │   └── views.py                     # RegisterView, LoginView, UserProfileView
│   │
│   ├── doctors/                         # Doctor Management Module
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── interfaces.py                # IDoctorRepository abstraction
│   │   ├── models.py                    # Doctor model with DB indexes
│   │   ├── repositories.py              # DjangoDoctorRepository (ORM)
│   │   ├── serializers.py               # Doctor serializers & validation
│   │   ├── services.py                  # DoctorService (DI)
│   │   ├── urls.py                      # Doctor URL routing
│   │   └── views.py                     # DoctorListCreateView, DoctorDetailView
│   │
│   └── patients/                        # Patient Management Module
│       ├── __init__.py
│       ├── apps.py
│       ├── interfaces.py                # IPatientRepository abstraction
│       ├── models.py                    # Patient model with composite indexes
│       ├── repositories.py              # DjangoPatientRepository (ORM with user scoping)
│       ├── serializers.py               # Patient serializers & validation
│       ├── services.py                  # PatientService (DI with ownership scoping)
│       ├── urls.py                      # Patient URL routing
│       └── views.py                     # PatientListCreateView, PatientDetailView
│
├── tests/                               # Centralized Pytest Test Suite
│   ├── __init__.py
│   ├── conftest.py                      # Global fixtures & DI Container auto-mocking
│   ├── mocks.py                         # In-memory mock repositories (User, Doctor, Patient, Mapping)
│   ├── test_init_setup.py               # Core smoke tests
│   ├── test_auth_feature.py             # Auth & Security Pytest Feature Suite (11 test cases)
│   ├── test_doctor_feature.py           # Doctor Management Pytest Feature Suite (16 test cases)
│   └── test_patient_feature.py          # Patient Management Pytest Feature Suite (16 test cases)
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

### 3. Run All Pytest Tests Inside Docker
```powershell
docker compose exec web pytest
```

---

## 📋 Available APIs

### 1. Authentication APIs (`/api/auth/`)

| Method | Endpoint | Description | Request Body | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register/` | Register a new user | `{"name": "Dr. Watson", "email": "watson@live.com", "password": "SuperSecret123!"}` | `201 Created` |
| `POST` | `/api/auth/login/` | Authenticate user & get JWT | `{"email": "watson@live.com", "password": "SuperSecret123!"}` | `200 OK` |
| `GET` | `/api/auth/me/` | Current user profile | None (Bearer JWT required) | `200 OK` |

### 2. Patient Management APIs (`/api/patients/`)

| Method | Endpoint | Description | Request Body | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/patients/` | Add a new patient | `{"name": "James Moriarty", "age": 55, "gender": "Male", "contact_number": "+1555999888", "email": "moriarty@org.com", "address": "Reichenbach", "medical_history": "None"}` | `201 Created` |
| `GET` | `/api/patients/` | Retrieve all patients created by authenticated user | Query params: `?search=James` (optional) | `200 OK` |
| `GET` | `/api/patients/<id>/` | Get details of a specific patient | None (Bearer JWT required) | `200 OK` |
| `PUT` | `/api/patients/<id>/` | Full update of patient details | Full patient JSON | `200 OK` |
| `PATCH`| `/api/patients/<id>/` | Partial update of patient details | Partial patient JSON | `200 OK` |
| `DELETE`| `/api/patients/<id>/` | Delete a patient record | None (Bearer JWT required) | `204 No Content` |

### 3. Doctor Management APIs (`/api/doctors/`)

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
