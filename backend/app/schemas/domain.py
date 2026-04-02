from pydantic import BaseModel, Field


class OCRDocument(BaseModel):
    text: str
    provider: str
    confidence: float = 0.0
    page_count: int = 1


class QuestionBlueprint(BaseModel):
    question_number: str
    prompt: str
    marks: float
    section: str | None = None
    expected_points: list[str] = Field(default_factory=list)


class AnswerSegment(BaseModel):
    text: str
    detected_question_number: str | None = None
    start_index: int = 0


class MappedAnswer(BaseModel):
    question_number: str
    answer_text: str
    confidence: float
    mapping_reason: str


class AnswerMappingBundle(BaseModel):
    mapped_answers: list[MappedAnswer] = Field(default_factory=list)
    detected_order: list[str] = Field(default_factory=list)
