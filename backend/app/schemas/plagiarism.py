from pydantic import BaseModel, Field


class PlagiarismCheckResponse(BaseModel):
    submission_id: str
    is_flagged: bool
    matches: list[dict] = Field(default_factory=list)
