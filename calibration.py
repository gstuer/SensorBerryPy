import adafruit_scd30
import board
import busio
import sys
import time

# Initialize sensor
i2c = busio.I2C(board.SCL, board.SDA, frequency=50000)
scd = adafruit_scd30.SCD30(i2c)

if len(sys.argv) <= 1:
    # Print current sensor configuration to command line
    print("Temperature offset:", scd.temperature_offset, " °C")
    print("Measurement interval:", scd.measurement_interval, " s")
    print("Self-calibration enabled:", scd.self_calibration_enabled)
    print("Forced recalibration reference:", scd.forced_recalibration_reference, " ppm")
    print("Ambient Pressure:", scd.ambient_pressure, " mbar")
    print("Altitude:", scd.altitude, " m a.s.l.")
elif len(sys.argv) <= 3:
    # Read type of calibration & reference value to be set from program arguments
    calibrationType = sys.argv[1]
    newReference = sys.argv[2]

    # Perform recalibration
    print("Starting calibration...")
    if calibrationType == "temperature":
        scd.temperature_offset = float(newReference)
        print("Temperature calibration finished!")
    elif calibrationType == "co2":
        scd.forced_recalibration_reference = int(newReference)
        print("Carbon dioxide calibration finished!")
    else:
        print("Calibration failed due to unknown type!")
