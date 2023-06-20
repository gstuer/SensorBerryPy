from flask import Flask, request, jsonify
import time
import threading

# Required for DHT sensor
import Adafruit_DHT

# Required for Adafruit PiOLED
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

DHT_SENSOR_TYPE = Adafruit_DHT.AM2302
DHT_SENSOR_PIN = 18
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

def refreshOLED():
    # SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
    # SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
    # SPDX-License-Identifier: MIT

    global readCache

    # Create the I2C interface.
    i2c = busio.I2C(SCL, SDA)

    # Create the SSD1306 OLED class.
    # The first two parameters are the pixel width and pixel height.  Change these
    # to the right size for your display!
    display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

    # Clear display.
    display.fill(0)
    display.show()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = display.width
    height = display.height
    image = Image.new("1", (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = -2
    top = padding
    bottom = height - padding
    # Move left to right keeping track of the current x position for drawing shapes.
    x = 0

    # Load default font.
    font = ImageFont.load_default()
    while True:
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Write four lines of text.
        if readCache is not None:
            timestamp, humidity, temperature = readCache
            currentTime = int(time.time())
            dataAge = currentTime - int(timestamp)
            draw.text((x, top + 0), "Data Age: " + str(dataAge) + " s", font=font, fill=255)
            draw.text((x, top + 8), "Temperature: " + "{:.2f}".format(temperature) + " °C", font=font, fill=255)
            draw.text((x, top + 16), "Humidity: " + "{:.2f}".format(humidity) + " %", font=font, fill=255)
            draw.text((x, top + 25), "CO2: 400 PPM", font=font, fill=255)
        else:
            draw.text((x, top + 0), "Reading sensors...", font=font, fill=255)

        # Display image.
        display.image(image)
        display.show()
        time.sleep(0.1)

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

screenThread = threading.Thread(target=refreshOLED)
sensorThreadDHT = threading.Thread(target=readSensorDHT)
sensorThreadDHT.start()
screenThread.start()
