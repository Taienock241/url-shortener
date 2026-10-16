# URL Shortener Dashboard

**Live site:** [Open the deployed dashboard](https://your-url-shortener-domain.example.com)

> Replace the placeholder URL above with the public application URL after deploying.

## About the app

This project is a full-stack URL shortener that turns long web addresses into
short, shareable links. The dashboard provides a simple interface for creating
links and reviewing their performance.

When a visitor submits a valid `http` or `https` URL, the FastAPI backend
generates a unique short code and stores the record in PostgreSQL. Opening the
short link redirects the visitor to the original destination and increments its
click count. The dashboard reads the real records from the API to display recent
links, creation dates, total links, total clicks, and average clicks per link.

The frontend uses plain HTML, CSS, and JavaScript, so it does not require a
JavaScript framework or frontend build step.

## Technology stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **Frontend:** HTML5, CSS3, vanilla JavaScript
- **Testing:** pytest with an isolated SQLite test database

## Features

- Create short URLs through `POST /api/urls`
- Redirect short links using HTTP `302 Found`
- Retrieve URL metadata through `GET /api/urls/{short_code}`
- Browse recent links through `GET /api/urls`
- View live link and click totals in the dashboard
- Validate URL format and allow only `http` and `https`
- Generate random seven-character codes using a 62-character alphabet
- Enforce code uniqueness in the database and retry collisions
- Persist records in PostgreSQL
- Track click counts
- Test core behavior with pytest

## Requirements

- Python 3.10+
- PostgreSQL 14+ (or a compatible recent version)
- PowerShell on Windows, or a terminal on macOS/Linux

## Setup on Windows PowerShell

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Create the PostgreSQL database and user

Open `psql` as a PostgreSQL administrator, then run:

```sql
CREATE USER urlshortener WITH PASSWORD 'replace-this-password';
CREATE DATABASE urlshortener OWNER urlshortener;
```

If you use different credentials, update `DATABASE_URL` accordingly.

### 4. Configure environment variables

Copy `.env.example` to `.env`, then update its values. The app reads operating-system environment variables; it does not automatically parse `.env`. To load the values in PowerShell for the current terminal session, run:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://urlshortener:replace-this-password@localhost:5432/urlshortener"
$env:BASE_URL = "http://127.0.0.1:8000"
```

Use the same `DATABASE_URL` in every terminal where you run the app. Never commit real credentials.

### 5. Run the application

From the project root:

```powershell
python -m uvicorn app.main:app --reload
```

Open:
- Dashboard: http://127.0.0.1:8000/
- API health: http://127.0.0.1:8000/health
- Interactive docs: http://127.0.0.1:8000/docs
- Database health: http://127.0.0.1:8000/health/database

The application creates the MVP database table on startup. For production deployments, use Alembic migrations.

## API endpoints

### Create a short URL

`POST /api/urls`

Request:

```json
{
  "url": "https://example.com/articles/software-engineering"
}
```

Success response (`201 Created`):

```json
{
  "original_url": "https://example.com/articles/software-engineering",
  "short_code": "aB3x9Qp",
  "short_url": "http://127.0.0.1:8000/aB3x9Qp",
  "created_at": "2026-01-01T12:00:00"
}
```

The short code and timestamp above are examples; actual values are generated at runtime.

### Redirect to the original URL

`GET /{short_code}`

Returns `302 Found` with a `Location` header pointing to the original URL. Unknown codes return `404 Not Found`.

### Retrieve URL information

`GET /api/urls/{short_code}`

Returns the original URL, short code, creation time, and click count.

### List recent URLs

`GET /api/urls?limit=50&offset=0`

Returns up to 100 URL records, newest first. Each record includes the original URL,
short URL, creation time, short code, and click count. The dashboard calculates its
total link and click cards from this response.

## Error behavior

- `201 Created`: URL stored successfully
- `302 Found`: redirect to the original URL
- `404 Not Found`: short code does not exist
- `422 Unprocessable Entity`: missing, malformed, or disallowed URL input
- `503 Service Unavailable`: code generation repeatedly collided

FastAPI provides structured validation error responses. Unexpected database failures are not intentionally disguised as client errors.

## Short-code design

The code generator selects each character securely from uppercase letters, lowercase letters, and digits: 62 possible characters per position. With seven characters, the theoretical code space is `62^7` (about 3.52 trillion combinations).

Random collisions remain possible. The database `UNIQUE` constraint is the final guarantee that two records cannot share a code. If an insert violates a constraint, the service rolls back and retries with a newly generated code up to the configured retry limit.

## Testing

Tests use an isolated in-memory SQLite database so the core endpoints can be tested without a running PostgreSQL server. The application itself uses PostgreSQL by default.

```powershell
python -m pytest -v
```

## Project structure

```text
app/                    FastAPI application and database logic
frontend/index.html     Dashboard markup
frontend/style.css      Responsive dashboard styling
frontend/script.js      API calls and dashboard interactions
tests/                  Isolated endpoint tests
```

## Important limitations and security notes

- URL validation checks syntax and allowed schemes; it does not prove that a destination is safe or trustworthy.
- A public deployment should add abuse prevention/rate limiting, monitoring, and a policy for malicious destinations.
- Click counts are a simple MVP metric, not detailed analytics.
- `Base.metadata.create_all()` is convenient for a course MVP. Production changes should use versioned migrations such as Alembic.
- Configure `BASE_URL` to the public origin when deploying. Do not expose the local development URL as a production short link.
- The app intentionally has no authentication in the MVP.

## Suggested Git workflow

```powershell
git init
git add .
git commit -m "Build FastAPI URL shortener MVP"
```

Review `.gitignore` and confirm `.env` and `venv/` are not tracked before pushing to GitHub.
