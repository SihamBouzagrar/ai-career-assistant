
from career_assistant.extraction.skill_extractor import SkillExtractor


def test_extract_basic_skills():

    text = """
    I have experience in Python, SQL, Docker
    and Machine Learning.
    """

    results = SkillExtractor.extract(text)

    skills = [item["skill"] for item in results]

    assert "Python" in skills
    assert "SQL" in skills
    assert "Docker" in skills
    assert "Machine Learning" in skills


def test_extract_aliases():

    text = """
    Experience with PowerBI, sklearn,
    Postgres and RAG.
    """

    results = SkillExtractor.extract(text)

    skills = [item["skill"] for item in results]

    assert "Power BI" in skills
    assert "Scikit-learn" in skills
    assert "PostgreSQL" in skills
    assert "RAG" in skills


def test_no_false_positive():

    text = "I enjoy programming and reading books."

    results = SkillExtractor.extract(text)

    assert results == []


def test_evidence_is_returned():

    text = "Developed applications using Python and Docker."

    results = SkillExtractor.extract(text)

    python_skill = next(
        item for item in results
        if item["skill"] == "Python"
    )

    assert len(python_skill["evidence"]) > 0
    assert "Python" in python_skill["evidence"][0]
