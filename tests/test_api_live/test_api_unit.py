from unittest.mock import MagicMock, patch
import pytest
from Event import app as flask_app

@pytest.fixture()
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as test_client:
        yield test_client

@pytest.fixture()
def mocked_database():
    # We patch 'Event.get_db' because Event.py imports get_db directly
    with patch("Event.get_db") as mock_get_db:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        
        mock_get_db.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        yield mock_get_db, mock_connection, mock_cursor



def test_create_event_with_mocked_database(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3

    response = client/post("/api/v1/events",
                           json={"id": 3,
                                 "name": "Code Reviews",
                                 "date": "10/24/2026",
                                 "time": "17:00",
                                 "capacity": 35,
                                 "location": "Library"},
                                 )

    assert response.status_code == 201
    assert response.get_json() == {
        "data": {
           "id": 3,
            "name": "Code Reviews",
            "date": "10/24/2026",
            "time": "17:00",
            "capacity": 35,
            "location": "Library", 
        }
    }

    mock_get_db.assert_called_once_with()
    mock_connection.cursor.assert_called_once_with()

    sql, parameters = mock_cursor.execute.call_args[0]
    assert "INSERT INTO events" in sql
    assert parameters == ("Code Reviews", "10/24/2026", "17:00", 35, "Library")

    mock_connection.commit.assert_called_once_with()
    mock_cursor.close.assert_called_once_with()
    mock_connection.close.assert_called_once_with()