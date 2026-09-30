# Voice AI API

A FastAPI backend for a Voice AI application. The current version provides PostgreSQL persistence, user signup and login, JWT bearer authentication, protected user details, and a protected placeholder chat endpoint. The actual AI integration is the next step.

## Current features

- User registration with unique email validation
- Secure password hashing through `pwdlib`
- Login with a JWT access token
- Protected `/me` and `/chat` endpoints
- SQLAlchemy 2.0 ORM models and database sessions
- PostgreSQL connectivity through Psycopg 3
- Automatic Swagger UI and ReDoc documentation

## Project structure

```text
voice_ai/
|-- backend/
|   |-- auth.py          # Creates, validates, and expires JWT access tokens
|   |-- database.py      # Configures SQLAlchemy and provides database sessions
|   |-- main.py          # Creates the API, request schemas, and route handlers
|   `-- models.py        # Defines tables as SQLAlchemy ORM model classes
|-- .env                 # Local secrets and database configuration (do not commit)
|-- .gitignore           # Files and directories excluded from Git
|-- requirements.txt     # Exact Python package versions used by the project
`-- README.md            # Project setup, architecture, and API documentation
```

## Essential role of every file

### `backend/database.py`

This module owns the database configuration shared by the rest of the application.

- `load_dotenv()` loads values from the root `.env` file.
- `DATABASE_URL` reads the PostgreSQL connection string.
- `engine` manages SQLAlchemy connections to the database.
- `SessionLocal` creates a new ORM session for each request that needs database access.
- `Base` is the parent class for all ORM models.
- `get_db()` is a FastAPI dependency. It yields a session to a route and closes it in `finally`, including when the route raises an error.

### `backend/models.py`

This module describes the database tables as Python classes. It currently contains one model:

```python
class User(Base):
    __tablename__ = "users"
```

Because `User` inherits from `Base`, SQLAlchemy registers it in `Base.metadata`. Its fields map to columns in the `users` table:

| Attribute | Database type | Purpose |
|---|---|---|
| `id` | Integer primary key | Unique user identifier |
| `name` | `String(100)` | User's name |
| `email` | `String(255)` | Unique, indexed login email |
| `password_hash` | `String(255)` | Password hash; the plain password is never stored |

#### How `models.py` is used

`main.py` imports the complete module with `from backend import models`. This import is essential for two reasons:

1. It loads `User`, registering the `users` table with `Base.metadata` before `Base.metadata.create_all(bind=engine)` runs.
2. It gives route handlers access to `models.User` for queries and new records.

Examples from the current application:

```python
# Find a user by email during signup or login.
select(models.User).where(models.User.email == user.email)

# Find a user by primary key in protected endpoints.
db.get(models.User, user_id)

# Construct a new database row during signup.
new_user = models.User(...)
```

The model defines data structure only. Querying, validation, password hashing, commits, and API responses remain in `main.py`.

### `backend/auth.py`

This module contains JWT authentication utilities.

- Reads `JWT_SECRET_KEY` from `.env`.
- Uses the `HS256` signing algorithm.
- Sets access tokens to expire after 30 minutes.
- `security = HTTPBearer()` extracts bearer credentials from the `Authorization` header.
- `create_access_token(user_id)` places the user's ID in the JWT `sub` claim and adds an expiry time.
- `verify_access_token(token)` validates the signature and expiration, then returns the user ID.
- Invalid, malformed, or expired tokens produce an HTTP `401 Unauthorized` response.

### `backend/main.py`

This is the application entry point.

- Imports `models` so ORM tables are registered.
- Calls `Base.metadata.create_all(bind=engine)` at startup to create missing tables.
- Creates the FastAPI application as `app`.
- Defines Pydantic request models for signup, login, and chat.
- Configures the recommended `pwdlib` password hasher.
- Implements all current API routes.
- Uses `Depends(get_db)` to give routes a managed SQLAlchemy session.
- Uses `Depends(security)` and `verify_access_token()` on protected routes.

### `.env`

Stores machine-specific settings and secrets outside the Python source code. The current application requires:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/voice_ai_db
JWT_SECRET_KEY=replace_with_a_long_random_secret
```

Do not commit this file. Use a strong, unpredictable JWT secret in real environments.

### `.gitignore`

Prevents local-only or generated files—especially `.env`, virtual environments, caches, and editor settings—from being committed. Confirm that `.env` is ignored before pushing the repository.

### `requirements.txt`

Pins the project's Python dependencies and their versions so the environment can be reproduced. The main direct technologies represented are FastAPI, Uvicorn, SQLAlchemy, Psycopg, Pydantic, `python-dotenv`, `pwdlib`, and Argon2.

The source also imports the `jwt` package. If a fresh installation reports `ModuleNotFoundError: No module named 'jwt'`, install PyJWT and then record it in `requirements.txt`:

```bash
pip install PyJWT
```

### `README.md`

Documents the current architecture, setup, authentication flow, and endpoint behavior. It should be updated whenever routes, models, environment variables, or setup steps change.

## How the application works

```text
Client request
    |
    v
FastAPI route in main.py
    |
    +-- request validation through a Pydantic model
    +-- optional JWT validation through auth.py
    `-- database session supplied by database.py
             |
             v
       models.User maps Python operations to the PostgreSQL users table
```

The authentication flow is:

1. The client signs up with a name, email, and password.
2. The password is hashed before the user is saved.
3. The client logs in with the same email and password.
4. The API verifies the password and returns a bearer token.
5. The client sends that token to `/me` or `/chat` in the `Authorization` header.
6. The API validates the token, extracts the user ID, and loads that user through `models.User`.

## Setup

### Prerequisites

- Python 3.10 or newer
- A running PostgreSQL database

### Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Configure environment variables

Create `.env` in the project root and add `DATABASE_URL` and `JWT_SECRET_KEY` as shown above. Ensure the target PostgreSQL database already exists; SQLAlchemy creates missing tables, not the database itself.

## Run the application

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API normally runs at `http://127.0.0.1:8000`.

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API endpoints

### `GET /`

Public health check.

```json
{
  "message": "Voice AI API is running"
}
```

### `POST /signup`

Creates a user.

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepassword123"
}
```

Successful response:

```json
{
  "message": "User created successfully",
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

Returns `400` when the email is already registered.

### `POST /login`

Verifies credentials and returns a token.

```json
{
  "email": "jane@example.com",
  "password": "securepassword123"
}
```

Successful response:

```json
{
  "access_token": "<signed-jwt-token>",
  "token_type": "bearer"
}
```

Returns `401` when the email or password is invalid.

### `GET /me`

Returns the authenticated user's public details. Send the login token as:

```http
Authorization: Bearer <access_token>
```

Successful response:

```json
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

### `POST /chat`

A protected placeholder for the future Voice AI chat integration. It currently confirms the authenticated user and echoes the submitted message.

Header:

```http
Authorization: Bearer <access_token>
```

Request body:

```json
{
  "message": "Hello"
}
```

Current response:

```json
{
  "user_id": 1,
  "message": "Hello",
  "response": "AI will be connected next"
}
```

## Current limitations and next steps

- `/chat` does not yet call an AI or voice service.
- Table creation uses `create_all`; production schema changes should use migrations such as Alembic.
- Request fields currently use basic string validation and can be strengthened with email, length, and password rules.
- JWT tokens expire after 30 minutes; refresh tokens and logout/revocation are not implemented.
- Automated tests are not yet included.
