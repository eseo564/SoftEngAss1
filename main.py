from flask import Flask, request, jsonify
from db import get_db
from Event import event_bp
#from Registration import reg_bp
from Participant import participant_bp

app = Flask(__name__)

app.register_blueprint(event_bp)
#app.register_blueprint(reg_bp)
app.register_blueprint(participant_bp)

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
