import Adafruit_DHT
from flask import Flask, request, jsonify
import time
import threading

SENSOR_TYPE = Adafruit_DHT.AM2302
SENSOR_PIN = 2
SENSOR_READ_PAUSE = 15

app = Flask(__name__)
readCache = None
readAttempts = list()

def readSensor():
    global readCache
    global readAttempts
    while True:
        currentTime = time.time()
        print("Read attempt at " + str(currentTime) + "...")
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR_TYPE, SENSOR_PIN)
        # Reading the sensor may take a couple of seconds -> Time needs to be refreshed.
        currentTime = time.time()
        print("Finished at " + str(currentTime) + ": ")
        if humidity is not None and temperature is not None:
            print("Successful")
            readCache = (currentTime, humidity, temperature)
        else:
            print("Unsuccessful")
        time.sleep(SENSOR_READ_PAUSE)

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

sensorThread = threading.Thread(target=readSensor)
sensorThread.start()
