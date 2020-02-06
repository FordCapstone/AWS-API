import json
import psycopg2
import os

def lambda_handler(event, context):

    ar_tag = tuple(event)
    conn = dbConnection()
    insertArTag(conn, ar_tag)
  

def insertArTag(conn, ar_tag):
    """Inserts an AR feature tag data into the ar_tag table

    Arguments: 
        conn: A connection to the database
        ar_tag: A tuple containing the AR feature tagging data

    """
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS ar_tag 
            (arId int4 NOT NULL, 
            tagId int4 NOT NULL, 
            PRIMARY KEY (arId, tagId));""")  

            cursor.execute("INSERT INTO ar_tag VALUES %s", [ar_tag,])

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