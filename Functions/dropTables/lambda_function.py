import os
import psycopg2
import json
import commonCode as cc


def lambda_handler(event, context):
    
    #Create a connection to the database
    conn = cc.db_connect(os.environ["dbName"], os.environ["dbUser"],
                           os.environ["dbHost"], os.environ["dbPass"])
    
    # Drop all the tables
    try:
        with conn, conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS media CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS tag CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS ar_tag CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS car CASCADE;")
    except psycopg2.Error as e:
        print(f"Error: {e}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Called dropTables.')
    }
