# CareerLens

### AI-Powered Resume & Job Intelligence Platform

CareerLens is a Flask-based backend application that helps users analyze their resumes against job descriptions using traditional text processing and AI/LLM-powered analysis.

The project is designed as a production-style REST API with authentication, PostgreSQL, database migrations, resume processing, job processing, AI matching, testing, and containerization.

---

## 🚀 Features

### Authentication & Security

- User registration
- Secure password hashing
- JWT-based authentication
- Protected API endpoints
- Current-user identification
- User ownership and authorization
- Input validation using Pydantic
- Secure environment variable configuration
- Centralized API error handling

### Resume Management

- Upload resumes through REST APIs
- PDF resume processing
- Resume text extraction
- Resume processing pipeline
- Resume metadata storage
- Resume ownership per user

### Job Description Management

- Create job descriptions
- Store job information
- Retrieve jobs
- Update jobs
- Delete jobs
- Process job descriptions
- Associate jobs with authenticated users

### AI-Powered Analysis

CareerLens can analyze a resume against a job description and provide insights such as:

- Matching skills
- Missing skills
- Relevant keywords
- Resume-job compatibility
- ATS-style analysis
- Improvement suggestions
- AI-generated recommendations

### Backend Engineering

- Flask Application Factory
- Flask Blueprints
- Service-layer architecture
- SQLAlchemy ORM
- PostgreSQL
- Flask-Migrate / Alembic
- Pydantic validation
- RESTful API design
- Logging
- Error handling
- Database constraints and indexes
- Automated testing with pytest

### Deployment

- Docker support
- Environment-based configuration
- Production Flask configuration
- Gunicorn support
- Docker Compose support

---

# 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │      Client         │
                    │ Postman / Frontend  │
                    └──────────┬──────────┘
                               │
                               │ HTTP / REST
                               ▼
                    ┌─────────────────────┐
                    │      Flask API      │
                    │                     │
                    │  Routes / Blueprints│
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
          ┌──────────┐   ┌──────────┐   ┌──────────┐
          │ Schemas  │   │ Services │   │   Auth   │
          │ Pydantic │   │ Business │   │   JWT    │
          │          │   │  Logic   │   │          │
          └──────────┘   └─────┬────┘   └──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
          ┌──────────┐   ┌──────────┐   ┌──────────┐
          │ Resume   │   │   Jobs   │   │ Matching │
          │Processing│   │Processing│   │  Engine  │
          └──────────┘   └──────────┘   └─────┬────┘
                                              │
                                              ▼
                                      ┌──────────────┐
                                      │  LLM / AI    │
                                      │   Service    │
                                      └──────────────┘

                               │
                               ▼
                    ┌─────────────────────┐
                    │     PostgreSQL      │
                    │                     │
                    │ Users               │
                    │ Resumes             │
                    │ Jobs                │
                    │ Analyses            │
                    └─────────────────────┘

```

# TECH STACK

| Technology         | Purpose                    |
| ------------------ | -------------------------- |
| Python             | Backend programming        |
| Flask              | Web framework / REST API   |
| PostgreSQL         | Relational database        |
| SQLAlchemy         | ORM                        |
| Flask-Migrate      | Database migrations        |
| Alembic            | Migration engine           |
| Pydantic           | Request validation         |
| Flask-JWT-Extended | JWT authentication         |
| Werkzeug           | Password hashing           |
| PDF Processing     | Resume text extraction     |
| LLM API            | AI-powered resume analysis |
| pytest             | Automated testing          |
| Docker             | Containerization           |
| Gunicorn           | Production WSGI server     |
| Git & GitHub       | Version control            |



# 📁 Project Structure
```
FLASK1/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── resume.py
│   │   ├── job.py
│   │   └── analysis.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── job.py
│   │   └── analysis.py
│   │
│   ├── routes/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── resumes.py
│   │   ├── jobs.py
│   │   └── analyses.py
│   │
│   └── services/
│       ├── auth.py
│       ├── resume_processing.py
│       ├── resume_storage.py
│       ├── job_processing.py
│       ├── matching.py
│       ├── llm.py
│       ├── analytics.py
│       ├── cache.py
│       └── background_tasks.py
│
├── migrations/
│   ├── versions/
│   └── ...
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_jobs.py
│   ├── test_resumes.py
│   └── test_matching.py
│
├── .gitignore
├── requirements.txt
├── run.py
├── Dockerfile
├── docker-compose.yml
└── README.md
```

# 🔐 Authentication Flow

### CareerLens uses JWT-based authentication.

```
             REGISTER
                │
                ▼
       Validate user input
                │
                ▼
       Hash password securely
                │
                ▼
          PostgreSQL
                │
                ▼
             LOGIN
                │
                ▼
       Verify password hash
                │
                ▼
          Generate JWT
                │
                ▼
       Return access token
                │
                ▼
      Client sends token with
       protected API requests
                │
                ▼
       Verify JWT identity
                │
                ▼
        Access API resource
```

###The AI layer can be used to generate:

 - Skill matching
 - Missing skill identification
 - Keyword analysis
 - Resume improvement suggestions
 - Job-specific recommendations
 - ATS-oriented feedback

API credentials are stored through environment variables rather than being hard-coded into the source code.


# ⚙️ Local Setup

### 1. Clone the repository
 - git clone https://github.com/Shaunak-Suryawanshi/AI-RESUME-.git
cd AI-RESUME-

### 2. Create a virtual environment
 - python -m venv .venv

### Activate it:
.venv\Scripts\activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Configure environment variables

Create a .env file:

FLASK_ENV=development

SECRET_KEY=your-secret-key

JWT_SECRET_KEY=your-jwt-secret-key

DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/careerlens

### 5. Run database migrations

flask --app run:app db upgrade

### 6. Start the application

python run.py

### The API will be available at:
http://127.0.0.1:5000
