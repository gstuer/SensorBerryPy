import Adafruit_DHT
from flask import Flask, request, jsonify
import time
import threading

DHT_SENSOR_TYPE = Adafruit_DHT.AM2302
DHT_SENSOR_PIN = 2
DHT_SENSOR_READ_PAUSE = 15

app = Flask(__name__)
readCache = None

def readSensorDHT():
    global readCache
    while True:
        currentTime = time.time()
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, DHT_SENSOR_PIN)
        # Reading the sensor may take a couple of seconds -> Time needs to be refreshed.
        currentTime = time.time()
        if humidity is not None and temperature is not None:
            readCache = (currentTime, humidity, temperature)
        time.sleep(DHT_SENSOR_READ_PAUSE)

@app.route("/sensors/temperature", methods=["GET"])
def getTemperature():
    if readCache is not None:
        timestamp, humidity, temperature = readCache
        return jsonify({"value": temperature, "unit": "°C", "timestamp": timestamp}), 200
    else:
        return jsonify({"error": "Reading sensor failed"}), 500

@app.route("/sensors/humidity", methods=["GET"])
def getHumidity():
    if readCache is not None:
        timestamp, humidity, temperature = readCache
        return jsonify({"value": humidity, "unit": "%RH", "timestamp": timestamp}), 200
    else:
        return jsonify({"error": "Reading sensor failed"}), 500

sensorThreadDHT = threading.Thread(target=readSensorDHT)
sensorThreadDHT.start()
