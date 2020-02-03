"""
commonCode is a AWS Lambda layer created to support the API of
TeamFord's Capstone project. (TeamFord Augmented Reality Owner's Manual)

This file contains common variables and functions that are used across
multiple Lambda functions.
"""
#
# Import staements
#
import collections
import psycopg2


#
# Const / static variables
#
valid_platforms = ["web", "ios"]


#
# Functions / classes
#
def dbConnection(dbName, dbUser, dbHost, dbPass):
    """
    Makes a connection the database specified by the parameters.
    Returns the connection to the database.
    """
    try:
        conn = psycopg2.connect(f"dbname={dbName} user={dbUser} host={dbHost} password={dbPass}")
        return conn
    except psycopg2.Error as e: 
        print(e)


def get_platform(event):
    """
    Gets the target platform for the API call,
    where event is the Lambda event object passed to the handler.
    Returns the platform as a string if a valid one is found.
    Otherwise returns an empty string.
    """
    platform = ""
    
    # Check if a platform is specified
    if "queryStringParameters" in event and event["queryStringParameters"] and "platform" in event["queryStringParameters"]:
        platform = event["queryStringParameters"]["platform"]
        
        # Make sure the platform is valid
        if not platform in valid_platforms:
            return ""
    
    return platform


#
# HTTP response functions
#
def response_ok(body, other_info={}):
    """
    Creates a HTTP 200 (OK) response message.
    Adds other_info (dict) to the response if it is specified.
    Returns the HTTP response formatted for Lambda.
    """
    response = other_info.copy() if isinstance(other_info, collections.Mapping) else {}
    response.update({"statusCode": 200, "body": body})
    return response


def response_bad_request(reason, other_info={}):
    """
    Creates a HTTP 400 (Bad Request) response message.
    Adds other_info (dict) to the response if it is specified.
    Returns the HTTP response formatted for Lambda.
    """
    response = other_info.copy() if isinstance(other_info, collections.Mapping) else {}
    response.update({"statusCode": 400, "body": reason})
    return response