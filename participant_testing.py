from Participant import *
import pytest



"""
TESTS:
1) Valid constructor input
  - "Normal" id/name/email
2) Test userID
  - "1"  -> string input (fail)
  - 1.5  -> floating point input (fail)
  - True -> boolean input (fail)
  - -1   -> negative integer (fail)
  - 0    -> Pass
  - 6969 -> Pass
3) Test name inputs
  - "" -> Empty name (Assertion error)
  - " "  -> whitespace name (fail)
  - "\t\n" -> whitespace name (fail)
  - " Patrick\t\r\v" -> valid name with whitespace (Pass)
4) Test email inputs
  - "" -> empty email (Assertion error)
  - " "  -> whitespace email (fail)
  - "\t\n" -> whitespace email (fail)
  - "nchri421@mtroyal.ca\t\r\v\n\n" -> valid email with whitespace
"""

def makeParticipant(userID, name, email):
	return Participant(userID, name, email)



def testConstructorInputs(userID: int, name: str, email: str):
	p = Participant(userID, name, email)
	assert p.userID == userID
	assert p.name == name
	assert p.email == email


@pytest.mark.parametrize("user_id", ["1", 1.5, None, True, 0, 69])
def test_constructor_rejects_non_integer_user_id(user_id):
	with pytest.raises(AssertionError, match="Invalid userID"):
		Participant(user_id, "Alice", "alice@example.com")

@pytest.mark.parametrize("user_id", [0, -1])
def test_constructor_integer_id_boundary_behavior(user_id):
	participant = makeParticipant(userID=user_id)
	assert participant.userID == user_id

