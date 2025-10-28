# Install pgvector Extension for PostgreSQL

## Option 1: Quick Fix - Remove Vector Fields (Temporary)

If you want to proceed without face recognition for now, we can temporarily disable vector fields.

## Option 2: Install pgvector (Recommended)

### Step 1: Download pgvector for Windows

1. Download from: https://github.com/pgvector/pgvector/releases
2. Get the Windows .dll file for your PostgreSQL version

### Step 2: Install via psql

Open **pgAdmin** or **psql** and run:

```sql
-- Connect to safenest database
\c safenest

-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_available_extensions WHERE name = 'vector';
```

### Step 3: Re-run migrations

```bash
python manage.py migrate
```

---

## Option 3: Use SQLite Instead (Quick Development)

If pgvector is difficult to install, we can switch to SQLite for development:

Change `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Note: Face embeddings won't work efficiently with SQLite, but everything else will.

---

## Option 4: Docker PostgreSQL with pgvector

Use Docker to get PostgreSQL with pgvector pre-installed:

```bash
docker run -d \
  --name safenest-postgres \
  -e POSTGRES_DB=safenest \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=root \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

Which option would you like to use?
