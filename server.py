from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ------------------------
# Storage (in-memory for now)
# ------------------------
# For live sensor values
live_data = {"x": "error", "y": "error", "z": "error", "status": "No Data", "time": ""}

# Event history (scratches, hits)
events_history = []  # List of dicts: {"x":..., "y":..., "z":..., "status":..., "time":...}

# ------------------------
# Route: ESP32 sends data here
# ------------------------
@app.route('/adxl_data', methods=['POST'])
def receive_adxl():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON received"}), 400

    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["time"] = timestamp

    # Save live data
    live_data.update(data)

    # Add to event history if status is hit/error
    if data.get("status") != "ok":
        events_history.append(data)

    print("📥 Received from ESP32:", data)
    return jsonify({"status": "OK"}), 200

# ------------------------
# Route: Return live sensor data
# ------------------------
@app.route('/live', methods=['GET'])
def get_live():
    return jsonify(live_data)

# ------------------------
# Route: Return event history
# ------------------------
@app.route('/events', methods=['GET'])
def get_events():
    return jsonify(events_history)

# ------------------------
# Health check route
# ------------------------
@app.route('/', methods=['GET'])
def home():
    return "SafePark Server is running!"

# ------------------------
# Run server (Render requires dynamic PORT)
# ------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)