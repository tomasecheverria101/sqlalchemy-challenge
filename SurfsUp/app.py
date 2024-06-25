# Import the dependencies.

import numpy as np
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/Hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    date_one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query for the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= date_one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()

    # Convert the results to a list
    stations_list = [station[0] for station in results]

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year ago from the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    date_one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Get the most active station id
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    most_active_station_id = active_stations[0][0]

    # Query the last 12 months of temperature observation data for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= date_one_year_ago).all()

    # Convert the results to a list
    temperature_list = [tobs for date, tobs in temperature_data]

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start, end=None):
    try:
        # Calculate the most recent date
        most_recent_date = session.query(func.max(Measurement.date)).scalar()
        print("Most recent date:", most_recent_date)  # Debug print

        # Convert the start and end dates to datetime objects
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d") if end else dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
        print("Start date:", start_date)  # Debug print
        print("End date:", end_date)  # Debug print

        # Query the minimum, average, and maximum temperature for the specified date range
        temperature_stats = session.query(
            func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)
        ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        print("Query executed successfully")  # Debug print

        # Convert the results to a list
        stats_list = list(np.ravel(temperature_stats))
        print("Temperature stats:", stats_list)  # Debug print

        return jsonify(stats_list)
    except Exception as e:
        print("Error:", e)  # Print the error for debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
