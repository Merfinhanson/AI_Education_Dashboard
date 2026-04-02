from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.models import EvaluationResult, Submission
from app.db.session import get_session
from app.schemas.common import ApiEnvelope
from app.schemas.evaluation import PlagiarismReportResponse
from app.services.plagiarism_service import PlagiarismService


router = APIRouter(prefix="/plagiarism", tags=["plagiarism"])
service = PlagiarismService()


@router.post("/submissions/{submission_id}", response_model=ApiEnvelope[PlagiarismReportResponse])
def run_plagiarism_check(
    submission_id: str,
    session: Session = Depends(get_session),
) -> ApiEnvelope[PlagiarismReportResponse]:
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    current_results = session.exec(
        select(EvaluationResult).where(EvaluationResult.submission_id == submission.id)
    ).all()
    report = service.check_submission(session, submission, current_results)
    submission.plagiarism_flag = report.is_flagged
    session.add(submission)
    session.commit()
    return ApiEnvelope(message="Plagiarism check completed.", data=report)
