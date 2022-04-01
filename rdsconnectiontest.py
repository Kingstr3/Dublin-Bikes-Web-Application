'''
This script will test the connection from the ec2 instance with the database
as well as testing the correct setup of the engine and connection
methods on a linux system.
'''
import myPrivates
import sqlalchemy.dialects
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, DateTime
from sqlalchemy import Table, Column, String, MetaData

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

values = [{'name':'ec2','job':'mule'},{'name':'Ultron','job':'overlord'}]

meta = MetaData()

testTable = Table('testTable',meta,
	Column('name',String(128)),
	Column('job',String(128)))

ins = testTable.insert().values(values)
engine.execute(ins)
