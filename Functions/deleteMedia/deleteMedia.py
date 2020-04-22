import os
import psycopg2
from psycopg2 import sql
import json
import commonCode as cc


def lambda_handler(event, context):
    """
    Handler function for Lambda events
    Deletes a media entry from the database
    """
    # Get the mediaId
    mediaId = cc.get_queryString(event, "mediaid")
    try:
        if not mediaId.isdigit():
            raise Exception
    except Exception as e:
        # Return an error to the client if a mediaId is not specified correctly
        msg = f"'mediaid' must be specified in the queryStringParameters header and must be an integer."
        reason = {"reason": msg}
        return cc.response_bad_request(json.dumps(reason))
    
    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                           os.environ["dbHost"], os.environ["dbPass"])
    
    # Delete the media entry
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute(sql.SQL("DELETE FROM {} WHERE mediaid = %s;").format(sql.Identifier("media")), [mediaId])
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return cc.response_bad_request(json.dumps(json.dumps("An error occured when removing the media entry.")))
    
    return cc.response_ok(json.dumps(f'Removed the media entry for mediaid: {mediaId}.'))
