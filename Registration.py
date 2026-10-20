from flask import Flask, request, jsonify
from datetime import datetime
from db import get_db
import json

app = Flask(__name__)


#declaring INSTANCES (unique copies, not global variables) 
class Registration:
    __slots__ = ("registrationID", "eventID", "userID", "registeredAt")

    def __init__(
        self,
        registrationID: int,
        eventID: int,
        userID: int,
        registeredAt: str
    ):

	#isinstance checks if they are ints
        #len + .strip() checks date isn't empty or whitespace
        assert isinstance(registrationID, int), "Invalid registrationID"
        assert isinstance(eventID, int), "Invalid eventID"
        assert isinstance(userID, int), "Invalid userID"
        assert len(registeredAt.strip()) > 0, "Invalid registration date"

        self.registrationID = registrationID
        self.eventID = eventID
        self.userID = userID
        self.registeredAt = registeredAt

    #checks if you are comparing between Registration class to begin with
    def __eq__(self, other: "Registration"):
        if not isinstance(other, Registration):
            return NotImplemented

        return (
            self.eventID == other.eventID
            and self.userID == other.userID
        )

    def toDict(self):
        return {
            "registrationID": self.registrationID,
            "eventID": self.eventID,
            "userID": self.userID,
            "registeredAt": self.registeredAt
        }


# Helper functions
#reads registration data from a JSON file, converts to list of Registration objects
def loadDatabase():
    try:
        with open("RegistrationDatabase.json", "r") as database:
            registrations = json.load(database)
    except FileNotFoundError:
        registrations = []

    return [
        Registration(
            registration["registrationID"],
            registration["eventID"],
            registration["userID"],
            registration["registeredAt"]
        )
        for registration in registrations
    ]


def saveDatabase(registrations):
    with open("RegistrationDatabase.json", "w") as database:
        json.dump(
            [registration.toDict() for registration in registrations],
            database,
            indent=4
        )


def loadEvents():
    try:
        with open("EventDatabase.json", "r") as database:
            return json.load(database)
    except FileNotFoundError:
        return []


def loadParticipants():
    try:
        with open("ParticipantDatabase.json", "r") as database:
            return json.load(database)
    except FileNotFoundError:
        return []

#1 check if an event ID exists
def eventExists(eventID: int, events: list) -> bool:
    for event in events:
        if event["eventID"] == eventID:
            return True
    return False

# not handing in right list handing list of participants when it should be list of registration
#2 check if a participant ID exists
def participantExists(id: int, participants: list) -> bool:
    for participant in participants:

        if participant["id"] == userID:
            return True
    return False

#3 check if a registration is allowed
def registrationChecker(
    eventID: int,
    registrations: list,
    events: list,
    currentTime: datetime
) -> bool:

    event = None

    for e in events:
        if e["eventID"] == eventID:
            event = e
            break

    if event is None:
        return False

    count = 0

    for registration in registrations:
        if registration.eventID == eventID:
            count += 1

    if count >= event["capacity"]:
        return False

    try:
        startTime = datetime.strptime(
            event["startTime"],
            "%Y-%m-%d %H:%M"
        )
    except (ValueError, TypeError, KeyError):
        return False

    if startTime <= currentTime:
        return False

    return True

#4 check whether a registration ID already exists
def registrationExists(
    registrationID: int,
    registrations: list
) -> bool:

    for registration in registrations:
        if registration.registrationID == registrationID:
            return True

    return False

#5 check whether a time is in the future
def timeValid(time: str, currentTime: str) -> bool:
    return time > currentTime


# POST: Register a participant for an event
@app.post("/api/v1/registrations")
def registerEvent():
    body = request.get_json(silent=True) or {}

    eventID = body.get("eventID")
    userID = body.get("userID")

    if type(eventID) is not int or eventID <= 0:
        return jsonify({"error": "eventID must be a positive integer"}), 400

    if type(userID) is not int or userID <= 0:
        return jsonify({"error": "userID must be a positive integer"}), 400

    registrations = loadDatabase()
    events = loadEvents()
    participants = loadParticipants()

    if not eventExists(eventID, events):
        return jsonify({"error": "Event does not exist"}), 404

    if not participantExists(userID, participants):
        return jsonify({"error": "Participant does not exist"}), 404

    for registration in registrations:
        if (
            registration.eventID == eventID
            and registration.userID == userID
        ):
            return jsonify({
                "error": "Participant already registered!"
            }), 409

    currentTime = datetime.now()

    if not registrationChecker(
        eventID, registrations, events, currentTime
    ):
        return jsonify({
            "error": "Event is full or has already started"
        }), 400

    registrationID = 1

    for registration in registrations:
        if registration.registrationID >= registrationID:
            registrationID = registration.registrationID + 1

    newRegistration = Registration(
        registrationID,
        eventID,
        userID,
        currentTime.strftime("%Y-%m-%d %H:%M:%S")
    )

    registrations.append(newRegistration)
    saveDatabase(registrations)

    return jsonify({"data": newRegistration.toDict()}), 201


# GET: List all registrations
@app.get("/api/v1/registrations")
def listRegistrations():
    registrations = loadDatabase()

    return jsonify({
        "data": [
            registration.toDict()
            for registration in registrations
        ]
    }), 200


# DELETE: Cancel a participant's registration
@app.delete("/api/v1/registrations/<int:eventID>/<int:userID>")
def cancelRegistration(eventID, userID):
    registrations = loadDatabase()
    events = loadEvents()
    participants = loadParticipants()

    if not eventExists(eventID, events):
        return jsonify({"error": "Event does not exist"}), 404

    if not participantExists(userID, participants):
        return jsonify({"error": "Participant does not exist"}), 404

    for registration in registrations:
        if (
            registration.eventID == eventID
            and registration.userID == userID
        ):
            registrations.remove(registration)
            saveDatabase(registrations)

            return jsonify({
                "message": "Registration successfully canceled"
            }), 200

    return jsonify({
        "error": "Registration does not exist"
    }), 404


# GET: List participants registered for an event
@app.get("/api/v1/registrations/events/<int:eventID>/participants")
def listEventParticipants(eventID):
    events = loadEvents()
    participants = loadParticipants()
    registrations = loadDatabase()

    if not eventExists(eventID, events):
        return jsonify({"error": "Event does not exist"}), 404

    result = []

    for registration in registrations:
        if registration["eventID"] == eventID:
            for participant in participants:
                if participant["id"] == registration["userID"]:
                    result.append(participant)
                    break

    return jsonify({"data": result}), 200


#if __name__ == "__main__":
    #print(participantExists(1, [Registration(1,1,1,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]))
#    app.run(host="0.0.0.0", port=5000, debug=True)
