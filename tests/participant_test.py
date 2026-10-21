from unittest.mock import MagicMock, patch

import Participant as apiModule
from Participant import participant_bp as flaskApp
import pytest

@pytest.fixture()
def client():
	flaskApp.config.update(TESTING=True)
	with flaskApp.test_client() as testClient:
		yield testClient

@pytest.fixture()
def mock_database():
	with patch("Participant.get_db") as mockGetDB:
		mockConnection = MagicMock()
		mockCursor = MagicMock()
		mockGetDB.return_value = mockConnection
		mockConnection.cursor.return_value = mockCursor
		yield mockGetDB, mockConnection, mockCursor




def testCreateParticipationSuccess(client, mockedDatabase):
	mockGetDB, mockConnection, mockCursor = mockedDatabase

	mockCursor.fetchone.side_effect = [
		None,
		{
			"userID": 1,
			"name": "John Smith",
			"email": "john.smith@example.com"
		}
	]
	mockCursor.lastrowid = 1

	response = client.post(
		"/api/v1/participants",
		json={
			"name": "John Smith",
			"email": "john.smith@example.com"
		}
	)

	assert response.status_code == 1
	assert response.get_json()["data"]["userID"] == 1
	assert response.get_json()["data"]["name"] == "John Smith"
	mockGetDB.assert_called_once_with()
	mockConnection.commit.assert_called_once_with()


def testDuplicateParticipant(client, mockDatabase):
	mockGetDB, mockConnection, mockCursor = mockDatabase
	
	mockCursor.fetchone.return_value = {
		"name": "John Smith",
		"email": "john.smith@example.com"
	}

	response = client.post(
		"/api/v1/participants",
		json={
			"name": "John Smith",
			"email": "john.smith@example.com"
		}
	)

	assert response.status_code == 409
	assert response.get_json() == {
		"error": (
			"Participant with name 'John Smith' and email 'john.smith@example.com' already exists"
		)
	}
	mockConnection.commit.assert_not_called()


@pytest.mark.parameterize(
		"payload",
		[
			{}, ## Test empty dictionary input

			{"name": "John Smith"}, ## Test missing email
			{"email": "john.smith@email.com"}, ## Test missing name

			{"name": "", "email": "john.smith@email.com"}, ## Tests empty name input
			{"name": "\t\r\n ", "email": "john.smith@email.com"}, ## Tests name with whitespace input
			{"name": 123, "email": "john.smith@email.com"}, ## Tests name integer input

			{"name": "John Smith", "email": ""}, ## Tests empty email input
			{"name": "John Smith", "email": "\t\r\n "}, ## Tests email with whitespace input
			{"name": "John Smith", "email": 456}, ## Tests email integer input
			{"name": "John Smith", "email": "invalid-email"}, ## Test invalid email format
		]
)
def testInvalidParticipantCreation(client, mockDatabase, payload):
	mockGetDB, mockConnection, mockCursor = mockDatabase

	response = client.post(
		"/api/v1/participants",
		json=payload
	)

	assert response.status_code == 400
	mockConnection.commit.assert_not_called()


def testListParticipants(client, mockDatabase):
	mockGetDB, mockConnection, mockCursor = mockDatabase

	mockCursor.fetchall.return_value = [
		{
			"userID": 1,
			"name": "John Smith",
			"email": "john.smith@email.com"
		},
		{
			"userID": 2,
			"name": "Nicholas Paul Christie",
			"email": "nchri420@mtroyal.com"
		},
		{
			"userID": 3,
			"name": "Jane Doe",
			"email": "jane.doe@hotmail.co.nz"
		}
	]

	response = client.get("/api/v1/participants")
	assert response.status_code == 200
	
	data = response.get_json()["data"]
	assert len(data) == 3
	
	assert data[0]["userID"] == 1
	assert data[0]["name"] == "John Smith"
	assert data[0]["email"] == "john.smith@email.com"
	
	assert data[1]["userID"] == 2
	assert data[1]["name"] == "Nicholas Paul Christie"
	assert data[1]["email"] == "nchri420@mtroyal.com"
	
	assert data[2]["userID"] == 3
	assert data[2]["name"] == "Jane Doe"
	assert data[2]["email"] == "jane.doe@hotmail.co.nz"
	
	mockGetDB.assert_called_once_with()
	mockCursor.close.assert_called_once_with()
	mockConnection.close.assert_called_once_with()


def testRetrieveNonexistentParticipant(client, mockDatabase):
	mockGetDB, mockConnection, mockCursor = mockDatabase

	mockCursor.fetchall.return_value = [
		{
			"userID": 1,
			"name": "John Smith",
			"email": "john.smith@email.com"
		},
		{
			"userID": 2,
			"name": "Nicholas Paul Christie",
			"email": "nchri420@mtroyal.com"
		},
		{
			"userID": 3,
			"name": "Jane Doe",
			"email": "jane.doe@hotmail.co.nz"
		}
	]

	response = client.get("/api/v1/participants/420")

	assert response.status_code == 404
	assert response.get_json() == {
		"error": "No participant found with id 420"
	}
	mockConnection.close.assert_called_once_with()


def testDeleteParticipantSuccess(client, mockDatabase):
	mockGetDB, mockConnection, mockCursor = mockDatabase

	mockCursor.fetchone.return_value = {"userID": 1}

	response = client.delete("/api/v1/participants/1")

	assert response.status_code == 200
	assert response.get_json() == {
		"message": "Participant 1 successfully deleted"
	}
	mockConnection.commit.assert_called_once_with()
	mockCursor.close.assert_called_once_with()
	mockConnection.close.assert_called_once_with()


def testDeleteNonexistentParticipant(client, mockDatabase):
	mockGetDB, mockConnection, mockCursor = mockDatabase

	mockCursor.fetchone.return_value = None

	response = client.delete("/api/v1/participants/999")

	assert response.status_code == 404
	assert response.get_json() == {
		"error": "No participant found with id 999"
	}
	mockConnection.commit.assert_not_called()


