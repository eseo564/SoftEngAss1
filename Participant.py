from flask import Blueprint, request, jsonify
import json
import re

participant_bp = Blueprint('participant_bp', __name__)

class Participant:
	__slots__ = ("userID", "name", "email")
	
	def __init__(self, userID: int, name: str, email: str):
		## Validate userID
		assert userID is not None, "userID cannot be null"
		assert isinstance(userID, int), "userID must be an integer"
		assert userID >= 0, "userID must be non-negative"

		## Validate name
		assert name is not None, "name cannot be null"
		assert isinstance(name, str), "name must be a string"
		assert len(name.strip()) > 0, "Cannot have blank name"

		## Validate email
		assert email is not None, "email cannot be null"
		assert isinstance(email, str), "email must be a string"
		assert len(email.strip()) > 0, "Cannot have blank email"
		
		pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
		#pattern = r"^[A-Za-z0-9._%+-]+@mtroyal.ca$"
		assert bool(re.match(pattern, email)), f"Invalid email format"
		
		## Setup participant identifiers
		self.userID = userID
		self.name = name.strip()
		self.email = email.strip()

	## Checks if 2 Participant classes are equal
	def __eq__(self, other: "Participant"):
		if (not isinstance(other, Participant)):
			return NotImplemented
		
		return (self.name == other.name and self.email == other.email)

	def __str__(self):
		return f"userID: {self.userID}\nName:	{self.name}\nEmail:   {self.email}"

	def __repr__(self):
		return f"Participant({self.userID}, '{self.name}', '{self.email}')"

	def toDict(self) -> dict:
		return {
			"userID": self.userID,
			"name": self.name,
			"email": self.email
		}

"""
Helper functions
"""
def loadParticipantDatabase() -> list[Participant]:
	try:
		with open("ParticipantDatabase.json", 'r') as database:
			people = json.load(database)
	except Exception as e:
		print(e)
		people = []

	return [
		Participant(
			p["userID"],
			p["name"],
			p["email"]
		)
		for p in people
	]

def saveParticipantDatabase(participants: list[Participant]):
	with open("ParticipantDatabase.json", 'w') as database:
		json.dump(
			[p.toDict() for p in participants],
			database,
			indent=4
		)


def participantExists(userID: int, participants: list[Participant]) -> bool:
	for p in participants:
		if (p.userID == userID):
			return True
	return False


def checkParticipant(name: str, email: str) -> bool:
	if (not isinstance(name, str)):
		return jsonify({"error": "name must be a string"}), 400
	if (len(name.strip()) == 0):
		return jsonify({"error": "name is required"}), 400

	## Check for valid email
	if (not isinstance(email, str)):
		return jsonify({"error": "email must be a string"}), 400
	if (len(email.strip()) == 0):
		return jsonify({"error": "email is required"}), 400
	pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
	if (not bool(re.match(pattern, email))):
		return jsonify({"error": "Invalid email format"}), 400

	return None


"""
Database functions
"""
@participant_bp.post("/api/v1/participants")
def createParticipant():
	body = request.get_json(silent=True) or {}
	
	name = body.get("name")
	email = body.get("email")

	## Validate Participant's name/email
	response = checkParticipant(name, email)
	if (response):
		return response

	participants = loadParticipantDatabase()

	## Check for existance of new participant
	for p in participants:
		if (p.name == name and p.email == email):
			return jsonify({
				"error": "Participant already exists"
			}), 409
	
	## Generate participant id
	newUserID = 1
	for p in participants:
		if (p.userID >= newUserID):
			newUserID = p.userID + 1
	
	newParticipant = Participant(
		newUserID,
		name,
		email
	)
	participants.append(newParticipant)
	saveParticipantDatabase(participants)
	
	return jsonify({"data": newParticipant.toDict()}), 201

@participant_bp.get("/api/v1/participants")
def listParticipants():
	participants = loadParticipantDatabase()
	
	return jsonify({
		"data": [
			p.toDict()
			for p in participants
		]
	}), 200

@participant_bp.get("/api/v1/participants/<int:userID>")
def retrieveParticipant(userID: int):
	participants = loadParticipantDatabase()
	for p in participants:
		if (p.userID == userID):
			return jsonify({"data": p.toDict()}), 200

	return jsonify({"error": f"No participant found with id {userID}"}), 404


@participant_bp.delete("/api/v1/participants/<int:userID>")
def deleteParticipant(userID):
	participants = loadParticipantDatabase()
	if (not participantExists(userID, participants)):
		return jsonify({"error": f"No participant found with id {userID}"}), 404

	# Finish me

@participant_bp.put("/api/v1/participants/<int:userID>")
def updateParticipant(userID):
	body = request.get_json(silent=True) or {}
	userID = body.get("userID")
	name = body.get("name").strip()
	email = body.get("email").strip()

	## Check if input is correct
	errorResponse = checkParticipant(name, email)
	if (errorResponse):
		return errorResponse

	participants = loadParticipantDatabase()

	## Find participant
	participant = None
	for p in participants:
		if (p.userID == userID):
			participant = p
			break

	if (participant is None):
		return jsonify({"error": f"No participant found with id {userID}"}), 404

	## Check for duplicate participants
	for p in participants:
		if (p == participant and p.userID != participant.userID):
			return jsonify({"error": "Participant already exists"}), 409

	## Create and save updated participant
	updatedParticipant = Participant(
		userID,
		name,
		email
	)

	idx = participants.index(participant)
	participants[idx] = updatedParticipant
	saveParticipantDatabase(participants)
	
	return jsonify({"data": updatedParticipant.toDict()}), 200



#if (__name__ == "__main__"):
#	try:
#		db = loadParticipantDatabase()
#	except Exception as e:
#		print(e)
#		input()
