from datetime import datetime

from pydantic import BaseModel, Field


class QuestionEvaluationResponse(BaseModel):
    question_number: str
    question_text: str
    answer_excerpt: str
    awarded_marks: float
    max_marks: float
    mapped_confidence: float
    evaluation_confidence: float
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_key_points: list[str] = Field(default_factory=list)
    ideal_answer_outline: list[str] = Field(default_factory=list)
    justification: str


class EvaluationSummaryResponse(BaseModel):
    total_marks_obtained: float
    total_marks_possible: float
    percentage: float
    grade: str
    summary: str
    suggestions: list[str] = Field(default_factory=list)


class PlagiarismMatchResponse(BaseModel):
    matched_submission_id: str
    matched_student_name: str
    text_similarity: float
    structural_similarity: float
    image_similarity: float
    overall_similarity: float
    upload_timestamp: datetime
    copied_sections: list[str] = Field(default_factory=list)


class PlagiarismReportResponse(BaseModel):
    is_flagged: bool = False
    matches: list[PlagiarismMatchResponse] = Field(default_factory=list)


class EvaluationReportResponse(BaseModel):
    submission_id: str
    student_name: str
    student_id: str | None = None
    status: str
    created_at: datetime
    question_results: list[QuestionEvaluationResponse] = Field(default_factory=list)
    summary: EvaluationSummaryResponse
    plagiarism_report: PlagiarismReportResponse


class SubmissionListItem(BaseModel):
    submission_id: str
    student_name: str
    student_id: str | None = None
    status: str
    total_score: float | None = None
    total_marks: float | None = None
    grade: str | None = None
    created_at: datetime
