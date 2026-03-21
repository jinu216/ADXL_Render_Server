from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

latest_data = {
    "status": "No Data",
    "time": "",
    "x": "error",
    "y": "error",
    "z": "error"
}

@app.route("/adxl_data", methods=["POST"])
def adxl_data():
    global latest_data
    data = request.get_json(force=True)

    latest_data = {
        "status": data.get("status", "error"),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "x": data.get("x", "error"),
        "y": data.get("y", "error"),
        "z": data.get("z", "error")
    }

    return jsonify({"status": "OK"})

@app.route("/live", methods=["GET"])
def live():
    return jsonify(latest_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 👈 IMPORTANT for Render
    app.run(host="0.0.0.0", port=port)