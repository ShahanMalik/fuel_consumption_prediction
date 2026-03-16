# =============================================================
# Fix My Ride - Fuel Efficiency Estimator
# Train and Save Model
# =============================================================

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.pipeline import Pipeline
import pickle
import os

# =============================================================
# Step 1 — Load and Clean Dataset
# =============================================================

def load_and_clean_data(filepath="dataset/auto-mpg.csv"):
    print("Loading dataset...")

    # Load dataset
    # The auto-mpg dataset sometimes uses '?' for missing horsepower
    df = pd.read_csv(filepath, na_values='?')

    print(f"Original shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")

    # Drop rows with missing values
    df = df.dropna()
    print(f"After dropping nulls: {df.shape}")

    # Drop car name column - not useful for prediction
    if 'car name' in df.columns:
        df = df.drop(columns=['car name'])

    # Rename columns for clarity if needed
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

    print("\nDataset sample:")
    print(df.head())
    print("\nDataset stats:")
    print(df.describe())

    return df


# =============================================================
# Step 2 — Feature Engineering
# =============================================================

def prepare_features(df):
    # Features we use to predict MPG
    feature_cols = [
        'cylinders',
        'displacement',
        'horsepower',
        'weight',
        'acceleration',
        'model_year',
        'origin'
    ]

    # Target variable
    target_col = 'mpg'

    X = df[feature_cols]
    y = df[target_col]

    return X, y, feature_cols


# =============================================================
# Step 3 — Train Multiple Models and Compare
# =============================================================

def train_and_evaluate(X, y):
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples:  {len(X_test)}")

    # Define models to compare
    models = {
        "Linear Regression": Pipeline([
            ('scaler', StandardScaler()),
            ('model', LinearRegression())
        ]),
        "Random Forest": Pipeline([
            ('scaler', StandardScaler()),
            ('model', RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            ))
        ]),
        "Gradient Boosting": Pipeline([
            ('scaler', StandardScaler()),
            ('model', GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            ))
        ])
    }

    results = {}
    best_model = None
    best_r2 = -999

    print("\n=== Model Comparison ===")
    print(f"{'Model':<25} {'MAE':>8} {'RMSE':>8} {'R2':>8}")
    print("-" * 55)

    for name, pipeline in models.items():
        # Train
        pipeline.fit(X_train, y_train)

        # Predict
        y_pred = pipeline.predict(X_test)

        # Evaluate
        mae  = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2   = r2_score(y_test, y_pred)

        results[name] = {"mae": mae, "rmse": rmse, "r2": r2}
        print(f"{name:<25} {mae:>8.2f} {rmse:>8.2f} {r2:>8.3f}")

        # Track best model
        if r2 > best_r2:
            best_r2 = r2
            best_model = pipeline
            best_model_name = name

    print(f"\n✅ Best Model: {best_model_name} (R2 = {best_r2:.3f})")
    return best_model, best_model_name, results, X_test, y_test


# =============================================================
# Step 4 — Save Model
# =============================================================

def save_model(model, feature_cols, filepath="model/fuel_model.pkl"):
    os.makedirs("model", exist_ok=True)

    # Save model and feature columns together
    model_data = {
        "model": model,
        "feature_cols": feature_cols
    }

    with open(filepath, 'wb') as f:
        pickle.dump(model_data, f)

    print(f"\n✅ Model saved to: {filepath}")


# =============================================================
# Step 5 — Test Prediction
# =============================================================

def test_prediction(model, feature_cols):
    print("\n=== Testing Prediction ===")

    # Sample car: Toyota Corolla-like specs
    sample = pd.DataFrame([{
        'cylinders':    4,
        'displacement': 120.0,
        'horsepower':   88.0,
        'weight':       2500.0,
        'acceleration': 15.0,
        'model_year':   82,
        'origin':       3        # Asian car
    }])

    predicted_mpg = model.predict(sample[feature_cols])[0]
    kmpl = predicted_mpg * 0.425144  # Convert MPG to KM/L

    print(f"Sample Car Specs: 4 cylinders, 120cc, 88hp, 2500kg")
    print(f"Predicted Fuel Efficiency: {predicted_mpg:.1f} MPG")
    print(f"Converted to KM/L:         {kmpl:.1f} km/l")


# =============================================================
# Main
# =============================================================

if __name__ == "__main__":
    # Load data
    df = load_and_clean_data("dataset/auto-mpg.csv")

    # Prepare features
    X, y, feature_cols = prepare_features(df)

    # Train models
    best_model, best_name, results, X_test, y_test = train_and_evaluate(X, y)

    # Save best model
    save_model(best_model, feature_cols)

    # Test it
    test_prediction(best_model, feature_cols)

    print("\n🎉 Training complete! Run app.py to start the API.")
