from fastapi import APIRouter, Depends, status, HTTPException, Response
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
from sqlalchemy.orm import Session
from datetime import date

from ..dependencies import get_db
from .users import UserResponse
from ..models.daily_metrics import DailyMetrics
from ..models.user import User
from ..oauth2 import get_current_user
from ..utils import check_user



router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
)

class SleepingQuality(str, Enum):
    excellent = "excellent"
    good = "good"
    sufficient = "sufficient"
    bad = "bad"
    terrible = "terrible"

class MetricsModel(BaseModel):
    body_weight: Optional[float] = Field(default=None, alias="bodyWeight")
    calories: Optional[int] = Field(default=None)
    hydration: Optional[float] = Field(default=None)
    steps: Optional[int] = Field(default=None)
    sleeping_hours: Optional[float] = Field(default=None, alias="sleepingHours")
    sleeping_quality: Optional[SleepingQuality] = Field(default=None, alias="sleepingQuality")

    class Config:
        allow_population_by_field_name = True

    @validator("*", pre=True, always=True)
    def check_at_least_one_field(self, v, values, **kwargs):
        if all(field is None for field in values.values()):
            raise ValueError("At least one value must be not None")

        return v

    @validator("body_weight", "calories", "hydration", "steps", "sleeping_hours")
    def check_non_negative(self, v):
        if v < 0:
            raise ValueError(f"{v} is not a valid value, it must be >= 0")

        return v

class MetricsResponse(BaseModel):
    id: int
    user_id: int
    register_dt: date = Field(alias="registerDt")
    body_weight: float = Field(alias="bodyWeight")
    calories: int
    hydration: float
    steps: int
    sleeping_hours: float = Field(alias="sleepingHours")
    sleeping_quality: SleepingQuality = Field(alias="sleepingQuality")
    user: UserResponse

    class Config:
        from_orm = True


@router.get("/{user_id}", response_model=List[MetricsResponse])
def get_user_metrics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # Query parameters
    start_dt: date = None,
    end_dt: date = None,
    min_body_weight: float = None,
    max_body_weight: float = None,
    min_calories: int = None,
    max_calories: int = None,
    min_hydration: float = None,
    max_hydration: float = None,
    min_steps: int = None,
    max_steps: int = None,
    min_sleeping_hours: float = None,
    max_sleeping_hours: float = None,
    sleeping_quality: SleepingQuality = None,
) -> DailyMetrics:
    check_user(user_id, current_user)

    metrics_query = db.query(DailyMetrics).filter(DailyMetrics.user_id == user_id)

    if start_dt is not None:
        metrics_query = metrics_query.filter(DailyMetrics.register_dt >= start_dt)
    if end_dt is not None:
        metrics_query = metrics_query.filter(DailyMetrics.register_dt <= end_dt)
    if min_body_weight is not None:
        metrics_query = metrics_query.filter(DailyMetrics.body_weight >= min_body_weight)
    if max_body_weight is not None:
        metrics_query = metrics_query.filter(DailyMetrics.body_weight <= max_body_weight)
    if min_calories is not None:
        metrics_query = metrics_query.filter(DailyMetrics.calories >= min_calories)
    if max_calories is not None:
        metrics_query = metrics_query.filter(DailyMetrics.calories <= max_calories)
    if min_hydration is not None:
        metrics_query = metrics_query.filter(DailyMetrics.hydration >= min_hydration)
    if max_hydration is not None:
        metrics_query = metrics_query.filter(DailyMetrics.hydration <= max_hydration)
    if min_steps is not None:
        metrics_query = metrics_query.filter(DailyMetrics.steps >= min_steps)
    if max_steps is not None:
        metrics_query = metrics_query.filter(DailyMetrics.steps <= max_steps)
    if min_sleeping_hours is not None:
        metrics_query = metrics_query.filter(DailyMetrics.sleeping_hours >= min_sleeping_hours)
    if max_sleeping_hours is not None:
        metrics_query = metrics_query.filter(DailyMetrics.sleeping_hours <= max_sleeping_hours)
    if sleeping_quality is not None:
        metrics_query = metrics_query.filter(DailyMetrics.sleeping_quality == sleeping_quality)

    daily_metrics = metrics_query.all()

    return daily_metrics

@router.post("/{user_id}", status_code=status.HTTP_201_CREATED, response_model=MetricsResponse)
def create_user_metrics(
    user_id: int,
    metrics: MetricsModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DailyMetrics:
    check_user(user_id, current_user)

    new_metrics = DailyMetrics(
        user_id=user_id,
        **metrics.model_dump(),
    )

    db.add(new_metrics)
    db.commit()
    db.refresh(new_metrics)

    return new_metrics

@router.delete("/{metrics_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_metrics(
    metrics_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    metrics = db.query(DailyMetrics).filter(DailyMetrics.id == metrics_id).first()

    if metrics is not None:
        check_user(metrics.user_id, current_user)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")

    db.delete(metrics)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{metrics_id}", response_model=MetricsResponse)
def update_user_metrics(
    metrics_id: int,
    metrics_data: MetricsModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DailyMetrics:
    metrics_query = db.query(DailyMetrics).filter(DailyMetrics.id == metrics_id)
    metrics = metrics_query.first()

    if metrics is not None:
        check_user(metrics.user_id, current_user)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")

    metrics_query.update(metrics_data.model_dump(), synchronize_session="fetch")
    db.commit()

    return metrics_query.first()
