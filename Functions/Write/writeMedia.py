import json
import psycopg2
import os

def lambda_handler(event, context):

    media = tuple(event)
    conn = dbConnection()
    insertMedia(conn, media)
  

def insertMedia(conn, media):
    """Inserts media data into the media table

    Arguments: 
        conn: A connection to the database
        media: A tuple containing the media data

    """
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS media 
            (mediaId SERIAL NOT NULL, 
            carId int4 NOT NULL, 
            name varchar(100),
            type varchar(30) NOT NULL,
            link varchar(250) NOT NULL,
            primaryTag int4 NOT NULL,
            secondaryTag int4,
            PRIMARY KEY (mediaId));""")  

            cursor.execute("INSERT INTO media (carId, name, type, link, primaryTag, secondaryTag) VALUES %s", [media,])

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