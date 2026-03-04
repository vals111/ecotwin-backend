import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

def get_connection():

    conn = psycopg2.connect(
        DATABASE_URL,
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    return conn