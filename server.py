from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # allow cross-origin requests for Flutter Web

# Store latest sensor data
latest_data = {"x": 0, "y": 0, "z": 0, "status": "No Data", "time": ""}

# Store events (Hit/Scratch)
events = []

# Excel file path
EXCEL_FILE = "sensor_events.xlsx"

hit_threshold = 15.0
scratch_threshold = 7.0

# --- Route to get live sensor data ---
@app.route("/live", methods=["GET"])
def get_live():
    return jsonify(latest_data)

# --- Route to push sensor data ---
@app.route("/adxl_data", methods=["POST"])
def push_data():
    global latest_data, events
    data = request.get_json()
    x = float(data.get("x", 0))
    y = float(data.get("y", 0))
    z = float(data.get("z", 0))
    status = data.get("status", "ok")
    now = datetime.now()
    latest_data = {"x": x, "y": y, "z": z, "status": status, "time": now.strftime("%Y-%m-%d %H:%M:%S")}

    # Check if Hit or Scratch
    absX, absY, absZ = abs(x), abs(y), abs(z)
    event_type = None
    if absX > hit_threshold or absY > hit_threshold or absZ > hit_threshold:
        event_type = "Hit"
    elif absX > scratch_threshold or absY > scratch_threshold or absZ > scratch_threshold:
        event_type = "Scratch"

    if event_type:
        event_entry = {
            "time": now.strftime("%H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "x": x, "y": y, "z": z,
            "type": event_type
        }
        events.append(event_entry)
        save_to_excel()
    return jsonify({"status": "OK"})

# --- Route to get all events ---
@app.route("/events", methods=["GET"])
def get_events():
    return jsonify(events[::-1])  # newest first

# --- Route to download Excel file ---
@app.route("/download", methods=["GET"])
def download_excel():
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True)
    else:
        return jsonify({"status": "No Excel file"}), 404

# --- Helper function to save events to Excel ---
def save_to_excel():
    df = pd.DataFrame(events)
    df.to_excel(EXCEL_FILE, index=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)