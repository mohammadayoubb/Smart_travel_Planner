from pydantic import BaseModel, Field


class TravelStyleFeatures(BaseModel):
    avg_daily_budget_usd: float = Field(gt=0)
    warm_weather_score: float = Field(ge=1, le=10)
    tourist_crowd_score: float = Field(ge=1, le=10)
    hiking_score: float = Field(ge=1, le=10)
    beach_score: float = Field(ge=1, le=10)
    museum_score: float = Field(ge=1, le=10)
    nightlife_score: float = Field(ge=1, le=10)
    family_score: float = Field(ge=1, le=10)
    luxury_score: float = Field(ge=1, le=10)
    safety_score: float = Field(ge=1, le=10)
    description: str = Field(min_length=5)


class TravelStylePredictionResponse(BaseModel):
    travel_style: str