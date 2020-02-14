import json
import psycopg2
import os
import commonCode as cc

def lambda_handler(event, context):

    car = tuple(event)

    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                         os.environ["dbHost"], os.environ["dbPass"])
    if(conn != None):
        response = insertCar(conn, car)
        return response
    else:
        return "Error connecting to database."
    
    
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
            icon varchar(100) NOT NULL,
            UNIQUE (make, model, year),
            PRIMARY KEY (carId));""")  

            cursor.execute("INSERT INTO car (make, model, year, ownerManual, icon) VALUES %s RETURNING carId", [car,])
            
            #Return the carId of the row just inserted
            return cursor.fetchone()[0]

    except psycopg2.Error as e:
        if  isinstance(e, psycopg2.IntegrityError):
            return "Unable to add duplicate vehicle. Combination of make, model, and year must be unique."
        else:
            return "Unable to add vehicle." 