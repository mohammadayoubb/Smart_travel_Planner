import pytest
from pydantic import ValidationError

from app.schemas.agent import AgentQuestionRequest
from app.schemas.ml import TravelStyleFeatures


def test_agent_question_valid():
    request = AgentQuestionRequest(
        question="I want a cheap destination with food and culture"
    )

    assert request.question.startswith("I want")


def test_agent_question_too_short():
    with pytest.raises(ValidationError):
        AgentQuestionRequest(question="Hi")


def test_ml_features_valid():
    features = TravelStyleFeatures(
        avg_daily_budget_usd=80,
        warm_weather_score=8,
        tourist_crowd_score=4,
        hiking_score=7,
        beach_score=3,
        museum_score=9,
        nightlife_score=4,
        family_score=5,
        luxury_score=2,
        safety_score=8,
        description="Budget cultural city with food and museums",
    )

    assert features.avg_daily_budget_usd == 80


def test_ml_features_invalid_score():
    with pytest.raises(ValidationError):
        TravelStyleFeatures(
            avg_daily_budget_usd=80,
            warm_weather_score=15,
            tourist_crowd_score=4,
            hiking_score=7,
            beach_score=3,
            museum_score=9,
            nightlife_score=4,
            family_score=5,
            luxury_score=2,
            safety_score=8,
            description="Invalid score test",
        )