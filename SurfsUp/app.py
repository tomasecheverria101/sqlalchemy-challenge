# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
import numpy as np  # Add this line at the beginning of the file

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
