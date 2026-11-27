
import pytest

from career_assistant.document.job_url_extractor import JobURLExtractor



class FakeResponse:

    def __init__(self, text, status_code=200, headers=None):
        self.text = text
        self.status_code = status_code
        self.headers = headers or {"Content-Type": "text/html"}

        self.is_redirect = status_code in (301, 302, 303, 307, 308)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")



class FakeSession:

    def __init__(self, response):
        self.response = response

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def get(self, *args, **kwargs):
        return self.response


def test_extract_job_page(monkeypatch):

    html = """
    <html>
        <head><title>AI Engineer Internship</title></head>
        <body>
            <nav>Navigation</nav>
            <main>
                <h1>AI Engineer Internship</h1>
                <p>We are looking for a Python and SQL developer.</p>
                <p>Experience with Docker and Machine Learning is required.</p>
            </main>
            <footer>Footer content</footer>
        </body>
    </html>
    """

    response = FakeResponse(html)

    monkeypatch.setattr(
        JobURLExtractor,
        "_validate_url",
        staticmethod(lambda url: None)
    )

    monkeypatch.setattr(
        "career_assistant.document.job_url_extractor.requests.Session",
        lambda: FakeSession(response)
    )

    result = JobURLExtractor.extract("https://example.com/job")

    assert result["title"] == "AI Engineer Internship"
    assert "Python" in result["text"]
    assert "Docker" in result["text"]
    assert "Navigation" not in result["text"]
    assert result["source"] == "URL"


def test_reject_empty_url():

    with pytest.raises(ValueError):
        JobURLExtractor.extract("")


def test_reject_page_without_readable_content(monkeypatch):

    response = FakeResponse(
        "<html><body><p>Too short</p></body></html>"
    )

    monkeypatch.setattr(
        JobURLExtractor,
        "_validate_url",
        staticmethod(lambda url: None)
    )

    monkeypatch.setattr(
        "career_assistant.document.job_url_extractor.requests.Session",
        lambda: FakeSession(response)
    )

    with pytest.raises(ValueError, match="Not enough readable text"):
        JobURLExtractor.extract("https://example.com/job")
