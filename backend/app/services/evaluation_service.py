from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.core.config import get_settings
from app.db.models import EvaluationResult, QuestionPaper, Submission
from app.pipelines.answer_mapper import AnswerMapper
from app.pipelines.evaluation_engine import RuleBasedEvaluationEngine
from app.pipelines.ocr import OCRPipeline
from app.pipelines.question_parser import QuestionPaperParser
from app.schemas.evaluation import (
    EvaluationReportResponse,
    EvaluationSummaryResponse,
    QuestionEvaluationResponse,
)
from app.services.plagiarism_service import PlagiarismService
from app.services.storage_service import LocalStorageService
from app.utils.text import dump_json, load_json_list


class EvaluationService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.storage = LocalStorageService()
        self.ocr = OCRPipeline()
        self.parser = QuestionPaperParser()
        self.mapper = AnswerMapper()
        self.evaluator = RuleBasedEvaluationEngine()
        self.plagiarism_service = PlagiarismService()

    async def run_evaluation(
        self,
        session: Session,
        student_name: str,
        student_id: str | None,
        question_paper_title: str | None,
        question_paper_file: UploadFile,
        answer_sheet_file: UploadFile,
        marking_scheme_file: UploadFile | None = None,
    ) -> EvaluationReportResponse:
        question_paper_path = await self.storage.save_upload(question_paper_file, "question-papers")
        answer_sheet_path = await self.storage.save_upload(answer_sheet_file, "answer-sheets")
        marking_scheme_path = (
            await self.storage.save_upload(marking_scheme_file, "marking-schemes")
            if marking_scheme_file
            else None
        )

        try:
            question_paper_doc = self.ocr.extract_text(question_paper_path)
            answer_sheet_doc = self.ocr.extract_text(answer_sheet_path)
            marking_scheme_text = (
                self.ocr.extract_text(marking_scheme_path).text if marking_scheme_path else None
            )
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        questions = self.parser.parse(question_paper_doc.text, marking_scheme_text)
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No questions could be parsed from the uploaded question paper.",
            )

        question_paper = QuestionPaper(
            title=question_paper_title or question_paper_file.filename or "Untitled Question Paper",
            question_paper_path=question_paper_path,
            raw_text=question_paper_doc.text,
            structure_json=dump_json([question.model_dump() for question in questions]),
            marking_scheme_text=marking_scheme_text,
        )
        session.add(question_paper)
        session.commit()
        session.refresh(question_paper)

        mapping_bundle = self.mapper.map_answers(questions, answer_sheet_doc.text)
        mapped_lookup = {answer.question_number: answer for answer in mapping_bundle.mapped_answers}

        question_responses: list[QuestionEvaluationResponse] = []
        db_results: list[EvaluationResult] = []
        for question in questions:
            result = self.evaluator.evaluate(
                question=question,
                mapped_answer=mapped_lookup[question.question_number],
                similarity_threshold=self.settings.evaluation_similarity_threshold,
            )
            question_responses.append(result)
            db_results.append(
                EvaluationResult(
                    submission_id="pending",
                    question_number=result.question_number,
                    question_text=result.question_text,
                    answer_text=mapped_lookup[result.question_number].answer_text,
                    awarded_marks=result.awarded_marks,
                    max_marks=result.max_marks,
                    mapped_confidence=result.mapped_confidence,
                    evaluation_confidence=result.evaluation_confidence,
                    strengths_json=dump_json(result.strengths),
                    weaknesses_json=dump_json(result.weaknesses),
                    missing_points_json=dump_json(result.missing_key_points),
                    ideal_outline_json=dump_json(result.ideal_answer_outline),
                    justification=result.justification,
                )
            )

        summary = self._build_summary(question_responses)
        submission = Submission(
            student_name=student_name,
            student_id=student_id,
            question_paper_id=question_paper.id,
            question_paper_path=question_paper_path,
            answer_sheet_path=answer_sheet_path,
            answer_sheet_text=answer_sheet_doc.text,
            answer_order_json=dump_json(mapping_bundle.detected_order),
            status="processed",
            total_score=summary.total_marks_obtained,
            total_marks=summary.total_marks_possible,
            grade=summary.grade,
            feedback_summary=summary.summary,
            plagiarism_flag=False,
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)

        for db_result in db_results:
            db_result.submission_id = submission.id
            session.add(db_result)
        session.commit()

        current_results = session.exec(
            select(EvaluationResult).where(EvaluationResult.submission_id == submission.id)
        ).all()
        plagiarism_report = self.plagiarism_service.check_submission(session, submission, current_results)

        submission.plagiarism_flag = plagiarism_report.is_flagged
        session.add(submission)
        session.commit()
        session.refresh(submission)

        return EvaluationReportResponse(
            submission_id=submission.id,
            student_name=submission.student_name,
            student_id=submission.student_id,
            status=submission.status,
            created_at=submission.created_at,
            question_results=question_responses,
            summary=summary,
            plagiarism_report=plagiarism_report,
        )

    def get_submission_report(self, session: Session, submission_id: str) -> EvaluationReportResponse:
        submission = session.get(Submission, submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found.")

        results = session.exec(
            select(EvaluationResult).where(EvaluationResult.submission_id == submission.id)
        ).all()
        question_results = [
            QuestionEvaluationResponse(
                question_number=result.question_number,
                question_text=result.question_text,
                answer_excerpt=result.answer_text[:280] if result.answer_text else "No answer detected.",
                awarded_marks=result.awarded_marks,
                max_marks=result.max_marks,
                mapped_confidence=result.mapped_confidence,
                evaluation_confidence=result.evaluation_confidence,
                strengths=load_json_list(result.strengths_json),
                weaknesses=load_json_list(result.weaknesses_json),
                missing_key_points=load_json_list(result.missing_points_json),
                ideal_answer_outline=load_json_list(result.ideal_outline_json),
                justification=result.justification,
            )
            for result in results
        ]

        plagiarism_report = self.plagiarism_service.get_report(session, submission.id)
        summary = self._build_summary(question_results, submission.feedback_summary, submission.grade)
        return EvaluationReportResponse(
            submission_id=submission.id,
            student_name=submission.student_name,
            student_id=submission.student_id,
            status=submission.status,
            created_at=submission.created_at,
            question_results=question_results,
            summary=summary,
            plagiarism_report=plagiarism_report,
        )

    def _build_summary(
        self,
        question_results: list[QuestionEvaluationResponse],
        existing_summary: str | None = None,
        existing_grade: str | None = None,
    ) -> EvaluationSummaryResponse:
        total_possible = round(sum(result.max_marks for result in question_results), 2)
        total_obtained = round(sum(result.awarded_marks for result in question_results), 2)
        percentage = round((total_obtained / total_possible) * 100, 2) if total_possible else 0.0
        grade = existing_grade or self._grade_for_percentage(percentage)

        common_missing_points: list[str] = []
        for result in question_results:
            common_missing_points.extend(result.missing_key_points[:1])
        suggestions = [point for point in common_missing_points[:4] if point]

        summary = existing_summary or (
            f"The student scored {total_obtained} out of {total_possible}. "
            f"Performance is strongest where rubric coverage is high and weaker where key points are missing."
        )
        return EvaluationSummaryResponse(
            total_marks_obtained=total_obtained,
            total_marks_possible=total_possible,
            percentage=percentage,
            grade=grade,
            summary=summary,
            suggestions=suggestions,
        )

    @staticmethod
    def _grade_for_percentage(percentage: float) -> str:
        if percentage >= 90:
            return "A+"
        if percentage >= 80:
            return "A"
        if percentage >= 70:
            return "B"
        if percentage >= 60:
            return "C"
        if percentage >= 50:
            return "D"
        return "F"
