from flask import Blueprint, request, jsonify
from datetime import datetime
from db import get_db

reg_bp = Blueprint("reg_bp", __name__)


def event_exists(eventID: int, db) -> bool:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT eventID FROM events WHERE eventID = %s",
        (eventID,),
    )
    row = cursor.fetchone()
    cursor.close()
    return row is not None


def participant_exists(userID: int, db) -> bool:
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT userID FROM participants WHERE userID = %s",
        (userID,),
    )
    row = cursor.fetchone()
    cursor.close()
    return row is not None


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


@reg_bp.get("/api/v1/registrations")
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


@reg_bp.get("/api/v1/registrations/<int:registrationID>")
def getRegistration(registrationID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT registrationID, eventID, userID, currentTime AS registeredAt
        FROM registrations
        WHERE registrationID = %s
        """,
        (registrationID,),
    )
    row = cursor.fetchone()
    cursor.close()
    db.close()

    if row is None:
        return jsonify({"error": "Registration does not exist"}), 404

    if row.get("registeredAt") and hasattr(row["registeredAt"], "strftime"):
        row["registeredAt"] = row["registeredAt"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({"data": row}), 200


@reg_bp.post("/api/v1/registrations")
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
    cursor.execute(
        """
        INSERT INTO registrations (eventID, userID)
        VALUES (%s, %s)
        """,
        (eventID, userID),
    )
    db.commit()
    new_id = cursor.lastrowid

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


@reg_bp.delete("/api/v1/registrations/<int:registrationID>")
def cancelRegistration(registrationID):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Check it exists first
    cursor.execute(
        "SELECT registrationID FROM registrations WHERE registrationID = %s",
        (registrationID,),
    )
    row = cursor.fetchone()
    if row is None:
        cursor.close()
        db.close()
        return jsonify({"error": "Registration does not exist"}), 404

    cursor.execute(
        "DELETE FROM registrations WHERE registrationID = %s",
        (registrationID,),
    )
    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Registration successfully canceled"}), 200
