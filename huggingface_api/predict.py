# =============================================================
# Fix My Ride - Fuel Efficiency Predictor
# Core prediction logic (Hugging Face Deployment)
# =============================================================

import pickle
import pandas as pd
import numpy as np
import os

# =============================================================
# Load Model
# =============================================================

# Resolve model path relative to this file's directory
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuel_model.pkl")

def load_model(filepath=MODEL_PATH):
    with open(filepath, 'rb') as f:
        model_data = pickle.load(f)
    return model_data["model"], model_data["feature_cols"]


# =============================================================
# Conversion Helpers
# =============================================================

def mpg_to_kmpl(mpg: float) -> float:
    """Convert Miles Per Gallon to Kilometers Per Liter"""
    return round(mpg * 0.425144, 2)

def kmpl_to_lper100km(kmpl: float) -> float:
    """Convert KM/L to Liters per 100 KM (European standard)"""
    if kmpl == 0:
        return 0
    return round(100 / kmpl, 2)

def get_efficiency_rating(kmpl: float) -> dict:
    """Rate fuel efficiency from Very Poor to Excellent"""
    if kmpl >= 18:
        return {"rating": "Excellent",  "emoji": "🟢", "description": "Very fuel efficient vehicle"}
    elif kmpl >= 14:
        return {"rating": "Good",       "emoji": "🟢", "description": "Good fuel efficiency"}
    elif kmpl >= 10:
        return {"rating": "Average",    "emoji": "🟡", "description": "Average fuel efficiency"}
    elif kmpl >= 7:
        return {"rating": "Poor",       "emoji": "🟠", "description": "Below average fuel efficiency"}
    else:
        return {"rating": "Very Poor",  "emoji": "🔴", "description": "Very poor fuel efficiency"}


# =============================================================
# Fuel Tips Based on Car Profile
# =============================================================

def get_fuel_tips(cylinders: int, weight: float, kmpl: float) -> list:
    """Return personalized fuel saving tips based on car specs"""
    tips = []

    # Always applicable tips
    tips.append("Maintain correct tyre pressure — low pressure increases fuel consumption by up to 3%.")
    tips.append("Avoid sudden acceleration and hard braking — smooth driving saves up to 20% fuel.")
    tips.append("Remove unnecessary weight from the car — extra 50kg increases fuel use by 2%.")

    # Based on cylinders
    if cylinders >= 6:
        tips.append("Your engine has many cylinders — consider using cruise control on highways to save fuel.")
        tips.append("High cylinder engines benefit greatly from regular air filter replacements.")

    # Based on weight
    if weight > 3500:
        tips.append("Your vehicle is heavy — avoid idling for long periods as it wastes more fuel.")

    # Based on efficiency rating
    if kmpl < 10:
        tips.append("Consider getting an engine tune-up — worn spark plugs can reduce efficiency by 30%.")
        tips.append("Check if engine oil needs changing — old oil increases engine friction and fuel use.")

    if kmpl >= 14:
        tips.append("Your car is efficient — maintain this by following scheduled service intervals.")

    # General tips
    tips.append("Drive at 80-90 km/h on highways — this is the most fuel-efficient speed range.")
    tips.append("Use air conditioning wisely — AC can increase fuel consumption by 10-15%.")

    return tips[:5]  # Return top 5 most relevant tips


# =============================================================
# Monthly Cost Estimator
# =============================================================

def estimate_monthly_cost(
    kmpl: float,
    daily_km: float = 40,
    fuel_price_per_liter: float = 280  # PKR default
) -> dict:
    if kmpl <= 0:
        return {}

    daily_liters   = daily_km / kmpl
    monthly_liters = daily_liters * 30
    monthly_cost   = monthly_liters * fuel_price_per_liter

    return {
        "daily_km":           daily_km,
        "daily_liters":       round(daily_liters, 2),
        "monthly_liters":     round(monthly_liters, 2),
        "monthly_cost_pkr":   round(monthly_cost, 0),
        "fuel_price_per_liter": fuel_price_per_liter
    }


# =============================================================
# Main Prediction Function
# =============================================================

def predict_fuel_efficiency(
    cylinders:    int,
    displacement: float,
    horsepower:   float,
    weight:       float,
    acceleration: float,
    model_year:   int,
    origin:       int,
    daily_km:     float = 40,
    fuel_price:   float = 280
) -> dict:
    """
    Main function to predict fuel efficiency.

    Parameters:
    -----------
    cylinders    : Number of engine cylinders (e.g. 4, 6, 8)
    displacement : Engine displacement in cc (e.g. 1300, 1800)
    horsepower   : Engine horsepower (e.g. 88, 120)
    weight       : Vehicle weight in kg (e.g. 1200, 1800)
    acceleration : 0-60 mph time in seconds (e.g. 12.5)
    model_year   : Last 2 digits of year (e.g. 98 for 1998, 15 for 2015)
    origin       : 1=American, 2=European, 3=Asian
    daily_km     : Average daily driving distance in km
    fuel_price   : Fuel price per liter in PKR

    Returns:
    --------
    dict with mpg, kmpl, rating, tips, cost estimate
    """

    # Load model
    model, feature_cols = load_model()

    # Build input dataframe
    input_data = pd.DataFrame([{
        'cylinders':    cylinders,
        'displacement': displacement,
        'horsepower':   horsepower,
        'weight':       weight,
        'acceleration': acceleration,
        'model_year':   model_year,
        'origin':       origin
    }])

    # Predict MPG
    predicted_mpg = model.predict(input_data[feature_cols])[0]
    predicted_mpg = max(predicted_mpg, 1)  # prevent negative values

    # Convert units
    kmpl        = mpg_to_kmpl(predicted_mpg)
    lper100km   = kmpl_to_lper100km(kmpl)

    # Get rating
    rating_info = get_efficiency_rating(kmpl)

    # Get tips
    tips = get_fuel_tips(cylinders, weight, kmpl)

    # Estimate cost
    cost = estimate_monthly_cost(kmpl, daily_km, fuel_price)

    return {
        "prediction": {
            "mpg":              round(predicted_mpg, 1),
            "kmpl":             kmpl,
            "liters_per_100km": lper100km,
        },
        "rating":   rating_info,
        "tips":     tips,
        "monthly_cost_estimate": cost,
        "input_summary": {
            "cylinders":    cylinders,
            "displacement": displacement,
            "horsepower":   horsepower,
            "weight_kg":    weight,
            "model_year":   f"{'19' if model_year > 20 else '20'}{model_year:02d}"
        }
    }
