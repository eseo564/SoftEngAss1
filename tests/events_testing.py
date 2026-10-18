from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
import app as api_module
from Event import app as flask_app

@pytest.fixture()
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as test_client:
        yield test_client

@pytest.fixture()
def mocked_database():
    with patch("Event2.get_db") as mock_get_db:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()


        mock_get_db.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor


        yield mock_get_db, mock_connection, mock_cursor

# Tests that listEvents() successfully returns the correct data for existing events
def test_listEvents__returns_mocked_rows(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "Event 1"},
        {"id": 2, "name": "Event 2"},
    ]

    response = client.get("/api/v1/events")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"id": 1, "name": "Event 1"},
            {"id": 2, "name": "Event 2"},
        ]
    }

    mock_get_db.assert_called_once_with()
    mock_connection.cursor.assert_called_once_with(dictionary=True)
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once_with()
    mock_connection.close.assert_called_once_with()

# Tests that listEvents() successfully returns the correct data for existing events when a name query is provided
def test_listEvents_with_name_query(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "Event 1"},
    ]

    response = client.get("/api/v1/events?name=Event")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"id": 1, "name": "Event 1"},
        ]
    }

    mock_get_db.assert_called_once_with()
    mock_connection.cursor.assert_called_once_with(dictionary=True)
    mock_cursor.execute.assert_called_once()
    sql, parameters = mock_cursor.execute.call_args[0]
    assert "WHERE LOWER(name) LIKE %s" in sql
    assert parameters == ("%event%",)

 # Tests that listEvents() successfully returns an empty list when a name query is used but no events match
def test_listEvents_with_name_query_no_results(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchall.return_value = []

    response = client.get("/api/v1/events?name=NonExistentEvent")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": []
    }

    mock_get_db.assert_called_once_with()
    mock_connection.cursor.assert_called_once_with(dictionary=True)
    mock_cursor.execute.assert_called_once()
    sql, parameters = mock_cursor.execute.call_args[0]
    assert "WHERE LOWER(name) LIKE %s" in sql
    assert parameters == ("%nonexistentevent%",)

# Tests that listEvents() successfully returns all events when a name query is used but is an empty string
def test_listEvents_with_name_query_empty_string(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "Event 1"},
        {"id": 2, "name": "Event 2"},
    ]

    response = client.get("/api/v1/events?name=")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"id": 1, "name": "Event 1"},
            {"id": 2, "name": "Event 2"},
        ]
    }

    mock_get_db.assert_called_once_with()
    mock_connection.cursor.assert_called_once_with(dictionary=True)
    mock_cursor.execute.assert_called_once()

# Tests that listEvents() successfully returns all events when a name query is used but only whitespace
def test_listEvents_with_name_query_whitespace(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "Event 1"},
        {"id": 2, "name": "Event 2"},
    ]

    response = client.get("/api/v1/events?name=   ")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": [
            {"id": 1, "name": "Event 1"},
            {"id": 2, "name": "Event 2"},
        ]
    }

    mock_get_db.assert_called_once_with()
    mock_connection.cursor.assert_called_once_with(dictionary=True)
    mock_cursor.execute.assert_called_once()

# Tests that retrieveEvent() successfully returns the correct data for an existing event 
def test_retrieveEvent__returns_a_mocked_row(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchone.return_value = {
        "id": 3,
        "name": "Code Reviews",
        "date": "10/24/2026",
        "time": "17:00",
        "capacity": 35,
        "location": "Library"
    }

    response = client.get("/api/v1/events/3")

    assert response.status_code == 200
    assert response.get_json() == {
        "data": {
            "id": 3,
            "name": "Code Reviews",
            "date": "10/24/2026",
            "time": "17:00",
            "capacity": 35,
            "location": "Library"
        }
    }

    mock_get_db.assert_called_once_with()
    mock_connection.cursor.assert_called_once_with(dictionary=True)


    sql, parameters = mock_cursor.execute.call_args[0]
    assert "WHERE id = %s" in sql
    assert parameters == (3,)


    mock_cursor.close.assert_called_once_with()
    mock_connection.close.assert_called_once_with()

# Tests that retrieveEvent() returns a 404 error when requested event does not exist
def test_retrieveEvent_checks_non_existing_event (client, mocked_database) :
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchone.return_value = None

    response = client.get("/api/v1/events/3")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "No event found with id 3" 
    }

    mock_get_db.assert_called_once_with()
    mock_connection.cursor.assert_called_once_with(dictionary=True)

# Tests retrieveEvent() below lower boundary returns 404
def test_retrieveEvent_with_negative_id(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    response = client.get("/api/v1/events/-1")

    assert response.status_code == 404

    mock_get_db.assert_not_called()

# Tests retrieveEvent() returns 404 when id type is a string
def test_retrieveEvent_with_string_id(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    response = client.get("/api/v1/events/hello")

    assert response.status_code == 404

    mock_get_db.assert_not_called()

# Tests deleteEvent() to see if it works as intended
def test_deleteEvent_with_existing_event(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchone.return_value = {"id": 1}

    response = client.delete("/api/v1/events/1")

    assert response.status_code == 200

    sql, parameters = mock_cursor.execute.call_args[0]
    assert "DELETE FROM events" in sql
    assert parameters == (1,)
    
    mock_get_db.assert_called_once_with()

# Tests deleteEvent() to see if it returns 404 when the event does not exist
def test_deleteEvent_with_non_existing_event(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchone.return_value = None

    response = client.delete("/api/v1/events/999")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "No event found with id 999"
    }

    sql, parameters = mock_cursor.execute.call_args[0]    
    assert "SELECT id" in sql
    assert "FROM events" in sql
    assert "WHERE id = %s" in sql
    assert parameters == (999,)
    
    mock_get_db.assert_called_once_with()

# Tests deleteEvent() to see if it returns 404 when the event has already been deleted
def test_deleteEvent_with_duplicate_deletes(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    
    mock_cursor.fetchone.side_effect = [
        {"id": 1},  # First call: event exists
        None       # Second call: event no longer exists
    ]

    # First delete attempt
    response1 = client.delete("/api/v1/events/1")
    assert response1.status_code == 200

    # Second delete attempt on the same event
    response2 = client.delete("/api/v1/events/1")
    assert response2.status_code == 404
    assert response2.get_json() == {
        "error": "No event found with id 1"
    }

    assert mock_cursor.execute.call_count == 3  # Two SELECTs and one DELETE

# Tests deleteEvent() to see if it returns 404 when the event id is negative
def test_deleteEvent_with_negative_id(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    response = client.delete("/api/v1/events/-1")

    assert response.status_code == 404
   
    mock_get_db.assert_not_called()

# Tests deleteEvent() to see if it returns 404 when the event id is a string
def test_deleteEvent_with_string_id(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    response = client.delete("/api/v1/events/hello")

    assert response.status_code == 404

    mock_get_db.assert_not_called()
