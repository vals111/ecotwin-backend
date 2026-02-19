from flask import Flask, jsonify, request, abort
from services.auth_service import verify_user_otp
from flask_cors import CORS
from config import APP_NAME
from database.db import get_connection
from services.auth_service import register_user, login_user
from services.ml_service import predict_future_score, explain_prediction
from services.lstm_service import predict_next_value
from services.twin_service import (
    get_digital_twin_data,
    update_energy,
    update_water,
    update_traffic,
    simulate_scenario,
    calculate_sustainability,
    simulate_sustainability_comparison,
    get_sustainability_history
)

app = Flask(__name__)
CORS(app)

# ===============================
# SECURITY HELPERS
# ===============================

def require_user():
    user_id = request.headers.get("User-ID")
    if not user_id:
        abort(401)
    return user_id


def require_admin():
    user_id = request.headers.get("User-ID")
    if not user_id:
        abort(401)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user or user["role"] != "admin":
        abort(403)

# ===============================
# HEALTH CHECK
# ===============================

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "running",
        "project": APP_NAME
    })

# ===============================
# AUTH ROUTES
# ===============================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    return jsonify(
        register_user(email, username, password)
    )

@app.route("/api/verify-otp", methods=["POST"])
def verify_otp_route():

    data = request.get_json()

    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify({
            "status": "error",
            "message": "Email and OTP are required."
        }), 400

    result = verify_user_otp(email, otp)

    return jsonify(result)


@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    return jsonify(
        login_user(email, password)
    )


# ===============================
# USER ROUTES
# ===============================

@app.route("/api/twin", methods=["GET"])
def twin_data():
    require_user()
    return jsonify(get_digital_twin_data())

@app.route("/api/update/energy", methods=["POST"])
def update_energy_route():
    require_user()
    data = request.get_json()
    return jsonify(update_energy(data.get("value")))

@app.route("/api/update/water", methods=["POST"])
def update_water_route():
    require_user()
    data = request.get_json()
    return jsonify(update_water(data.get("value")))

@app.route("/api/update/traffic", methods=["POST"])
def update_traffic_route():
    require_user()
    data = request.get_json()
    return jsonify(update_traffic(data.get("value")))

@app.route("/api/simulate", methods=["POST"])
def simulate():
    require_user()
    data = request.get_json()

    result = simulate_scenario(
        data.get("energy_factor", 1),
        data.get("water_factor", 1),
        data.get("traffic_factor", 1)
    )

    return jsonify(result)

@app.route("/api/sustainability")
def sustainability():
    user_id = require_user()
    return jsonify(calculate_sustainability(user_id))

@app.route("/api/compare", methods=["POST"])
def compare():
    require_user()
    data = request.get_json()
    user_id = require_user()
    result = simulate_sustainability_comparison(
        user_id,
        data.get("energy_factor", 1),
        data.get("water_factor", 1),
        data.get("traffic_factor", 1)
        )
    return jsonify(result)

@app.route("/api/history", methods=["GET"])
def history():
    require_user()
    return jsonify(get_sustainability_history())

@app.route("/api/predict", methods=["POST"])
def predict():
    require_user()
    data = request.get_json()
    days = data.get("days", 1)
    result = predict_future_score(days)
    return jsonify({"predicted_score": result})

@app.route("/api/lstm_predict", methods=["POST"])
def lstm_predict():
    user_id = require_user()  # Protect route
    data = request.get_json()
    days = data.get("days", 7)
    result = predict_lstm(days)
    return jsonify({"prediction": result})


@app.route("/api/explain", methods=["POST"])
def explain():
    data = request.get_json()
    explanation = explain_prediction(
        data.get("energy"),
        data.get("water"),
        data.get("traffic")
    )
    return jsonify(explanation)

# ===============================
# ADMIN ROUTES
# ===============================
@app.route("/api/admin/users")
def admin_users():
    require_admin()
    conn = get_connection()
    cursor = conn.cursor()
    # Only fetch normal users
    cursor.execute("""
        SELECT id, username, role
        FROM users
        WHERE role = 'user'
    """)
    users = cursor.fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])


@app.route("/api/admin/delete_user", methods=["POST"])
def delete_user():
    require_admin()
    data = request.get_json()
    user_id = data.get("user_id")
    conn = get_connection()
    cursor = conn.cursor()
    # Ensure we only delete normal users
    cursor.execute("""
        DELETE FROM users
        WHERE id=? AND role='user'
    """, (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route("/api/admin/global_metrics", methods=["GET"])
def global_metrics():
    require_admin()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(total_impact) as total FROM sustainability_history")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as count FROM users")
    count = cursor.fetchone()["count"]

    conn.close()

    return jsonify({
        "total_impact": total or 0,
        "total_users": count
    })

# ===============================
# RUN SERVER
# ===============================

if __name__ == "__main__":
    app.run()
