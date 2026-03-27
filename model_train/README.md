# Fix My Ride — Fuel Efficiency Estimator

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Dataset
- Go to: https://www.kaggle.com/datasets/uciml/autompg-dataset
- Download `auto-mpg.csv`
- Place it in the `dataset/` folder

### 3. Train the model
```bash
python train_model.py
```
Expected output:
```
Model         MAE     RMSE      R2
Linear Reg   2.50     3.20   0.820
Random Forest 1.80    2.60   0.890
Gradient Boost 1.70   2.40   0.905  ← best

Best model saved to: model/fuel_model.pkl
```

### 4. Start the API
```bash
python app.py
```

---

## API Usage

### Predict Fuel Efficiency
```bash
POST http://localhost:5001/predict/fuel
```

**Request:**
```json
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
```

**Response:**
```json
{
    "success": true,
    "data": {
        "prediction": {
            "mpg": 32.5,
            "kmpl": 13.8,
            "liters_per_100km": 7.2
        },
        "rating": {
            "rating": "Good",
            "emoji": "🟢",
            "description": "Good fuel efficiency"
        },
        "tips": [
            "Maintain correct tyre pressure...",
            "Avoid sudden acceleration..."
        ],
        "monthly_cost_estimate": {
            "daily_km": 50,
            "daily_liters": 3.62,
            "monthly_liters": 108.7,
            "monthly_cost_pkr": 30436,
            "fuel_price_per_liter": 280
        }
    }
}
```

---

## Origin Values
| Value | Meaning |
|-------|---------|
| 1 | American car (Ford, Chevrolet) |
| 2 | European car (BMW, VW) |
| 3 | Asian car (Toyota, Honda, Suzuki) |

## Model Year
Use last 2 digits only:
- 1998 → 98
- 2005 → 05
- 2015 → 15

 
