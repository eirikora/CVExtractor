import os
import tempfile
import json
import base64
import mammoth
import quopri
import re
from bs4 import BeautifulSoup
from urllib.parse import unquote


encodedfile = ''

# Open the file in read mode
with open('encodedtest.txt', 'r') as file:
    # Read the content of the file into a string variable
    encodedfile = file.read()
    # Print the content
    # print(encodedfile)


print('RAW    :'+encodedfile[0:63])


decoded_body = base64.b64decode(encodedfile)
print('base64d:'+str(decoded_body[0:363]))

# Convert each byte to hexadecimal and print
for byte in decoded_body[0:163]:
    hex_code = f"\\x{byte:02x}" #f"\\x{ord(byte)}"
    print(f"{hex_code}", end="")
print(" ")



utfdecoded = decoded_body.encode('utf-8')
print('UTF-8  :'+str(utfdecoded[0:63]))

# Convert each byte to hexadecimal and print
for byte in utfdecoded[0:63]:
    hex_code = f"\\x{byte:02x}"
    print(f"{hex_code}", end="")
print(" ")


urldecoded = unquote(utfdecoded)
if (str(urldecoded) == str(utfdecoded)):
    print(' - URLDECODE had no effect!')
print('URL-dec:'+urldecoded[0:63])

# Convert each byte to hexadecimal and print
for byte in urldecoded[0:63]:
    hex_code = f"\\x{ord(byte):02x}" #f"\\x{byte:02x}"
    print(f"{hex_code}", end="")
print(" ")
            # unpacked_data = base64.b64decode(req_body[5:])
            # logging.info('1_UNPACKED:' + str(unpacked_data[0:40]))
            #content_data = unpacked_data.decode('utf-8')
            #logging.info('2_CONTENT :' + str(content_data[0:40]))
            # decoded_data = unpacked_data.encode('ascii') #ase64.b64decode(content_data)
            # logging.info('3_DECODED :' + str(decoded_data[0:40]))
            
            #logging.info('Document sent as URL encoded and base64 encoded Body parameter (Zoho style).')
            #decoded_body = base64.b64decode(req_body[5:])  #.decode('utf-8')
            #logging.info('1_UNPACKED:' + str(decoded_body[0:40]))
            #content_data = decoded_body.decode('utf-8').encode(encoding='utf-8')
            #content_data = unquote(urlencoded_content)
            #logging.info('2_CONTENT :' + str(content_data[0:40]))



# decoded02 = unquote(utfdecoded)
# if (decoded02 == decoded_body):
#     print(' - URLDECODE had no effect second time neither!')
# print('URL-dec:'+decoded02[0:63])

# # Convert each byte to hexadecimal and print
# for byte in decoded02[0:63]:
#     hex_code = hex(ord(byte)) #f"\\x{byte:02x}"
#     print(f"{hex_code}", end="")