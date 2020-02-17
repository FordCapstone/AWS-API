import os
import psycopg2
import json
import commonCode as cc


def lambda_handler(event, context):
    """
    Handler function for Lambda events
    Returns all of the media in the database for a specified car as JSON
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
    
    # Get the optional tagNames
    tagNames = cc.get_queryString(event, "tagnames")
    
    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                           os.environ["dbHost"], os.environ["dbPass"])
    
    # Return the list of media
    if(conn != None):
        if tagNames and tagNames == "true":
            mediaJson = get_media_by_car(conn, carId)
            tagJson = get_tag_by_car(conn, carId)
            
            tagDict = {td["tagid"]:td["name"] for td in tagJson}
            
            for md in mediaJson:
                md["primarytagname"] = tagDict[md["primarytag"]]
                md["secondarytagname"] = "N/A" if md["secondarytag"] == None else tagDict[md["secondarytag"]]
            
            return cc.response_ok(json.dumps(mediaJson))
        
        # Get the media without the tag names
        return cc.response_ok(json.dumps(get_media_by_car(conn, carId)))


def get_media_by_car(conn, carId):
    """
    Retrieves all media for a specific carId from the database
    Returns all the media entries as JSON
    """
    return cc.db_get_where(conn, "media", ["carid"], [carId])


def get_tag_by_car(conn, carId):
    """
    Retrieves all Tags for a specific carId from the database
    Returns all the Tags as JSON
    """
    return cc.db_get_where(conn, "tag", ["carid"], [carId])
