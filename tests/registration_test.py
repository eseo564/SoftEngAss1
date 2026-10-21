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
    assert response.get_json() == {"error": "Participant already registered!"}
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


def test_create_registration_missing_or_null_body(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    # completely missing body
    response = client.post("/api/v1/registrations")
    assert response.status_code == 400
    mock_get_db.assert_not_called()

    # explicit null
    response = client.post("/api/v1/registrations", json=None)
    assert response.status_code == 400
    mock_get_db.assert_not_called()

    # empty object
    response = client.post("/api/v1/registrations", json={})
    assert response.status_code == 400
    mock_get_db.assert_not_called()

    # missing userID
    response = client.post("/api/v1/registrations", json={"eventID": 1})
    assert response.status_code == 400
    mock_get_db.assert_not_called()

    # missing eventID
    response = client.post("/api/v1/registrations", json={"userID": 1})
    assert response.status_code == 400
    mock_get_db.assert_not_called()

    # null eventID
    response = client.post(
        "/api/v1/registrations",
        json={"eventID": None, "userID": 1},
    )
    assert response.status_code == 400
    mock_get_db.assert_not_called()

    # null userID
    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 1, "userID": None},
    )
    assert response.status_code == 400
    mock_get_db.assert_not_called()

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

def test_capacity_release_and_rebooking(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

    #1st registration (user 1)
    mock_cursor.fetchone.side_effect = [
        {"eventID": 10},
        {"userID": 1},
        None,
        {"capacity": 2, "startTime": future},
        {"current_registrations": 0},
        {
            "registrationID": 101,
            "eventID": 10,
            "userID": 1,
            "registeredAt": datetime(2026, 10, 20, 12, 0, 0),
        },
    ]
    mock_cursor.lastrowid = 101

    response1 = client.post(
        "/api/v1/registrations",
        json={"eventID": 10, "userID": 1},
    )
    assert response1.status_code == 201
    data1 = response1.get_json()["data"]
    assert data1["registrationID"] == 101
    assert data1["eventID"] == 10
    assert data1["userID"] == 1
    mock_connection.commit.assert_called()

    #2nd registration (user 2)
    mock_cursor.fetchone.side_effect = [
        {"eventID": 10},
        {"userID": 2},
        None,
        {"capacity": 2, "startTime": future},
        {"current_registrations": 1},
        {
            "registrationID": 102,
            "eventID": 10,
            "userID": 2,
            "registeredAt": datetime(2026, 10, 20, 12, 1, 0),
        },
    ]
    mock_cursor.lastrowid = 102

    response2 = client.post(
        "/api/v1/registrations",
        json={"eventID": 10, "userID": 2},
    )
    assert response2.status_code == 201
    data2 = response2.get_json()["data"]
    assert data2["registrationID"] == 102
    assert data2["userID"] == 2

    #3rd registration (user 3), rejection
    mock_cursor.fetchone.side_effect = [
        {"eventID": 10},
        {"userID": 3},
        None,
        {"capacity": 2, "startTime": future},
        {"current_registrations": 2},
    ]

    response3 = client.post(
        "/api/v1/registrations",
        json={"eventID": 10, "userID": 3},
    )
    assert response3.status_code == 400
    assert response3.get_json() == {"error": "Event is full or has already started"}

    #cancel user 1 (releases one seat)
    mock_cursor.fetchone.side_effect = [
        {"eventID": 10},
        {"userID": 1},
    ]
    mock_cursor.rowcount = 1

    cancel_response = client.delete("/api/v1/registrations/10/1")
    assert cancel_response.status_code == 200
    assert cancel_response.get_json() == {
        "message": "Registration successfully canceled"
    }
    mock_connection.commit.assert_called()

    #user 3 can register (one seat free)
    mock_cursor.fetchone.side_effect = [
        {"eventID": 10},
        {"userID": 3},
        None,
        {"capacity": 2, "startTime": future},
        {"current_registrations": 1},
        {
            "registrationID": 103,
            "eventID": 10,
            "userID": 3,
            "registeredAt": datetime(2026, 10, 20, 12, 5, 0),
        },
    ]
    mock_cursor.lastrowid = 103

    response3_again = client.post(
        "/api/v1/registrations",
        json={"eventID": 10, "userID": 3},
    )
    assert response3_again.status_code == 201
    data3 = response3_again.get_json()["data"]
    assert data3["registrationID"] == 103
    assert data3["eventID"] == 10
    assert data3["userID"] == 3
