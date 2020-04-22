import os
import psycopg2
from psycopg2 import sql
import json
import commonCode as cc


def lambda_handler(event, context):
    """
    Handler function for Lambda events
    Removes a specific car and all associated data from the database
    """
    # Get the carId
    carId = cc.get_queryString(event, "carid")
    try:
        if not carId.isdigit():
            raise Exception
    except Exception as e:
        # Return an error to the client if a carId is not specified correctly
        msg = f"'carid' must be specified in the queryStringParameters header and must be an integer."
        reason = {"reason": msg}
        return cc.response_bad_request(json.dumps(reason))
    
    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                           os.environ["dbHost"], os.environ["dbPass"])
    
    # Delete the car and all its data
    try:
        with conn, conn.cursor() as cursor:
            # Remove all the media for the car
            cursor.execute(sql.SQL("DELETE FROM {} WHERE carid = %s;").format(sql.Identifier("media")), [carId])
            
            # Remove all ar_tag entries for the car
            cursor.execute(sql.SQL("DELETE FROM {} USING ar WHERE ar.carid = %s AND ar.arid = ar_tag.arid;").format(sql.Identifier("ar_tag")), [carId])
            
            # Remove all the tags for the car
            cursor.execute("DELETE FROM tag WHERE carid = %s", [carId])
            
            # Remove all the ar tags for the car
            cursor.execute("DELETE FROM ar WHERE carid = %s", [carId])
            
            # Remove the car
            cursor.execute("DELETE FROM car WHERE carid = %s", [carId])
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return cc.response_bad_request(json.dumps(json.dumps("An error occured when removing the car.")))
    
    return cc.response_ok(json.dumps(f'Removed the car and all data for carid: {carId}.'))
