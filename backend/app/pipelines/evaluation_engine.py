from app.schemas.domain import MappedAnswer, QuestionBlueprint
from app.schemas.evaluation import QuestionEvaluationResponse
from app.utils.text import coverage_against_points, cosine_overlap, keyword_candidates, tokenize


def round_score(value: float, max_marks: float) -> float:
    if max_marks <= 2:
        increment = 0.25
    elif max_marks <= 5:
        increment = 0.5
    else:
        increment = 1.0
    return round(round(value / increment) * increment, 2)


class RuleBasedEvaluationEngine:
    def evaluate(
        self,
        question: QuestionBlueprint,
        mapped_answer: MappedAnswer,
        similarity_threshold: float,
    ) -> QuestionEvaluationResponse:
        expected_points = question.expected_points or keyword_candidates(
            question.prompt,
            limit=max(3, int(round(question.marks)) + 2),
        )
        answer_text = mapped_answer.answer_text.strip()

        if not answer_text:
            return QuestionEvaluationResponse(
                question_number=question.question_number,
                question_text=question.prompt,
                answer_excerpt="No answer detected.",
                awarded_marks=0.0,
                max_marks=question.marks,
                mapped_confidence=mapped_answer.confidence,
                evaluation_confidence=0.3,
                strengths=[],
                weaknesses=["No answer content was found for this question."],
                missing_key_points=expected_points,
                ideal_answer_outline=expected_points,
                justification="Zero marks awarded because the answer could not be detected or mapped.",
            )

        coverage = coverage_against_points(answer_text, expected_points)
        covered_points = [point for point, score in coverage if score >= similarity_threshold]
        missing_points = [point for point, score in coverage if score < similarity_threshold]
        completeness = len(covered_points) / max(len(expected_points), 1)
        semantic_alignment = cosine_overlap(answer_text, " ".join(expected_points))
        depth = min(1.0, len(tokenize(answer_text)) / max(int(question.marks * 14), 16))
        score_ratio = min(1.0, (0.55 * completeness) + (0.25 * semantic_alignment) + (0.20 * depth))
        raw_score = question.marks * score_ratio
        awarded_marks = min(question.marks, round_score(raw_score, question.marks))

        strengths: list[str] = []
        weaknesses: list[str] = []

        if covered_points:
            strengths.append(f"Covered {len(covered_points)} of {len(expected_points)} expected rubric points.")
        if semantic_alignment >= 0.45:
            strengths.append("The answer stays reasonably aligned with the expected concepts.")
        if depth >= 0.7:
            strengths.append("The answer includes sufficient detail for the allocated marks.")

        if missing_points:
            weaknesses.append("Some important rubric points are missing or only weakly addressed.")
        if depth < 0.45:
            weaknesses.append("The answer lacks depth relative to the mark allocation.")
        if semantic_alignment < 0.35:
            weaknesses.append("Concept alignment is weak and needs a clearer explanation.")

        evaluation_confidence = round(
            min(0.98, 0.45 + (0.25 * completeness) + (0.20 * semantic_alignment) + (0.10 * mapped_answer.confidence)),
            2,
        )

        justification = (
            f"Marks were assigned from rubric coverage ({completeness:.0%}), "
            f"concept alignment ({semantic_alignment:.0%}), and answer depth ({depth:.0%})."
        )

        return QuestionEvaluationResponse(
            question_number=question.question_number,
            question_text=question.prompt,
            answer_excerpt=answer_text[:280],
            awarded_marks=awarded_marks,
            max_marks=question.marks,
            mapped_confidence=mapped_answer.confidence,
            evaluation_confidence=evaluation_confidence,
            strengths=strengths,
            weaknesses=weaknesses,
            missing_key_points=missing_points,
            ideal_answer_outline=expected_points,
            justification=justification,
        )
