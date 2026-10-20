from unittest.mock import patch

import pytest
import Registration as api_module
from Registration import app as flask_app, Registration


@pytest.fixture()
def client():
    flask_app.config.update(TESTING=True)

    with flask_app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def mocked_database():
    with (
        patch.object(api_module, "loadDatabase") as mock_load_db,
        patch.object(api_module, "saveDatabase") as mock_save_db,
        patch.object(api_module, "loadEvents") as mock_load_events,
        patch.object(api_module, "loadParticipants") as mock_load_participants,
    ):
        mock_load_db.return_value = []
        mock_save_db.return_value = None

        mock_load_events.return_value = [
            {
                "eventID": 1,
                "eventName": "Python Workshop",
                "capacity": 2,
                "startTime": "2026-12-31 23:59",
            },
            {
                "eventID": 2,
                "eventName": "Full Event",
                "capacity": 0,
                "startTime": "2026-12-31 23:59",
            },
            {
                "eventID": 3,
                "eventName": "Past Event",
                "capacity": 10,
                "startTime": "2020-01-01 10:00",
            },
        ]

        mock_load_participants.return_value = [
            {"id": 1, "name": "Jane Doe"},
            {"id": 2, "name": "Gru"},
        ]

        yield (
            mock_load_db,
            mock_save_db,
            mock_load_events,
            mock_load_participants,
        )


# Tests successful registration creation
def test_create_registration_success(client, mocked_database):
    mock_load_db, mock_save_db, _, _ = mocked_database

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 1, "userID": 1},
    )

    assert response.status_code in (200, 201)
    mock_load_db.assert_called()
    mock_save_db.assert_called_once()


# Tests that duplicate registrations are rejected
def test_create_duplicate_registration(client, mocked_database):
    mock_load_db, mock_save_db, _, _ = mocked_database
    mock_load_db.return_value = [
<<<<<<< HEAD:tests/registration_testing.py
=======
#        {
#            "registrationID": 1,
#            "eventID": 1,
#            "userID": 1,
#            "registeredAt": "2026-10-01 12:00:00",
#        }
>>>>>>> f52dc0e8b5f5b5d9a412faf77f14183574640c90:tests/registration_test.py
        Registration(1, 1, 1, "2026-10-01 12:00:00")
    ]
    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 1, "userID": 1},
    )
    assert response.status_code == 409
    mock_save_db.assert_not_called()


# Tests registration for a nonexistent event
def test_create_registration_nonexistent_event(client, mocked_database):
    _, mock_save_db, _, _ = mocked_database

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 999, "userID": 1},
    )

    assert response.status_code == 404
    mock_save_db.assert_not_called()


# Tests registration for a nonexistent participant
def test_create_registration_nonexistent_participant(client, mocked_database):
    _, mock_save_db, _, _ = mocked_database

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 1, "userID": 999},
    )

    assert response.status_code == 404
    mock_save_db.assert_not_called()


# Tests registration when an event is full
# Error Code 400?
def test_create_registration_full_event(client, mocked_database):
    _, mock_save_db, _, _ = mocked_database

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 2, "userID": 1},
    )

    assert response.status_code == 400
    mock_save_db.assert_not_called()


# Tests registration for a past event
def test_create_registration_past_event(client, mocked_database):
    _, mock_save_db, _, _ = mocked_database

    response = client.post(
        "/api/v1/registrations",
        json={"eventID": 3, "userID": 1},
    )

    assert response.status_code == 400
    mock_save_db.assert_not_called()


# Tests invalid registration IDs
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
    _, mock_save_db, _, _ = mocked_database

    response = client.post("/api/v1/registrations", json=payload)

    assert response.status_code == 400
    mock_save_db.assert_not_called()


# Tests retrieving all registrations
def test_get_registrations(client, mocked_database):
    mock_load_db, _, _, _ = mocked_database
    mock_load_db.return_value = [
<<<<<<< HEAD:tests/registration_testing.py
=======
#        {
#            "registrationID": 1,
#            "eventID": 1,
#            "userID": 1,
#            "registeredAt": "2026-10-01 12:00:00",
#        }
>>>>>>> f52dc0e8b5f5b5d9a412faf77f14183574640c90:tests/registration_test.py
        Registration(1, 1, 1, "2026-10-01 12:00:00")
    ]
    response = client.get("/api/v1/registrations")
    assert response.status_code == 200
    assert response.get_json() is not None


# Tests retrieving participants registered for an event
def test_get_event_participants(client, mocked_database):
    mock_load_db, _, _, _ = mocked_database
    mock_load_db.return_value = [
        Registration(1, 1, 1, "2026-10-01 12:00:00")
    ]
    response = client.get("/api/v1/registrations/events/1/participants")
    assert response.status_code == 200
    assert response.get_json() is not None


# Tests retrieving participants for a nonexistent event
def test_get_participants_nonexistent_event(client, mocked_database):
    response = client.get("/api/v1/registrations/events/999/participants")

    assert response.status_code == 404


# Tests cancelling an existing registration
def test_delete_registration(client, mocked_database):
    mock_load_db, mock_save_db, _, _ = mocked_database
    mock_load_db.return_value = [
<<<<<<< HEAD:tests/registration_testing.py
        Registration(1, 1, 1, "2026-10-01 12:00:00")
=======
#        {
#            "registrationID": 1,
#            "eventID": 1,
#            "userID": 1,
#            "registeredAt": "2026-10-01 12:00:00",
#        }
	Registration(1, 1, 1, "2026-10-01 12:00:00")
>>>>>>> f52dc0e8b5f5b5d9a412faf77f14183574640c90:tests/registration_test.py
    ]
    response = client.delete("/api/v1/registrations/1/1")
    assert response.status_code == 200
    mock_save_db.assert_called_once()


# Tests cancelling a nonexistent registration
def test_delete_nonexistent_registration(client, mocked_database):
    _, mock_save_db, _, _ = mocked_database

    response = client.delete("/api/v1/registrations/1/999")

    assert response.status_code == 404
    mock_save_db.assert_not_called()
