import json
import psycopg2
import os

def lambda_handler(event, context):

    tag = tuple(event)
    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                         os.environ["dbHost"], os.environ["dbPass"])
    insertTag(conn, tag)
  

def insertTag(conn, tag):
    """Inserts a tag into the tag table

    Arguments: 
        conn: A connection to the database
        tag: A tuple containing the tag data
    """
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS tag 
            (tagId SERIAL NOT NULL, 
            carId int4 NOT NULL, 
            name varchar(100) NOT NULL, 
            primaryTag bool NOT NULL, 
            page int4, 
            primaryTagId int4, 
            PRIMARY KEY (tagId));""")  

            cursor.execute("INSERT INTO tag (carId, name, primaryTag, page, primaryTagId) VALUES %s", [tag,])

    except psycopg2.Error as e:
        print(e)