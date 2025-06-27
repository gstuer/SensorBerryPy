# Required for DHT sensor
import adafruit_dht
import board

sensor = adafruit_dht.DHT22(board.D18)
print("Temperature ", sensor.temperature)
print("Humidity ", sensor.humidity)
sensor.exit()
