import json
import psycopg2
import psycopg2.extras
import commonCode as cc
import os

def lambda_handler(event, context):

    arButtons = list()
    #Try to retrieve the appropriate data from the body. If an error occurs, send a 400 error code as a responset
    try:
        for arButton in event:
            data = list()
            data.append(arButton['feature'])
            data.append(arButton['section'])
            data.append(arButton['image'])
            arButtons.append(tuple(data))
    except:
        return cc.response_bad_request("Invalid body format")

    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                         os.environ["dbHost"], os.environ["dbPass"])
    return insertArButtons(conn, arButtons)
  

def insertArButtons(conn, buttons):
    """Inserts AR buttons into the ar_button table

    Arguments: 
        conn: A connection to the database
        media: A list of tuples containing the AR buttons
    """
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS ar_button
            (ar_buttonId SERIAL NOT NULL, 
            feature varchar(100) NOT NULL, 
            section varchar(50) NOT NULL, 
            image varchar(250) NOT NULL, 
            PRIMARY KEY (ar_buttonId));""")  

            #Executes an insert SQL query to insert the player data
            psycopg2.extras.execute_values(cursor, "INSERT INTO ar_button (feature, section, image) VALUES %s", buttons)

            #If all of the writes were successfuly, return a 200 response code.
            return cc.response_ok("Successfully added AR buttons to database")

    except psycopg2.Error as e:
        print(e)
        #If the writing failed return a 400 response code.
        return cc.response_bad_request(repr(e))

