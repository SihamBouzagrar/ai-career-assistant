
from career_assistant.extraction.job_requirements import (
    JobRequirementsExtractor
)


def test_classify_required_skills():
    text = """
    Required skills: Python and SQL.
    """

    skills = [
        {"skill": "Python", "evidence": ["Required skills: Python and SQL"]},
        {"skill": "SQL", "evidence": ["Required skills: Python and SQL"]},
    ]

    result = JobRequirementsExtractor.extract(text, skills)

    assert result["required"] == ["Python", "SQL"]
    assert result["preferred"] == []


def test_classify_preferred_skills():
    text = """
    Python is required.
    Knowledge of Docker would be a plus.
    """

    skills = [
        {"skill": "Python", "evidence": ["Python is required"]},
        {"skill": "Docker", "evidence": ["Knowledge of Docker would be a plus"]},
    ]

    result = JobRequirementsExtractor.extract(text, skills)

    assert result["required"] == ["Python"]
    assert result["preferred"] == ["Docker"]


def test_unclassified_skills():
    text = "Experience with Python and SQL."

    skills = [
        {"skill": "Python", "evidence": ["Experience with Python"]},
        {"skill": "SQL", "evidence": ["Experience with SQL"]},
    ]

    result = JobRequirementsExtractor.extract(text, skills)

    assert result["unclassified"] == ["Python", "SQL"]
    assert result["classification_complete"] is False


def test_empty_input():
    result = JobRequirementsExtractor.extract("", [])

    assert result["required"] == []
    assert result["preferred"] == []
    assert result["unclassified"] == []
