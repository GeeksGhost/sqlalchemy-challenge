# Import the dependencies.
import numpy as np

import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
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
def start():
    """List all available api routes."""
    return(
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    # create our session link from python to the db
    session = Session(engine)

    # Design a query to retrieve the last 12 months of precipitation data
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    # Close the session
    session.close()
    
    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create a session link from python to the db
    session = Session(engine)

    # Return list of stations from dataset 
    stations = session.query(Measurement.station).distinct().all()
    
    # Extract station names from the result
    station_list = [station.station for station in stations]

    # Close the session
    session.close()
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session link from python to the db
    session = Session(engine)

    # Query to select the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Calculate the date one year ago from the most recent date in the database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query to retrieve the last 12 months of temperature observation data for the most active station
    temperature_data = session.query(Measurement.tobs).\
                        filter(Measurement.station == most_active_station).\
                        filter(Measurement.date >= one_year_ago).all()
    
    # Close the session
    session.close()
    
    # Convert the query results to a list of temperature observations
    temperature_list = [temp[0] for temp in temperature_data]
    
    return jsonify({"station": most_active_station, "temperatures": temperature_list})

@app.route("/api/v1.0/<start>")
def start_temp(start):
    # Create a session Link from Python to the db
    session = Session(engine)
    
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    session.close()
    
    # Convert list of tuples into a list
    result = list(np.ravel(temp_data))
    
    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
     # Create a session Link from Python to the db
    session = Session(engine)

    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
     
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <=end_date).all()
    
    session.close()
    
    # Convert list of tuples into a list
    result = list(np.ravel(temp_data))
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)