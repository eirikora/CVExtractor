
import PyPDF2

pdf_filename = ".\input.pdf"

# Read and convert PDF for text analysis
text = ""

# creating a pdf file object
pdfFileObj = open(pdf_filename, 'rb')
  
# creating a pdf reader object
pdfReader = PyPDF2.PdfReader(pdfFileObj)
  
# printing number of pages in pdf file
print(len(pdfReader.pages))
  
for page in range(len(pdfReader.pages)):
    pageObj = pdfReader.pages[page]
    # extracting text from page
    text += pageObj.extract_text()
# closing the pdf file object
pdfFileObj.close()

print(text)