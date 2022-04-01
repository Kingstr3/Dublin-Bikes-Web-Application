import json
import time
import traceback
from sqlalchemy import create_engine
import requests
import config
import sqlalchemy as sqla
from datetime import datetime

metadata = sqla.MetaData()

# station table
station = sqla.Table('station', metadata,
                     sqla.Column('address', sqla.String(256), nullable=False),
                     sqla.Column('banking', sqla.Integer),
                     sqla.Column('bike_stands', sqla.Integer),
                     sqla.Column('bonus', sqla.Integer),
                     sqla.Column('contract_name', sqla.String(256)),
                     sqla.Column('name', sqla.String(256)),
                     sqla.Column('number', sqla.Integer, unique=True),  # unique numbers
                     sqla.Column('position_lat', sqla.REAL),
                     sqla.Column('position_lng', sqla.REAL),
                     sqla.Column('status', sqla.String(256))
                     )

# availability table
availability = sqla.Table('availability', metadata,
                          sqla.Column('available_bikes', sqla.Integer),
                          sqla.Column('available_bike_stands', sqla.Integer),
                          sqla.Column('number', sqla.Integer),
                          sqla.Column('last_update', sqla.DateTime)
                          )

# connect to database
engine = create_engine(
    "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(config.DB_USER, config.DB_PASSWORD, config.DB_URL, config.DB_PORT,
                                                   config.DB_NAME))


def get_station(data):
    """ extract station static data"""
    return {
        "number": data['number'],
        "contract_name": data['contract_name'],
        "name": data['name'],
        "address": data['address'],
        "position_lat": data['position']['lat'],
        "position_lng": data['position']['lng'],
        "banking": data['banking'],
        "bonus": data['bonus'],
        "bike_stands": data['bike_stands'],
        "status": data['status']
    }


def get_availability(data):
    """ extract station dynamic data"""
    return {
        "number": data['number'],
        "available_bike_stands": data['available_bike_stands'],
        "available_bikes": data['available_bikes'],
        "last_update": datetime.fromtimestamp(int(data['last_update']/1e3))
    }


def store(stations):
    """save station data to database"""
    # add all stations or new stations (ignore duplicate errors)
    engine.execute(station.insert(prefixes=['IGNORE']), *map(get_station, stations))
    # add bike availability data
    engine.execute(availability.insert(), *map(get_availability, stations))


# creates the database tables only if missing
metadata.create_all(engine, checkfirst=True)

while True:
    try:
        # get data from JCDecaux url
        r = requests.get(config.API_URL, params={"apiKey": config.API_KEY, "contract": config.NAME})
        print("fetching", r.url)
        store(json.loads(r.text))
        print('done')

        # wait 5 min
        time.sleep(5 * 60)

    except:
        print(traceback.format_exc())
