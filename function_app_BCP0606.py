import azure.functions as func
import logging
import os
import tempfile
import json
import base64
import mammoth
import re
from bs4 import BeautifulSoup

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="ExtractCVData", auth_level=func.AuthLevel.ANONYMOUS)
def ExtractCVData(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ExtractCVData trigger function processed a request.')

    # Get the CV body word data
    word_data=b''
    try:
        req_body = req.get_body()
    except ValueError:
        word_data = b''
        pass
    else:
        word_data = req_body
    logging.info('Got a document to analyze of length '+str(len(word_data)))

    # Try to decode the data in case it's base64-encoded
    try:
        # Parse JSON and extract content
        json_data = json.loads(word_data)
        encoded_content = json_data["parameters"]["body"]["$content"]  #json_data.get('$content')
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
        return func.HttpResponse(json.dumps(resultset), mimetype="application/json", status_code=200)
    else:
        logging.info('Did not find a CV in request body!')
        return func.HttpResponse(
             "This HTTP triggered function executed successfully, but lacked cv in docx format to analyze.",
             status_code=200
        )
