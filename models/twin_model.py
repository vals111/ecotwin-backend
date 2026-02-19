class DigitalTwin:
    def __init__(self):
        self.energy_system = {
            "current_usage_kwh": 1200,
            "peak_demand_kwh": 1500,
            "status": "stable"
        }

        self.water_system = {
            "current_usage_liters": 50000,
            "leakage_detected": False,
            "status": "normal"
        }

        self.traffic_system = {
            "avg_vehicle_count": 3200,
            "congestion_level": "moderate",
            "status": "controlled"
        }

    def to_dict(self):
        return {
            "energy_system": self.energy_system,
            "water_system": self.water_system,
            "traffic_system": self.traffic_system
        }
