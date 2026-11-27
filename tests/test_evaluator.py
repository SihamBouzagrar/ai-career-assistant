
import pytest

from career_assistant.evaluation.evaluator import ResponseEvaluator


def test_evaluate_good_answer():

    question = "Which skills are missing?"

    context = (
        "The candidate has Python and SQL. "
        "The job requires Python, SQL and AWS."
    )

    answer = (
        "AWS is missing from the candidate profile. "
        "Python and SQL are already present."
    )

    expected_points = [
        "AWS is missing from the candidate profile",
        "Python is already present",
        "SQL is already present"
    ]

    result = ResponseEvaluator.evaluate(
        question=question,
        answer=answer,
        context=context,
        expected_points=expected_points
    )

    assert result["metrics"]["relevance"] > 0
    assert result["metrics"]["groundedness"] > 0
    assert result["metrics"]["completeness"] > 0
    assert 0 <= result["metrics"]["overall_score"] <= 100


def test_evaluate_empty_answer():

    with pytest.raises(ValueError):
        ResponseEvaluator.evaluate(
            question="Test question",
            answer="",
            context="Some context",
            expected_points=["Expected information"]
        )


def test_evaluate_invalid_context():

    with pytest.raises(ValueError):
        ResponseEvaluator.evaluate(
            question="Test question",
            answer="Some answer",
            context=None,
            expected_points=[]
        )


def test_hallucination_proxy():

    result = ResponseEvaluator.evaluate(
        question="What skills does the candidate have?",
        answer="Python and Quantum Computing",
        context="The candidate has Python skills.",
        expected_points=["Python"]
    )

    assert result["metrics"]["hallucination_proxy"] > 0


def test_empty_expected_points():

    result = ResponseEvaluator.evaluate(
        question="General question",
        answer="A general answer.",
        context="Some context.",
        expected_points=[]
    )

    assert result["metrics"]["relevance"] == 0
    assert result["metrics"]["completeness"] == 0
