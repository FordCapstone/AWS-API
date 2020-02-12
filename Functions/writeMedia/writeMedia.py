import json
import psycopg2
import commonCode as cc
import os

def lambda_handler(event, context):

    #Try to retrieve the appropriate data from the body. If an error occurs, send a 400 error code as a response
    try:
        body = json.loads(event["body"])
        carId  = body["carId"]
        name = body["name"]
        type = body["type"]
        link = body["link"]
        primaryTag = body["primaryTag"]
        secondaryTag = body["secondaryTag"]
    except:
        return cc.response_bad_request("Invalid body format")
    
    #Create a tuple containing the media data
    media = (carId, name, type, link, primaryTag, secondaryTag)

    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                         os.environ["dbHost"], os.environ["dbPass"])
    return insertMedia(conn, media)
  

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
            PRIMARY KEY (mediaId),
            FOREIGN KEY (carId) REFERENCES car (carId),
            FOREIGN KEY (primaryTag) REFERENCES tag(tagId),
            FOREIGN KEY (secondaryTag) REFERENCES tag (tagId));""")  

            cursor.execute("INSERT INTO media (carId, name, type, link, primaryTag, secondaryTag) VALUES %s", [media,])

            #If all of the writes were successfuly, return a 200 response code.
            return cc.response_ok("Successfully added media to database")

    except psycopg2.Error as e:
        print(e)
        #If all of the writes were successfuly, return a 200 response code.
        return cc.response_bad_request(repr(e))