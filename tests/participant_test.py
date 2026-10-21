from unittest.mock import mock_open, patch
import json

import Participant as apiModule
from Participant import app as flaskApp, Participant
import pytest

@pytest.fixture()
def client():
	flaskApp.config.update(TESTING=True)

	with flaskApp.test_client() as testClient:
		yield testClient

@pytest.fixture()
def mockDB():
	with (
		patch.object(apiModule, "loadParticipantDatabase") as mockLoadDB,
		patch.object(apiModule, "loadParticipantDatabase") as mockSaveDB,
	):
		mockLoadDB.return_value = [
			Participant(1, "Nicholas Christie", "nchri421@mtroyal.ca"),
			Participant(2, "Jane Doe", "jane@gmail.com"),
			Participant(3, "Edward Smith", "ed.smith.1969@hotmail.co.nz")
		]
		mockSaveDB.return_value = None

		yield mockLoadDB, mockSaveDB





@pytest.mark.parametrize(
		"userID, name, email", 
		[
			(0, "John Smith", "john.smith@email.co.uk"),
			(1000000, "\t\r\v\nJohn Smith        ", "john.smith@example.com"),
			(1, "John Smith\t\r\v\n ", "john.smith@email.com"),
			(1, "John Smith ", "\t\r\v\n john.smith@email.com"),
			(1, "John Smith ", "john.smith@email.com"),
		]
	)
def testConstructorInputs(userID: int, name: str, email: str):
	p = Participant(userID, name, email)
	assert p.userID == userID
	assert p.name == name
	assert p.email == email


@pytest.mark.parametrize(
		"userID, expected", 
		[
			("1", "userID must be an integer"),
			(1.0, "userID must be an integer"),
			(True, "userID must be an integer"),
			(-1, "userID must be non-negative"),
			(None, "userID cannot be null"),
		]
	)
def testInvalidUserID(userID, expected):
	with pytest.raises(AssertionError, match=f"^{expected}"):
		Participant(userID, "Alice", "alice@example.com")


@pytest.mark.parametrize(
		"name, expected", 
		[
			("", "Cannot have blank name"),
			("\t\n\r", "Cannot have blank name"),
			(1.0, "name must be a string"),
			(True, "name must be a string"),
			(-1, "name must be a string"),
			(None, "name cannot be null"),
		]
	)
def testInvalidName(name, expected):
	with pytest.raises(AssertionError, match=f"^{expected}"):
		Participant(1, name, "example@example.com")


@pytest.mark.parametrize(
		"email, expected", 
		[
			("", "Cannot have blank email"),
			("\t\n\r ", "Cannot have blank email"),
			(1.0, "email must be a string"),
			(True, "email must be a string"),
			(-1, "email must be a string"),
			(None, "email cannot be null"),
		]
	)
def testInvalidEmail(email, expected):
	with pytest.raises(AssertionError, match=f"^{expected}"):
		Participant(1, "John Doe", email)


def testParticipantEquality():
	a = Participant(1, "John Smith", "john.smith@email.com")
	b = Participant(2, "John Smith", "john.smith@email.com")
	c = Participant(3, "Nicholas Paul Christie", "nchri@mtroyal.ca")

	assert a == b
	assert a != c
	assert a != object()



