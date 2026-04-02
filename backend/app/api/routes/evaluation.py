from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.common import ApiEnvelope
from app.schemas.evaluation import EvaluationReportResponse
from app.services.evaluation_service import EvaluationService


router = APIRouter(prefix="/evaluations", tags=["evaluations"])
service = EvaluationService()


@router.post("/run", response_model=ApiEnvelope[EvaluationReportResponse])
async def run_evaluation(
    student_name: str = Form(...),
    student_id: str | None = Form(None),
    question_paper_title: str | None = Form(None),
    question_paper: UploadFile = File(...),
    answer_sheet: UploadFile = File(...),
    marking_scheme: UploadFile | None = File(None),
    session: Session = Depends(get_session),
) -> ApiEnvelope[EvaluationReportResponse]:
    report = await service.run_evaluation(
        session=session,
        student_name=student_name,
        student_id=student_id,
        question_paper_title=question_paper_title,
        question_paper_file=question_paper,
        answer_sheet_file=answer_sheet,
        marking_scheme_file=marking_scheme,
    )
    return ApiEnvelope(message="Evaluation completed.", data=report)


@router.get("/submissions/{submission_id}", response_model=ApiEnvelope[EvaluationReportResponse])
def get_evaluation_report(
    submission_id: str,
    session: Session = Depends(get_session),
) -> ApiEnvelope[EvaluationReportResponse]:
    report = service.get_submission_report(session, submission_id)
    return ApiEnvelope(message="Submission report loaded.", data=report)
