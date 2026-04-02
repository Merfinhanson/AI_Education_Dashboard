from sqlmodel import Session, select

from app.core.config import get_settings
from app.db.models import EvaluationResult, PlagiarismIncident, Submission
from app.pipelines.plagiarism_engine import PlagiarismDetector
from app.schemas.evaluation import PlagiarismMatchResponse, PlagiarismReportResponse
from app.utils.text import dump_json, load_json_list


class PlagiarismService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.detector = PlagiarismDetector()

    def check_submission(
        self,
        session: Session,
        submission: Submission,
        current_results: list[EvaluationResult],
    ) -> PlagiarismReportResponse:
        existing_incidents = session.exec(
            select(PlagiarismIncident).where(PlagiarismIncident.source_submission_id == submission.id)
        ).all()
        for incident in existing_incidents:
            session.delete(incident)
        session.commit()

        historic_submissions = session.exec(
            select(Submission).where(
                Submission.question_paper_id == submission.question_paper_id,
                Submission.id != submission.id,
            )
        ).all()

        historic_payload: list[dict] = []
        for candidate in historic_submissions:
            candidate_results = session.exec(
                select(EvaluationResult).where(EvaluationResult.submission_id == candidate.id)
            ).all()
            historic_payload.append(
                {
                    "submission_id": candidate.id,
                    "student_name": candidate.student_name,
                    "answer_sheet_path": candidate.answer_sheet_path,
                    "answer_sheet_text": candidate.answer_sheet_text,
                    "answer_order": load_json_list(candidate.answer_order_json),
                    "question_answers": {
                        result.question_number: result.answer_text for result in candidate_results
                    },
                    "created_at": candidate.created_at,
                }
            )

        matches = self.detector.compare_submission(
            current={
                "submission_id": submission.id,
                "student_name": submission.student_name,
                "answer_sheet_path": submission.answer_sheet_path,
                "answer_sheet_text": submission.answer_sheet_text,
                "answer_order": load_json_list(submission.answer_order_json),
                "question_answers": {
                    result.question_number: result.answer_text for result in current_results
                },
                "created_at": submission.created_at,
            },
            historic_submissions=historic_payload,
            text_threshold=self.settings.plagiarism_text_threshold,
            structural_threshold=self.settings.plagiarism_structural_threshold,
        )

        persisted_matches: list[PlagiarismMatchResponse] = []
        for match in matches:
            session.add(
                PlagiarismIncident(
                    source_submission_id=submission.id,
                    matched_submission_id=match["matched_submission_id"],
                    text_similarity=match["text_similarity"],
                    structural_similarity=match["structural_similarity"],
                    image_similarity=match["image_similarity"],
                    overall_similarity=match["overall_similarity"],
                    copied_sections_json=dump_json(match["copied_sections"]),
                )
            )
            persisted_matches.append(PlagiarismMatchResponse(**match))

        session.commit()
        return PlagiarismReportResponse(
            is_flagged=bool(persisted_matches),
            matches=persisted_matches,
        )

    def get_report(self, session: Session, submission_id: str) -> PlagiarismReportResponse:
        incidents = session.exec(
            select(PlagiarismIncident).where(PlagiarismIncident.source_submission_id == submission_id)
        ).all()
        if not incidents:
            return PlagiarismReportResponse(is_flagged=False, matches=[])

        matches: list[PlagiarismMatchResponse] = []
        for incident in incidents:
            matched_submission = session.get(Submission, incident.matched_submission_id)
            if not matched_submission:
                continue
            matches.append(
                PlagiarismMatchResponse(
                    matched_submission_id=incident.matched_submission_id,
                    matched_student_name=matched_submission.student_name,
                    text_similarity=incident.text_similarity,
                    structural_similarity=incident.structural_similarity,
                    image_similarity=incident.image_similarity,
                    overall_similarity=incident.overall_similarity,
                    upload_timestamp=matched_submission.created_at,
                    copied_sections=load_json_list(incident.copied_sections_json),
                )
            )

        return PlagiarismReportResponse(is_flagged=bool(matches), matches=matches)
