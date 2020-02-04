import os
import psycopg2
import toJson
import json
import commonCode as cc


def lambda_handler(event, context):
    """
    Handler function for Lambda events
    Returns all of the AR and Tag information for a specific car
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
    
     # Return the list of ar features and tags
    if(conn != None):
        return cc.response_ok(json.dumps([get_ar_by_car(conn, carId), get_tag_by_car(conn, carId)]))


def get_ar_by_car(conn, carId):
    """
    Retrieves all AR info for a specific carId from the database
    Returns all the AR info as JSON
    """
    return cc.db_get_where(conn, "ar", ["carId"], [carId])


def get_tag_by_car(conn, carId):
    """
    Retrieves all Tags for a specific carId from the database
    Returns all the Tags as JSON
    """
    return cc.db_get_where(conn, "tag", ["carId"], [carId])
