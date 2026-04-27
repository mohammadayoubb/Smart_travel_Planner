from pathlib import Path

import joblib


MODEL_PATH = Path("data/best_model.joblib")


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

    return joblib.load(MODEL_PATH)


def predict_travel_style(features: dict) -> str:
    model = load_model()
    prediction = model.predict([features])
    return str(prediction[0])