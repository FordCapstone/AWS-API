import json
import psycopg2
import os

def lambda_handler(event, context):

    ar = tuple(event)
    conn = dbConnection()
    insertAr(conn, ar)
  

def insertAr(conn, ar):
    """Inserts an AR feature into the AR table

    Arguments: 
        conn: A connection to the database
        ar: A tuple containing the AR feature data

    """
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS ar 
            (arId SERIAL NOT NULL, 
            carId int4 NOT NULL, 
            feature varchar(100) NOT NULL, 
            PRIMARY KEY (arId));""")  

            cursor.execute("INSERT INTO ar (carId, feature) VALUES %s", [ar,])

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