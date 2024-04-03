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
            raise ValueError("Almeno un campo deve essere valido e non None")

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
):
    pass

@router.post("/{user_id}", status_code=status.HTTP_201_CREATED, response_model=MetricsResponse)
def create_user_metrics(
    user_id: int,
    metrics: MetricsModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
):
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
):
    metrics_query = db.query(DailyMetrics).filter(DailyMetrics.id == metrics_id)
    metrics = metrics_query.first()

    if metrics is not None:
        check_user(metrics.user_id, current_user)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")

    metrics_query.update(metrics_data.model_dump(), synchronize_session="fetch")
    db.commit()

    return metrics_query.first()
