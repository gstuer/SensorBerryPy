import time
import board
import busio
import adafruit_scd30
import adafruit_dht
from repository import Repository # Required for data persistence

PERSISTENCE_WRITE_PAUSE = 10 # 60 / 10 = 6 measurements per minute
ERROR_WRITE_PAUSE = 1
ENABLED_SELF_CALIBRATION = True
STARTUP_TIMEOUT = 5 # Timeout before I2C is activated in seconds

time.sleep(STARTUP_TIMEOUT)
i2c = busio.I2C(board.SCL, board.SDA, frequency=50000)
scd = adafruit_scd30.SCD30(i2c)
scd.self_calibration_enabled = ENABLED_SELF_CALIBRATION

dht = adafruit_dht.DHT22(board.D17)

repository = Repository()
while True:
    try:
        if scd.data_available:
            # Create measurement & persist in repository
            currentTime = time.time()
            measurement = (currentTime, round(dht.temperature, 1), round(dht.humidity, 1), round(scd.CO2, 1))
            repository.persistMeasurement(measurement)
    except RuntimeError as error:
        print("Sensor Runtime Error: ", error)
        time.sleep(ERROR_WRITE_PAUSE)
    except OSError as error:
        print("OS Error: ", error)
        time.sleep(ERROR_WRITE_PAUSE)
    finally:
        time.sleep(PERSISTENCE_WRITE_PAUSE)
