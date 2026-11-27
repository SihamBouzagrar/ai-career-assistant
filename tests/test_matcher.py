
import career_assistant.matching.matcher


def make_skill(name):
    return {
        "skill": name,
        "occurrences": 1,
        "evidence": [f"Evidence for {name}"]
    }


def test_basic_matching():

    cv = [
        make_skill("Python"),
        make_skill("SQL"),
        make_skill("Docker")
    ]

    job = [
        make_skill("Python"),
        make_skill("SQL"),
        make_skill("AWS")
    ]

    result = career_assistant.matching.matcher.SkillMatcher.match(cv, job)

    assert result["cv_skill_count"] == 3
    assert result["job_skill_count"] == 3

    assert len(result["common_skills"]) == 2
    assert len(result["missing_skills"]) == 1
    assert len(result["extra_skills"]) == 1

    assert result["metrics"]["precision"] == 66.67
    assert result["metrics"]["recall"] == 66.67
    assert result["metrics"]["f1_score"] == 66.67


def test_empty_cv():

    result = career_assistant.matching.matcher.SkillMatcher.match(
        [],
        [make_skill("Python")]
    )

    assert result["metrics"]["recall"] == 0
    assert result["metrics"]["precision"] == 0


def test_empty_job():

    result = career_assistant.matching.matcher.SkillMatcher.match(
        [make_skill("Python")],
        []
    )

    assert result["metrics"]["recall"] == 0
    assert result["metrics"]["precision"] == 0


def test_perfect_matching():

    skills = [
        make_skill("Python"),
        make_skill("SQL")
    ]

    result = career_assistant.matching.matcher.SkillMatcher.match(skills, skills)

    assert result["metrics"]["f1_score"] == 100
