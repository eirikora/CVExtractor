import quopri

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

mime_string = '=_Windows-1252_Q_Minikonkurranse_Bistand_til_produkteier_=F8konomisysteme_=_=_Windows-1252_Q_ne.doc_='
#'1687345523883_=_iso-8859-1_Q_Minikonkurranse_-_tildelingsskjema_Bistand_til_produkteier_=_=_iso-8859-1_Q__Portef=F8ljesys.doc_='
#'=_Windows-1252_Q_beskrivelse__lederst=F8tte_PMO.docx_='
print(decode_mime_string(mime_string))