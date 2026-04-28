from fastapi import APIRouter

from app.schemas.ml import TravelStyleFeatures, TravelStylePredictionResponse
from app.services.ml_service import predict_travel_style

router = APIRouter(
    prefix="/ml",
    tags=["ML Classifier"],
)


@router.post("/predict-style", response_model=TravelStylePredictionResponse)
async def predict_style(
    features: TravelStyleFeatures,
):
    travel_style = predict_travel_style(features)

    return TravelStylePredictionResponse(
        travel_style=travel_style,
    )