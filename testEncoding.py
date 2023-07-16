import unicodedata

title = "\u201cHer og nå!"
print(title)
print(unicodedata.normalize('NFKD', title).encode('ascii','ignore'))