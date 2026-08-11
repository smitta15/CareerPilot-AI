"""Unit tests for CareerPilot AI FastAPI endpoints."""

import os
import pytest
from types import SimpleNamespace
from pydantic import ValidationError

# Set environment variables before importing app
os.environ.setdefault("RAPIDAPI_KEY", "test_key")
os.environ.setdefault("GROQ_API_KEY", "test_key")
os.environ.setdefault("ADZUNA_APP_ID", "test_id")
os.environ.setdefault("ADZUNA_APP_KEY", "test_key")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

from app.main import app, health_check, chat, analyze_job, apply, list_applications
from app.models.request_models import JobRequest, AnalyzeRequest, ApplyRequest


class DummyGraph:
    """Mock LangGraph for testing."""

    def __init__(self, return_value=None):
        self.return_value = return_value or {}

    def invoke(self, *args, **kwargs):
        """Mock invoke - returns state or return_value."""
        if args:
            first = args[0]
            # If first looks like a state dict, echo it back for inspection
            if isinstance(first, dict):
                return first
        return self.return_value

    def get_state(self, *args, **kwargs):
        return SimpleNamespace(values=self.return_value)

    def update_state(self, *args, **kwargs):
        if len(args) > 1 and isinstance(args[1], dict):
            self.return_value.update(args[1])
        return self.return_value


@pytest.fixture
def mock_graph():
    """Provide mock graph for tests."""
    return DummyGraph()


def test_health_check():
    """Test health check endpoint."""
    response = health_check()
    assert response["status"] == "healthy"


def test_chat_endpoint_with_mock(mock_graph):
    """Test /chat endpoint with mocked graph."""
    # Mock app.state.graph
    app.state.graph = mock_graph

    req = JobRequest(user_query="Backend internships")
    data = chat(req)

    assert "thread_id" in data
    assert "request_id" in data


def test_analyze_job_builds_response(mock_graph):
    """Test /analyze-job endpoint response building."""
    fake_state = {
        "selected_job": {
            "id": "1",
            "title": "Backend Intern",
            "company": "Acme",
            "location": "Remote",
            "description": "Work with FastAPI",
            "skills": ["Python", "FastAPI"],
            "apply_link": "http://acme/careers/1",
        },
        "shortlisted_jobs": [
            {
                "id": "1",
                "title": "Backend Intern",
                "company": "Acme",
                "location": "Remote",
                "description": "Work with FastAPI",
                "skills": ["Python", "FastAPI"],
                "apply_link": "http://acme/careers/1",
                "match_score": 87,
                "match_reason": "Good skills match",
            }
        ],
        "match_score": 87,
        "match_reason": "Good skills match",
        "company_report": {"overview": "Acme is..."},
        "skill_gap": {"missing": ["Docker"]},
        "tailored_resume": "# Resume",
        "decision": {"recommendation": "Apply"},
    }

    app.state.graph = DummyGraph(return_value=fake_state)

    req = AnalyzeRequest(thread_id="tid-123", job_index=0)
    data = analyze_job(req).model_dump()

    assert data["job"]["company"] == "Acme"
    assert data["match_score"] == 87
    assert data["tailored_resume"].startswith("# Resume")
    assert data["status"] == "analyzed"


def test_apply_returns_applications_list(mock_graph):
    """Test /apply endpoint returns applications."""
    app.state.graph = mock_graph

    req = ApplyRequest(thread_id="tid-123", approved=True)
    data = apply(req)

    assert "applications" in data
    assert isinstance(data["applications"], list)
    assert "request_id" in data


def test_analyze_job_missing_thread_id():
    """Test /analyze-job with missing thread_id."""
    app.state.graph = DummyGraph()

    with pytest.raises(ValidationError):
        AnalyzeRequest(job_index=0)


def test_apply_missing_thread_id():
    """Test /apply with missing thread_id."""
    app.state.graph = DummyGraph()

    with pytest.raises(ValidationError):
        ApplyRequest(approved=True)


def test_list_applications():
    """Test /applications endpoint."""
    data = list_applications()

    assert "applications" in data
    assert "count" in data
    assert isinstance(data["applications"], list)
