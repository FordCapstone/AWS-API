import json
import commonCode as cc
import boto3
import os

lambdaClient = boto3.client('lambda')

def lambda_handler(event, context):
    
    #Try to retrieve the appropriate data from the body. If an error occurs, send a 400 error code as a response
    try:
        body = json.loads(event["body"])
        make = body["make"]
        model = body["model"]
        year = body["year"]
        ownerManual = body["ownermanual"]
    except:
        return cc.response_bad_request("Invalid body format. Please follow formatting instructions.")
    
    #Create a tuple containing the vehicle data
    car = [make, model, year, ownerManual]

    #Call the writeCar function and get a response containing the carId of the row written to the DB
    writeCarResponse = lambdaClient.invoke(
            FunctionName= os.environ['writeCarArn'],
            InvocationType='RequestResponse',
            LogType='None',
            Payload=json.dumps(car),
        )

    print(writeCarResponse)

    #Check the writeCarResponse to see if the car was successfully written to the database
    if(isinstance(writeCarResponse, int)):
        #Call generateTags Lambda to generate tags from the linked owner's manual and wait for a response
        payload = {"carId": response, "manualUrl": ownerManual}
        generateTagsResponse = lambdaClient.invoke(
            FunctionName= os.environ['generateTagsArn'],
            InvocationType='RequestResponse',
            LogType='None',
            Payload=json.dumps(payload),
        )
    else:
        #Return the error message from attempting to write the car to the database
        return writeCarResponse


    #Check the response from generating the tags
    if(isinstance(generateTagsResponse, int)):
        #Call generateTags Lambda to generate tags from the linked owner's manual and wait for a response
        payload = {"carId": response, "manualUrl": ownerManual}
        writeTagsResponse = lambdaClient.invoke(
            FunctionName= os.environ['writeTagsArn'],
            InvocationType='RequestResponse',
            LogType='None',
            Payload=json.dumps(payload),
        )
    else:
        #Return the error message from attempting to write the car to the database
        return generateTagsResponse

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

    
        