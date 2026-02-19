from database.db import get_connection

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT,
            password BLOB NOT NULL,
            role TEXT DEFAULT 'user',
            is_verified INTEGER DEFAULT 0,
            otp_code TEXT,
            otp_expiry TEXT
        )
    """)


    # Sustainability history table (unchanged)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sustainability_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            timestamp TEXT,
            total_impact REAL,
            score REAL,
            simulated_impact REAL,
            simulated_score REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
