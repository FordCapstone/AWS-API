import os
import psycopg2
import json
import commonCode as cc


def lambda_handler(event, context):
    """
    Handler function for Lambda events
    Returns all of the available AR buttons
    """
    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                         os.environ["dbHost"], os.environ["dbPass"])
    
     # Return the list of ar features and tags
    if(conn != None):
        return cc.response_ok(json.dumps(getArButtons(conn)))


def getArButtons(conn):
    """
    Retrieves all AR buttons
    Returns all the Tags as JSON
    """
    return cc.db_get_all(conn, "ar_button")
