import os
import psycopg2
import toJson
import json
import commonCode as cc


def lambda_handler(event, context):
    """
    Handler function for Lambda events
    Returns all of the cars in the database as JSON
    """
    # Get the platform: web or iOS
    platform = cc.get_queryString(event, "platform")
    if not platform in cc.valid_platforms:
        # Return an error to the client if a platform is not specified correctly
        msg = f"'platform' must be specified in the queryStringParameters header with a value from: {cc.valid_platforms}."
        reason = {"reason": msg}
        return cc.response_bad_request(json.dumps(reason))
    
    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                           os.environ["dbHost"], os.environ["dbPass"])
    
    # Return the list of cars
    if(conn != None):
        return cc.response_ok(json.dumps(get_car_all(conn, platform)))


def get_car_all(conn, platform):
    """
    Retrieves all cars from the database
    Returns the cars from the database as JSON
    
    TODO: vary the returned JSON depending on the platform
    """
    return cc.db_get_all(conn, "car")
