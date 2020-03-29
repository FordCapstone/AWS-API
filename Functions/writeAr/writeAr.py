import json
import psycopg2
import commonCode as cc
import os

def lambda_handler(event, context):

    #Try to retrieve the appropriate data from the body. If an error occurs, send a 400 error code as a response
    try:
        body = json.loads(event["body"])
        carId  = body["carId"]
        enabled = body["enabled"]
        location = body["location"]
        primaryTag = body["primaryTag"]
        secondaryTag = body["secondaryTag"]
        arButtonId = body["arButtonId"]
    except:
        return cc.response_bad_request("Invalid body format")
    
    #Create a tuple containing the media data
    ar = (carId, enabled, location, primaryTag, secondaryTag, arButtonId)

    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                         os.environ["dbHost"], os.environ["dbPass"])
    return insertAr(conn, ar)
  

def insertAr(conn, ar):
    """Inserts AR data into the ar table

    Arguments: 
        conn: A connection to the database
        ar: A tuple containing the AR data
    """
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS ar 
            (arId SERIAL NOT NULL, 
            carId int4 NOT NULL, 
            enabled bool NOT NULL, 
            location varchar(50) NOT NULL, 
            primaryTag int4 NOT NULL, 
            secondaryTag int4, 
            ar_buttonid int4 NOT NULL, 
            PRIMARY KEY (arId));""")  

            cursor.execute("INSERT INTO ar (carId, enabled, location, primaryTag, secondaryTag, ar_buttonid) VALUES %s", [ar,])

            #If all of the writes were successful, return a 200 response code.
            return cc.response_ok("Successfully added AR to database")

    except psycopg2.Error as e:
        print(e)
        #If the write fails, return a 400 response code.
        return cc.response_bad_request(repr(e))
