import json
import time
import traceback
from sqlalchemy import create_engine, Table, Column, DateTime, Integer, Float, String
import requests
import config
import sqlalchemy as sqla
from datetime import datetime

from sqlalchemy.exc import IntegrityError

metadata = sqla.MetaData()

# connect to database
engine = create_engine(
    "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(config.DB_USER, config.DB_PASSWORD, config.DB_URL, config.DB_PORT,
                                                   config.DB_NAME))

# current weather
current = Table('current_weather', metadata,
                Column("dt", DateTime, primary_key=True),
                Column("sunrise", DateTime),
                Column("sunset", DateTime),
                Column("temp", Float),
                Column("feels_like", Float),
                Column("pressure", Integer),
                Column("humidity", Integer),
                Column("dew_point", Float),
                Column("uvi", Float),
                Column("clouds", Integer),
                Column("visibility", Integer),
                Column("wind_speed", Float),
                Column("wind_deg", Float),
                Column("weather_id", Integer),
                Column("weather_main", String(100)),
                Column("weather_description", String(200)),
                Column("weather_icon", String(10)))

# daily weather
daily = Table('daily_weather', metadata,
              Column("dt", DateTime, primary_key=True),
              Column("future_dt", DateTime, primary_key=True),
              Column("sunrise", DateTime),
              Column("sunset", DateTime),
              Column("temp_day", Float),
              Column("temp_min", Float),
              Column("temp_max", Float),
              Column("temp_night", Float),
              Column("temp_eve", Float),
              Column("temp_morn", Float),
              Column("feels_like_day", Float),
              Column("feels_like_night", Float),
              Column("feels_like_eve", Float),
              Column("feels_like_morn", Float),
              Column("pressure", Integer),
              Column("humidity", Integer),
              Column("dew_point", Float),
              Column("wind_speed", Float),
              Column("wind_deg", Float),
              Column("weather_id", Integer),
              Column("weather_main", String(100)),
              Column("weather_description", String(200)),
              Column("weather_icon", String(10)),
              Column("clouds", Integer),
              Column("pop", Float),
              Column("uvi", Float))

# hourly weather
hourly = Table('hourly_weather', metadata,
               Column("dt", DateTime, primary_key=True),
               Column("future_dt", DateTime, primary_key=True),
               Column("temp", Float),
               Column("feels_like", Float),
               Column("pressure", Integer),
               Column("humidity", Integer),
               Column("dew_point", Float),
               Column("uvi", Float),
               Column("clouds", Integer),
               Column("visibility", Integer),
               Column("wind_speed", Float),
               Column("wind_deg", Float),
               Column("weather_id", Integer),
               Column("weather_main", String(100)),
               Column("weather_description", String(200)),
               Column("weather_icon", String(10)),
               Column("pop", Float))


def get_current_weather(data):
    """ extract current weather"""
    return {
        "dt": datetime.fromtimestamp(int(data['dt'])),
        "sunrise": datetime.fromtimestamp(int(data['sunrise'])),
        "sunset": datetime.fromtimestamp(int(data['sunset'])),
        "temp": data["temp"],
        "feels_like": data["feels_like"],
        "pressure": data["pressure"],
        "humidity": data["humidity"],
        "dew_point": data["dew_point"],
        "uvi": data["uvi"],
        "clouds": data["clouds"],
        "visibility": data["visibility"],
        "wind_speed": data["wind_speed"],
        "wind_deg": data["wind_deg"],
        "weather_id": data["weather"][0]["id"],
        "weather_main": data["weather"][0]["main"],
        "weather_description": data["weather"][0]["description"],
        "weather_icon": data["weather"][0]["icon"]
    }


def get_daily_weather(current_dt, data):
    """ extract daily weather"""
    return {
        "dt": datetime.fromtimestamp(int(current_dt)),
        "future_dt": datetime.fromtimestamp(int(data['dt'])),
        "sunrise": datetime.fromtimestamp(int(data['sunrise'])),
        "sunset": datetime.fromtimestamp(int(data['sunset'])),
        "temp_day": data["temp"]["day"],
        "temp_min": data["temp"]["min"],
        "temp_max": data["temp"]["max"],
        "temp_night": data["temp"]["night"],
        "temp_eve": data["temp"]["eve"],
        "temp_morn": data["temp"]["morn"],
        "feels_like_day": data["feels_like"]["day"],
        "feels_like_night": data["feels_like"]["night"],
        "feels_like_eve": data["feels_like"]["eve"],
        "feels_like_morn": data["feels_like"]["morn"],
        "pressure": data["pressure"],
        "humidity": data["humidity"],
        "dew_point": data["dew_point"],
        "wind_speed": data["wind_speed"],
        "wind_deg": data["wind_deg"],
        "weather_id": data["weather"][0]["id"],
        "weather_main": data["weather"][0]["main"],
        "weather_description": data["weather"][0]["description"],
        "weather_icon": data["weather"][0]["icon"],
        "clouds": data["clouds"],
        "pop": data["pop"],
        "uvi": data["uvi"]
    }


def get_hourly_weather(current_dt, data):
    """ extract hourly weather"""
    return {
        "dt": datetime.fromtimestamp(int(current_dt)),
        "future_dt": datetime.fromtimestamp(int(data['dt'])),
        "temp": data["temp"],
        "feels_like": data["feels_like"],
        "pressure": data["pressure"],
        "humidity": data["humidity"],
        "dew_point": data["dew_point"],
        "uvi": data["uvi"],
        "clouds": data["clouds"],
        "visibility": data["visibility"],
        "wind_speed": data["wind_speed"],
        "wind_deg": data["wind_deg"],
        "weather_id": data["weather"][0]["id"],
        "weather_main": data["weather"][0]["main"],
        "weather_description": data["weather"][0]["description"],
        "weather_icon": data["weather"][0]["icon"],
        "pop": data["pop"]
    }


def write_to_db(table_obj, data):
    """write data to table"""
    with engine.connect() as connection:
        for entry in data:
            try:
                connection.execute(table_obj.insert().values(entry))
            except IntegrityError as error:
                print("Integrity error.", error)
            except:
                print(traceback.format_exc())


def store(weather):
    """store all weather data"""
    # store current weather
    current_weather = get_current_weather(weather["current"])
    write_to_db(current, [current_weather])

    current_dt = weather["current"]['dt']
    # store daily weather
    daily_weather = [get_daily_weather(current_dt, item) for item in weather["daily"]]
    write_to_db(daily, daily_weather)

    # store hourly weather
    hourly_weather = [get_hourly_weather(current_dt, item) for item in weather["hourly"]]
    write_to_db(hourly, hourly_weather)


# creates the database tables only if missing
metadata.create_all(engine, checkfirst=True)

while True:
    try:
        # get the data from openweather
        data = {
            "appid": config.OPENWEATHER_KEY,
            "lat": 53.344,
            "lon": -6.2672,
            "exclude": "minutely"
        }
        r = requests.get(config.OPENWEATHER_URL, params=data)
        print("fetching", r.url)
        store(json.loads(r.text))
        print('done')

        # wait 30 min
        time.sleep(30 * 60)

    except:
        print(traceback.format_exc())