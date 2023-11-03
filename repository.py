import sqlite3

REPOSITORY_FILE = "./data.db"

connection = None

def connect():
    global connection
    if connection is None:
        connection = sqlite3.connect(REPOSITORY_FILE)
    return connection

def initialize():
    # Initialize table if not done before
    cursor = connect().cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS measurements (
        timestamp REAL PRIMARY KEY,
        temperature REAL,
        humidity REAL,
        carbon_dioxide REAL
    );""")

def persistMeasurement(measurement):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO measurements (timestamp, temperature, humidity, carbon_dioxide) VALUES (?, ?, ?, ?);", measurement)
    connection.commit()

def findMeasurementsWithMaxAge(seconds):
    connection = connect()
    cursor = connection.cursor()
    maxAgeTimestamp = time.time() - seconds
    cursor.execute(f'SELECT timestamp, temperature, humidity, carbon_dioxide FROM measurements WHERE timestamp >= {maxAgeTimestamp};')
    return cursor.fetchall()
