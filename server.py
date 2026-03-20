from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

latest_data = {}
history = []
events = []

# 🚨 Simple event detection
def detect_event(data):
    try:
        x = float(data["x"])
        y = float(data["y"])
        z = float(data["z"])

        magnitude = (x**2 + y**2 + z**2) ** 0.5

        if magnitude > 15:
            return "HIT"
        elif magnitude > 11:
            return "VIBRATION"
        else:
            return "NORMAL"
    except:
        return "ERROR"


@app.route("/")
def home():
    return "SafePark Server Running!"

# 📥 Receive data from ESP32
@app.route("/adxl_data", methods=["POST"])
def update_data():
    global latest_data, history, events

    data = request.get_json()
    if not data:
        return jsonify({"status": "error"}), 400

    # Add timestamp
    data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Detect event
    event_type = detect_event(data)
    data["event"] = event_type

    latest_data = data
    history.append(data)

    # Save only important events
    if event_type in ["HIT", "VIBRATION"]:
        events.append(data)

    print("📥", data)

    return jsonify({"status": "success"})


# 📡 Latest live data
@app.route("/live", methods=["GET"])
def live():
    return jsonify(latest_data)


# 📜 Full history
@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(history)


# 🚨 Events only
@app.route("/events", methods=["GET"])
def get_events():
    return jsonify(events)


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)