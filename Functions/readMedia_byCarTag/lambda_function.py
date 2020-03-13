import os
import psycopg2
import json
import commonCode as cc


def lambda_handler(event, context):
    """
    Handler function for Lambda events
    Returns all of the media in the database for a specified car and tag as JSON
    """
    # Get the carid
    carId = cc.get_queryString(event, "carid")
    try:
        if not carId.isdigit():
            raise Exception
    except Exception as e:
        # Return an error to the client if a carId is not specified correctly
        msg = f"'carid' must be specified in the queryStringParameters header and must be an integer."
        reason = {"reason": msg}
        return cc.response_bad_request(json.dumps(reason))
    
    # Get the tagid
    tagId = cc.get_queryString(event, "tagid")
    try:
        if not tagId.isdigit():
            raise Exception
    except Exception as e:
        # Return an error to the client if a tagId is not specified correctly
        msg = f"'tagid' must be specified in the queryStringParameters header and must be an integer."
        reason = {"reason": msg}
        return cc.response_bad_request(json.dumps(reason))
    
    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                           os.environ["dbHost"], os.environ["dbPass"])
    
    # Return the list of media
    if(conn != None):
        return cc.response_ok(json.dumps(get_media_by_car_tag(conn, carId, tagId)))


def get_media_by_car_tag(conn, carId, tagId):
    """
    Retrieves all AR info for a specific carId from the database
    Returns all the AR info as JSON
    """
    return cc.db_get_where(conn, "media", ["carid", "primarytag", "secondarytag"], [carId, tagId, tagId], [False, True])
