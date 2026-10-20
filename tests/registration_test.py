from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import pytest

import Registration as api_module
from Registration import app as flask_app


@pytest.fixture()
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def mocked_database():
    with patch("Registration.get_db") as mock_get_db:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        yield mock_get_db, mock_connection, mock_cursor

def test_create_registration_success(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

    mock_cursor.fetchone.side_effect = [
        {"eventID": 1},
        {"userID": 1},
        None,
        {"capacity": 10, "startTime": future},
        {"current_registrations": 0},
        {
            "registrationID": 42,
            "eventID": 1,
            "userID": 1,
            "registeredAt": datetime(2026, 10, 20, 12, 0, 0),
        },
    ]
    mock_cursor.lastrowid = 42

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 1, "userID": 1},
    )

    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["registrationID"] == 42
    assert data["eventID"] == 1
    assert data["userID"] == 1
    mock_get_db.assert_called()
    mock_connection.commit.assert_called_once_with()


def test_create_duplicate_registration(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchone.side_effect = [
        {"eventID": 1},
        {"userID": 1},
        {"registrationID": 1},
    ]

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 1, "userID": 1},
    )

    assert response.status_code == 409
    assert response.get_json() == {"error": "Participant already registered"}
    mock_connection.commit.assert_not_called()


def test_create_registration_nonexistent_event(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    mock_cursor.fetchone.return_value = None

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 999, "userID": 1},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Event does not exist"}
    mock_connection.commit.assert_not_called()


def test_create_registration_nonexistent_participant(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    mock_cursor.fetchone.side_effect = [
        {"eventID": 1},
        None,
    ]

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 1, "userID": 999},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Participant does not exist"}
    mock_connection.commit.assert_not_called()


def test_create_registration_full_event(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

    mock_cursor.fetchone.side_effect = [
        {"eventID": 2},
        {"userID": 1},
        None,
        {"capacity": 2, "startTime": future},
        {"current_registrations": 2},
    ]

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 2, "userID": 1},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Event is full or has already started"}
    mock_connection.commit.assert_not_called()


def test_create_registration_past_event(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchone.side_effect = [
        {"eventID": 3},
        {"userID": 1},
        None,
        {"capacity": 10, "startTime": "2020-01-01 10:00:00"},
        {"current_registrations": 0},
    ]

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 3, "userID": 1},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Event is full or has already started"}
    mock_connection.commit.assert_not_called()


@pytest.mark.parametrize(
    "payload",
    [
        {"eventID": 0, "userID": 1},
        {"eventID": 1, "userID": 0},
        {"eventID": -1, "userID": 1},
        {"eventID": 1, "userID": -1},
        {"eventID": "hello", "userID": 1},
        {"eventID": 1, "userID": "hello"},
    ],
)
def test_create_registration_invalid_ids(client, mocked_database, payload):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    response = client.post("/api/v1/registrations", json=payload)

    assert response.status_code == 400
    mock_get_db.assert_not_called()


def test_get_registrations(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    mock_cursor.fetchall.return_value = [
        {
            "registrationID": 1,
            "eventID": 1,
            "userID": 1,
            "registeredAt": datetime(2026, 10, 1, 12, 0, 0),
        }
    ]

    response = client.get("/api/v1/registrations")

    assert response.status_code == 200
    body = response.get_json()
    assert "data" in body
    assert len(body["data"]) == 1
    assert body["data"][0]["registrationID"] == 1
    assert body["data"][0]["registeredAt"] == "2026-10-01 12:00:00"
    mock_get_db.assert_called_once_with()
    mock_connection.cursor.assert_called_once_with(dictionary=True)
    mock_cursor.close.assert_called_once_with()
    mock_connection.close.assert_called_once_with()


def test_get_event_participants(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    # 1. event_exists
    # 2. JOIN query → fetchall
    mock_cursor.fetchone.return_value = {"eventID": 1}
    mock_cursor.fetchall.return_value = [
        {"userID": 1, "name": "Jane Doe", "email": "jane@example.com"}
    ]

    response = client.get("/api/v1/registrations/events/1/participants")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"userID": 1, "name": "Jane Doe", "email": "jane@example.com"}
        ]
    }
    mock_get_db.assert_called()


def test_get_participants_nonexistent_event(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    mock_cursor.fetchone.return_value = None

    response = client.get("/api/v1/registrations/events/999/participants")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Event does not exist"}


def test_delete_registration(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    # 1. event_exists
    # 2. participant_exists
    # 3. DELETE (rowcount = 1)
    mock_cursor.fetchone.side_effect = [
        {"eventID": 1},
        {"userID": 1},
    ]
    mock_cursor.rowcount = 1

    response = client.delete("/api/v1/registrations/1/1")

    assert response.status_code == 200
    assert response.get_json() == {"message": "Registration successfully canceled"}
    mock_connection.commit.assert_called_once_with()


def test_delete_nonexistent__registration(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchone.side_effect = [
        {"eventID": 1},
        {"userID": 999},
    ]
    mock_cursor.rowcount = 0

    response = client.delete("/api/v1/registrations/1/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Registration does not exist"}
