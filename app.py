import Adafruit_DHT
from flask import Flask, request, jsonify
import time

SENSOR_TYPE = Adafruit_DHT.AM2302
SENSOR_PIN = 2
SENSOR_READ_PAUSE = 15

app = Flask(__name__)
readCache = None

def readSensor():
    cacheTimestamp, cachedHumidity, cachedTemperature = readCache
    currentTime = time.time()
    if cacheTimestamp + SENSOR_READ_PAUSE <= currentTime:
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR_TYPE, SENSOR_PIN)
        if humidity is not None and temperature is not None:
            readCache = (currentTime, humidity, temperature)
    return readCache

@app.get("/sensors/temperature")
def getTemperature():
    measurement = readSensor()
    if measurement is not None:
        timestamp, humidity, temperature = measurement
        return jsonify({"value": temperature, "unit": "°C", "timestamp": timestamp}), 200
    else:
        return {"error": "Reading sensor failed"}, 500

@app.get("/sensors/humidity")
def getHumidity():
    measurement = readSensor()
    if measurement is not None:
        timestamp, humidity, temperature = measurement
        return jsonify({"value": humidity, "unit": "%RH", "timestamp": timestamp}), 200
    else:
        return {"error": "Reading sensor failed"}, 500
