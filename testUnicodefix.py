

textline = """<b>Bistand til prosjekt: IKT-støtte til byggeprosjekt og eiendomsforvaltning <\/b><br> Prosjektet \u201dIKT-støtte til byggeprosjekt og eiendomsforvaltning\u201d i Helse Vest har behov for bistand fra en IKT-virksomhetsarkitekt. <br> Prosjektets første fase, konseptvurderingen, vil gi en anbefaling for hvilke valg Helse Vest bør ta for at regionen skal få fullverdig og fremtidsrettet IKT-støtte for alle fagområdene i eiendomsforvaltning, med utgangspunkt i valgmulighetene skissert i mandat. Videre skal konseptvurderingen avklare hastegraden for implementering av ny løsning ut fra behovet for å ta i bruk BIM i regionen og at dagens FDV-løsning har \u201dend-of-life\u201d etter 2025. Anbefalte valg må begrunnes og konsekvensene må diskuteres, så langt det er hensiktsmessig."""

charactermap = { "\u2002":" ",
                "\u201c":"\"",
                "\u201d":"\"",
                "\u2013":"-",
                "\u2014":"-"
                    }

for (code, translated) in charactermap.items():
    print("X")
    textline = textline.replace(code, translated)

print(textline)