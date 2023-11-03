from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/sensors/temperature", methods=["GET"])
def getTemperature():
    if dhtCache is not None:
        timestamp, humidity, temperature = dhtCache
        return jsonify({"value": temperature, "unit": "°C", "timestamp": timestamp}), 200
    else:
        return jsonify({"error": "Reading sensor failed"}), 500

@app.route("/sensors/humidity", methods=["GET"])
def getHumidity():
    if dhtCache is not None:
        timestamp, humidity, temperature = dhtCache
        return jsonify({"value": humidity, "unit": "%RH", "timestamp": timestamp}), 200
    else:
        return jsonify({"error": "Reading sensor failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
