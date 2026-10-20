from flask import Flask, request, jsonify
#from db import get_db
from mock_db import get_db, add_event
from datetime import datetime

app = Flask(__name__)

@app.post("/api/v1/events")
def createEvent():
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    date = body.get("date")
    time = body.get("time")
    capacity = body.get("capacity")
    location = body.get("location")

    error_response = checkReqs(name, date, time, capacity, location)
    if error_response: 
        return error_response

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute (
        """
        INSERT INTO events(name, date, time, capacity, location) 
        VALUES (%s, %s, %s, %s, %s)
        """,
        (str(name).strip(), date, time, capacity, str(location).strip()),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    event = {
		"id":  new_id,
        "name" : str(name).strip(),
        "date":	date,
        "time": time,
        "capacity": capacity,
        "location": location,
    }
	
    return jsonify({"data": event}), 201
    

@app.get("/api/v1/events")
def listEvents():
    name_query = request.args.get("name")
    db= get_db()
    cursor = db.cursor(dictionary=True)

    if name_query:
        q = f"%{name_query.strip().lower()}%"
        cursor.execute(
            """
            SELECT id, name
            FROM events
            WHERE LOWER(name) LIKE %s
            ORDER BY id
            """,
            (q,),
        )
    else:
        cursor.execute(
            """
            SELECT id, name
            FROM events
            ORDER BY id
            """
        )

    events = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify({"data": events}), 200

@app.get("/api/v1/events/<int:eventID>")
def retrieveEvent(eventID):
    db= get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, name, date, time, capacity, location
        FROM events
	WHERE id = %s
        """,
        (eventID,),
    )
    row = cursor.fetchone()
    cursor.close()
    db.close()

    if row is None:
        return jsonify({"error": f"No event found with id {eventID}"}), 404

    return jsonify({"data": row}), 200

@app.delete("/api/v1/events/<int:eventID>")
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
        DELETE FROM events
        WHERE id = %s
        """,
        (eventID,),
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "message": f"Event {eventID} successfully deleted"
    }), 200

@app.put("/api/v1/events/<int:eventID>")
def updateEvent(eventID):
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    date = body.get("date")
    time = body.get("time")
    capacity = body.get("capacity")
    location = body.get("location")

    #check to see if the input is correct
    error_response = checkReqs(name, date, time, capacity, location)
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
        SET name = %s, date = %s, location = %s, time = %s, capacity = %s
        WHERE id = %s
        """,
        (str(name).strip(), date, str(location).strip(), time, capacity, eventID)
    )

    db.commit()
    cursor.close()
    db.close() 

    updated_event = {
        "id": eventID,
        "name": str(name).strip(),
        "date": date,
        "time": time,
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
        SELECT id
        FROM events
        WHERE id = %s
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
        WHERE event_id = %s
        """,
        (eventID,)
    )

    count_row = cursor.fetchone()
    current_count = count_row["current_registrations"]

    if capacity < current_count:
        cursor.close()
        db.close() 
        return jsonify({"error": "changing amount lower than registered amount"}),400

    cursor.close()
    db.close()
    return None   


def checkReqs(name, date, time, capacity, location):
    if not name or not str(name).strip():
        return jsonify({"error": "name is required"}),400

    if not location or not str(location).strip():
            return jsonify({"error": "location is required"}),400

    if type(capacity) is int:
        if capacity <= 0:
            return jsonify({"error": "capacity has to be a positive integer"}),400

    else:
        return jsonify({"error": "capacity must be an integer"}), 400

    #checks if date is the right format
    try:
        datetime.strptime(date, "%m/%d/%Y")

    except ValueError:
        return jsonify({"error": "wrong date format (MM/DD/YYYY)"}),400

    #checks if time is in the right format
    try:
        datetime.strptime(time, "%H:%M")

    except ValueError:
        return jsonify({"error": "wrong time format (XX:XX)"}), 400

    #checks if the start time is in the future
    try:
        event_datetime_str = f"{date} {time}"
        event_datetime = datetime.strptime(event_datetime_str, "%m/%d/%Y %H:%M" )

        if event_datetime < datetime.now():
            return jsonify({"error": "start time must be in the future"}), 400

    except ValueError:
        return jsonify({"error": "wrong date or time format"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
