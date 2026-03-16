# =============================================================
# Fix My Ride - Fuel Efficiency Estimator API
# Flask REST API
# =============================================================

from flask import Flask, request, jsonify
from predict import predict_fuel_efficiency
import traceback

app = Flask(__name__)


# =============================================================
# Health Check
# =============================================================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "module": "Fuel Efficiency Estimator"})


# =============================================================
# Main Prediction Endpoint
# =============================================================

@app.route('/predict/fuel', methods=['POST'])
def predict_fuel():
    """
    POST /predict/fuel
    
    Request Body (JSON):
    {
        "cylinders":    4,
        "displacement": 1300,
        "horsepower":   88,
        "weight":       1200,
        "acceleration": 15.0,
        "model_year":   98,
        "origin":       3,
        "daily_km":     50,
        "fuel_price":   280
    }
    
    origin values:
        1 = American car  (Ford, GM, Chevrolet)
        2 = European car  (BMW, Volkswagen, Peugeot)
        3 = Asian car     (Toyota, Honda, Suzuki)
    
    model_year:
        Last 2 digits only. e.g. 1998 → 98, 2015 → 15
    """

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # ── Required fields ──────────────────────────────────
        required = ['cylinders', 'displacement', 'horsepower', 'weight',
                    'acceleration', 'model_year', 'origin']

        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                "error": f"Missing required fields: {missing}"
            }), 400

        # ── Validate ranges ───────────────────────────────────
        errors = []

        if not (2 <= int(data['cylinders']) <= 16):
            errors.append("cylinders must be between 2 and 16")

        if not (500 <= float(data['displacement']) <= 8000):
            errors.append("displacement must be between 500 and 8000 cc")

        if not (30 <= float(data['horsepower']) <= 500):
            errors.append("horsepower must be between 30 and 500")

        if not (500 <= float(data['weight']) <= 5000):
            errors.append("weight must be between 500 and 5000 kg")

        if not (1 <= int(data['origin']) <= 3):
            errors.append("origin must be 1 (American), 2 (European), or 3 (Asian)")

        if errors:
            return jsonify({"error": "Validation failed", "details": errors}), 400

        # ── Optional fields with defaults ─────────────────────
        daily_km    = float(data.get('daily_km',    40))
        fuel_price  = float(data.get('fuel_price',  280))  # PKR default

        # ── Run prediction ────────────────────────────────────
        result = predict_fuel_efficiency(
            cylinders    = int(data['cylinders']),
            displacement = float(data['displacement']),
            horsepower   = float(data['horsepower']),
            weight       = float(data['weight']),
            acceleration = float(data['acceleration']),
            model_year   = int(data['model_year']),
            origin       = int(data['origin']),
            daily_km     = daily_km,
            fuel_price   = fuel_price
        )

        return jsonify({
            "success": True,
            "data": result
        })

    except FileNotFoundError:
        return jsonify({
            "error": "Model not trained yet. Please run train_model.py first."
        }), 500

    except Exception as e:
        return jsonify({
            "error": "Prediction failed",
            "details": str(e)
        }), 500


# =============================================================
# Compare Two Cars Endpoint
# =============================================================

@app.route('/predict/fuel/compare', methods=['POST'])
def compare_cars():
    """
    Compare fuel efficiency of two cars side by side.

    POST /predict/fuel/compare
    {
        "car1": { ...same fields as /predict/fuel... },
        "car2": { ...same fields as /predict/fuel... }
    }
    """
    try:
        data = request.get_json()

        if 'car1' not in data or 'car2' not in data:
            return jsonify({"error": "Provide both 'car1' and 'car2'"}), 400

        def get_prediction(car_data):
            return predict_fuel_efficiency(
                cylinders    = int(car_data['cylinders']),
                displacement = float(car_data['displacement']),
                horsepower   = float(car_data['horsepower']),
                weight       = float(car_data['weight']),
                acceleration = float(car_data['acceleration']),
                model_year   = int(car_data['model_year']),
                origin       = int(car_data['origin']),
                daily_km     = float(car_data.get('daily_km', 40)),
                fuel_price   = float(car_data.get('fuel_price', 280))
            )

        car1_result = get_prediction(data['car1'])
        car2_result = get_prediction(data['car2'])

        # Determine which is better
        car1_kmpl = car1_result['prediction']['kmpl']
        car2_kmpl = car2_result['prediction']['kmpl']

        if car1_kmpl > car2_kmpl:
            winner = "car1"
            diff   = round(car1_kmpl - car2_kmpl, 2)
        elif car2_kmpl > car1_kmpl:
            winner = "car2"
            diff   = round(car2_kmpl - car1_kmpl, 2)
        else:
            winner = "tie"
            diff   = 0

        return jsonify({
            "success": True,
            "car1":    car1_result,
            "car2":    car2_result,
            "comparison": {
                "winner":               winner,
                "difference_kmpl":      diff,
                "more_efficient_by":    f"{diff} km/l"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================
# Run
# =============================================================

if __name__ == '__main__':
    print("🚗 Fix My Ride - Fuel Efficiency API")
    print("📍 Running on http://localhost:5001")
    print("📌 Endpoints:")
    print("   GET  /health")
    print("   POST /predict/fuel")
    print("   POST /predict/fuel/compare")
    app.run(debug=True, port=5001)
