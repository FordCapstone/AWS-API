import json
import psycopg2
import os
import commonCode as cc

def lambda_handler(event, context):

    car =  tuple(json.loads(event["body"]).values())
    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                         os.environ["dbHost"], os.environ["dbPass"])
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
            UNIQUE (make, model, year),
            PRIMARY KEY (carId));""")  

            cursor.execute("INSERT INTO car (make, model, year, ownerManual) VALUES %s", [car,])

    except psycopg2.Error as e:
        print(e)