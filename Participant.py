from flask import Flask, request, jsonify
from db import get_db
import re

participant_bp = Flask(__name__)

"""
Helper functions
"""
def participantExists(userID: int, db) -> bool:
	cursor = db.cursor(dictionary=True)
	cursor.execute(
		"SELECT userID FROM participants WHERE userID = %s",
		(userID,),
	)
	row = cursor.fetchone()
	cursor.close()
	return row is not None

def participantExists2(name: str, email: str, db) -> bool:
	cursor = db.cursor(dictionary=True)
	cursor.execute(
		"""
		SELECT name, email
		FROM participants
		WHERE name = %s AND email = %s""",
		(name, email),
	)
	row = cursor.fetchone()
	cursor.close()
	return row is not None


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

	db = get_db()

	## Validate Participant's name/email
	response = checkParticipant(name, email)
	if (response):
		return response

	if participantExists2(name, email, db):
		return jsonify({"error": f"Participant with name '{name}' and email '{email}' already exists"}), 409

	cursor = db.cursor(dictionary=True)
	cursor.execute(
		"""
		INSERT INTO participants (name, email)
		VALUES (%s, %s)
		""",
		(name, email,),
	)
	db.commit()

	## Fetch newly inserted row for return
	newID = cursor.lastrowid
	cursor.execute(
		"""
		SELECT registrationID, eventID, userID, currentTime AS registeredAt
		FROM registrations
		WHERE registrationID = %s
		""",
		(newID,),
	)
	row = cursor.fetchone()
	cursor.close()
	db.close()
	
	return jsonify({"data": row}), 201

@participant_bp.get("/api/v1/participants")
def listParticipants():
	db = get_db()
	cursor = db.cursor(dictionary=True)
	cursor.execute(
		"""
		SELECT userID, name, email AS people
		FROM participants
		ORDER BY userID
		"""
	)
	rows = cursor.fetchall()
	cursor.close()
	db.close()
	
	return jsonify({"data": rows}), 200

@participant_bp.get("/api/v1/participants/<int:userID>")
def retrieveParticipant(userID: int):
	db = get_db()
	cursor = db.cursor(dictionary=True)
	cursor.execute(
		"""
		SELECT userID, name, email
		FROM participants
		WHERE userID = %s
		""",
		(userID,),
	)
	row = cursor.fetchone()
	cursor.close()
	db.close()

	if (row is None):
		return jsonify({"error": f"No participant found with id {userID}"}), 404

	return jsonify({"error": row}), 200


@participant_bp.delete("/api/v1/participants/<int:userID>")
def deleteParticipant(userID):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	## CHeck if participant exists
	if (not participantExists(userID, db)):
		cursor.close()
		db.close()
		return jsonify({"error": f"No participant found with id {userID}"}), 404

	cursor.execute(
		"""
		DELETE FROM participants
		WHERE userID = %s
		""",
		(userID,),
	)
	
	db.commit()

	cursor.close()
	db.close()

	return jsonify({
		"message": f"Participant {userID} successfully deleted"
	}), 200

@participant_bp.put("/api/v1/participants/<int:userID>")
def updateParticipant(userID):
	body = request.get_json(silent=True) or {}
	name = body.get("name").strip()
	email = body.get("email").strip()

	## Check if input is correct
	errorResponse = checkParticipant(name, email)
	if (errorResponse):
		return errorResponse

	db = get_db()

	if (participantExists(userID, db)):
		return jsonify({"error": f"Participant not found"}), 404


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
	
	return jsonify({"data": {"userID": userID, "name": name, "email": email}}), 200



if (__name__ == "__main__"):
	participant_bp.run(host="0.0.0.0", port=5000, debug=True)
