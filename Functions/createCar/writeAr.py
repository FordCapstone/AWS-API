import json
import psycopg2
import os

def lambda_handler(event, context):

    ar = tuple(event)

    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                         os.environ["dbHost"], os.environ["dbPass"])

    insertAr(conn, ar)
  

def insertAr(conn, ar):
    """Inserts an AR feature into the AR table

    Arguments: 
        conn: A connection to the database
        ar: A tuple containing the AR feature data
    """
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("""CREATE TABLE ar 
            (arId SERIAL NOT NULL, 
            carId int4 NOT NULL, 
            feature varchar(100) NOT NULL, 
            location varchar(50) NOT NULL, 
            primaryTag int4 NOT NULL, 
            secondaryTag int4, 
            PRIMARY KEY (arId),
            FOREIGN KEY(secondaryTag) REFERENCES tag(tagId),
            FOREIGN KEY(primaryTag) REFERENCES tag(tagId));""")  

            cursor.execute("INSERT INTO ar (carId, feature, location, primaryTag, secondaryTag) VALUES %s", [ar,])

    except psycopg2.Error as e:
        print(e)
