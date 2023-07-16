import azure.functions as func
import logging
import os
import tempfile
import json
import base64
import mammoth
import quopri
import re
from bs4 import BeautifulSoup
from urllib.parse import unquote


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def headingToRegex(heading):
    # Trim space before and after
    heading = heading.strip()
    if heading.endswith(":"):
        heading = heading.rstrip(":")
    if ":" in heading:
        # Remove any trailing colons as will be added as option at end
        heading = heading.split(":")[0] + "¤SPACE¤:" + "¤KEEP_ANYTHING¤"
    # Escape characters that need escaping
    heading = heading.replace("/", "\/")
    heading = heading.replace("^", "\^")
    heading = heading.replace("[", "\[")
    heading = heading.replace("]", "\]")
    heading = heading.replace("-", "\-")

    # Find generic elements in heading
    heading = re.sub("[ \n\t]", "¤SPACE¤", heading)
    heading = heading.replace("*", "¤STAR¤")
    heading = heading.replace(")", "¤CLOSEBRACKET¤")
    heading = heading.replace("(", "¤OPENBRACKET¤")
    heading = heading.replace("?", "¤QUESTION¤")
    heading = re.sub("^[0-9a-zA-Z]\\)", "¤alphanumeric¤\\)", heading)
    heading = re.sub("\\.[0-9]", "¤NUMBER¤", heading)
    heading = re.sub("[0-9]", "¤NUMBER¤", heading)
    heading = heading.replace(".", "\.")
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
    # heading = "(^|[^T][^¤]\\n)\s?\s?\s?(" + heading + ")[ ]*(\\n|$)" # Match start of doc or heading right after lineshift that is NOT preceded by ¤HEADSTAR[T¤] (to avoid rematching) and expect only space until end of line(evt. doc)
    # return heading
    heading = "(^|[^T]¤\\n|[^¤]\\n)\s?\s?\s?(" + heading + ")[ ]*(\\n|$)" # Match start of doc or heading right after lineshift that is NOT preceded by ¤HEADSTAR[T¤] (to avoid rematching) and expect only space until end of line(evt. doc)
    return heading

bucketstore = {}

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
        if finalBlock not in bucketstore[bucket]:
            bucketstore[bucket] += finalBlock

@app.route(route="DocSeparator", auth_level=func.AuthLevel.ANONYMOUS)
def DocSeparator(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('DocSeparator trigger function processed a request.')
    # logging.info('Request is:'+str(req.get_body()))

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
             "Could not find request body in json format. Please try again!",
             status_code=400
        )
    
    if not 'headingmap' in req_body or len(req_body['headingmap']) == 0:
        return func.HttpResponse(
             "Could not find a valid headingmap in the request. Please try again!",
             status_code=400
        )
    
    if not 'texttoseparate' in req_body or len(req_body['texttoseparate']) == 0:
        return func.HttpResponse(
             "Could not find a valid texttoseparate in the request. Please try again!",
             status_code=400
        )
    
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

    for bucket in allbuckets:
        bucketstore[bucket] = ""

    # print(bucketstore)
    logging.info(str(regexmap))

    # Match all the heading regex against the textfile to identify the location of the headings
    for OverskriftRegex in regexmap.keys():
        buckets = json.dumps(regexmap[OverskriftRegex])
        textToSeparate = re.sub(OverskriftRegex, "\g<1>¤HEADSTART¤" + "\g<2>" + "¤BUCKETINFO¤" + buckets + "¤HEADEND¤\n", textToSeparate) # The heading is now match group 2. Match group is what we tested BEFORE heading.
        
    logging.info("MATCHED:"+textToSeparate)

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

    return func.HttpResponse(json.dumps(bucketstore), mimetype="application/json", status_code=200)

def decode_mime_string(s):
    if '=' in s:
        start = s.find('=')
        prefix = s[:start]
        #print(prefix)
        mimestring = s[start:]
        #print(mimestring)
        mime_elements = mimestring.split('=_=')
        #print(mime_elements)
        decoded_text = ''
        for submime in mime_elements:
            charset, encoded_text = submime.strip('=_').strip('_=').split('_Q_', 1)
            #decoded_text += quopri.decodestring(encoded_text.replace('_', '=')).decode(charset).replace('=', ' ')
            decoded_text += quopri.decodestring(encoded_text).decode(charset)
        return prefix + decoded_text
    else:
        return s


@app.route(route="MimeDecode", auth_level=func.AuthLevel.ANONYMOUS)
def MimeDecode(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('MimeDecode trigger function processed a request.')

    mime_string = req.params.get('mime_string')
    if not mime_string:
        try:
            req_body = req.get_json()
        except ValueError:
            mime_string = str(req.get_body(), 'utf-8')
        else:
            mime_string = req_body.get('mime_string')

    if mime_string:
        decoded_string = decode_mime_string(mime_string) # Now also handles prefixed mime-strings
        return func.HttpResponse(decoded_string, mimetype="text/plain;charset=UTF-8", status_code=200)
    else:
        return func.HttpResponse(
             "Please pass a mime_string on the query string or in the request body",
             status_code=400
        )

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route(route="Word2Text", auth_level=func.AuthLevel.ANONYMOUS)
def Word2Text(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Word2Text trigger function processed a request.')

    file_content = b''
    file_name = ''
    if 'content' not in req.files:
        try:
            logging.info('Getting the body...')
            req_body = req.get_body()
            json_data = json.loads(req_body, strict=False)
            encoded_content = json_data["parameters"]["body"]["$content"]
            # Decode the content
            file_content = base64.b64decode(encoded_content)
            file_name = "powerapp.docx"
        except ValueError:
            logging.info('ERROR: No file part in the request.')
            return func.HttpResponse('ERROR: No file part in the request', mimetype="text/plain;charset=UTF-8", status_code=400)
        #return 'No file part in the request', 400
        #return func.HttpResponse(str(req_body[0:100]), mimetype="text/plain;charset=UTF-8", status_code=400)
    else:
        file = req.files['content']
        file_content = file.read()
        file_name = file.filename

    # Expect a Word filename to attempt convert
    if allowed_file(file_name):
        logging.info('Converting file ' + file_name)
        # Write the binary data to a temp Word file
        with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix=".docx") as f:
            f.write(file_content)
            temp_filename = f.name
        
        # Read and convert temp Word file into HTML for analysis
        with open(temp_filename, "rb") as docx_file:
            try:
                result = mammoth.convert_to_html(docx_file)
                html = result.value
            except Exception as e:
                html = "<p>Word2Text ERROR: Document was not a Microsoft Word document in .docx format (Zip file) that could be analyzed.</p>\n"
                # hex_representation = file_content[0:200].hex()
                # hex_representation_spaced = ' '.join(hex_representation[i:i+2] for i in range(0, len(hex_representation), 2))
                # html = html + "<p>" + hex_representation_spaced + "</p>\n"
                # html = html + "<p>" + str(req_body)[2:40] + "</p>\n"
        # Delete temp file
        try:
            os.remove(temp_filename)
        except OSError:
            pass
        
        # Create a BeautifulSoup object
        soup = BeautifulSoup(html, 'html.parser')

        plain_text = soup.get_text(separator='\n')
        # Return the resultset
        return func.HttpResponse(plain_text, mimetype="text/plain;charset=UTF-8", status_code=200)
    else:
        logging.info('ERROR: Did not find a Word document to convert in request body!')
        return func.HttpResponse(
             "ERROR: Could not find a file in doc/docx format that we can convert. File received was: " + file_name,
             status_code=400
        )


@app.route(route="ExtractCVData", auth_level=func.AuthLevel.ANONYMOUS)
def ExtractCVData(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ExtractCVData trigger function processed a request.')

    # Get the CV body word data
    word_data=b''
    try:
        logging.info('Getting the body...')
        req_body = req.get_body()
    except ValueError:
        logging.info('Body has a value error.')
        word_data = b''
        pass
    else:
        logging.info('Getting body.')
        word_data = req_body
    logging.info('Got a document to analyze of length '+str(len(word_data)))

    #json_data='nada'
    #json_data = json.loads(word_data, strict=False)
    decoded_data = b''

    # Try to decode the data in case it's base64-encoded
    try:
        # Parse JSON and extract content
        logging.info(f"Trying to decode...")
        #json_data = word_data
        json_data = json.loads(word_data, strict=False)
        encoded_content = json_data["parameters"]["body"]["$content"]  #json_data.get('$content')
        logging.info('Got the encoded string starting with ' + encoded_content[0:10])
        # Decode base64-encoded content
        decoded_data = base64.b64decode(encoded_content)
        logging.info("Data was base64-encoded. Successfully decoded.") 
    except Exception as e:
        logging.info(f"Data was not encoded. Treating it as binary data.")
        decoded_data = word_data

    # Expect at least 20 bytes
    if (len(decoded_data) > 20):
        # Write the binary data to a temp Word file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
            f.write(decoded_data)
            temp_filename = f.name

        # Read and convert temp Word file into HTML for analysis
        with open(temp_filename, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value

        # Delete temp file
        os.remove(temp_filename)

        standard_headings = ['Nøkkelkompetanse', 'Kompetanse', 'key competency', 'kvalifikasjoner', 'qualifications',
            'Prosjekterfaring', 'Erfaring', 'experience', 'Utdanning', 'Utdannelse', 'education', 
            'Kurs', 'courses', 'Kurs/Sertifiseringer', 'courses/certifications', 'Annet', 'other',
            'Spesialkunnskap', 'Relevant spesialkunnskap', 'relevant special knowledge', 
            'Arbeidsgivere', 'employers', 'Språk', 'languages']
        
        # Create a BeautifulSoup object
        soup = BeautifulSoup(html, 'html.parser')

        # Find all <p> tags
        paragraphs = soup.find_all('p')

        # Iterate over each <p> tag to identify all headings and mark them with <h1>
        for paragraph in paragraphs:
            if isinstance(paragraph.string, str):
                # Check if the paragraph can be a recognizable heading
                for standard_heading in standard_headings:
                    if re.match("^"+standard_heading.lower(), paragraph.string.lower().strip()):
                        # Create a new <h1> tag and replace the paragraph with it
                        bold_tag = soup.new_tag("h1")
                        bold_tag.string = paragraph.string.strip()
                        paragraph.replace_with(bold_tag)
                        break
        
        #Find all h1 headings again
        allheadings=[]
        headings = soup.find_all('h1')
        for tag in headings:
            heading = tag.get_text().strip()
            allheadings.append(heading)

        # Heading Translation map
        translationdict = {'Nøkkelkompetanse':'key competency', 
            'Kompetanse':'key competency',
            'Kvalifikasjoner':'qualifications',
            'Prosjekterfaring':'experience', 
            'Erfaring':'experience', 
            'Utdanning':'education', 
            'Utdannelse':'education', 
            'Kurs':'courses/certifications', 
            'Kurs/Sertifiseringer':'courses/certifications', 
            'Annet':'other',
            'Spesialkunnskap':'relevant special knowledge', 
            'Relevant spesialkunnskap':'relevant special knowledge', 
            'Arbeidsgivere':'employers', 
            'Språk':'languages'}
        language = 'English'

        # Collect all text per heading/section
        resultset = {} #"docname":docname, "consultantname":consultantname }
        #logging.info("All headings found:" + repr(allheadings))
        for tag in headings:
            heading = tag.get_text().replace(':','').strip()
            headingkey = heading.lower()
            if heading in translationdict.keys():
                headingkey = translationdict[heading].lower()
                language = 'Norwegian'

            # print("\nExtracting SECTION: "+heading)
            sectioncontent = ""
            fathertag = tag #.parent # Need to go one level up (p-tag)
            # Collect text until next heading in CV
            for sibling in fathertag.next_siblings:
                if sibling.get_text().strip() in allheadings:
                    # End of current section
                    resultset[headingkey] = sectioncontent
                    sectioncontent = ""
                    break
                else: # Add one more line to current section
                    for textline in sibling.stripped_strings:
                        sectioncontent += textline+'\n'
            if (len(sectioncontent) > 0):
                resultset[headingkey] = sectioncontent

        resultset['cv language'] = language

        # Return the resultset
        return func.HttpResponse(json.dumps(resultset), mimetype="application/json", status_code=200)# Expect at least 20 bytes
    if (len(decoded_data) > 20):
        # Write the binary data to a temp Word file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
            f.write(decoded_data)
            temp_filename = f.name

        # Read and convert temp Word file into HTML for analysis
        with open(temp_filename, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value

        # Delete temp file
        os.remove(temp_filename)

        standard_headings = ['Nøkkelkompetanse', 'Kompetanse', 'key competency', 'kvalifikasjoner', 'qualifications',
            'Prosjekterfaring', 'Erfaring', 'experience', 'Utdanning', 'Utdannelse', 'education', 
            'Kurs', 'courses', 'Kurs/Sertifiseringer', 'courses/certifications', 'Annet', 'other',
            'Spesialkunnskap', 'Relevant spesialkunnskap', 'relevant special knowledge', 
            'Arbeidsgivere', 'employers', 'Språk', 'languages']
        
        # Create a BeautifulSoup object
        soup = BeautifulSoup(html, 'html.parser')

        # Find all <p> tags
        paragraphs = soup.find_all('p')

        # Iterate over each <p> tag to identify all headings and mark them with <h1>
        for paragraph in paragraphs:
            if isinstance(paragraph.string, str):
                # Check if the paragraph can be a recognizable heading
                for standard_heading in standard_headings:
                    if re.match("^"+standard_heading.lower(), paragraph.string.lower().strip()):
                        # Create a new <h1> tag and replace the paragraph with it
                        bold_tag = soup.new_tag("h1")
                        bold_tag.string = paragraph.string.strip()
                        paragraph.replace_with(bold_tag)
                        break
        
        #Find all h1 headings again
        allheadings=[]
        headings = soup.find_all('h1')
        for tag in headings:
            heading = tag.get_text().strip()
            allheadings.append(heading)

        # Heading Translation map
        translationdict = {'Nøkkelkompetanse':'key competency', 
            'Kompetanse':'key competency',
            'Kvalifikasjoner':'qualifications',
            'Prosjekterfaring':'experience', 
            'Erfaring':'experience', 
            'Utdanning':'education', 
            'Utdannelse':'education', 
            'Kurs':'courses/certifications', 
            'Kurs/Sertifiseringer':'courses/certifications', 
            'Annet':'other',
            'Spesialkunnskap':'relevant special knowledge', 
            'Relevant spesialkunnskap':'relevant special knowledge', 
            'Arbeidsgivere':'employers', 
            'Språk':'languages'}
        language = 'English'

        # Collect all text per heading/section
        resultset = {} #"docname":docname, "consultantname":consultantname }
        #logging.info("All headings found:" + repr(allheadings))
        for tag in headings:
            heading = tag.get_text().replace(':','').strip()
            headingkey = heading.lower()
            if heading in translationdict.keys():
                headingkey = translationdict[heading].lower()
                language = 'Norwegian'

            # print("\nExtracting SECTION: "+heading)
            sectioncontent = ""
            fathertag = tag #.parent # Need to go one level up (p-tag)
            # Collect text until next heading in CV
            for sibling in fathertag.next_siblings:
                if sibling.get_text().strip() in allheadings:
                    # End of current section
                    resultset[headingkey] = sectioncontent
                    sectioncontent = ""
                    break
                else: # Add one more line to current section
                    for textline in sibling.stripped_strings:
                        sectioncontent += textline+'\n'
            if (len(sectioncontent) > 0):
                resultset[headingkey] = sectioncontent

        resultset['cv language'] = language

        # Return the resultset
        return func.HttpResponse(json.dumps(resultset), mimetype="application/json", status_code=200)
    else:
        logging.info('Did not find a CV in request body!')
        return func.HttpResponse(
             "This HTTP triggered function executed successfully, but lacked cv in docx format to analyze.",
             status_code=400
        )
