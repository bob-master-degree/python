import json
import pytest
from backend.core import gpt_client

@pytest.fixture
def mock_session(monkeypatch):
    class DummySession(dict):
        pass
    dummy = DummySession()
    monkeypatch.setattr(gpt_client, "session", dummy)
    return dummy

def test_analyze_text_claims_success(monkeypatch, mock_session):
    mock_session["openai_api_key"] = "fakekey"

    class MockResponseMessage:
        def __init__(self):
            self.content = json.dumps({"facts": []})

    class MockChoice:
        def __init__(self):
            self.message = MockResponseMessage()

    class MockCompletions:
        @staticmethod
        def create(*args, **kwargs):
            return type("R", (), {"choices": [MockChoice()]})

    class MockChatAPI:
        def __init__(self):
            self.completions = MockCompletions()

    class MockClient:
        def __init__(self):
            self.chat = MockChatAPI()

    monkeypatch.setattr(gpt_client, "_get_client", lambda api_key: MockClient())

    data = gpt_client.analyze_text_claims("тест")
    assert "facts" in data
    assert isinstance(data["facts"], list)
