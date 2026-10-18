from flask import Flask, request, jsonify
import json
import re

app = Flask(__name__)


class Participant:
	__slots__ = ("userID", "name", "email")
	
	def __init__(self, userID: int, name: str, email: str):
		## Validate userID
		assert isinstance(userID, int), "userID must be an integer"
		assert userID >= 0, "userID must be non-negative"

		## Validate name
		assert isinstance(name, str), "name must be a string"
		assert len(name.strip()) > 0, "Cannot have blank name"

		## Validate email
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
		
		return (
			self.name == other.name 
			and self.email == other.email
		)

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
		print(e, flush=True)
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


def participantChecker(name: str, email: str) -> bool:
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
		return jsonify({"error": "Invalid email format"})


"""
Database functions
"""
@app.post("/api/v1/participants")
def createParticipant():
	body = request.get_json(silent=True) or {}
	
	name = body.get("name")
	email = body.get("email")

	## Validate Participant's name/email
	response = participantChecker(name, email)
	if (response):
		return response

	participants = loadParticipantDatabase()
	userID = 0
	while (participantExists(userID, participants)):
		userID += 1
	newParticipant = Participant(
		userID=userID,
		name=name,
		email=email
	)
	
	participants.append(newParticipant)
	saveParticipantDatabase(participants)
	
	return jsonify({"data": newParticipant.toDict()}), 201

@app.get("/api/v1/participants")
def listParticipants():
	participants = loadParticipantDatabase()
	return jsonify({
		"data": [
			p.toDict()
			for p in participants
		]
	}), 200

@app.get("/api/v1/participants/<int:userID>")
def retrieveParticipant(userID: int):
	db = get_db()
	cursor = db.sursor(dictionary=True)
	cursor.execute(
		"""
		SELECT userID, name, email
		WHERE userID = %s
		FROM participants
		""",
		(userID,),
	)

@app.delete("/api/v1/participants/<int:userID>")
def deleteParticipant(userID):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	# check to see if the event exists
	dbParticiapntResponse = participantExists(userID, db) 
	if (dbParticiapntResponse):
		cursor.close()
		db.close()
		return dbParticiapntResponse

	cursor.execute(
		"""
		DELETE FROM participants
		WHERE userID = %s
		""",
		(userID,),
	)

	db.commit()

	row = cursor.fetchone()
	cursor.close()

	if (row is None):
		return jsonify({
			"error": f"No participant found with id {userID}"
		}), 404

	return None

@app.put("/api/v1/participants/<int:userID>")
def updateParticipant(userID):
	body = request.get_json(silent=True) or {}
	userID = body.get("userID")
	name = body.get("name")
	email = body.get("email")

	## Check if input is correct
	errorResponse = participantChecker(name, email)
	if (errorResponse):
		return errorResponse

	db = get_db()
	
	## Check if participant exists
	dbParticipantResponse = participantExists(userID, db)
	if (dbParticipantResponse):
		return dbParticipantResponse

	cursor = db.cursor(dictionary=True)
	cursor.execute(
		"""
		UPDATE participants
		SET name = %s, email = %s
		WHERE userID = %s
		""",
		(str(name).strip(), str(email).strip(), userID)
	)

	db.commit()
	cursor.close()
	db.close() 

	updatedParticipant = {
		"userID": userID,
		"name": str(name).strip(),
		"email": str(email).strip(),
	}
	
	return jsonify({"data": updatedParticipant}), 200



if (__name__ == "__main__"):
	try:
		db = loadParticipantDatabase()
	except Exception as e:
		print(e)
		input()
