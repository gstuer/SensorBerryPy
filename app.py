import time
import threading
import RPi.GPIO as GPIO

# Required for DHT sensor
import Adafruit_DHT

# Required for Adafruit PiOLED
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Required for MHZ-19
import serial

# Required for data persistence
from repository import Repository

DHT_SENSOR_TYPE = Adafruit_DHT.AM2302
DHT_SENSOR_PIN = 18
DHT_SENSOR_READ_PAUSE = 15
DISPLAY_ON_TIME = 30
INTERACTION_SENSOR_PIN = 17
INTERACTION_SENSOR_PULL = GPIO.PUD_DOWN
INTERACTION_SENSOR_DETECTION_EDGE = GPIO.FALLING
INTERACTION_SENSOR_DEBOUNCE_TIME = 0.25
MHZ_SENSOR_READ_PAUSE = 15
SERIAL_PORT = "/dev/ttyS0"
SERIAL_BAUDRATE = 9600
SERIAL_BYTESIZE = serial.EIGHTBITS
SERIAL_PARITY = serial.PARITY_NONE
SERIAL_STOPBITS = serial.STOPBITS_ONE
SERIAL_TIMEOUT = 1.0
SERIAL_TRIES = 4
PERSISTENCE_WRITE_PAUSE = 60

dhtCache = None
mhzCache = None
displayEnabledTimestamp = time.time()

def readSensorDHT():
    global dhtCache
    while True:
        currentTime = time.time()
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, DHT_SENSOR_PIN)
        # Reading the sensor may take a couple of seconds -> Time needs to be refreshed.
        currentTime = time.time()
        if humidity is not None and temperature is not None:
            dhtCache = (currentTime, humidity, temperature)
        time.sleep(DHT_SENSOR_READ_PAUSE)

def readSensorMHZ():
    global mhzCache
    sensor = serial.Serial(SERIAL_PORT, baudrate=SERIAL_BAUDRATE, bytesize=SERIAL_BYTESIZE,
            parity=SERIAL_PARITY, stopbits=SERIAL_STOPBITS, timeout=SERIAL_TIMEOUT)

    while True:
        value = None
        fetchTime = None
        for i in range(SERIAL_TRIES):
            # Send read command to sensor & fetch result data
            sensor.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
            data = sensor.read(9)
            fetchTime = time.time()

            # Extract information & validate result
            startByte = data[0]
            commandByte = data[1]
            dataSum = sum(data[1:-1])
            checksumCalculated = 0xff - (dataSum % 0x100) + 0x01
            checksumAppended = data[8]
            if len(data) == 9 and startByte == 0xff and commandByte == 0x86 and (checksumCalculated == checksumAppended):
                # Fetching data was successful
                valueHigh = data[2]
                valueLow = data[3]
                value = valueHigh * 256 + valueLow
                break
            else:
                # Fetching data was not successful
                continue

        if value is not None:
            mhzCache = (fetchTime, value)
        time.sleep(MHZ_SENSOR_READ_PAUSE)

def detectInteraction():
    global displayEnabledTimestamp

    # Configure GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(INTERACTION_SENSOR_PIN, GPIO.IN, pull_up_down=INTERACTION_SENSOR_PULL)
    while True:
        if GPIO.wait_for_edge(INTERACTION_SENSOR_PIN, INTERACTION_SENSOR_DETECTION_EDGE) is not None:
            displayEnabledTimestamp = time.time()
        time.sleep(INTERACTION_SENSOR_DEBOUNCE_TIME)

# Based on snippets from https://github.com/adafruit/Adafruit_CircuitPython_SSD1306
# MIT License: https://github.com/adafruit/Adafruit_CircuitPython_SSD1306/blob/500ec2cbd2f7758a10efb1c54c536c38fd36a851/LICENSE
def refreshOLED():
    global dhtCache
    global displayEnabledTimestamp

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
        currentTime = time.time()
        if (currentTime - displayEnabledTimestamp) < DISPLAY_ON_TIME:
            if dhtCache is not None and mhzCache is not None:
                timestampDHT, humidity, temperature = dhtCache
                timestampMHZ, co2 = mhzCache
                dataAge = int(currentTime) - int(timestampDHT)
                draw.text((x, top + 0), "Data Age: " + str(dataAge) + " s", font=font, fill=255)
                draw.text((x, top + 8), "Temperature: " + "{:.1f}".format(temperature) + " °C", font=font, fill=255)
                draw.text((x, top + 16), "Humidity: " + "{:.1f}".format(humidity) + " %", font=font, fill=255)
                draw.text((x, top + 25), "CO2: " + str(co2) + " PPM", font=font, fill=255)
            else:
                draw.text((x, top + 0), "Reading sensors...", font=font, fill=255)

        # Display image.
        display.image(image)
        display.show()
        time.sleep(0.1)

def persistMeasurement():
    repository = Repository()
    while True:
        if dhtCache is not None and mhzCache is not None:
            # Fetch data that should be persisted
            currentTime = time.time()
            timestampDHT, humidity, temperature = dhtCache
            timestampMHZ, co2 = mhzCache

            # Create measurement & persist in repository
            measurement = (currentTime, round(temperature, 1), round(humidity, 1), co2)
            repository.persistMeasurement(measurement)

        # Pause at least given time before next measurement gets persisted
        time.sleep(PERSISTENCE_WRITE_PAUSE)

# Create and start threads
threading.Thread(target=readSensorDHT).start()
threading.Thread(target=readSensorMHZ).start()
threading.Thread(target=detectInteraction).start()
threading.Thread(target=refreshOLED).start()
threading.Thread(target=persistMeasurement).start()
