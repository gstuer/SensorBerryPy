import Adafruit_DHT
from flask import Flask, request, jsonify
import time

SENSOR_TYPE = Adafruit_DHT.AM2302
SENSOR_PIN = 2
SENSOR_READ_PAUSE = 15

app = Flask(__name__)
readCache = None

def readSensor():
    global readCache
    if readCache is not None:
        cacheTimestamp, cachedHumidity, cachedTemperature = readCache
    else:
        cacheTimestamp = time.time() - 2 * SENSOR_READ_PAUSE
    currentTime = time.time()
    if cacheTimestamp + SENSOR_READ_PAUSE <= currentTime:
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR_TYPE, SENSOR_PIN)
        # Reading the sensor may take a couple of seconds -> Time needs to be refreshed.
        currentTime = time.time()
        if humidity is not None and temperature is not None:
            readCache = (currentTime, humidity, temperature)
    return readCache

@app.route("/sensors/temperature", methods=["GET"])
def getTemperature():
    measurement = readSensor()
    if measurement is not None:
        timestamp, humidity, temperature = measurement
        return jsonify({"value": temperature, "unit": "°C", "timestamp": timestamp}), 200
    else:
        return jsonify({"error": "Reading sensor failed"}), 500

@app.route("/sensors/humidity", methods=["GET"])
def getHumidity():
    measurement = readSensor()
    if measurement is not None:
        timestamp, humidity, temperature = measurement
        return jsonify({"value": humidity, "unit": "%RH", "timestamp": timestamp}), 200
    else:
        return jsonify({"error": "Reading sensor failed"}), 500
