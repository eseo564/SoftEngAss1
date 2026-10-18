from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
import app as api_module
from Event2 import app as flask_app

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

    # The route should not query the database
    mock_get_db.assert_not_called()

# Tests deleteEvent() to see if it works as intended
def test_deleteEvent_with_existing_event(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.fetchone.return_value = {"id": 1}

    response = client.delete("/api/v1/events/1")

    assert response.status_code == 200

    # Verify the DELETE query was executed
    sql, parameters = mock_cursor.execute.call_args[0]
    assert "DELETE FROM events" in sql
    assert parameters == (1,)
    
    mock_get_db.assert_called_once_with()
