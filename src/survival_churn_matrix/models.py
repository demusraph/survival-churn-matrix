from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import numpy as np

class Event(BaseModel):
    customer_id: str
    time: float = Field(..., gt=0)
    event_observed: bool  # True if churned, False if censored

class CohortRequest(BaseModel):
    cohort_id: str
    events: List[Event]

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: List[Event]) -> List[Event]:
        if not v:
            raise ValueError("Cohort must contain at least one event.")
        return v

class SurvivalPoint(BaseModel):
    time: float
    survival_probability: float
    confidence_interval_lower: float
    confidence_interval_upper: float

class SurvivalAnalysisResult(BaseModel):
    cohort_id: str
    median_survival_time: Optional[float]
    curve: List[SurvivalPoint]