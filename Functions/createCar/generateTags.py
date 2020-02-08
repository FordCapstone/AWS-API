import PyPDF2 
import requests
import boto3
import io
import json

#List of tags to ignore when parsing Owner's Manual tags
ignoreTags = ["Table of Contents",
"Copyright",
"About This Manual",
"Symbols Glossary",
"SYMBOL GLOSSARY",
"EXPORT UNIQUE",
"Data Recording",
"California Proposition",
"Perchlorate",
"Ford Credit",
"Replacement Parts Recommendation",
"Special Notices",
"Mobile Communications Equipment",
"Export Unique Options",
"General Information",
"Principles of Operation",
"Principle of Operation",
"Conditions of Operation",
"Index",
"Appendices",
"End User License Agreement",
"Type Approvals",
"Congratulations",
"Exceptions",
"The Better Business Bureau",
"In California",
"Utilizing The Mediation Or Arbitration Program",
"General Hints",
"Locations",
"Technical Specifications",
"Troubleshooting",
"From Inside Your Vehicle",
"From Outside Your Vehicle"
"Plastic",
"Blank Page"]


def lambda_handler(event, context):
    carId = event["carId"]
    url = event["manualUrl"]
    tags = loadPdf(carId, url)
    return tags

def loadPdf(carId, url):
    """[summary]
    
    Args:
        carId ([type]): [description]
        manualUrl ([type]): [description]
    """

    response = requests.get(url)

    with io.BytesIO(response.content) as open_pdf_file:
        pdf = PyPDF2.PdfFileReader(open_pdf_file)
        return parseTags(pdf, carId)
    

def cleanTag(tag):
    """Reformats a tag to remove specified characters,
    convert to title case, strip whitespaces, and check if the 
    tag is an ignored tag.
    
    Args:
        tag (string): The tag to format
    
    Returns:
        string: the formatted tag, False if the tag is ignored
    """

    #Check if the tag contains any of the ignored tags
    for ignoredTag in ignoreTags:
        if ignoredTag.lower() in tag.lower():
            return False

    #Reformat the tag to remove anything in parenthesis
    tag = tag.split('(', 1)[0]
    #Remove any copyright, or other legal chracters
    tag = tag.replace('™', '')
    tag = tag.replace('©', '')
    tag = tag.replace('®', '')
    tag = tag.replace('?', '')
    #Convert the tag to title case
    tag = tag.title()
    #Strip any leading or trailing whitespace
    tag = tag.strip()

    #If after all of the formatting, the tag is not empty, return the formatted tag
    if(tag != ""):
        return tag
    else:
        return False
  
def parseTags(pdf, carId): 
    """[summary]
    
    Args:
        pdf ([type]): [description]
    """
    outline = pdf.getOutlines()

    tags = list()
    tagsSet = set()

    #This works for new version of owners manual
    currPrimaryTag = dict()
    for dest in outline:
        if not isinstance(dest, list):
            cleanedTag = cleanTag(dest.title)
            if cleanedTag != False and cleanedTag not in tagsSet:
                #Create a dictionary to be stored in JSON format as a top level entry in the tags list
                currPrimaryTag["carId"] = carId
                currPrimaryTag["name"] = cleanedTag
                currPrimaryTag["primaryTag"] = True
                currPrimaryTag["page"] = pdf.getDestinationPageNumber(dest) + 1
                currPrimaryTag["primaryTagId"] = None
                currPrimaryTag["secondaryTags"] = list()
                tagsSet.add(cleanedTag)
        else:
            for d in dest:
                if not isinstance(d, list):
                    cleanedTag = cleanTag(d.title)
                    if cleanedTag != False and cleanedTag not in tagsSet and len(currPrimaryTag) != 0:
                        secondaryTag = dict()
                        secondaryTag["carId"] = carId
                        secondaryTag["name"] = cleanedTag
                        secondaryTag["primaryTag"] = False
                        secondaryTag["page"] = pdf.getDestinationPageNumber(d) + 1
                        currPrimaryTag["secondaryTags"].append(secondaryTag.copy())
                        tagsSet.add(cleanedTag)
            tags.append(currPrimaryTag.copy())

    return tags
