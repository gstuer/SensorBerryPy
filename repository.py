import time
import os
import sqlite3

class Repository:
    REPOSITORY_FILE_DEFAULT = os.path.join(os.path.dirname(__file__), "data.db")
    def __init__(self, file = REPOSITORY_FILE_DEFAULT):
        # Open connection to database
        self.connection = sqlite3.connect(file)

        # Initialize table if not done before
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS measurements (
            timestamp REAL PRIMARY KEY,
            temperature REAL,
            humidity REAL,
            carbon_dioxide REAL
        );""")

    def persistMeasurement(self, measurement):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO measurements (timestamp, temperature, humidity, carbon_dioxide) VALUES (?, ?, ?, ?);", measurement)
        self.connection.commit()

    def findMeasurements(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT timestamp, temperature, humidity, carbon_dioxide FROM measurements;")
        return cursor.fetchall()

    def findMeasurementsWithAge(self, minimum: float, maximum: float):
        cursor = self.connection.cursor()
        currentTime = time.time()

        if maximum is None or maximum > currentTime:
            maxAgeTimestamp = 0
        else:
            maxAgeTimestamp = currentTime - maximum

        if minimum is None or minimum < 0:
            minAgeTimestamp = currentTime
        else:
            minAgeTimestamp = currentTime - minimum

        cursor.execute(f'SELECT timestamp, temperature, humidity, carbon_dioxide FROM measurements WHERE timestamp >= {maxAgeTimestamp} AND timestamp <= {minAgeTimestamp};')
        return cursor.fetchall()
