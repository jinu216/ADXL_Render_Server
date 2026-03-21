from flask import Flask, request, jsonify
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)

# --- Thresholds ---
HIT_THRESHOLD = 15.0
SCRATCH_THRESHOLD = 7.0

# --- File to store events ---
EXCEL_FILE = "adxl_events.xlsx"

# --- Latest sensor reading ---
latest_data = {"status": "No Data", "time": "", "x": "error", "y": "error", "z": "error"}

# Ensure Excel file exists
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["type", "time", "x", "y", "z"])
    df.to_excel(EXCEL_FILE, index=False)

# -------------------- Routes --------------------

@app.route("/adxl_data", methods=["POST"])
def adxl_data():
    global latest_data
    data = request.json
    x, y, z = data.get("x"), data.get("y"), data.get("z")

    # Update latest_data for live display
    latest_data = {
        "status": "ok",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "x": x,
        "y": y,
        "z": z
    }

    # Determine event type
    event_type = None
    if any(abs(val) > HIT_THRESHOLD for val in [x, y, z]):
        event_type = "Hit"
    elif any(abs(val) > SCRATCH_THRESHOLD for val in [x, y, z]):
        event_type = "Scratch"

    # Save to Excel if Hit or Scratch
    if event_type:
        df_new = pd.DataFrame([{
            "type": event_type,
            "time": latest_data["time"],
            "x": x,
            "y": y,
            "z": z
        }])
        if os.path.exists(EXCEL_FILE):
            df_old = pd.read_excel(EXCEL_FILE)
            df = pd.concat([df_new, df_old], ignore_index=True)
        else:
            df = df_new
        # Keep only last 50 events
        df = df.head(50)
        df.to_excel(EXCEL_FILE, index=False)

    return jsonify({"status": "OK"})


@app.route("/live", methods=["GET"])
def live():
    return jsonify(latest_data)


@app.route("/events", methods=["GET"])
def events():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        return jsonify(df.to_dict(orient="records"))
    else:
        return jsonify([])


@app.route("/reset_events", methods=["POST"])
def reset_events():
    # Delete Excel content
    df = pd.DataFrame(columns=["type", "time", "x", "y", "z"])
    df.to_excel(EXCEL_FILE, index=False)
    return jsonify({"status": "Reset Done"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)