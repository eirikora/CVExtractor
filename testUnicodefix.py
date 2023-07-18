import re

def headingToRegex(heading):
    # TARGET REGEX is
    # (^|[^T]¤\\n|[^¤]\\n)(([\.0-9]+\s+)?(\s*[a-zA-Z0-9]\)\s+)?HEADING:?[^\\$]*)
    # where:
    # (^|[^T]¤\\n|[^¤]\\n) = Start of document or start of line, BUT NOT preceeded by T¤ which would indicate inside an existing match
    # ([\.0-9]+\s+)?(\s*[a-zA-Z0-9]\)\s+)? = Optional chapter number (e.g. "5.2") or "b)" or both
    # HEADING:? = Heading text with optional ":" at end
    # [^\\$]* = Some other characters until end of line or document
    # Trim space before and after
    heading = heading.strip()
    if heading.endswith(":"):
        heading = heading.rstrip(":")
    #if ":" in heading:
    #    # Remove any trailing colons as will be added as option at end
    #    heading = heading.split(":")[0] #+ "¤SPACE¤:" + "¤ANYTHING¤"
    # Escape characters that need escaping
    heading = heading.replace("/", "\/")
    heading = heading.replace("^", "\^")
    heading = heading.replace("[", "\[")
    heading = heading.replace("]", "\]")
    heading = heading.replace("-", "\-")

    # Find generic elements in heading
    #heading = re.sub("(^|\s)[a-zA-Z0-9]\\)", "\g<1>¤LISTNUM¤", heading)
    heading = re.sub("^\s*[\.0-9]+\s*", "", heading)
    heading = re.sub("^\s*[a-zA-Z0-9]\)\s+", "", heading)
    heading = re.sub("[ \n\t]", "¤SPACE¤", heading)
    heading = heading.replace("*", "¤STAR¤")
    heading = heading.replace(")", "¤CLOSEBRACKET¤")
    heading = heading.replace("(", "¤OPENBRACKET¤")
    heading = heading.replace("?", "¤QUESTION¤")
    heading = re.sub("\\.[0-9]", "¤NUMBER¤", heading)
    heading = re.sub("[0-9]", "¤NUMBER¤", heading)
    heading = heading.replace(".", "\.")
    # Remove duplicates
    heading = re.sub("(¤SPACE¤)+", "¤SPACE¤", heading)
    heading = re.sub("(¤NUMBER¤)+", "¤NUMBER¤", heading)
    # Make chapter number an option for all headings (reduces number of Regex)
    #if heading.startswith("¤NUMBER¤"):
    #    heading = re.sub("¤NUMBER¤", "¤MAYBENUMBER¤", heading, count=1) # Replace only leftmost number
    #else:
    #    heading = "¤MAYBENUMBER¤" + "¤SPACE¤" + heading
    # Insert correct Regex
    heading = heading.replace("¤MAYBENUMBER¤", "([\\.0-9]*|[a-zA-Z0-9]?\)?")
    heading = heading.replace("¤SPACE¤", "\\s*")
    #heading = heading.replace("¤LISTNUM¤", "[a-zA-Z0-9]?\)?")
    heading = heading.replace("¤NUMBER¤", "[\\.0-9]+")
    heading = heading.replace("¤STAR¤", "\\*")
    heading = heading.replace("¤CLOSEBRACKET¤", "\\)")
    heading = heading.replace("¤OPENBRACKET¤", "\\(")
    heading = heading.replace("¤QUESTION¤", "\\?")
    heading = heading.replace("¤ANYTHING¤", "(.*)")
    if ":" not in heading:
        # Add optional end colon for most headings
        heading = heading + ":?"
    # heading = "(^|[^T][^¤]\\n)\s?\s?\s?(" + heading + ")[ ]*(\\n|$)" # Match start of doc or heading right after lineshift that is NOT preceded by ¤HEADSTAR[T¤] (to avoid rematching) and expect only space until end of line(evt. doc)
    # return heading
    # heading = "(^|[^T]¤\\n|[^¤]\\n)\s?\s?\s?(" + heading + "([:;].*|\s*))(\\n|$))" # Match start of doc or heading right after lineshift that is NOT preceded by ¤HEADSTAR[T¤] (to avoid rematching) and expect only space until end of line(evt. doc)
    matchStartOfLine = "(^|[^T]¤¨|[^¤]¨)"
    matchOptionalChapternum = "([\.0-9]+\s+)?(\s*[a-zA-Z0-9]\)\s+)?"
    matchRestOfLine = "[^¨$]*"
    regex = matchStartOfLine + "(" + matchOptionalChapternum + heading + matchRestOfLine + ")" # Brackets mark Match group 2
    return regex

textline = """<b>Bistand til prosjekt: IKT-støtte til byggeprosjekt og eiendomsforvaltning <\/b><br> Prosjektet \u201dIKT-støtte til byggeprosjekt og eiendomsforvaltning\u201d i Helse Vest har behov for bistand fra en IKT-virksomhetsarkitekt. <br> Prosjektets første fase, konseptvurderingen, vil gi en anbefaling for hvilke valg Helse Vest bør ta for at regionen skal få fullverdig og fremtidsrettet IKT-støtte for alle fagområdene i eiendomsforvaltning, med utgangspunkt i valgmulighetene skissert i mandat. Videre skal konseptvurderingen avklare hastegraden for implementering av ny løsning ut fra behovet for å ta i bruk BIM i regionen og at dagens FDV-løsning har \u201dend-of-life\u201d etter 2025. Anbefalte valg må begrunnes og konsekvensene må diskuteres, så langt det er hensiktsmessig."""

charactermap = { "\u2002":" ",
                "\u201c":"\"",
                "\u201d":"\"",
                "\u2013":"-",
                "\u2014":"-"
                    }

for (code, translated) in charactermap.items():
    textline = textline.replace(code, translated)

print(textline)
print(headingToRegex("Del I: Oppdragsgiver"))