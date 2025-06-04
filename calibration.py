import adafruit_scd30
import board
import busio
import time

i2c = busio.I2C(board.SCL, board.SDA, frequency=50000)
scd = adafruit_scd30.SCD30(i2c)
scd.self_calibration_enabled = False

print("Starting calibration...")
scd.forced_recalibration_reference = 420
print("Calibration finished!")
