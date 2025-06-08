from flask import Flask, request, jsonify, render_template
from flask_cors import cross_origin
from repository import Repository
from statistics import fmean

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/", methods=["GET"])
def getIndex():
    return render_template("index.html")

@app.route("/measurements", methods=["GET"])
@cross_origin()
def getMeasurements():
    # Get request arguments from url
    maxAge = float(request.args.get("max_age")) if request.args.get("max_age") is not None else None
    minAge = float(request.args.get("min_age")) if request.args.get("min_age") is not None else None

    # Initialize repository and fetch rows
    repository = Repository()
    rows = repository.findMeasurementsWithAge(minimum = minAge, maximum = maxAge)

    # Add rows as dictionary to list
    measurements = list()
    for row in rows:
        # Get values from row
        timestamp, temperature, humidity, carbonDioxide = row
        measurement = {"timestamp": timestamp, "temperature": temperature, "humidity": humidity, "carbon_dioxide": carbonDioxide}
        measurements.append(measurement)

    # Calculate aggregate functions for data
    response = {}
    temperatureValues = [measurement["temperature"] for measurement in measurements]
    temperatureAggregates = {
        "maximum": max(temperatureValues),
        "mean_arithmetic": fmean(temperatureValues),
        "minimum": min(temperatureValues)
    }
    humidityValues = [measurement["humidity"] for measurement in measurements]
    humidityAggregates = {
        "maximum": max(humidityValues),
        "mean_arithmetic": fmean(humidityValues),
        "minimum": min(humidityValues)
    }
    carbonDioxideValues = [measurement["carbon_dioxide"] for measurement in measurements]
    carbonDioxideAggregates = {
        "maximum": max(carbonDioxideValues),
        "mean_arithmetic": fmean(carbonDioxideValues),
        "minimum": min(carbonDioxideValues)
    }

    # Construct http response object
    aggregates = {"temperature": temperatureAggregates, "humidity": humidityAggregates, "carbon_dioxide": carbonDioxideAggregates}
    response["aggregates"] = aggregates
    response["measurements"] = measurements

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
