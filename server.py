from flask import Flask, request, jsonify, send_file
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)

# --- File to store all data ---
EXCEL_FILE = "adxl_all_data.xlsx"

# --- Latest sensor reading ---
latest_data = {"status": "No Data", "time": "", "x": "error", "y": "error", "z": "error"}

# Ensure Excel file exists
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["time", "x", "y", "z", "status"])
    df.to_excel(EXCEL_FILE, index=False)

# -------------------- Routes --------------------

@app.route("/adxl_data", methods=["POST"])
def adxl_data():
    global latest_data
    data = request.json
    x, y, z = data.get("x"), data.get("y"), data.get("z")
    status = data.get("status", "")

    # Update latest_data for /live
    latest_data = {
        "status": "ok",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "x": x,
        "y": y,
        "z": z
    }

    # Save all data to Excel
    df_new = pd.DataFrame([{
        "time": latest_data["time"],
        "x": x,
        "y": y,
        "z": z,
        "status": status
    }])

    if os.path.exists(EXCEL_FILE):
        df_old = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_excel(EXCEL_FILE, index=False)

    return jsonify({"status": "OK"})


@app.route("/live", methods=["GET"])
def live():
    return jsonify(latest_data)


@app.route("/download", methods=["GET"])
def download():
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True)
    else:
        return "No Excel file yet", 404


@app.route("/reset_excel", methods=["POST"])
def reset_excel():
    df = pd.DataFrame(columns=["time", "x", "y", "z", "status"])
    df.to_excel(EXCEL_FILE, index=False)
    return jsonify({"status": "Excel reset done"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)