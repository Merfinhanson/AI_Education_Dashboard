import re

from app.schemas.domain import QuestionBlueprint
from app.utils.text import keyword_candidates, normalize_identifier, normalize_whitespace


QUESTION_START_RE = re.compile(
    r"^\s*(?:Q(?:uestion)?\s*)?(\d+[A-Za-z]?)\s*[\).:-]\s*(.+)$",
    re.IGNORECASE,
)
SECTION_RE = re.compile(r"^\s*(Part|Section)\s+([A-Z0-9]+)\s*[:.-]?\s*(.*)$", re.IGNORECASE)
MARKS_RE = re.compile(r"[\[(](\d+(?:\.\d+)?)\s*(?:marks?|m)\s*[\])]", re.IGNORECASE)


class QuestionPaperParser:
    def parse(
        self,
        question_paper_text: str,
        marking_scheme_text: str | None = None,
    ) -> list[QuestionBlueprint]:
        rubric_lookup = self._parse_marking_scheme(marking_scheme_text or "")
        lines = question_paper_text.splitlines()

        section_name: str | None = None
        current_question_number: str | None = None
        current_prompt_lines: list[str] = []
        question_marks = 1.0
        questions: list[QuestionBlueprint] = []

        def flush_question() -> None:
            nonlocal current_question_number, current_prompt_lines, question_marks
            if not current_question_number:
                return

            prompt = normalize_whitespace(" ".join(current_prompt_lines))
            prompt = MARKS_RE.sub("", prompt).strip(" -:")
            normalized_number = normalize_identifier(current_question_number) or current_question_number
            points = rubric_lookup.get(normalized_number) or keyword_candidates(
                prompt,
                limit=max(3, int(round(question_marks)) + 2),
            )

            questions.append(
                QuestionBlueprint(
                    question_number=normalized_number,
                    prompt=prompt,
                    marks=question_marks,
                    section=section_name,
                    expected_points=points,
                )
            )
            current_question_number = None
            current_prompt_lines = []
            question_marks = 1.0

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            section_match = SECTION_RE.match(line)
            if section_match:
                flush_question()
                section_name = normalize_whitespace(" ".join(section_match.groups()))
                continue

            question_match = QUESTION_START_RE.match(line)
            if question_match:
                flush_question()
                current_question_number = question_match.group(1)
                remainder = question_match.group(2)
                marks_match = MARKS_RE.search(line)
                question_marks = float(marks_match.group(1)) if marks_match else 1.0
                current_prompt_lines.append(remainder)
                continue

            if current_question_number:
                current_prompt_lines.append(line)

        flush_question()
        return questions

    def _parse_marking_scheme(self, text: str) -> dict[str, list[str]]:
        current_question: str | None = None
        lookup: dict[str, list[str]] = {}

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            question_match = QUESTION_START_RE.match(line)
            if question_match:
                current_question = normalize_identifier(question_match.group(1))
                lookup.setdefault(current_question, [])
                remainder = normalize_whitespace(question_match.group(2))
                if remainder:
                    lookup[current_question].append(remainder)
                continue

            bullet_match = re.match(r"^[-*•]\s+(.+)$", line)
            if current_question and bullet_match:
                lookup.setdefault(current_question, []).append(normalize_whitespace(bullet_match.group(1)))
                continue

            if current_question:
                lookup.setdefault(current_question, []).append(normalize_whitespace(line))

        return {
            question: [item for item in items if item]
            for question, items in lookup.items()
        }
