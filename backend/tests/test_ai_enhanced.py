"""Tests for AI enhanced endpoints."""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.app_factory import create_full_app
from app.api.auth import DEMO_ACCESS_TOKEN


@pytest.fixture()
def client():
    return TestClient(create_full_app())


@pytest.fixture()
def auth_headers():
    return {"Authorization": f"Bearer {DEMO_ACCESS_TOKEN}"}


def test_daily_analysis_returns_structure(client, auth_headers):
    """GET /ai/daily-analysis should return DailyAnalysis-shaped JSON."""
    with patch("app.api.ai.call_qwen_api", new_callable=AsyncMock) as mock_qwen:
        mock_qwen.return_value = (
            '{"date":"2026-05-30","summary":"震颤稳定",'
            '"tremor_summary":{"total_detections":0,"avg_severity":0,'
            '"max_severity":0,"trend":"same","comparison_text":"暂无对比数据"},'
            '"key_observations":["暂无数据"],"concerns":[],'
            '"positive_notes":[],"recommendations":["继续监测"],'
            '"generated_at":"2026-05-30T00:00:00"}'
        )
        response = client.get("/api/ai/daily-analysis", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "tremor_summary" in data
    assert "key_observations" in data
    assert "recommendations" in data
    assert "generated_at" in data


def test_doctor_report_returns_structure(client, auth_headers):
    """POST /ai/doctor-report should return DoctorVisitReport-shaped JSON."""
    payload = {"start_date": "2026-05-01", "end_date": "2026-05-30"}
    with patch("app.api.ai.call_qwen_api", new_callable=AsyncMock) as mock_qwen:
        mock_qwen.return_value = (
            '{"executive_summary":"近期状态稳定","key_metrics":[],'
            '"frequency_analysis":"暂无数据","severity_distribution":{},'
            '"peak_times":[],"notable_patterns":[],"ai_observations":[],'
            '"questions_for_doctor":[]}'
        )
        response = client.post("/api/ai/doctor-report", json=payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "period" in data
    assert "summary" in data
    assert "tremor_analysis" in data
    assert "ai_observations" in data
    assert data["period"]["start"] == "2026-05-01"
    assert data["period"]["end"] == "2026-05-30"


def test_symptom_check_returns_structure(client, auth_headers):
    """POST /ai/symptom-check should return SymptomCheckResponse-shaped JSON."""
    payload = {
        "symptoms": ["手部震颤", "行动迟缓"],
        "duration": "weeks",
        "severity": 3,
        "associated_factors": ["疲劳"],
    }
    with patch("app.api.ai.call_qwen_api", new_callable=AsyncMock) as mock_qwen:
        mock_qwen.return_value = (
            '{"assessment":"症状提示需关注",'
            '"possible_causes":["帕金森病症状波动"],'
            '"urgency_level":"soon",'
            '"recommendations":["尽快就医"],'
            '"should_see_doctor":true,'
            '"related_to_parkinsons_likelihood":"medium"}'
        )
        response = client.post("/api/ai/symptom-check", json=payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "assessment" in data
    assert "urgency_level" in data
    assert data["urgency_level"] in ("routine", "soon", "urgent")
    assert "should_see_doctor" in data
    assert "related_to_parkinsons_likelihood" in data
    assert data["related_to_parkinsons_likelihood"] in ("low", "medium", "high")


def test_symptom_check_requires_symptoms(client, auth_headers):
    """POST /ai/symptom-check with empty symptoms should return 422."""
    payload = {"symptoms": [], "duration": "days", "severity": 2}
    response = client.post("/api/ai/symptom-check", json=payload, headers=auth_headers)
    assert response.status_code == 422
