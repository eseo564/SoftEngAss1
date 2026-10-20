from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
import Event as api_module
from Event import app as flask_app

@pytest.fixture()
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as test_client:
        yield test_client

@pytest.fixture()
def mocked_database():
    with patch("Event.get_db") as mock_get_db:
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


# Tests that createEvent() is functioning properly
def test_create_event_with_mocked_database(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3

    response = client.post("/api/v1/events",
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


# Tests to see if the system uniquely id's with every new event
def test_create_event_with_duplicate_name(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3

    response1 = client.post("/api/v1/events",
                           json={"id": 3,
                                 "name": "Tour",
                                 "date": "10/24/2026",
                                 "time": "17:00",
                                 "capacity": 35,
                                 "location": "Library"},
                                 )

    assert response1.status_code == 201
    assert response1.get_json() == {
        "data": {
           "id": 3,
            "name": "Tour",
            "date": "10/24/2026",
            "time": "17:00",
            "capacity": 35,
            "location": "Library", 
        }
    }

    id_1 = response1.get_json()["data"]["id"]

    mock_cursor.lastrowid = 4
    response2 = client.post("/api/v1/events",
                           json={"id": 3,
                                 "name": "Tour",
                                 "date": "10/24/2026",
                                 "time": "17:00",
                                 "capacity": 35,
                                 "location": "Library"},
                                 ) 

    assert response2.status_code == 201
    assert response2.get_json() == {
        "data": {
           "id": 4,
            "name": "Tour",
            "date": "10/24/2026",
            "time": "17:00",
            "capacity": 35,
            "location": "Library", 
        }
    }

    id_2 = response2.get_json()["data"]["id"]

    assert id_1 != id_2 

    sql, parameters = mock_cursor.execute.call_args[0]
    assert "INSERT INTO events" in sql
    assert parameters == ("Tour", "10/24/2026", "17:00", 35, "Library")

# Tests createEvent() to see if it returns a 400 when a field is missing
def test_create_event_with_missing_information(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3

    response = client.post("/api/v1/events",
                           json={"id": 3,
                                 "name": "Code Reviews",
                                 "date": "10/24/2026",
                                 "time": "",
                                 "capacity": 35,
                                 "location": "Library"},
                                 )

    assert response.status_code == 400
    assert response.get_json() == {"error": "wrong time format (XX:XX)"
    }

# Tests createEvent() to see if it returns a 400 when provided a negative integer
def test_create_event_with_negative_capacity(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3
    response = client.post("/api/v1/events",
                           json={"id": 3,
                                 "name": "Code Reviews",
                                "date": "10/24/2026",
                                "time": "17:00",
                                "capacity": -10,
                                "location": "Library"},
                                )
    assert response.status_code == 400
    assert response.get_json() == {"error": "capacity has to be a positive integer"}


# Tests createEvent() to see if it returns a 400 when provided an invalid date format
def test_create_event_invalid_date(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3
    response = client.post("/api/v1/events",
                            json={"id": 3,
                                "name": "Code Reviews",
                                "date": "2026-10-21",
                                "time": "17:00",
                                "capacity": 35,
                                "location": "Library"},
                                    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "wrong date format (MM/DD/YYYY)"}

# Tests createEvent() to see if it returns a 400 when provided an invalid time
def test_create_event_invalid_time(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3
    response = client.post("/api/v1/events",
                            json={"id": 3,
                                "name": "Code Reviews",
                                "date": "10/21/2026",
                                "time": "25:30",
                                "capacity": 35,
                                "location": "Library"},
                                    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "wrong time format (XX:XX)"}

# Tests createEvent() to see if it returns a 400 when provided the wrong data type 
def test_create_event_with_wrong_data_type(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3
    response = client.post("/api/v1/events",
                        json={"id": 3,
                            "name": "Code Reviews",
                            "date": "10/21/2026",
                            "time": "25:30",
                            "capacity": "35",
                            "location": "Library"},
                                )

    assert response.status_code == 400
    assert response.get_json() == {"error": "capacity must be an integer"}

# Tests updateEvent() to see if it returns a 200 for a successful change
def test_update_event(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    mock_cursor.fetchone.return_value = {"id": 3, "current_registrations": 0}

    response = client.put("/api/v1/events/3",
                            json={"id": 3,
                                "name": "Code Reviews",
                                "date": "10/24/2026",
                                "time": "17:00",
                                "capacity": 35,
                                "location": "B103"},
                                )


    assert response.status_code == 200
    assert response.get_json() == {
        "data": {
           "id": 3,
            "name": "Code Reviews",
            "date": "10/24/2026",
            "time": "17:00",
            "capacity": 35,
            "location": "B103", 
        }
    }

    
# Tests updateEvent() to see if it returns a 400 for missing information 
def test_update_event_with_missing_information(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    mock_cursor.lastrowid = 3
    response = client.put("/api/v1/events/3",
                          json={"id": 3,
                                "name": "Code Reviews",
                                "date": "10/24/2026",
                                "time": "",
                                "capacity": 35,
                                "location": "Library"},
                                )

    assert response.status_code == 400
    assert response.get_json() == {"error": "wrong time format (XX:XX)"}  


# Tests updateEvent() to see if it returns a 400 when provided a negative integer
def test_update_event_with_negative_capacity(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3
    response = client.put("/api/v1/events/3",
                           json={"id": 3,
                                 "name": "Code Reviews",
                                "date": "10/24/2026",
                                "time": "17:00",
                                "capacity": -10,
                                "location": "Library"},
                                )
    assert response.status_code == 400
    assert response.get_json() == {"error": "capacity has to be a positive integer"}                


# Tests updateEvent() to see if it returns a 400 when provided an invalid date format
def test_update_event_invalid_date(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3
    response = client.put("/api/v1/events/3",
                            json={"id": 3,
                                "name": "Code Reviews",
                                "date": "2026-10-21",
                                "time": "17:00",
                                "capacity": 35,
                                "location": "Library"},
                                    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "wrong date format (MM/DD/YYYY)"}


# Tests updateEvent() to see if it returns a 400 when provided an invalid time
def test_update_event_invalid_time(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3
    response = client.put("/api/v1/events/3",
                            json={"id": 3,
                                "name": "Code Reviews",
                                "date": "10/21/2026",
                                "time": "25:30",
                                "capacity": 35,
                                "location": "Library"},
                                    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "wrong time format (XX:XX)"}



# Tests updateEvent() to see if it returns a 400 when provided the wrong data type 
def test_update_event_with_wrong_data_type(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3
    response = client.put("/api/v1/events/3",
                        json={"id": 3,
                            "name": "Code Reviews",
                            "date": "10/21/2026",
                            "time": "10:30",
                            "capacity": "35",
                            "location": "Library"},
                                )

    assert response.status_code == 400
    assert response.get_json() == {"error": "capacity must be an integer"}


# Tests updateEvent() to see if it returns a 400 when provided a lower capacity than currently registered users
def test_update_event_with_lowering_capacity(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database
    mock_cursor.fetchone.return_value = {"id": 3, "current_registrations": 50}

    response = client.put("/api/v1/events/3",
                        json={"id": 3,
                            "name": "Code Reviews",
                            "date": "10/21/2026",
                            "time": "10:30",
                            "capacity": 20,
                            "location": "Library"},
                                )

    assert response.status_code == 400
    assert response.get_json() == {"error": "changing amount lower than registered amount"}
