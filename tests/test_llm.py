from career_assistant.llm.client import OllamaClient


def test_generate(monkeypatch):

    class FakeResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "message": {
                    "content": "AI Career Assistant test successful."
                }
            }

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "career_assistant.llm.client.requests.post",
        fake_post
    )

    client = OllamaClient()

    result = client.generate("Test prompt")

    assert result == "AI Career Assistant test successful."