from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel


def _uuid() -> str:
    return str(uuid4())


class QuestionPaper(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    title: str
    question_paper_path: str | None = None
    raw_text: str
    structure_json: str = "[]"
    marking_scheme_text: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Submission(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    student_name: str
    student_id: str | None = None
    question_paper_id: str = Field(foreign_key="questionpaper.id")
    question_paper_path: str
    answer_sheet_path: str
    answer_sheet_text: str
    answer_order_json: str = "[]"
    status: str = "processed"
    total_score: float | None = None
    total_marks: float | None = None
    grade: str | None = None
    feedback_summary: str | None = None
    plagiarism_flag: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EvaluationResult(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    submission_id: str = Field(foreign_key="submission.id", index=True)
    question_number: str
    question_text: str
    answer_text: str
    awarded_marks: float
    max_marks: float
    mapped_confidence: float
    evaluation_confidence: float
    strengths_json: str = "[]"
    weaknesses_json: str = "[]"
    missing_points_json: str = "[]"
    ideal_outline_json: str = "[]"
    justification: str


class PlagiarismIncident(SQLModel, table=True):
    id: str = Field(default_factory=_uuid, primary_key=True)
    source_submission_id: str = Field(foreign_key="submission.id", index=True)
    matched_submission_id: str = Field(foreign_key="submission.id", index=True)
    text_similarity: float
    structural_similarity: float
    image_similarity: float
    overall_similarity: float
    copied_sections_json: str = "[]"
    created_at: datetime = Field(default_factory=datetime.utcnow)
