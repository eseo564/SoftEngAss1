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




def test_update_event_with_wrong_data_type(client, mocked_database):
    mock_get_db, mock_connection, mock_cursor = mocked_database

    mock_cursor.lastrowid = 3
    response = client.put("/api/v1/events/3",
                        json={"id": 3,
                            "name": "Code Reviews",
                            "date": "10/21/2026",
                            "time": "25:30",
                            "capacity": "35",
                            "location": "Library"},
                                )

    assert response.status_code == 400
    assert response.get_json() == {"error": "capacity must be an integer"}



def test_update_event_with_lowering_capacity(client, mocked_database):
    mock_cursor = mocked_database

    mock_cursor.fetchone.return_value = {"id": 3, "current_registrations": 50}

    response = client.put("/api/v1/events/3",
                        json={"id": 3,
                            "name": "Code Reviews",
                            "date": "10/21/2026",
                            "time": "25:30",
                            "capacity": 20,
                            "location": "Library"},
                                )

    assert response.status_code == 400
    assert response.get_json() == {"error": "changing amount lower than registered amount"}