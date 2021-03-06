import requests
import json
import commonCode as cc
import boto3
import os
import re

lambdaClient = boto3.client('lambda')

def lambda_handler(event, context):
    
    #Try to retrieve the appropriate data from the body. If an error occurs, send a 400 error code as a response
    try:
        body = json.loads(event["body"])
        make = body["make"].title()
        model = body["model"].title()
        year = body["year"]
        icon = "https://owner.ford.com/ownerlibs/content/dam/assets/ford/vehicle/" + str(year) + "/" + str(year) + "-" + make.lower() + "-" + model.lower() + "-s.png"
    except Exception as e: 
        print(e)
        return cc.response_bad_request("Invalid body format. Please follow formatting instructions.")

    if(int(year) < 2005):
        return cc.response_bad_request("Cannot add vehicle prior to 2005.")
    
    try:
        #Build the url to retrieve the PDFs for this vehicle
        url = "https://www.fleet.ford.com/aemservices/cache/ownermanuals?" "year="+ str(year) + "&" + "make=" + make.lower() + "&" + "model=" + model.title() + "&country=USA&language=EN-US"
        page = requests.get(url)
        data = json.loads(page.text)

        #Parse the returned JSON to find the latest version of the owner's manual
        ownerManual = ""

        pattern = re.compile("Owner's Manual Printing \d")
        for item in data:
            if(pattern.match(item["title"])):
                ownerManual = item["link"]
        print(ownerManual)
    except Exception as e: 
        print(e)
        return cc.response_bad_request("Invalid vehicle make, model, or year.")
    
    #Create a tuple containing the vehicle data
    car = [make, model, year, ownerManual, icon]

    #Call the writeCar function and get a response containing the carId of the row written to the DB
    writeCarResponse = lambdaClient.invoke(
            FunctionName= os.environ['writeCarArn'],
            InvocationType='RequestResponse',
            LogType='None',
            Payload=json.dumps(car),
        )

    writeCarResponse = writeCarResponse['Payload'].read().decode('utf-8').strip('\"')
    print(writeCarResponse)

    #Check the writeCarResponse to see if the car was successfully written to the database
    try:
        #Try to convert the response to an int. If it fails, it means the database write failed.
        carId = int(writeCarResponse)
        #Call generateTags Lambda to generate tags from the linked owner's manual and wait for a response
        payload = {"carId": carId, "manualUrl": ownerManual}
        generateTagsResponse = lambdaClient.invoke(
            FunctionName= os.environ['generateTagsArn'],
            InvocationType='RequestResponse',
            LogType='None',
            Payload=json.dumps(payload),
        )
        generateTagsResponse = generateTagsResponse['Payload'].read().decode('utf-8').strip('\"')
        print(generateTagsResponse)
    except:
        #Return the error message from attempting to write the car to the database
        return cc.response_bad_request(writeCarResponse)


    #Check the response from generating the tags
    try:
        list(generateTagsResponse)
        #Call writeTags Lambda to write the generated tags to the database
        writeTagsResponse = lambdaClient.invoke(
            FunctionName= os.environ['writeTagsArn'],
            InvocationType='RequestResponse',
            LogType='None',
            Payload=json.dumps(generateTagsResponse),
        )
    except:
        #Return the error message from attempting to write the car to the database
        return cc.response_bad_request("Unable to generate tags for the vehicle. Ensure the link to the owner's manual is the correct PDF")
        
    #If all of the writes were successfuly, return a 200 response code.
    return cc.response_ok("Successfully created new vehicle")


    #TODO: Write AR features after writeMedia has been completed and AR tagging writing is next.
    """
    #Check the response from writing the tags
    if(isinstance(writeTagsResponse, int)):
        #Call generateTags Lambda to generate tags from the linked owner's manual and wait for a response
        payload = {"carId": response, "manualUrl": ownerManual}
        writeArResponse = lambdaClient.invoke(
            FunctionName= os.environ['writeArArn'],
            InvocationType='RequestResponse',
            LogType='None',
            Payload=json.dumps(payload),
        )
        return writeArResponse
    else:
        #Return the error message from attempting to write the car to the database
        return writeTagsResponse
    """
