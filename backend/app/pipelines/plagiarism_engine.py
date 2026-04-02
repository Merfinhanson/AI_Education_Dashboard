from app.utils.text import cosine_overlap, file_sha256, order_similarity


class PlagiarismDetector:
    def compare_submission(
        self,
        current: dict,
        historic_submissions: list[dict],
        text_threshold: float,
        structural_threshold: float,
    ) -> list[dict]:
        matches: list[dict] = []
        current_hash = file_sha256(current["answer_sheet_path"])

        for candidate in historic_submissions:
            candidate_hash = file_sha256(candidate["answer_sheet_path"])
            text_similarity = round(
                cosine_overlap(current["answer_sheet_text"], candidate["answer_sheet_text"]),
                4,
            )
            structural_similarity = round(
                order_similarity(current["answer_order"], candidate["answer_order"]),
                4,
            )
            image_similarity = 1.0 if current_hash == candidate_hash else 0.0

            copied_sections = []
            for question_number, answer_text in current["question_answers"].items():
                candidate_answer = candidate["question_answers"].get(question_number, "")
                if not answer_text or not candidate_answer:
                    continue
                section_similarity = cosine_overlap(answer_text, candidate_answer)
                if section_similarity >= text_threshold:
                    copied_sections.append(question_number)

            overall_similarity = round(
                (0.65 * text_similarity) + (0.25 * structural_similarity) + (0.10 * image_similarity),
                4,
            )

            should_flag = (
                overall_similarity >= text_threshold
                or structural_similarity >= structural_threshold
                or len(copied_sections) >= 2
                or image_similarity == 1.0
            )

            if should_flag:
                matches.append(
                    {
                        "matched_submission_id": candidate["submission_id"],
                        "matched_student_name": candidate["student_name"],
                        "text_similarity": text_similarity,
                        "structural_similarity": structural_similarity,
                        "image_similarity": image_similarity,
                        "overall_similarity": overall_similarity,
                        "upload_timestamp": candidate["created_at"],
                        "copied_sections": copied_sections,
                    }
                )

        return sorted(matches, key=lambda item: item["overall_similarity"], reverse=True)
