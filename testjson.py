import json

requestbin = b'{"texttoseparate":" p\xc3\xa5 kunnskap\\n\\u2022\tEvne til \xc3\xa5 fungere konstruktivt og l\xc3\xb8sningsorientert under stort press\\n\\u2022\tArbeider selvstendig, er strukturert og tar ansvar\\n\\u2022\tGod til \xc3\xa5 kommunisere og fremst\xc3\xa5r med faglig overbevisning\\n\\u2022\tM\xc3\xa5lrettet, har evne til \xc3\xa5 beholde ro og oversikt ved stor aktivitet\\n\\u2022\tEvne til \xc3\xa5 skape godt samarbeidsklima\\n\\u2022\tP\xc3\xa5litelighet, integritet "}'

# Decode bytes to string with correct encoding
data_str = requestbin.decode("utf-8")  

print(data_str)

# Replace unescaped tab characters with their escaped version
data_str = data_str.replace("\t", "\\t")

print(data_str)

# Convert string to Python dictionary
data_dict = json.loads(data_str)

# Now you can access elements in the dictionary
print(data_dict['texttoseparate'])
