import time
import board
import busio
import adafruit_scd30
# Required for data persistence
from repository import Repository

# 60 / 15 = 4 measurements per minute
PERSISTENCE_WRITE_PAUSE = 15

i2c = busio.I2C(board.SCL, board.SDA, frequency=50000)
scd = adafruit_scd30.SCD30(i2c)
scd.self_calibration_enabled = False

repository = Repository()
while True:
    if scd.data_available:
        # Create measurement & persist in repository
        currentTime = time.time()
        measurement = (currentTime, round(scd.temperature, 1), round(scd.relative_humidity, 1), round(scd.CO2, 1))
        repository.persistMeasurement(measurement)
time.sleep(PERSISTENCE_WRITE_PAUSE)
