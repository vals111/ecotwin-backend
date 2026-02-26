import datetime
# ===== GLOBAL TWIN STATE =====
digital_twin = {
    "energy_system": {
        "current_usage_kwh": 5000,
        "peak_demand_kwh": 1500,
        "status": "stable"
    },
    "water_system": {
        "current_usage_liters": 50000,
        "leakage_detected": False,
        "status": "normal"
    },
    "traffic_system": {
        "avg_vehicle_count": 3200,
        "congestion_level": "moderate",
        "status": "controlled"
    }
}

from database.db import get_connection

# ===== BASIC DATA =====

def get_digital_twin_data():
    return digital_twin


def update_energy(value):
    digital_twin["energy_system"]["current_usage_kwh"] = value
    return digital_twin["energy_system"]


def update_water(value):
    digital_twin["water_system"]["current_usage_liters"] = value
    return digital_twin["water_system"]


def update_traffic(value):
    digital_twin["traffic_system"]["avg_vehicle_count"] = value
    return digital_twin["traffic_system"]


# ===== SIMULATION =====

def simulate_scenario(energy_factor, water_factor, traffic_factor):

    base = get_digital_twin_data()

    projected_energy = int(base["energy_system"]["current_usage_kwh"] * energy_factor)
    projected_water = int(base["water_system"]["current_usage_liters"] * water_factor)
    projected_traffic = int(base["traffic_system"]["avg_vehicle_count"] * traffic_factor)

    return {
        "energy_system": {
            "projected_usage_kwh": projected_energy
        },
        "water_system": {
            "projected_usage_liters": projected_water
        },
        "traffic_system": {
            "projected_vehicle_count": projected_traffic
        }
    }


# ===== SUSTAINABILITY CALCULATION =====

def calculate_sustainability(user_id):

    energy = digital_twin["energy_system"]["current_usage_kwh"]
    water = digital_twin["water_system"]["current_usage_liters"]
    traffic = digital_twin["traffic_system"]["avg_vehicle_count"]

    energy_emission = energy * 0.2
    traffic_emission = traffic * 0.1
    water_index = water / 5000

    total_impact = energy_emission + traffic_emission + water_index
    score = max(0, 100 - (total_impact / 100))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sustainability_history
        (user_id, type, timestamp, total_impact, score)
        VALUES (%s, %s, NOW(), %s, %s)
    """, (user_id, "baseline", total_impact, score))

    conn.commit()
    conn.close()

    return {
        "energy_emission_kg": energy_emission,
        "traffic_emission_kg": traffic_emission,
        "water_impact_index": water_index,
        "total_environmental_impact": total_impact,
        "sustainability_score": score
    }


# ===== COMPARISON =====

def simulate_sustainability_comparison(user_id, energy_factor, water_factor, traffic_factor):

    base = calculate_sustainability(user_id)

    simulated = simulate_scenario(energy_factor, water_factor, traffic_factor)

    simulated_energy = simulated["energy_system"]["projected_usage_kwh"]
    simulated_water = simulated["water_system"]["projected_usage_liters"]
    simulated_traffic = simulated["traffic_system"]["projected_vehicle_count"]

    sim_energy_emission = simulated_energy * 0.2
    sim_traffic_emission = simulated_traffic * 0.1
    sim_water_index = simulated_water / 5000

    sim_total = sim_energy_emission + sim_traffic_emission + sim_water_index
    sim_score = max(0, 100 - (sim_total / 100))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sustainability_history
        (user_id, type, timestamp, simulated_impact, simulated_score)
        VALUES (%s, %s, NOW(), %s, %s)
    """, (user_id, "simulation", sim_total, sim_score))

    conn.commit()
    conn.close()

    return {
        "base_impact": base["total_environmental_impact"],
        "simulated_impact": sim_total,
        "impact_difference": sim_total - base["total_environmental_impact"],
        "base_score": base["sustainability_score"],
        "simulated_score": sim_score
    }


# ===== HISTORY =====

def get_sustainability_history():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM sustainability_history
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    history = []

    for row in rows:
        history.append({
            "id": row["id"],
            "type": row["type"],
            "timestamp": row["timestamp"],
            "score": row["score"],
            "simulated_score": row["simulated_score"]
        })

    return history

