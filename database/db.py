import os
import psycopg2

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

    