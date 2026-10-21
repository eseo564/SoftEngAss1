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
			(0, "John Smith", "john.smith@email.co.uk"), ## Tests userID valid low end
			(1000000, "John Smith", "john.smith@example.com"), ## Tests high userID
			(1, " John Smith\t\r\v\n ", "john.smith@email.com"), ## Tests name with whitespace
			(1, "John Smith ", "\t\n john.smith@email.com\r\v"), ## Tests email with whitespace
			(1, "John Smith", "john.smith@email.com"), ## Tests 'normal' user creation
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
			(-1, "userID must be non-negative"), ## Tests userID negative integer input
			("1", "userID must be an integer"), ## Tests userID string input
			(1.0, "userID must be an integer"), ## Tests userID float input
			(True, "userID must be an integer"), ## Tests userID boolean input
			(None, "userID cannot be null"),  ## Tests userID null input
		]
	)
def testInvalidUserID(userID, expected):
	with pytest.raises(AssertionError, match=f"^{expected}"):
		Participant(userID, "Alice", "alice@example.com")


@pytest.mark.parametrize(
		"name, expected", 
		[
			("", "Cannot have blank name"), ## Tests empty name input
			("\t\n\r", "Cannot have blank name"), ## Tests name with (only) whitespace input
			(1.0, "name must be a string"), ## Tests name float input
			(True, "name must be a string"), ## Tests name boolean input
			(-1, "name must be a string"), ## Tests name integer input
			(None, "name cannot be null"), ## Tests name null input
		]
	)
def testInvalidName(name, expected):
	with pytest.raises(AssertionError, match=f"^{expected}"):
		Participant(1, name, "example@example.com")


@pytest.mark.parametrize(
		"email, expected", 
		[
			("", "Cannot have blank email"), ## Tests empty email input
			("\t\n\r ", "Cannot have blank email"), ## Tests email with (only) whitespace input
			(1.0, "email must be a string"), ## Tests email float input
			(True, "email must be a string"), ## Tests email boolean input
			(-1, "email must be a string"), ## Tests email integer input
			(None, "email cannot be null"), ## Tests email null input
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



