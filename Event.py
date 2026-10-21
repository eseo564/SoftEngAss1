from flask import Blueprint, request, jsonify
from db import get_db
from datetime import datetime

event_bp = Blueprint('event_bp', __name__)

# added create
@event_bp.post("/api/v1/events")
def createEvent():
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    startTime = body.get("startTime")
    capacity = body.get("capacity")
    location = body.get("location")

    error_response = checkReqs(name, startTime, capacity, location)
    if error_response:
        return error_response

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute (
        """
        INSERT INTO events (name, startTime, capacity, location)
        VALUES (%s, %s, %s, %s)
        """,
        (str(name).strip(), startTime, capacity, str(location).strip()),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    event = {
        "data": {
	    "eventID": new_id,
            "name" : str(name).strip(),
            "startTime": startTime,
            "capacity": capacity,
            "location": location,
        }
    }

    return jsonify(event), 201

@event_bp.route("/api/v1/events")
#app.get("/api/v1/events")
def listEvents():
    name_query = request.args.get("name")
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if name_query:
        q = f"%{name_query.strip().lower()}%"
        cursor.execute(
            """
            SELECT eventID, name
            FROM events
            WHERE LOWER(name) LIKE %s
            ORDER BY eventID
            """,
            (q,),
        )
    else:
        cursor.execute(
            """
            SELECT eventID, name
            FROM events
            ORDER BY eventID
            """
        )

    events = cursor.fetchall()

    cursor.close()
    db.close()
    return jsonify({"data": events}), 200

@event_bp.get("/api/v1/events/<int:eventID>")
def retrieveEvent(eventID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT eventID, name, startTime, capacity, location
        FROM events
	WHERE eventID = %s
        """,
        (eventID,),
    )
    row = cursor.fetchone()
    cursor.close()
    db.close()

    if row is None:
        return jsonify({"error": f"No event found with id {eventID}"}), 404

    return jsonify({"data": row}), 200

@event_bp.delete("/api/v1/events/<int:eventID>")
def deleteEvent(eventID):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # check to see if the event exists
    db_event_response = checkEvent(eventID, db) 
    if db_event_response:
        cursor.close()
        db.close()
        return db_event_response

    cursor.execute(
        """
        SELECT COUNT(*) AS registration_count
        FROM registrations
        WHERE eventID = %s
        """,
        (eventID,),
    )

    result = cursor.fetchone()

    if result["registration_count"] > 0:
        cursor.close()
        db.close()
        return jsonify({
            "error": "Cannot delete an event with existing registrations"
        }), 400

    cursor.execute(
        """
        DELETE FROM events
        WHERE eventID = %s
        """,
        (eventID,),
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "message": f"Event {eventID} successfully deleted"
    }), 200

@event_bp.put("/api/v1/events/<int:eventID>")
def updateEvent(eventID):
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    startTime = body.get("startTime")
    capacity = body.get("capacity")
    location = body.get("location")

    #check to see if the input is correct
    error_response = checkReqs(name, startTime, capacity, location)
    if error_response:
        return error_response

    db = get_db()

    #check to see if the event exists
    db_event_response = checkEvent(eventID, db)
    if db_event_response:
        return db_event_response

    #check to see capacity changes
    db_capacity_response = checkCapacity(eventID, capacity, db)
    if db_capacity_response:
        return db_capacity_response

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        UPDATE events
        SET name = %s, startTime = %s, capacity = %s, location = %s
        WHERE eventID = %s
        """,
        (str(name).strip(), startTime, capacity, str(location).strip(), eventID)
    )

    db.commit()
    cursor.close()
    db.close()

    updated_event = {
        "eventID": eventID,
        "name": str(name).strip(),
        "startTime": startTime,
        "capacity": capacity,
        "location": str(location).strip(),
    }

    return jsonify({"data": updated_event}), 200

'''Helper functions'''
#gave the db as a parameter to avoid opening and closing the db multiple times
def checkEvent(eventID, db):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT eventID
        FROM events
        WHERE eventID = %s
        """,
        (eventID,),
    )

    row = cursor.fetchone()
    cursor.close()

    if row is None:
        return jsonify({
            "error": f"No event found with id {eventID}"
        }), 404

    return None

def checkCapacity(eventID, capacity, db):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT COUNT(*) AS current_registrations
        FROM registrations
        WHERE eventID = %s
        """,
        (eventID,)
    )

    count_row = cursor.fetchone()
    print (count_row)
    current_count = count_row["current_registrations"]

    if capacity < current_count:
        cursor.close()
        db.close()
        return jsonify({"error": "changing amount lower than registered amount"}),400

    cursor.close()
    return None


def checkReqs(name, startTime, capacity, location):
    if not name or not str(name).strip():
        return jsonify({"error": "name is required"}),400

    if not location or not str(location).strip():
            return jsonify({"error": "location is required"}),400

    if type(capacity) is int:
        if capacity <= 0:
            return jsonify({"error": "capacity has to be a positive integer"}),400

    else:
        return jsonify({"error": "capacity must be an integer"}), 400

    #checks if startTime is the right format

    try:
         time = datetime.strptime(startTime, "%Y/%m/%d %H:%M")

         #checks if the start time is in the future
         if time < datetime.now():
             return jsonify({"error": "start time must be in the future"}), 400

    except ValueError:
        return jsonify({"error": "wrong time format (YYYY/MM/DD XX:XX)"}),400
