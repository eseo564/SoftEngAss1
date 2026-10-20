from flask import Flask, request, jsonify
from db import get_db
import Event as api_module
import Registration as api_module
import Participant as api_module

app = Flask(__name__)

@app.get("/api")
def health():
    return (
        jsonify(
            {
                "status": "ok",
                "message": "Event Booking API is running",
            }
        ),
        200,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
