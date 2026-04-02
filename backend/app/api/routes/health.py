from fastapi import APIRouter

from app.schemas.common import ApiEnvelope, HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiEnvelope[HealthResponse])
def health_check() -> ApiEnvelope[HealthResponse]:
    return ApiEnvelope(message="Service is healthy.", data=HealthResponse())
