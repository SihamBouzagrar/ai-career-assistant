
from career_assistant.matching.matcher import SkillMatcher


def test_weighted_matching():
    cv_skills = [
        {"skill": "Python"},
        {"skill": "SQL"},
        {"skill": "Docker"},
    ]

    job_skills = [
        {"skill": "Python"},
        {"skill": "SQL"},
        {"skill": "AWS"},
        {"skill": "Docker"},
    ]

    result = SkillMatcher.match(
        cv_skills,
        job_skills,
        required_skills=["Python", "SQL", "AWS"],
        preferred_skills=["Docker"]
    )

    assert result["matched"] == ["docker", "python", "sql"]
    assert result["missing"] == ["aws"]

    assert result["coverage_score"] == 75.0
    assert result["weighted_score"] == 71.43

    assert result["missing_required"] == ["aws"]
    assert result["matched_preferred"] == ["docker"]


def test_empty_job_skills():
    result = SkillMatcher.match(
        cv_skills=["Python"],
        job_skills=[]
    )

    assert result["coverage_score"] == 0.0
    assert result["weighted_score"] == 0.0


def test_dictionary_and_string_inputs():
    result = SkillMatcher.match(
        cv_skills=["Python", {"skill": "SQL"}],
        job_skills=[{"skill": "Python"}, "SQL"]
    )

    assert result["coverage_score"] == 100.0
    assert result["matched"] == ["python", "sql"]
