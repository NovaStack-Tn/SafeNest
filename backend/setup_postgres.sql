-- SafeNest PostgreSQL Setup
-- Run this in pgAdmin or psql as superuser (postgres)

-- Create database if it doesn't exist
CREATE DATABASE safenest;

-- Connect to the database
\c safenest

-- Install pgvector extension for face embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE safenest TO postgres;

-- Verify
SELECT version();
SELECT * FROM pg_extension WHERE extname = 'vector';
