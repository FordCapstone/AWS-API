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
from psycopg2 import sql
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


def db_get_where(conn, table, columns, values, use_or=[]):
    """
    Gets all rows from the specified table that match the given conditions.
    The columns and values lists should be the same length.
    A value of True in the use_or list indicates that OR should be used to
    join those 2 constraints instead of AND.
    Returns all the matched rows formatted as JSON.
    """
    # Clean up the parameters
    pairs = min(len(columns), len(values))
    columns = columns[:pairs]
    values = values[:pairs]
    use_or.extend([False] * max(0, (pairs - 1) - len(use_or)))

    # Format the SELECT constraints
    constraint_list = ["{} = %s" for i in range(pairs)]

    # Add in 'AND' or 'OR' between the constraints
    constr_str = sql.SQL("").join([sql.SQL("".join(["(" if i < (pairs - 1) and use_or[i] else "", constraint_list[i], ")" if i > 0 and use_or[i-1] else "", "" if i >= (pairs - 1) else (" OR " if use_or[i] else " AND ")])).format(sql.Identifier(columns[i])) for i in range(pairs)])

    # Construct the query string
    query_str = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table))
    if pairs > 0:
        # Construct the WHERE constraints
        query_str = sql.SQL("").join([query_str, sql.SQL(" WHERE "), constr_str, sql.SQL(";")])
    else:
        # No constraints, get all rows
        query_str = sql.SQL("").join([query_str, sql.SQL(";")])

    # Attempt to get values from the database in the specified table
    print(f"DEBUG: {query_str.as_string(conn)}")
    results = None
    try:
        cursor = conn.cursor()
        final_query = cursor.mogrify(query_str, values)
        print("DEBUG: the query being executed: ", final_query)
        cursor.execute(final_query)
        results = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
    except psycopg2.Error as e:
        print(e)

    # Check that the database returned values
    if(results == None):
        print(f"ERROR: Unable to fetch any values from the table: {table}")
        return json.loads([])
    else:
        results_json = json.loads(to_json(colnames, results))
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


def to_json(columnNames, data):
    """ Takes in a list of column names and row data and converts to JSON format
    
    Args:
        columnNames (list): List of strings that represent the column names of the data
        data (list(tuple))): List of tuples, where each tuple is a row of data
    Returns:
         A JSON formatted string that represents the row data with column name keys
    """
    items = [dict(zip([key for key in columnNames], row)) for row in data]
    return json.dumps(items) 


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
    msg.update({"statusCode": statusCode, "body": body, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}})
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