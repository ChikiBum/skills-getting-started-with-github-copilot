from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Should be a dict with at least the prepopulated activities
    assert isinstance(data, dict)
    assert "Chess Club" in data


@pytest.fixture()
def reset_activities():
    # Make a deep-ish copy of participants, then restore after test
    original = {k: v["participants"].copy() for k, v in activities.items()}
    yield
    for k, plist in original.items():
        activities[k]["participants"] = plist


def test_signup_and_unsubscribe_flow(reset_activities):
    activity = "Chess Club"
    email = "test.user@example.com"

    # Ensure not already present
    assert email not in activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Signed up" in data.get("message", "")

    # Now the participant should be present
    assert email in activities[activity]["participants"]

    # Try signing up again -> should be 400
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Unregistered" in data.get("message", "")

    # Participant removed
    assert email not in activities[activity]["participants"]


def test_signup_for_unknown_activity():
    resp = client.post("/activities/UnknownActivity/signup?email=a@b.com")
    assert resp.status_code == 404


def test_unregister_nonexistent():
    activity = "Chess Club"
    email = "not.signed@example.com"
    # Ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 400
