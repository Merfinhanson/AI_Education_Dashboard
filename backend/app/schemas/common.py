from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


PayloadT = TypeVar("PayloadT")


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ApiEnvelope(BaseModel, Generic[PayloadT]):
    message: str
    data: PayloadT
