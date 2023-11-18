from flask import Flask, request, jsonify, render_template
from repository import Repository

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/", methods=["GET"])
def getIndex():
    return render_template("index.html")

@app.route("/measurements", methods=["GET"])
def getMeasurements():
    repository = Repository()
    maxAge = request.args.get("max_age")
    if maxAge is not None:
        # TODO Check whether type maxAge is valid (eg. int)
        rows = repository.findMeasurementsWithMaxAge(maxAge)
    else:
        rows = repository.findMeasurements()

    # Add rows as dictionary to List
    measurements = list()
    for row in rows:
        # Get values from row
        timestamp, temperature, humidity, carbon_dioxide = row
        measurement = {"timestamp": timestamp, "temperature": temperature, "humidity": humidity, "carbon_dioxide": carbon_dioxide}
        measurements.append(measurement)
    return jsonify(measurements), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
