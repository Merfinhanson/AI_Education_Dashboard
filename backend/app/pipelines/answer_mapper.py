import re

from app.schemas.domain import AnswerMappingBundle, AnswerSegment, MappedAnswer, QuestionBlueprint
from app.utils.text import cosine_overlap, normalize_identifier, normalize_whitespace


ANSWER_START_RE = re.compile(
    r"^\s*(?:Ans(?:wer)?\s*)?(?:Q(?:uestion)?\s*)?(\d+[A-Za-z]?)\s*[\).:-]\s*(.*)$",
    re.IGNORECASE,
)


class AnswerMapper:
    def split_answers(self, answer_text: str) -> list[AnswerSegment]:
        segments: list[AnswerSegment] = []
        current_number: str | None = None
        current_lines: list[str] = []
        start_index = 0
        line_index = 0

        def flush_segment() -> None:
            nonlocal current_lines, current_number, start_index
            joined = normalize_whitespace(" ".join(current_lines))
            if joined:
                segments.append(
                    AnswerSegment(
                        text=joined,
                        detected_question_number=normalize_identifier(current_number),
                        start_index=start_index,
                    )
                )
            current_lines = []
            current_number = None

        for raw_line in answer_text.splitlines():
            line = raw_line.strip()
            match = ANSWER_START_RE.match(line)
            if match:
                flush_segment()
                current_number = match.group(1)
                current_lines = [match.group(2)]
                start_index = line_index
            else:
                current_lines.append(line)
            line_index += 1

        flush_segment()
        if not segments and normalize_whitespace(answer_text):
            segments.append(AnswerSegment(text=normalize_whitespace(answer_text), start_index=0))
        return segments

    def map_answers(
        self,
        questions: list[QuestionBlueprint],
        answer_text: str,
    ) -> AnswerMappingBundle:
        segments = self.split_answers(answer_text)
        question_lookup = {normalize_identifier(question.question_number): question for question in questions}
        aggregated: dict[str, list[str]] = {question.question_number: [] for question in questions}
        confidences: dict[str, list[float]] = {question.question_number: [] for question in questions}
        reasons: dict[str, list[str]] = {question.question_number: [] for question in questions}
        detected_order: list[str] = []
        unmatched_segments: list[AnswerSegment] = []

        for segment in segments:
            detected = normalize_identifier(segment.detected_question_number)
            if detected and detected in question_lookup:
                aggregated[detected].append(segment.text)
                confidences[detected].append(0.97)
                reasons[detected].append("Mapped using explicit question number in the answer sheet.")
                detected_order.append(detected)
            else:
                unmatched_segments.append(segment)

        for segment in unmatched_segments:
            best_question = None
            best_score = -1.0

            for question in questions:
                reference_text = " ".join(
                    [question.prompt, question.section or "", " ".join(question.expected_points)]
                )
                score = cosine_overlap(segment.text, reference_text)
                if score > best_score:
                    best_score = score
                    best_question = question

            if best_question and best_score >= 0.18:
                aggregated[best_question.question_number].append(segment.text)
                confidences[best_question.question_number].append(round(min(0.88, 0.45 + best_score), 2))
                reasons[best_question.question_number].append(
                    "Mapped using semantic overlap with the question prompt and rubric points."
                )
                detected_order.append(best_question.question_number)
            else:
                next_unanswered = next(
                    (
                        question
                        for question in questions
                        if not aggregated[question.question_number]
                    ),
                    None,
                )
                if next_unanswered:
                    aggregated[next_unanswered.question_number].append(segment.text)
                    confidences[next_unanswered.question_number].append(0.42)
                    reasons[next_unanswered.question_number].append(
                        "Mapped using sequential fallback because no reliable question label was found."
                    )
                    detected_order.append(next_unanswered.question_number)

        mapped_answers: list[MappedAnswer] = []
        for question in questions:
            answers = aggregated[question.question_number]
            if answers:
                mapped_answers.append(
                    MappedAnswer(
                        question_number=question.question_number,
                        answer_text=normalize_whitespace("\n".join(answers)),
                        confidence=round(sum(confidences[question.question_number]) / len(confidences[question.question_number]), 2),
                        mapping_reason=" ".join(reasons[question.question_number]),
                    )
                )
            else:
                mapped_answers.append(
                    MappedAnswer(
                        question_number=question.question_number,
                        answer_text="",
                        confidence=0.0,
                        mapping_reason="No answer was confidently detected for this question.",
                    )
                )

        return AnswerMappingBundle(mapped_answers=mapped_answers, detected_order=detected_order)
