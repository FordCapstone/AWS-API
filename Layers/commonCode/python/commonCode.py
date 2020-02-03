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
import toJson
import json


#
# Const / static variables
#
valid_platforms = ["web", "ios"]


#
# Functions / classes
#
def db_connect(dbName, dbUser, dbHost, dbPass):
    """
    Makes a connection the postgres database specified by the parameters.
    Returns the connection to the database.
    """
    try:
        conn = psycopg2.connect(f"dbname={dbName} user={dbUser} host={dbHost} password={dbPass}")
        return conn
    except psycopg2.Error as e: 
        print(e)


def db_get_all(conn, table):
    """
    Gets all of the rows in the specified table.
    Returns all the rows formatted as JSON.
    """
    return db_get_where(conn, table, [], [])


def db_get_where(conn, table, columns, values):
    """
    Gets all rows from the specified table that match the given conditions.
    The columns and values lists should be the same length.
    Returns all the rows formatted as JSON.
    """
    # Format the SELECT constraints
    constr = list(zip(columns, values))
    pairs = len(constr)

    # Construct the query string
    query_str = f"SELECT * FROM {table}"
    if pairs > 0:
        # Construct the WHERE constraints
        query_str = query_str + " WHERE " + " AND ".join([" = ".join([t[0], f"'{str(t[1])}'" if isinstance(t[1], str) else str(t[1])]) for t in constr]) + ";"
    else:
        # No constraints, get all rows
        query_str = query_str + ";"

    # Attempt to get values from the database in the specified table
    try:
        cursor = conn.cursor()
        cursor.execute(query_str)
        results = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
    except psycopg2.Error as e:
        print(e)

    # Check that the database returned values
    if(results == None):
        print(f"ERROR: Unable to fetch any values from the table: {table}")
        return json.loads([])
    else:
        results_json = json.loads(toJson.ConvertToJson(colnames, results))
        return results_json


def get_queryString(event, parameter):
    """
    Gets the specified parameter from the queryStringParameters header,
    where event is the Lambda event object passed to the handler.
    Returns the value if one is found.
    Otherwise returns an empty string.
    """
    qSP_str = "queryStringParameters"
    value = ""
    
    # Check if a platform is specified
    if qSP_str in event and event[qSP_str] and parameter in event[qSP_str]:
        value = event[qSP_str][parameter]
    
    return value


#
# HTTP response functions
#
def response(statusCode, body, other_info):
    """
    Creates a HTTP response message with the given statusCode and body.
    Adds any other_info to the response.
    Returns the HTTP response formatted for Lambda.
    """
    msg = other_info.copy() if isinstance(other_info, collections.Mapping) else {}
    msg.update({"statusCode": statusCode, "body": body})
    return msg


def response_ok(body, other_info={}):
    """
    Creates a HTTP 200 (OK) response message.
    Adds other_info (dict) to the response if it is specified.
    Returns the HTTP response formatted for Lambda.
    """
    return response(200, body, other_info if isinstance(other_info, collections.Mapping) else {})


def response_bad_request(reason, other_info={}):
    """
    Creates a HTTP 400 (Bad Request) response message.
    Adds other_info (dict) to the response if it is specified.
    Returns the HTTP response formatted for Lambda.
    """
    return response(400, reason, other_info if isinstance(other_info, collections.Mapping) else {})