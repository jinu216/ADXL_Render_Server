from flask import Flask, request, jsonify

app = Flask(__name__)

# Store data from ESP32
esp_data = {}

@app.route('/')
def home():
    return "Server is running. Use /data/<device_id> to send or get sensor data."

# Endpoint for ESP32 to send data
@app.route('/data/<device_id>', methods=['POST'])
def receive_data(device_id):
    global esp_data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    esp_data[device_id] = data
    return jsonify({"status": "success"}), 200

# Endpoint for webpage to fetch latest data
@app.route('/data/<device_id>', methods=['GET'])
def send_data(device_id):
    if device_id in esp_data:
        return jsonify(esp_data[device_id])
    else:
        return jsonify({"error": "No data for this device"}), 404

if __name__ == '__main__':
    app.run(debug=True)