from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from app.schemas.ml import TravelStyleFeatures


MODEL_PATH = Path("data/best_model.joblib")


@lru_cache
def load_travel_style_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

    return joblib.load(MODEL_PATH)


def predict_travel_style(features: TravelStyleFeatures) -> str:
    model = load_travel_style_model()

    input_df = pd.DataFrame([features.model_dump()])

    prediction = model.predict(input_df)

    return str(prediction[0])
