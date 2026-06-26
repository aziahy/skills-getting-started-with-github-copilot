from urllib.parse import quote

import src.app as app_module


def activity_signup_path(activity_name):
    encoded_name = quote(activity_name, safe="")
    return f"/activities/{encoded_name}/signup"


def activity_participants_path(activity_name):
    encoded_name = quote(activity_name, safe="")
    return f"/activities/{encoded_name}/participants"


def test_get_activities_returns_expected_shape(client):
    # Arrange
    path = "/activities"

    # Act
    response = client.get(path)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert {
        "description",
        "schedule",
        "max_participants",
        "participants",
    } == set(payload["Chess Club"].keys())


def test_signup_adds_student_to_activity(client):
    # Arrange
    activity_name = "Science Club"
    email = "new.student@mergington.edu"
    path = activity_signup_path(activity_name)

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    path = activity_signup_path(activity_name)

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_when_activity_is_full(client):
    # Arrange
    activity_name = "Chess Club"
    max_slots = app_module.activities[activity_name]["max_participants"]
    app_module.activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(max_slots)
    ]
    email = "overflow@mergington.edu"
    path = activity_signup_path(activity_name)

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}


def test_signup_returns_400_for_duplicate_student(client):
    # Arrange
    activity_name = "Programming Class"
    email = app_module.activities[activity_name]["participants"][0]
    path = activity_signup_path(activity_name)

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_unregister_removes_student_from_activity(client):
    # Arrange
    activity_name = "Drama Club"
    email = app_module.activities[activity_name]["participants"][0]
    path = activity_participants_path(activity_name)

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    path = activity_participants_path(activity_name)

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_404_for_missing_participant(client):
    # Arrange
    activity_name = "Debate Team"
    email = "not.enrolled@mergington.edu"
    path = activity_participants_path(activity_name)

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}
