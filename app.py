from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/sensors/temperature")
def getTemperature():
    return jsonify({"value": 32.43, "unit": "°C"}), 200

@app.get("/sensors/humidity")
def getHumidity():
    return jsonify({"value": 54, "unit": "%"}), 200
