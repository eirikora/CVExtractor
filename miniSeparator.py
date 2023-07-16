import json

import re

def headingToRegex(heading):
    # Trim space before and after
    heading = heading.strip()
    if heading.endswith(":"):
        heading = heading.rstrip(":")
    if ":" in heading:
        # Remove any trailing colons as will be added as option at end
        heading = heading.split(":")[0] + "¤SPACE¤:" + "¤KEEP_ANYTHING¤"
    # Find generic elements in heading
    heading = re.sub("[ \n\t]", "¤SPACE¤", heading)
    heading = heading.replace("*", "¤STAR¤")
    heading = heading.replace(")", "¤CLOSEBRACKET¤")
    heading = heading.replace("(", "¤OPENBRACKET¤")
    heading = heading.replace("?", "¤QUESTION¤")
    heading = re.sub("^[0-9a-zA-Z]\\)", "¤alphanumeric¤\\)", heading)
    heading = re.sub("\\.[0-9]", "¤NUMBER¤", heading)
    heading = re.sub("[0-9]", "¤NUMBER¤", heading)
    # Remove duplicates
    heading = re.sub("(¤SPACE¤)+", "¤SPACE¤", heading)
    heading = re.sub("(¤NUMBER¤)+", "¤NUMBER¤", heading)
    # Insert correct Regex
    heading = heading.replace("¤SPACE¤", "\\s*")
    heading = heading.replace("¤NUMBER¤", "[\\.0-9]+")
    heading = heading.replace("¤STAR¤", "\\*")
    heading = heading.replace("¤CLOSEBRACKET¤", "\\)")
    heading = heading.replace("¤OPENBRACKET¤", "\\(")
    heading = heading.replace("¤QUESTION¤", "\\?")
    heading = heading.replace("¤alphanumeric¤", "[0-9a-zA-Z]")
    heading = heading.replace("¤KEEP_ANYTHING¤", "(.*)")
    if ":" not in heading:
        # Add optional end colon for most headings
        heading = heading + ":*"
    heading = "(^|[^T]¤\\n|[^¤]\\n)\s?\s?\s?(" + heading + ")[ ]*(\\n|$)" # Match start of doc or heading right after lineshift that is NOT preceded by ¤HEADSTAR[T¤] (to avoid rematching) and expect only space until end of line(evt. doc)
    return heading


# Specify the file path
file_path = "separator_request.json"

# Load the JSON data from the file
with open(file_path, "r") as file:
    req_body = json.load(file)

headingmap = req_body.get('headingmap')
textToSeparate = req_body.get('texttoseparate')

# Find all buckets and set them up. Calculate regexmap
allbuckets = []
regexmap = {}
for (heading, buckets) in headingmap.items():
    for bucket in buckets:
        if bucket not in allbuckets:
            allbuckets.append(bucket)
    regexforheading = headingToRegex(heading)
    regexmap[regexforheading] = buckets
# print(allbuckets)

bucketstore = {}
for bucket in allbuckets:
    bucketstore[bucket] = ""

# print(bucketstore)
# print(regexmap)

# Match all the heading regex against the textfile to identify the location of the headings
for OverskriftRegex in regexmap.keys():
    if "Bakgrunn" in OverskriftRegex:
        print("TRYING:"+OverskriftRegex)
    buckets = json.dumps(regexmap[OverskriftRegex])
    textToSeparate = re.sub(OverskriftRegex, "\g<1>\n¤HEADSTART¤" + "\g<2>" + "¤BUCKETINFO¤" + buckets + "¤HEADEND¤\n", textToSeparate) # The heading is now match group 2. Match group is what we tested BEFORE heading.
    
print(textToSeparate)

def writeBlockToBuckets(theblock):
    # Clean up the  text block so that it can be stored
    textHeading = re.sub("\n", "", theblock)
    textHeading = re.sub("¤HEADSTART¤(.+)¤BUCKETINFO¤.*¤HEADEND¤.*$", "\g<1>", textHeading)
    # info "HEADING:" + textHeading
    targetbucketstring = re.sub("\n", "", theblock)
    targetbucketstring = re.sub("^.+¤BUCKETINFO¤(.*)¤HEADEND¤.*$", "\g<1>", targetbucketstring)
    targetbuckets = json.loads(targetbucketstring)
    # info "TARGET BUCKETS:" + targetbuckets
    textBody = re.sub("\n", "¤LF¤", theblock)
    textBody = re.sub("¤HEADSTART¤.*¤BUCKETINFO¤.*¤HEADEND¤", "", textBody)
    textBody = textBody.replace("¤LF¤", "\n")
    # info "BODY:" + textBody
    finalBlock = textHeading + textBody + "\n"
    # Write the last text block to the selected buckets
    #print("DUMP " + finalBlock + " to " + str(targetbuckets))
    for bucket in targetbuckets:
        bucketstore[bucket] += finalBlock

# Separate the text file: Identify all text blocks and write them to the right buckets
insideBlock = False
blockContent = ""
for textline in textToSeparate.split("\n"):
    if insideBlock:
        if "¤HEADSTART¤" in textline:
            # Skriv blokken til buckets som er ønsket
            writeBlockToBuckets(blockContent)
            # Tøm tekstblokken og start på nytt med denne overskriftslinjen
            blockContent = textline + "\n";
        else:
            # Just another line of text to keep...
            blockContent = blockContent + textline + "\n"
    else:
        if "¤HEADSTART¤" in textline:
            # Vi starter en ny tekstblokk
            insideBlock = True
            blockContent = blockContent + textline + "\n"
            
if insideBlock:
    # Skriv også siste blokken til buckets som er ønsket
    writeBlockToBuckets(blockContent)
    
print(bucketstore)
