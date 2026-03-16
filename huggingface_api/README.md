---
title: Fix My Ride - Fuel Efficiency Estimator
emoji: 🚗
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Fix My Ride — Fuel Efficiency Estimator API

A machine learning API that predicts vehicle fuel efficiency based on car specifications.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and example request |
| GET | `/health` | Health check |
| POST | `/predict/fuel` | Predict fuel efficiency |
| POST | `/predict/fuel/compare` | Compare two cars |

## Usage

### Predict Fuel Efficiency

```bash
curl -X POST https://YOUR-SPACE-URL/predict/fuel \
  -H "Content-Type: application/json" \
  -d '{
    "cylinders": 4,
    "displacement": 1300,
    "horsepower": 88,
    "weight": 1200,
    "acceleration": 15.0,
    "model_year": 98,
    "origin": 3,
    "daily_km": 50,
    "fuel_price": 280
}'
```

### Response

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
    "tips": ["..."],
    "monthly_cost_estimate": {
      "daily_km": 50,
      "monthly_cost_pkr": 30436
    }
  }
}
```

### Compare Two Cars

```bash
curl -X POST https://YOUR-SPACE-URL/predict/fuel/compare \
  -H "Content-Type: application/json" \
  -d '{
    "car1": {
      "cylinders": 4, "displacement": 1300, "horsepower": 88,
      "weight": 1200, "acceleration": 15.0, "model_year": 98, "origin": 3
    },
    "car2": {
      "cylinders": 8, "displacement": 5000, "horsepower": 200,
      "weight": 2500, "acceleration": 10.0, "model_year": 82, "origin": 1
    }
}'
```

## Origin Values

| Value | Meaning |
|-------|---------|
| 1 | American car (Ford, Chevrolet) |
| 2 | European car (BMW, VW) |
| 3 | Asian car (Toyota, Honda, Suzuki) |

## Model Year

Use last 2 digits: 1998 → 98, 2005 → 05, 2015 → 15
