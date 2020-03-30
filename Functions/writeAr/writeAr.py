import json
import psycopg2
import psycopg2.extras
import commonCode as cc
import os

def lambda_handler(event, context):

    arFeatures = list()
    #Try to retrieve the appropriate data from the body. If an error occurs, send a 400 error code as a response
    try:
        body = json.loads(event["body"])

        #Try to retrieve the appropriate data from the body. If an error occurs, send a 400 error code as a responset
        for ar in body:
            data = list()
            data.append(ar["carId"])
            data.append(ar["enabled"])
            data.append(ar["location"])
            data.append(ar["primaryTag"])
            data.append(ar["secondaryTag"])
            data.append(ar["arButtonId"])
            arFeatures.append(tuple(data))  
    except:
        return cc.response_bad_request("Invalid body format")

    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                         os.environ["dbHost"], os.environ["dbPass"])
    return insertAr(conn, arFeatures)
  

def insertAr(conn, ar):
    """Inserts AR data into the ar table

    Arguments: 
        conn: A connection to the database
        ar: A list of tuples containing the AR data
    """
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS ar 
            (ar_buttonid int4 NOT NULL, 
            carId int4 NOT NULL, 
            enabled bool NOT NULL, 
            location varchar(50) NOT NULL, 
            primaryTag int4 NOT NULL, 
            secondaryTag int4, 
            PRIMARY KEY (ar_buttonid, carId));""") 

            #Executes an insert SQL query to insert the player data
            psycopg2.extras.execute_values(cursor, 
            """INSERT INTO ar 
            (carId, enabled, location, primaryTag, secondaryTag, ar_buttonid) VALUES %s
            ON CONFLICT (carId, ar_buttonid) DO UPDATE SET
            enabled = EXCLUDED.enabled,
            location = EXCLUDED. location,
            primaryTag = EXCLUDED.primaryTag,
            secondaryTag = EXCLUDED.secondaryTag
            """, ar)

            #If all of the writes were successful, return a 200 response code.
            return cc.response_ok("Successfully added AR to database")

    except psycopg2.Error as e:
        print(e)
        #If the write fails, return a 400 response code.
        return cc.response_bad_request(repr(e))
