import json

request_data = b'{"texttoseparate":"Bilag 1 Beskrivelse av Bistanden \\u2013 innleie av ressurs Digital Sikkerhetsr\xc3\xa5dgiver/Security Manager, IKT digital sikkerhet\\nFagomr\xc3\xa5de\\nSett kryss\\nIT prosjektledelse og r\xc3\xa5dgivningstjenester\\nArkitektur\\nx\\nTest\\nDigitale sikkerhetstjenester\\nx\\n\u2022 Samhandling- og portall\xc3\xb8sninger \\nAnalysetjenester\\nPlattformtjenester\\nIntegrasjonstjenester\\nNettverkstjenester\\nLeverand\xc3\xb8rer:\\nA2 Norge, Accenture"}'

# Decode byte string to a regular string
request_string = request_data.decode('utf-8')

# Parse the string into a JSON object
request_json = json.loads(request_string)

# Now you can access the elements of the JSON object
print(request_json['texttoseparate'])
