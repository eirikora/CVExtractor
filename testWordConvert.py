
import os

import json

import mammoth
from bs4 import BeautifulSoup

word_filename = ".\input.docx"

# Read and convert temp Word file into HTML for analysis
with open(word_filename, "rb") as docx_file:
    try:
        result = mammoth.convert_to_html(docx_file)
        html = result.value
    except Exception as e:
        html = "<p>Word2Text ERROR: Document was not a Microsoft Word document in .docx format (Zip file) that could be analyzed.</p>\n"
        print(html)
        # hex_representation = file_content[0:200].hex()
        # hex_representation_spaced = ' '.join(hex_representation[i:i+2] for i in range(0, len(hex_representation), 2))
        # html = html + "<p>" + hex_representation_spaced + "</p>\n"
        # html = html + "<p>" + str(req_body)[2:40] + "</p>\n"

# Create a BeautifulSoup object
soup = BeautifulSoup(html, 'html.parser')

print(soup)

plain_text = soup.get_text(separator='\n')

print (plain_text)