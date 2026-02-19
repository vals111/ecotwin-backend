import bcrypt
from database.db import get_connection

def create_admin():

    conn = get_connection()
    cursor = conn.cursor()

    email = "callmevish.c7@gmail.com"
    username = "Salaar"
    password = "Deva@123"

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    try:
        cursor.execute("""
            INSERT INTO users
            (email, username, password, role, is_verified)
            VALUES (?, ?, ?, ?, ?)
        """, (
            email,
            username,
            hashed_password,
            "admin",
            1   # Mark as verified
        ))

        conn.commit()

        print("Admin account created successfully.")
        print("Email:", email)
        print("Password:", password)

    except Exception as e:
        print("Admin creation failed or already exists:", e)

    finally:
        conn.close()


if __name__ == "__main__":
    create_admin()
