from flask import Flask, request, jsonify

app = Flask(__name__)

# Store latest data from each ESP32
device_data = {}

# ESP32 sends data here
@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    device_id = data.get("id", "unknown")  # ESP32 must send an ID
    device_data[device_id] = data
    return "OK", 200

# Browser can view latest data here
@app.route('/data/<device_id>')
def get_device_data(device_id):
    return jsonify(device_data.get(device_id, {}))

# Simple test page
@app.route('/')
def index():
    return "Server is running. Use /data/<device_id> to see sensor data."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)