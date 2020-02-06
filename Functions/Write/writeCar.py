import json
import psycopg2
import os

def lambda_handler(event, context):

    car = tuple(event)
    conn = dbConnection()
    insertCar(conn, car)
  

def insertCar(conn, car):
    """Inserts vehicle data into the car table

    Arguments: 
        conn: A connection to the database
        car: A tuple containing the car data

    """
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS car 
            (carId SERIAL NOT NULL, 
            make varchar(100) NOT NULL, 
            model varchar(100) NOT NULL, 
            year int4 NOT NULL, 
            ownerManual varchar(240) NOT NULL, 
            PRIMARY KEY (carId));""")  

            cursor.execute("INSERT INTO car (make, model, year, ownerManual) VALUES %s", [car,])

    except psycopg2.Error as e:
        print(e)

def dbConnection():
    """Makes a connection the database

    Returns:
        connection: The connection to the database
    """
    try:
        conn = psycopg2.connect("dbname={} user={} host={} password={}".format(
            os.environ['dbName'],os.environ['dbUser'],os.environ['dbHost'],os.environ['dbPass']))
        return conn
    except psycopg2.Error as e: 
        print(e)