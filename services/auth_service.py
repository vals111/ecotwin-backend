import bcrypt
import random
import string
from datetime import datetime, timedelta

from database.db import get_connection
from services.email_service import send_otp_email


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def register_user(email, username, password, role="user"):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )

    otp_code = generate_otp()
    otp_expiry = datetime.now() + timedelta(minutes=5)

    try:
        cursor.execute("""
            INSERT INTO users (email, username, password, role, is_verified, otp_code, otp_expiry)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            email,
            username,
            hashed_password,
            role,
            0,
            otp_code,
            otp_expiry
        ))

        conn.commit()

        # Send OTP email
        send_otp_email(email, otp_code)

        return {"status": "otp_sent"}

    except Exception:
        return {"status": "email_exists"}

    finally:
        conn.close()


def verify_user_otp(email, otp):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT otp_code, otp_expiry, is_verified
        FROM users
        WHERE email=?
    """, (email,))

    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"status": "user_not_found"}

    if user["is_verified"] == 1:
        conn.close()
        return {"status": "already_verified"}

    stored_otp = user["otp_code"]
    expiry_time = datetime.fromisoformat(user["otp_expiry"])

    if datetime.now() > expiry_time:
        conn.close()
        return {"status": "otp_expired"}

    if stored_otp != otp:
        conn.close()
        return {"status": "invalid_otp"}

    cursor.execute("""
        UPDATE users
        SET is_verified=1,
            otp_code=NULL,
            otp_expiry=NULL
        WHERE email=?
    """, (email,))

    conn.commit()
    conn.close()

    return {"status": "verified"}


def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email=?
    """, (email,))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"status": "invalid_credentials"}

    if user["is_verified"] == 0:
        return {"status": "not_verified"}

    if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return {
            "status": "success",
            "user_id": user["id"],
            "role": user["role"]
        }

    return {"status": "invalid_credentials"}
