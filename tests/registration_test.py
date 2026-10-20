from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import pytest
import Registration as api_module
from Registration import app as flask_app

@pytest.fixture()
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as test_client:
        yield test_client

def make_mock_db(
    *,
    event_row=None,
    participant_row=None,
    already_registered=False,
    registration_count=0,
    insert_id=1,
    delete_rowcount=1,
    list_rows=None,
    participants_for_event=None,
):
    """
    Build a fake connection + cursor that answers the queries
    the new registration.py makes.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Helpers that the routes call in sequence
    # We use side_effect so each execute() can return different data.
    def execute_side_effect(sql, params=None):
        sql_lower = " ".join(sql.lower().split())  # normalise whitespace

        # event_exists / registration_allowed (SELECT from events)
        if "from events" in sql_lower and "where eventid" in sql_lower:
            if "capacity" in sql_lower or "starttime" in sql_lower:
                # registration_allowed
                mock_cursor.fetchone.return_value = event_row
            else:
                # simple existence check
                mock_cursor.fetchone.return_value = (
                    {"eventID": params[0]} if event_row is not None else None
                )

        # participant_exists
        elif "from participants" in sql_lower:
            mock_cursor.fetchone.return_value = (
                {"userID": params[0]} if participant_row is not None else None
            )

        # already_registered
        elif "from registrations" in sql_lower and "and userid" in sql_lower:
            mock_cursor.fetchone.return_value = (
                {"registrationID": 1} if already_registered else None
            )

        # count registrations (capacity check)
        elif "count(*)" in sql_lower:
            mock_cursor.fetchone.return_value = {
                "current_registrations": registration_count
            }

        # INSERT
        elif sql_lower.strip().startswith("insert"):
            mock_cursor.lastrowid = insert_id
            # after insert we re-fetch the row
            mock_cursor.fetchone.return_value = {
                "registrationID": insert_id,
                "eventID": params[0],
                "userID": params[1],
                "registeredAt": datetime.now(),
            }

        # DELETE
        elif sql_lower.strip().startswith("delete"):
            mock_cursor.rowcount = delete_rowcount

        # list all registrations
        elif "from registrations" in sql_lower and "order by" in sql_lower:
            mock_cursor.fetchall.return_value = list_rows or []

        # list participants for an event (JOIN)
        elif "inner join registrations" in sql_lower:
            mock_cursor.fetchall.return_value = participants_for_event or []

        else:
            mock_cursor.fetchone.return_value = None
            mock_cursor.fetchall.return_value = []

    mock_cursor.execute.side_effect = execute_side_effect
    return mock_conn

# ---------------------------------------------------------------------------
# Success path
# ---------------------------------------------------------------------------
def test_create_registration_success(client):
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    event = {"capacity": 10, "startTime": future}

    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(
            event_row=event,
            participant_row={"userID": 1},
            already_registered=False,
            registration_count=0,
            insert_id=42,
        )
        response = client.post(
            "/api/v1/registrations",
            json={"eventID": 1, "userID": 1},
        )

    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["registrationID"] == 42
    assert data["eventID"] == 1
    assert data["userID"] == 1

# ---------------------------------------------------------------------------
# Duplicate
# ---------------------------------------------------------------------------
def test_create_duplicate_registration(client):
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    event = {"capacity": 10, "startTime": future}

    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(
            event_row=event,
            participant_row={"userID": 1},
            already_registered=True,          # <-- already exists
        )
        response = client.post(
            "/api/v1/registrations",
            json={"eventID": 1, "userID": 1},
        )

    assert response.status_code == 409

# ---------------------------------------------------------------------------
# Non-existent event / participant
# ---------------------------------------------------------------------------
def test_create_registration_nonexistent_event(client):
    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(event_row=None)
        response = client.post(
            "/api/v1/registrations",
            json={"eventID": 999, "userID": 1},
        )
    assert response.status_code == 404

def test_create_registration_nonexistent_participant(client):
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(
            event_row={"capacity": 10, "startTime": future},
            participant_row=None,             # participant missing
        )
        response = client.post(
            "/api/v1/registrations",
            json={"eventID": 1, "userID": 999},
        )
    assert response.status_code == 404

# ---------------------------------------------------------------------------
# Full event / past event
# ---------------------------------------------------------------------------
def test_create_registration_full_event(client):
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(
            event_row={"capacity": 2, "startTime": future},
            participant_row={"userID": 1},
            already_registered=False,
            registration_count=2,             # already at capacity
        )
        response = client.post(
            "/api/v1/registrations",
            json={"eventID": 2, "userID": 1},
        )
    assert response.status_code == 400

def test_create_registration_past_event(client):
    past = "2020-01-01 10:00:00"
    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(
            event_row={"capacity": 10, "startTime": past},
            participant_row={"userID": 1},
            already_registered=False,
            registration_count=0,
        )
        response = client.post(
            "/api/v1/registrations",
            json={"eventID": 3, "userID": 1},
        )
    assert response.status_code == 400

# ---------------------------------------------------------------------------
# Invalid IDs
# ---------------------------------------------------------------------------
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
def test_create_registration_invalid_ids(client, payload):
    # No DB call should even happen for pure validation errors,
    # but we still patch so the test doesn't accidentally hit a real DB.
    with patch.object(api_module, "get_db"):
        response = client.post("/api/v1/registrations", json=payload)
    assert response.status_code == 400

# ---------------------------------------------------------------------------
# GET list
# ---------------------------------------------------------------------------
def test_get_registrations(client):
    rows = [
        {
            "registrationID": 1,
            "eventID": 1,
            "userID": 1,
            "registeredAt": datetime(2026, 10, 1, 12, 0, 0),
        }
    ]
    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(list_rows=rows)
        response = client.get("/api/v1/registrations")

    assert response.status_code == 200
    body = response.get_json()
    assert "data" in body
    assert len(body["data"]) == 1
    assert body["data"][0]["registrationID"] == 1

# ---------------------------------------------------------------------------
# Participants for an event
# ---------------------------------------------------------------------------
def test_get_event_participants(client):
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    participants = [
        {"userID": 1, "name": "Jane Doe", "email": "jane@example.com"}
    ]
    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(
            event_row={"capacity": 10, "startTime": future},
            participants_for_event=participants,
        )
        response = client.get("/api/v1/registrations/events/1/participants")

    assert response.status_code == 200
    assert response.get_json()["data"] == participants

def test_get_participants_nonexistent_event(client):
    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(event_row=None)
        response = client.get("/api/v1/registrations/events/999/participants")
    assert response.status_code == 404

# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------
def test_delete_registration(client):
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(
            event_row={"capacity": 10, "startTime": future},
            participant_row={"userID": 1},
            delete_rowcount=1,                # one row deleted
        )
        response = client.delete("/api/v1/registrations/1/1")

    assert response.status_code == 200

def test_delete_nonexistent_registration(client):
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    with patch.object(api_module, "get_db") as mock_get_db:
        mock_get_db.return_value = make_mock_db(
            event_row={"capacity": 10, "startTime": future},
            participant_row={"userID": 999},
            delete_rowcount=0,                # nothing deleted
        )
        response = client.delete("/api/v1/registrations/1/999")

    assert response.status_code == 404
