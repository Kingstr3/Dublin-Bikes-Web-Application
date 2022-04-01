'''
Import all modules needed to request the data and convert to the 
table format needed to store on rds database.

myPrivates.py should contain sensitive information 
required to access the API and rds database.
'''
import myPrivates
import requests
import json
import traceback
import datetime
import time
import sqlalchemy.dialects
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, DateTime
from sqlalchemy import Table, Column, Integer, MetaData

'''
Below variables used in f strings are declared. These
variables specifically the priavte ones are defined here
for ease of reading while constructing strings
'''
name = "dublin"
stations_API = "https://api.jcdecaux.com/vls/v1/stations"
apikey = myPrivates.myKey
dbPass = myPrivates.dbPass
db_url = myPrivates.dbURL
user = "admin"
dbName = "dbikes"
sqlport = "3306"

'''
Create sql engine here as to not recreate every time data
is sent to the rds database
'''
engine = create_engine(f"mysql+mysqlconnector://{user}:{dbPass}@{db_url}:{sqlport}/{dbName}")

#define the structure of the table
meta = MetaData()
availability = Table('availability',meta,
	Column('number',Integer),
	Column('bike_stands',Integer),
	Column('available_bike_stands',Integer),
	Column('available_bikes',Integer),
	Column('last_update', DateTime))
		
def get_station(obj):
	#design dictionary to hold desiered data
	return {'number':obj['number'],'bike_stands':obj['bike_stands'],
	'available_bike_stands':obj['available_bike_stands'],'available_bikes':obj['available_bikes'],
	'last_update': datetime.datetime.fromtimestamp(int(obj['last_update']/1e3))
	}

#run all the time
while True:
	try:
		#request api from site
		r = requests.get(stations_API,params={"apiKey":apikey, "contract":name})
		#map json to list of dictionaries
		values = list(map(get_station,r.json()))
		#send values to database on mysql
		ins = availability.insert().values(values)
		engine.execute(ins)

		time.sleep(300)
	except:
		print(traceback.format_exc())
