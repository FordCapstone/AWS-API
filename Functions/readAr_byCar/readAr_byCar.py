import os
import psycopg2
import json
import commonCode as cc


def lambda_handler(event, context):
    """
    Handler function for Lambda events
    Returns all of the AR information for a specific car
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
        return cc.response_ok(json.dumps(get_ar_by_car(conn, carId)))


def get_ar_by_car(conn, carId):
    """ Retrieves all AR features for a car
    Args:
        conn: The database connection
        carId: The id of the car
    Returns:
         The AR features
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT ar.ar_buttonid, ar.enabled, ar_button.feature, 
        ar_button.section, ar.location, ar.primaryTag, ar.secondaryTag, ar_button.image
        FROM ar
        INNER JOIN ar_button ON ar.ar_buttonid = ar_button.ar_buttonId
        WHERE ar.carId = %s;""", 
        (carId,))
        arFeatures = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
    except psycopg2.Error as e:
        print(e)
        return

    if(arFeatures == None):
        print("No AR features found!")
    else:
        arFeatures = json.loads(cc.to_json(colnames, arFeatures))
        return arFeatures
    return None
