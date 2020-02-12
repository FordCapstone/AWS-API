import json
import psycopg2
import psycopg2.extras
import os
import commonCode as cc

def lambda_handler(event, context):

    tags = json.loads(event)
    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                         os.environ["dbHost"], os.environ["dbPass"])
    insertTags(conn, tags)


def insertTags(conn, tags):
    """Inserts the primary and secondary tags into the database
    
    Args:
        conn: a connection to the database
        tags (dict): A dictionary containing the primary and secondary tags
    """
    for primaryTag in tags:
        tag = (primaryTag["carId"], primaryTag["name"], primaryTag["primaryTag"], primaryTag["page"], primaryTag["primaryTagId"])
        tagId = insertPrimaryTag(conn, tag)
        secondaryTags = list()
        for secondaryTag in primaryTag["secondaryTags"]:
            tag = (secondaryTag["carId"], secondaryTag["name"], secondaryTag["primaryTag"], secondaryTag["page"], tagId)
            secondaryTags.append(tag)
        insertSecondaryTags(conn, secondaryTags)

def insertPrimaryTag(conn, tag):
    """Inserts a tag into the tag table

    Arguments: 
        conn: A connection to the database
        tag: A tuple containing the tag data
    """
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("DROP TABLE tag;")
            cursor.execute("""CREATE TABLE IF NOT EXISTS tag 
            (tagId SERIAL NOT NULL, 
            carId int4 NOT NULL, 
            name varchar(100) NOT NULL, 
            primaryTag bool NOT NULL, 
            page int4, 
            primaryTagId int4, 
            PRIMARY KEY (tagId),
            FOREIGN KEY (carId) REFERENCES car (carId),
            FOREIGN KEY (primaryTagId) REFERENCES tag (tagId));;""")  

            cursor.execute("INSERT INTO tag (carId, name, primaryTag, page, primaryTagId) VALUES %s RETURNING tagId;""", [tag,])

            #Return the carId of the row just inserted
            return cursor.fetchone()[0]

    except psycopg2.Error as e:
        print("Unable to insert primary tag into database")

def insertSecondaryTags(conn, tags):
    """Inserts a tag into the tag table

    Arguments: 
        conn: A connection to the database
        tags: A tuple containing the secondary tag data
    """
    try:
        with conn, conn.cursor() as cursor:
            psycopg2.extras.execute_values(cursor, "INSERT INTO tag (carId, name, primaryTag, page, primaryTagId) VALUES %s", tags)

    except psycopg2.Error as e:
        print("Unable to insert secondary tags into database")

