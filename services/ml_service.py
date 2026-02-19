import numpy as np
import shap
from sklearn.ensemble import RandomForestRegressor
from database.db import get_connection


# =====================================================
# PART 1 — SIMPLE FUTURE PREDICTION (PLACEHOLDER FOR LSTM)
# =====================================================

def predict_future_score(days_ahead):
    """
    Simple time-based declining trend prediction.
    Replace this later with real LSTM model.
    """

    base_score = 85
    decline_rate = 1.5  # points per day

    predicted = base_score - (days_ahead * decline_rate)

    return round(float(max(predicted, 0)), 2)


# =====================================================
# PART 2 — LOAD TRAINING DATA FROM DATABASE
# =====================================================

def load_training_data():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT total_impact, score
        FROM sustainability_history
        WHERE score IS NOT NULL
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows or len(rows) < 3:
        return None, None

    X = []
    y = []

    for row in rows:
        impact = row["total_impact"]
        score = row["score"]

        # Simulate feature breakdown
        energy = impact * 0.5
        water = impact * 0.3
        traffic = impact * 0.2

        X.append([energy, water, traffic])
        y.append(score)

    return np.array(X), np.array(y)


# =====================================================
# PART 3 — TRAIN SURROGATE MODEL FOR SHAP
# =====================================================

def train_surrogate_model():

    X, y = load_training_data()

    if X is None:
        return None, None

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    explainer = shap.Explainer(model, X)

    return model, explainer


# =====================================================
# PART 4 — SHAP EXPLAINABILITY FUNCTION
# =====================================================

def explain_prediction(energy, water, traffic):

    model, explainer = train_surrogate_model()

    if model is None:
        return {
            "error": "Not enough training data"
        }

    input_data = np.array([[energy, water, traffic]])

    shap_values = explainer(input_data)

    contributions = shap_values.values[0]

    return {
        "energy_contribution": round(float(contributions[0]), 2),
        "water_contribution": round(float(contributions[1]), 2),
        "traffic_contribution": round(float(contributions[2]), 2)
    }
