import time
import board
import busio
import adafruit_scd30
from repository import Repository # Required for data persistence

PERSISTENCE_WRITE_PAUSE = 10 # 60 / 10 = 6 measurements per minute
ENABLED_SELF_CALIBRATION = True

i2c = busio.I2C(board.SCL, board.SDA, frequency=50000)
scd = adafruit_scd30.SCD30(i2c)
scd.self_calibration_enabled = ENABLED_SELF_CALIBRATION

repository = Repository()
while True:
    if scd.data_available:
        # Create measurement & persist in repository
        currentTime = time.time()
        measurement = (currentTime, round(scd.temperature, 1), round(scd.relative_humidity, 1), round(scd.CO2, 1))
        repository.persistMeasurement(measurement)
    time.sleep(PERSISTENCE_WRITE_PAUSE)
