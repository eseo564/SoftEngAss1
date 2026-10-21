from flask import Blueprint, request, jsonify
from datetime import datetime
from db import get_db

<<<<<<< HEAD
reg_bp = Blueprint('reg_bp', __name__)
=======
app = Flask(__name__)

def event_exists(eventID: int, db) -> bool:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT eventID FROM events WHERE eventID = %s",
        (eventID,),
    )
    row = cursor.fetchone()
    cursor.close()
    return row is not None
>>>>>>> 0076aeabd1a2cc964283cc284cd741cbbb811781

def participant_exists(userID: int, db) -> bool:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT userID FROM participants WHERE userID = %s",
        (userID,),
    )
    row = cursor.fetchone()
    cursor.close()
    return row is not None

<<<<<<< HEAD
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
=======
def already_registered(eventID: int, userID: int, db) -> bool:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT registrationID
        FROM registrations
        WHERE eventID = %s AND userID = %s
        """,
        (eventID, userID),
    )
    row = cursor.fetchone()
    cursor.close()
    return row is not None
>>>>>>> 0076aeabd1a2cc964283cc284cd741cbbb811781

def registration_allowed(eventID: int, db) -> bool:
    """
    Returns True if the event exists, is not full, and has not started yet.
    """
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT capacity, startTime
        FROM events
        WHERE eventID = %s
        """,
        (eventID,),
    )
    event = cursor.fetchone()
    if event is None:
        cursor.close()
        return False

    cursor.execute(
        """
        SELECT COUNT(*) AS current_registrations
        FROM registrations
        WHERE eventID = %s
        """,
        (eventID,),
    )
    count_row = cursor.fetchone()
    current_count = count_row["current_registrations"]
    cursor.close()

    if current_count >= event["capacity"]:
        return False

    # startTime comes back as a datetime from the connector
    start_time = event["startTime"]
    if isinstance(start_time, str):
        try:
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            except ValueError:
                return False

    if start_time <= datetime.now():
        return False

    return True

<<<<<<< HEAD
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
@reg_bp.post("/api/v1/registrations")
=======
@app.post("/api/v1/registrations")
>>>>>>> 0076aeabd1a2cc964283cc284cd741cbbb811781
def registerEvent():
    body = request.get_json(silent=True) or {}
    eventID = body.get("eventID")
    userID = body.get("userID")

    if type(eventID) is not int or eventID <= 0:
        return jsonify({"error": "eventID must be a positive integer"}), 400
    if type(userID) is not int or userID <= 0:
        return jsonify({"error": "userID must be a positive integer"}), 400

    db = get_db()

    if not event_exists(eventID, db):
        db.close()
        return jsonify({"error": "Event does not exist"}), 404

    if not participant_exists(userID, db):
        db.close()
        return jsonify({"error": "Participant does not exist"}), 404

    if already_registered(eventID, userID, db):
        db.close()
        return jsonify({"error": "Participant already registered!"}), 409

    if not registration_allowed(eventID, db):
        db.close()
        return jsonify({"error": "Event is full or has already started"}), 400

    cursor = db.cursor(dictionary=True)
    # currentTime has DEFAULT CURRENT_TIMESTAMP, so we can omit it
    # or supply it explicitly – both work
    cursor.execute(
        """
        INSERT INTO registrations (eventID, userID)
        VALUES (%s, %s)
        """,
        (eventID, userID),
    )
    db.commit()
    new_id = cursor.lastrowid

    # fetch the row we just inserted so we can return the real timestamp
    cursor.execute(
        """
        SELECT registrationID, eventID, userID, currentTime AS registeredAt
        FROM registrations
        WHERE registrationID = %s
        """,
        (new_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    db.close()

    if row and hasattr(row["registeredAt"], "strftime"):
        row["registeredAt"] = row["registeredAt"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({"data": row}), 201

<<<<<<< HEAD
# GET: List all registrations
@reg_bp.get("/api/v1/registrations")
=======
@app.get("/api/v1/registrations")
>>>>>>> 0076aeabd1a2cc964283cc284cd741cbbb811781
def listRegistrations():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT registrationID, eventID, userID, currentTime AS registeredAt
        FROM registrations
        ORDER BY registrationID
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    for row in rows:
        if row.get("registeredAt") and hasattr(row["registeredAt"], "strftime"):
            row["registeredAt"] = row["registeredAt"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({"data": rows}), 200

<<<<<<< HEAD
# DELETE: Cancel a participant's registration
@reg_bp.delete("/api/v1/registrations/<int:eventID>/<int:userID>")
=======
@app.delete("/api/v1/registrations/<int:eventID>/<int:userID>")
>>>>>>> 0076aeabd1a2cc964283cc284cd741cbbb811781
def cancelRegistration(eventID, userID):
    db = get_db()

    if not event_exists(eventID, db):
        db.close()
        return jsonify({"error": "Event does not exist"}), 404

    if not participant_exists(userID, db):
        db.close()
        return jsonify({"error": "Participant does not exist"}), 404

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        DELETE FROM registrations
        WHERE eventID = %s AND userID = %s
        """,
        (eventID, userID),
    )
    deleted = cursor.rowcount
    db.commit()
    cursor.close()
    db.close()

    if deleted == 0:
        return jsonify({"error": "Registration does not exist"}), 404

    return jsonify({"message": "Registration successfully canceled"}), 200

<<<<<<< HEAD

# GET: List participants registered for an event
@reg_bp.get("/api/v1/registrations/events/<int:eventID>/participants")
=======
@app.get("/api/v1/registrations/events/<int:eventID>/participants")
>>>>>>> 0076aeabd1a2cc964283cc284cd741cbbb811781
def listEventParticipants(eventID):
    db = get_db()

    if not event_exists(eventID, db):
        db.close()
        return jsonify({"error": "Event does not exist"}), 404

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.userID, p.name, p.email
        FROM participants p
        INNER JOIN registrations r ON p.userID = r.userID
        WHERE r.eventID = %s
        ORDER BY p.userID
        """,
        (eventID,),
    )
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify({"data": rows}), 200

<<<<<<< HEAD
#if __name__ == "__main__":
    #print(participantExists(1, [Registration(1,1,1,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]))
#    app.run(host="0.0.0.0", port=5000, debug=True)
=======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
>>>>>>> 0076aeabd1a2cc964283cc284cd741cbbb811781
