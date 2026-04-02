from app.pipelines.answer_mapper import AnswerMapper
from app.schemas.domain import QuestionBlueprint


def test_answer_mapper_uses_explicit_question_numbers():
    mapper = AnswerMapper()
    questions = [
        QuestionBlueprint(question_number="1", prompt="Define force.", marks=2),
        QuestionBlueprint(question_number="2", prompt="Define work.", marks=2),
    ]
    bundle = mapper.map_answers(
        questions,
        "Q2: Work is force multiplied by displacement.\nQ1: Force is a push or pull.",
    )

    mapped = {item.question_number: item.answer_text for item in bundle.mapped_answers}
    assert mapped["1"].startswith("Force is a push or pull")
    assert mapped["2"].startswith("Work is force multiplied")
