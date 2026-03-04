import os
import psycopg2
import psycopg2.extras

# ✅ Uses SUPABASE_DB_URL from Render environment variables
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

def get_connection():
    if not DATABASE_URL:
        raise Exception("[DB ERROR] SUPABASE_DB_URL environment variable is not set!")
    conn = psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        cursor_factory=psycopg2.extras.RealDictCursor
    )
    return conn