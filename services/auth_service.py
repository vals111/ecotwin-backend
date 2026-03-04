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
    ).decode('utf-8')  # ✅ decode to string — PostgreSQL stores as TEXT, not BLOB

    otp_code = generate_otp()
    otp_expiry = datetime.now() + timedelta(minutes=5)

    try:
        cursor.execute("""
            INSERT INTO users
            (email, username, password, role, is_verified, otp_code, otp_expiry)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            email,
            username,
            hashed_password,
            role,
            False,
            otp_code,
            otp_expiry
        ))
        conn.commit()
        email_result = send_otp_email(email, otp_code)
        if email_result.get("status") == "error":
            print(f"[WARN] OTP saved but email failed: {email_result.get('message')}")
        return {"status": "otp_sent"}
    except Exception as e:
        print(f"[REGISTER ERROR] {str(e)}")
        return {"status": "email_exists"}
    finally:
        conn.close()

def verify_user_otp(email, otp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT otp_code, otp_expiry, is_verified
        FROM users
        WHERE email=%s
    """, (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"status": "user_not_found"}

    if user["is_verified"]:
        conn.close()
        return {"status": "already_verified"}

    # ✅ Handle both string and datetime otp_expiry from PostgreSQL
    otp_expiry = user["otp_expiry"]
    if isinstance(otp_expiry, str):
        otp_expiry = datetime.fromisoformat(otp_expiry)

    if datetime.now() > otp_expiry:
        conn.close()
        return {"status": "otp_expired"}

    if user["otp_code"] != otp:
        conn.close()
        return {"status": "invalid_otp"}

    cursor.execute("""
        UPDATE users
        SET is_verified=%s,
            otp_code=%s,
            otp_expiry=%s
        WHERE email=%s
    """, (True, None, None, email))
    conn.commit()
    conn.close()
    return {"status": "verified"}

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM users
        WHERE email=%s
    """, (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"status": "invalid_credentials"}

    if not user["is_verified"]:
        return {"status": "not_verified"}

    # ✅ Password is stored as string in PostgreSQL — encode before checking
    stored_password = user["password"]
    if isinstance(stored_password, str):
        stored_password = stored_password.encode('utf-8')

    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
        return {
            "status": "success",
            "user_id": user["id"],
            "role": user["role"]
        }

    return {"status": "invalid_credentials"}