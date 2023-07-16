
import os
import json
import re

def settKryssCleanup(document_text):
    return_text = ""
    innenfor = False
    last_line = ""
    for line in document_text.split("\n"):
        if innenfor:
            if line.strip() == "":
                innenfor = False
                last_line = ""
            elif line.strip().lower() == "x":
                return_text += last_line + "\n"
                last_line = ""
            else:
                last_line = line
        if not innenfor:
            cleanline = line.lower().replace(".","").replace(":","").replace(";","").strip()
            if cleanline.find("sett kryss") > -1: 
                innenfor = True
            else:
                return_text += line + "\n"
    return return_text

def identifyFooters(document):
    # Count frequency first
    frequencybank = {}
    maxfrequency = 0
    countuniquelines = 0
    for textline in document.split("\n"):
        # Remove EN_SPACE characters
        textline = textline.replace("\u2002", " ")
        # Remove space before end of line
        textline = textline.rstrip()
        if textline != "":
            if textline in frequencybank.keys():
                frequencybank[textline] += 1
                if frequencybank[textline] > maxfrequency:
                    maxfrequency = frequencybank[textline]
            else:
                frequencybank[textline] = 1
                countuniquelines += 1
    frequencyarray = []
    for i in frequencybank.values():
        frequencyarray.append(i)
    freqdistrib = {}
    for item in frequencyarray:
        freqdistrib[item] = freqdistrib.get(item, 0) + 1
    steps = []
    for i in freqdistrib.keys():
        steps.append(i)
    listlength = len(steps)
    footers = []
    if listlength > 0:
        steps.sort(reverse = True)
        accumulatedcount = 0
        for i in range(listlength):
            accumulatedcount += freqdistrib[steps[i]]
            if accumulatedcount > 5 or accumulatedcount > (countuniquelines // 20): # Less than 5% of all lines should be footers
                break
        i -= 1
        if i < 0:
            # no footers
            threshold = maxfrequency + 1
        else:
            threshold = steps[i]    
            for phrase in frequencybank.keys():
                if frequencybank[phrase] >= threshold:
                    footers.append(phrase)
    #print("Threshold frequency set at: "+ str(threshold) + " resulting in " + str(len(footers)) + " footers.")
    return footers

def cleanDocument(document_content):
    footers = identifyFooters(document_content)
    emptylines = 0
    seen_content = False
    result_content = ""
    memorybank = {}
    duplicateCount = 0
    totalDuplicateCount = 0
    buffer = ""
    # Traverse document line by line
    for textline in document_content.split("\n"):
        # Remove EN_SPACE characters
        textline = textline.replace("\u2002", " ")
        # Remove space before end of line
        textline = textline.rstrip()
        if textline == "" or textline in footers:
            emptylines += 1
        else:
            # Identify and remove duplicates
            seen_content = True
            emptylines = 0
            if textline in memorybank.keys():
                buffer += textline + "\n"
                memorybank[textline] += 1
                seen_content = False
                duplicateCount += 1
                # print(str(duplicateCount) + " duplicate " + str(memorybank[textline]) + ":" + textline)
                if duplicateCount >= 2: # After 2 repeating lines start emptying/deleting buffer
                    buffer = ""
            else:
                memorybank[textline] = 1
                totalDuplicateCount += duplicateCount
                duplicateCount = 0
            
        if seen_content and emptylines < 3:
            # Only outputs content once we have seen it (avoid trailing blanks) and only accepts 2 empty lines
            result_content += buffer + textline + "\n"
            buffer = ""
    totalDuplicateCount += duplicateCount
    
    if len(footers) > 0:
        result_content += "FOOTERS:\n"
        for line in footers:
            result_content += line + "\n"
        
    if totalDuplicateCount > 0:
        print( str(totalDuplicateCount)+ " duplicates removed!")

    # Interpret "Sett kryss" sections correctly
    final_result = settKryssCleanup(result_content)
    if final_result == "\n":
        final_result = ""
    return final_result

debugInfo = """[Fra kilde: Mail body]:
MATCHES IN DOCUMENT:
¤HEADSTART¤Avtale
¤BUCKETINFO¤["Oppdragsinformasjon"]¤HEADEND¤
¤HEADSTART¤Frist
¤BUCKETINFO¤["Frister"]¤HEADEND¤
¤HEADSTART¤Omfang
¤BUCKETINFO¤["Oppdragsinformasjon"]¤HEADEND¤
¤HEADSTART¤Beskrivelse
¤BUCKETINFO¤["Oppdragsbeskrivelse"]¤HEADEND¤
¤HEADSTART¤Krav
¤BUCKETINFO¤["Kompetansekrav"]¤HEADEND¤
¤HEADSTART¤Sted for utførelse vil være:
¤BUCKETINFO¤["Oppdragsinformasjon"]¤HEADEND¤
¤HEADSTART¤Vennlig hilsen
¤BUCKETINFO¤[]¤HEADEND¤
--- END MATCHES IN DOCUMENT ---
[Fra kilde: Minikonkurranse_Bistand_til_produkteier_økonomisystemene.docx]:
MATCHES IN DOCUMENT:
¤HEADSTART¤Rammeavtale:
¤BUCKETINFO¤["Rammeavtaleinfo"]¤HEADEND¤
¤HEADSTART¤Fremdriftsplan og frister for minikonkurransen:
¤BUCKETINFO¤["Frister"]¤HEADEND¤
¤HEADSTART¤Spørsmål kan sendes inntil
¤BUCKETINFO¤["Frister"]¤HEADEND¤
¤HEADSTART¤Tilbudsfrist (obligatorisk):
¤BUCKETINFO¤["Frister"]¤HEADEND¤
¤HEADSTART¤Oppstart av kontrakt:
¤BUCKETINFO¤["Frister"]¤HEADEND¤
¤HEADSTART¤Vedståelsesfrist (obligatorisk):
¤BUCKETINFO¤["Frister"]¤HEADEND¤
¤HEADSTART¤Tildelingsavtale og tildelingskriterier
¤BUCKETINFO¤["Konkurransekriterier"]¤HEADEND¤
¤HEADSTART¤Aktuell tildelingsavtale
¤BUCKETINFO¤["Konkurransekriterier"]¤HEADEND¤
¤HEADSTART¤Tildelingskriterier
¤BUCKETINFO¤["Konkurransekriterier"]¤HEADEND¤
¤HEADSTART¤Kompetanse
¤BUCKETINFO¤["Konkurransekriterier"]¤HEADEND¤
¤HEADSTART¤Pris
¤BUCKETINFO¤["Konkurransekriterier", "Prisinformasjon"]¤HEADEND¤
¤HEADSTART¤1. Arbeidsbeskrivelse - spesifikasjon av bistand
¤BUCKETINFO¤[]¤HEADEND¤
¤HEADSTART¤1.1 Bakgrunn
¤BUCKETINFO¤["Oppdragsbeskrivelse"]¤HEADEND¤
¤HEADSTART¤1.2 Kort beskrivelse av bistanden og Kundens behov
¤BUCKETINFO¤["Oppdragsbeskrivelse"]¤HEADEND¤
¤HEADSTART¤1.3  Rammer - økonomisk og tid
¤BUCKETINFO¤["Oppdragsinformasjon"]¤HEADEND¤
¤HEADSTART¤1.4 Krav til kompetanse
¤BUCKETINFO¤["Kompetansekrav"]¤HEADEND¤
¤HEADSTART¤3. Underleverandør(er)
¤BUCKETINFO¤[]¤HEADEND¤
¤HEADSTART¤4. Andre forhold
¤BUCKETINFO¤[]¤HEADEND¤
¤HEADSTART¤4.1 Taushetserklæring
¤BUCKETINFO¤[]¤HEADEND¤
¤HEADSTART¤4.2 Arbeidssted
¤BUCKETINFO¤["Oppdragsinformasjon"]¤HEADEND¤
¤HEADSTART¤5. Opsjon
¤BUCKETINFO¤["Oppdragsinformasjon"]¤HEADEND¤
¤HEADSTART¤6. Kontakt og adresseinformasjon
¤BUCKETINFO¤[]¤HEADEND¤
¤HEADSTART¤Sted og dato
¤BUCKETINFO¤["Oppdragsinformasjon"]¤HEADEND¤
--- END MATCHES IN DOCUMENT ---
"""
textMedKryss = """ Tant og fjas som ikke må tapes 1
Fagområde

Sett kryss
IT prosjektledelse og rådgivningstjenester
Arkitektur
X
Test
Digitale sikkerhetstjenester
X
Samhandling- og portalløsninger 
Analysetjenester
Plattformtjenester
Integrasjonstjenester
Nettverkstjenester

Tant og fjas som ikke må tapes 2
Fagområde

Sett kryss
A Juniorkonsulent
B Konsulent
X
C Seniorkonsulent
X
D Ekspert
X
E Spesialist

Tant og fjas som ikke må tapes 3
 """
    
myBucket = """Anbudsinformasjon for konsulenttjenester
Sammendrag av anbudsforespørsel
• REMA 1000 Ønsker å etablere rammeavtale(r) med utvalgte leverandører av konsulenttjenester
• Påmeldelse for å delta i anbudet senest 22. desember
• Informasjonsmøte for leverandører, 3. januar, kl 12:00 – 13:00 CET
• Frist for å levere tilbud: 10. januar. 2023 kl. 13:00 CET
Dette anbudet er å betrakte som konfidensiell og skal kun benyttes i forbindelse med
tilbudsgiving. Dette inkluderer all informasjon og korrespondanse i forbindelse med
anbudet.
I dette anbudet har REMA 1000 som mål å etablere rammeavtaler for kjøp av rådgivingstjenester.
Omfanget av tjenestene relatert til de forskjellige kategoriene er beskrevet senere i dette dokumentet under
“1.3 Omfanget på anbudet”.
1. REMA 1000 Norge AS – en introduksjon til anbudet
1.1 Introduksjon til anbudet
Som en del av Reitan Retail har REMA 1000 gleden av å invitere leverandører av generelle
konsulenttjenester til å delta i et kommende anbud.
Reitan Reital er et familieeid selskap og en av de største aktørene i den nordiske regionen innenfor
dagligvarebutikke.
Vi oppfordrer alle leverandører som deltar til å lese anbudsmateriale grundig.
Anbudsprosessen kommer til å foregå i Keelvar. Keelvar er en online-plattform med formål å kjøre
anbudskonkurranse og andre relaterte prosesser.

1



1.2 Hva ser vi etter?
REMA 1000 ønsker å etablere en rammeavtale for kjøp av konsulenttjenester. Målet med anbudsprosessen
er å inngå langsiktig samarbeid med utvalgte leverandører og konsolidere leverandørporteføljen. REMA vil
evaluere leverandørene på bakgrunn av:
1. Kommersielle betingelser
2. Kvalitet i leveransene til leverandør
3. Kategoridekning på tjenestetilbudet

REMA 1000 ønsker å etablere rammeavtaler for følgende tjenester, men ikke utelukkende:

Tjeneste Beskrivelse*
Operations Rådgiving innenfor operations, blant annet:
• Supply chain
• Sourcing & Procurement
• Transformasjon og forbedring av forretningsprosesser
• Generell lønnsomhetsforbedring
Strategi Strategirådgiving, blant annet:
• Corporate strategy
• Digital strategi
• Produktstrategi -og utvikling
Finansiell Finansiell rådgiving, blant annet:
• Økonomi/regnskapsnære tjenester
• M&A og transaksjoner
• Restrukturering
• Forbedring av regnskaps- og økonomifunksjoner
HR-rådgiving HR-rådgiving, blant annet:
• Rekruttering
• Organisasjonsutvikling
Risiko rådgiving Risiko rådgiving, blant annet:
• Risikovurdering & rådgiving på regulatoriske risikoer
• Granskning og compliance

* Ikke utelukkende


1.3 Omfanget på anbudet
Omfanget på anbudet er på ca. 57 (tusen) konsulenttimer per år de neste 3 årene. Vedlagt i tabell under er
estimert årlig volum fordelt utover konsulentroller (se prisark i Keelvar for forklaring per erfaringsnivå):


2

Konsulentroller Årlig estimert antall timer (tusen)*
Associate/Consultant 30
Senior Consultant 17
Manager/Project Manager 9
Associate Partner/Junior Partner & Partner 1
* Det estimerte volumet er basert på historisk data og budsjettert behov fro 2023. Disse volumene kan derfor ikke garanteres.

1.4 Invitasjon til informasjonsmøte på anbudsprosess
REMA 1000 arrangerer et informasjonsmøte for leverandører av konsulenttjenester. Formålet er å
introdusere anbudsprosessen for konsulenttjenester, inkludert en introduksjon av anbudsplattformen,
Keelvar.
Introduksjonsmøte vil bli holdt 21. desember. Kl 12:00 – 13:00 CET.
Vennligste bekreft deres deltakelse i anbudsprosessen og deltakelse på informasjonsmøte gjennom
meldingsfunksjonen i Keelvar, senest 22. desember.
Tilgang til Keelvar skal dere ha fått gjennom lenke vedlagt i egen e-post: «REMA 1000 – anbud for
konsulenttjenester». Vær oppmerksom på at den "systemgenererte e-posten" ovenfor kan havne i
søppelpostmappen din fra senderen: «no-reply@keelvar.com». Dersom du ikke har mottatt denne lenken, ta
kontakt med Martin Cappelen Smith.

For å delta i møtet, gå inn på vedlagte link:

https://teams.microsoft.com/l/meetup-
join/19%3ameeting_Njk3NTZmMTctMDY0Ni00YmJjLWE3YjktOTY4NTQyZWI1N2Zi%40thread.v2/0?co
ntext=%7b%22Tid%22%3a%22bbf77a8f-7fa8-45a0-81db-
7ad345a349c0%22%2c%22Oid%22%3a%22999ad771-0920-4877-82aa-238ac0baafb4%22%7d



2. Anbudsprosessen og tilhørende frister
Følgende tidslinje og frister har blitt satt for anbudet, det kan forekomme endringer i datoer:
Tidslinje Prosess Beskrivelse
20. Desember 2022 Anbudspublisering Anbudet vil bli holdt på en online e-sourcing plattform
som heter Keelvar. Her vil dere motta en invitasjon i
mailboksen fra følgende adresse: Keelvar Systems

3

no-reply@keelvar.com
3. januar 2023 Informasjonsmøte Online leverandørinformasjonsmøte: Informasjon om
REMA 1000 og anbudsprosessen.
Vennligst bekreft din deltakelse gjennom
meldingsfunksjonen i Keelvar senest 22. desember.
Invitasjonen til nettmøtet ligger under «1.3 Invitasjon til
informasjonsmøte på anbudsprosess».
10. januar 2023 Innsendelse av tilbud Tidsfrist for å sende inn i Keelvar, 10. januar 2023, Kl.
13:00 CET.
Uke 2 - 4 Evaluering av mottatte
tilbud
REMA vil evaluere mottatte tilbud.



2.1 Deltagelse i anbudsprosess
Hvis dere ønsker å delta i anbudet, ber vi dere vennligst gå til Keelvar og bekrefte deltakelse til
anbudsprosessen og informasjonsmøte 22. desember via meldingsfunksjonen i Keelvar. Dere vil få
tilgang til anbudsmaterialet i samme portal.
Vi håper at dette anbudet er interessant for dere, og vi ser frem til deres deltakelse i denne prosessen

2.2 Anbudspublisering og utsendelse
Dere vil finne alt av anbudsmateriale sammen med retningslinjer i Keelvar systemet. Anbudsmaterialet er
ikke offentlig publisert, ettersom det bare blir utsendt til forhåndsgodkjente leverandører. Som følge av dette,
skal ikke anbudsmateriale deles med andre parter/organisasjoner, hvis ikke de inngår som en del av
leverandørens tilbud – som en underleverandør.
For å bli ansett som kvalifisert for å bli vurdert, er det krav til at budet og alt av nødvendig dokumentasjon er
lastet opp i Keelvar. I tillegg må alle leverandører følge den oppsatte tidslinjen, samt godta REMA 1000 sine
standard vilkår og betingelser.

2.3 Innsending av spørsmål relatert til anbudsprosessen
Inviterte leverandører vil bli forespurt til å sende spørsmål relatert til innholdet i anbudet og de spesifikke
kravene via meldingssystemet på Keelvar.
All kommunikasjon i løpet av anbudsprosessen skal foregå gjennom Keelvar og blir håndtert av:
REMA Anskaffelser,
Martin Cappelen Smith
E-post: Martin.cappelen.smith@rema.no

4

(Denne e-posten skal kun benyttes dersom man ikke får tilgang eller har mottatt invitasjon til Keelvar. Andre
henvendelser vedrørende anbudet til denne e-posten vil ikke bli besvart.)
Vi ønsker ikke at dere henvender dere, eller kontakter, direkte til REMA 1000 / REMA 1000 ansatte eller
andre parter som har tilknytning til selskapet, dersom dere har ønske om ytterligere informasjon. Disse
partene har ikke tilgang til spørsmålene før etter tidsfristen. Vi ber om at all informasjon går igjennom
meldingssystemet til Keelvar. Dersom meldingene skulle inneholde informasjon sensitive til selskapet, vil
spørsmålene bli besvart kun til den aktuelle leverandøren.
Dersom dere skulle ha tekniske problemer med anbudsplattformen, Keelvar, vennligst ta kontakt med
Keelvar support på support@keelvar.com

2.4 Svar på skriftlige spørsmål
Alle skriftlige svar til innkommende spørsmål vil være anonymisert og besvares på fortløpende basis til alle
leverandører.

3. Innhold og struktur i anbudet

3.1 Krav til tilbud
Alle priser skal være i NOK ekskludert MVA.
Tilbud skal være gyldig i 16 uker etter frist til å gi tilbud.
Prisene oppgitt i dette anbudet skal inkludere alle honorarer og kostnader knyttet til kjøp av
konsulenttjenestene, eksklusiv eventuell overtidssats, transport- og losjikostnader (transport og losji betales
til kostpris uten påslag, og REMA 1000 kan bestemme hvilke hoteller som skal benyttes).

3.2 Dokumenter som må fylles ut og/eller legges ved i anbudet
For å kunne bli vurdert, er det påkrevd at leverandøren har fylt ut følgende dokumenter i anbudet.
Dokument Navn Formål Beskrivelse
0 Keelvar
introduksjonsguide
(PDF)
Informasjon til
leverandør
Introduksjon til Keelvar-plattformen
A Anbudsinformasjon
(PDF)
Informasjon til
leverandør
Detaljert informasjon på omfanget,
anbudsprosessen, definisjoner, krav for deltagelse
og evaluering.
B Rammeavtale for
kjøp av
konsulenttjenester
(PDF)
Informasjon til
leverandør
Rammeavtale for kjøp av konsulenttjenester
C REMA 1000 sine
etiske retningslinjer
(PDF)
Et hoveddokument og et tilhørende dokument med
forklaringer til REMA 1000 sin etiske retningslinjer
for leverandører
D Databehandleravtale
(PDF)
Databehandleravtale til REMA 1000

5

Keelvar RFI Utfylles av
leverandør
Leverandøren skal her svare på spørsmål relatert
til selskapet, kompetanse og tjenestetilbud, i tillegg
etterspørres det:
• Dokument som beskriver leverandøren og
dens hovedtjenester og
nøkkelkompetanser
• Eksempler på CV-er for alle roller som
leverandøren byr på, inkludert antall år
med relevant erfaring med hensyn til de
spesifikke kvalifikasjoner som er oppgitt i
anbudsdokumentet
• Dersom det er relevant, referanser fra
tidligere kunder med kontaktinformasjon
Keelvar Prisark Utfylles av
leverandør
Leverandøren skal her fylle ut priser på etterspurte
konsulentroller
Svar på prisarket gjøres ved å laste ned excel-
template som skal fylles ut og lastes opp

3.3 Guide til prisarket
Alle leverandører anbefales å gi et tilbud på alle tjenester i prisarket, dette er derimot ikke påkrevd.


3.4 Kommersielle betingelser
Rabatter på bakgrunn av endrede kommersielle betingelser vil bli lagt sammen. Det vil si at en rabatt på 3%
på betalingsbetingelser og 2% på kontraktslengde, vil til sammen gi en 5% rabatt på priser oppgitt i budarket.

Kolonnenavn Beskrivelse
Maksimum timepris eks. MVA
(onshore)
Maksimum timepriser er eks. mva., inkludert alle
ekstrakostnader unntatt, eventuell overtid, transport og losji.
Overtidssats (%) ved vanlig ukedag Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber over 8 timer hos kunde ved vanlig
ukedag.
Overtidssats (%) Lørdager, søn- og
helgedager
Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber lørdag, søndager og/eller helgedager
hos kunde.
Navn Beskrivelse
RABATT (%) Totalt forbruk hos
leverandør
Her har leverandøren mulighet til å legge inn rabatt basert på
hvor høyt forbruk REMA 1000 vil ha hos leverandøren.
Rabatten betales tilbake til REMA 1000 i slutten av året (en
kickback-modell).
RABATT (%) Betalingsbetingelser Standard betalingsbetingelser er 60 dager. Vennligst spesifiser
om du vil gi en rabatt eller en økning dersom andre
betalingsbetingelser gjelder.
RABATT (%) Kontraktslengde for
konsulenter ved avrop på rammeavtale
Standard kontraktslengde for konsulenter ved avrop på
rammeavtale er 0-6 måneder. Eventuelt kan leverandøren

6



3.5 Evaluering
Leverandøren skal oppfylle alle relevante krav i vedlagte dokumenter.

REMA 1000 forbeholder seg retten til å avvise tilbud som ikke oppfyller alle vurderingskriterier.
Det endelige utvalget av leverandører som vil få tilbud om kontrakt vil avhenge av hvilke tilbud som kommer.
REMA 1000 arbeider med en hypotese om at anbudsprosessen vil resultere i leverandørkonsolidering, og
dermed redusere antall leverandører per kategori.


4. Avtalebetingelser
Følgende kontraktuelle betingelser er gjeldende for dette anbudet:

• Betalingsbetingelser: 60 dager
• Prisene skal gjelde i hele avtaleperioden, med mindre det har vært en prisjustering i henhold til
Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Prisene skal årlig justeres 60% av Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Konsulentene skal føre timer til nærmeste kvarter
• Avtaleperioden for rammeavtalen er 3 år med opsjon på 1+1 forlengelse.
o Dersom avtalen ikke sies opp, vil avtalen fortsette å løpe med en oppsigelsesfrist på 3
måneders skriftlig varsel for begge parter.
• Kontraktslengde for konsulenter ved avrop på rammeavtale: 0 – 6 måneder
• Leverandør skal fakturere REMA etterskuddsvis for tjenester som leveres

Dersom tilbyder avdekker mangler i forespørselen eller konflikter mellom de ulike deler av denne, skal REMA
1000 øyeblikkelig varsles skriftlig om dette. Har dere andre spørsmål/kommentarer til forespørselen, skal
dette rettes skriftlig i spørsmålsfunksjonen til Keelvar.

spesifisere en prosentvis rabatt når konsulentkontraktens
lengde er mer enn 6 måneder.
RABATT (%) Kontraktslengde på
Rammeavtale (Standard 3 år)
Standard kontraktslengde er 3 år med mulighet for å forlenge
med ett år to ganger. Eventuelt kan leverandøren spesifisere en
prosentvis rabatt, som vil gi REMA 1000 incentiv til å inngå en
lengre kontrakt.
RABATT (%) dersom andre selskaper i
Reitangruppen benytter rammeavtalen
Rabatt som gis dersom andre selskaper i Reitangruppen velger
å benytte seg av rammeavtalen

Navn Beskrivelse
Total cost of ownership (TCO) De totale kostnadene ved leverandøren, inkludert forventet
påvirkning fra priser, gebyrer og kommersielle vilkår.
Kvalitet Kvalitet er en viktig parameter for å oppnå effekten man ønsker.
Kvalitet blir evaluert på graden av riktige konsulenter og
kompetanse for å matche oppgaveporteføljen hos REMA 1000.
Kategoridekning Leverandører vurderes på evnen til å gi en bred dekning av
rådgivingstjenester som er relevante for REMA 1000.

7

Forslaget til rammeavtale vil bli utarbeidet på bakgrunn av REMA 1000 sin standard rammeavtale. Denne
avtalen er basert på REMA 1000 sine krav og avtalte priser i denne anbudsrunden.
Kontrakter som inngås som følge av anbudsprosessen vil erstatte eksisterende kontrakter innenfor denne
kategorien. Annullering/erstatning av eksisterende kontrakter vil tre i kraft fra datoen ny kontrakt er signert.

5. Formelle krav til anbudsbesvarelsen
I det fremlagte tilbudet er det viktig at følgende krav er tilfredsstilt. Dersom dette ikke er tilfelle, er det
mulighet for at tilbudet kan bli avslått.
5.1 Formelle krav
Krav 1: Tilbudets innhold

Leverandørens tilbud må inneholde de følgende punktene:
1. Et komplett og utfylt prisark lastet opp i Keelvar før svarfristen.
2. Et komplett svar til alle RFI spørsmål før svarfristen.
a. Husk å laste opp alle påkrevde vedlegg

Krav 2: Tidsfrist

Tilbud kan ikke leveres senere enn 10. januar kl. 13:00 via Keelvar. Tilbud som blir levert etter denne fristen
risikerer å ikke bli akseptert og dermed heller ikke vurdert.

Krav 3: Tilbudets struktur

Strukturen til tilbudsforespørselen kan ikke bli endret. Alle relevante felter som dere ønsker å legge
inn tilbud på må fylles inn og oppfylle kravene til Keelvar. Vi oppfordrer leverandører til å legge inn tilbud på
så mange av områdene som mulig.

Krav 4: Tilbudets valuta

Leverandørens tilbud må være oppgitt i NOK.
Krav 5: Tilbudets gyldighet

Tilbudet skal være gyldig i 16 uker etter den satte fristen for levering.
Krav 6: Minimumskrav

Leverandøren må tilfredsstille alle REMA sine etiske krav (se vedlegg: REMA 1000 Etiske retningslinjer)


5.2 Andre krav til anbudet
- REMA 1000 vil teste tilbud gitt i dette anbudet på bakgrunn av mange ulike kriterier, og forbeholder
seg retten til å avvise alle tilbud. REMA 1000 har også retten til å evaluere alle vurderingskriterier i
dokumentasjonen og godkjenne tilbud som ikke har den laveste prisen.
- Enhver tvist som omhandler denne anbudsprosessen, vil løses under Norsk domstol

5.3 Ytterligere kostnader

8

REMA 1000 vil ikke godta kostnader knyttet til produktene utover det som fremkommer i dette anbudet.

5.4 Anonymitet, konfidensialitet, og taushetsplikt
REMA 1000 krever at alle deltagende leverandører holder all informasjon som kommer frem i
anbudsprosessen konfidensielt. REMA 1000 har samme prosedyre når det kommer til informasjonen fra
leverandørene.

5.5 Omfangsbegrensninger
Omfanget av dette anbudet gjelder bare REMA 1000 i Norge, som tilsier at omfanget utelater andre REMA
1000 institusjoner (f.eks. Reitan Convenience, REMA 1000 DK).

5.6 Kostnader relatert til anbudsprosessen
REMA 1000 vil ikke være ansvarlig for kostnader som påløpes hos leverandører som følger av denne
anbudsprosessen – dette referer til mulige kostnader tilknyttet utarbeidelsen av tilbudet eller deltagelse i
forhandlinger. Hvis det gjennomføres en test periode, vil leverandør(er) være ansvarlig for kostnader inntil
leverandør(ene) er godkjent.

5.7 Ansvarsfraskrivelse
REMA 1000 forbeholder seg retten, uten ansvar, til å kansellere anbudsrunden på ethvert tidspunkt.

5.8 Avslag på tilbud
Leverandører som ikke er kvalifisert eller oppfyller minstekravene kan bli avvist, og innholdet i et avvist tilbud
vil ikke bli vurdert nærmere.
Det er derfor svært viktig at tilbudet inneholder all nødvendig informasjon og leveres i formatet som
etterspørres.

5.9 Etiske retningslinjer
Det forventes at leverandører følger REMA 1000 sine etiske retningslinjer og bekrefter at disse
retningslinjene er fulgt ved å delta i anbudet.





oe 1[0[l0N

Lda FT Ee
\




Anbudsinformasjon for konsulenttjenester
Sammendrag av anbudsforespørsel
• REMA 1000 Ønsker å etablere rammeavtale(r) med utvalgte leverandører av konsulenttjenester
• Påmeldelse for å delta i anbudet senest 22. desember
• Informasjonsmøte for leverandører, 3. januar, kl 12:00 – 13:00 CET
• Frist for å levere tilbud: 10. januar. 2023 kl. 13:00 CET
Dette anbudet er å betrakte som konfidensiell og skal kun benyttes i forbindelse med
tilbudsgiving. Dette inkluderer all informasjon og korrespondanse i forbindelse med
anbudet.
I dette anbudet har REMA 1000 som mål å etablere rammeavtaler for kjøp av rådgivingstjenester.
Omfanget av tjenestene relatert til de forskjellige kategoriene er beskrevet senere i dette dokumentet under
“1.3 Omfanget på anbudet”.
1. REMA 1000 Norge AS – en introduksjon til anbudet
1.1 Introduksjon til anbudet
Som en del av Reitan Retail har REMA 1000 gleden av å invitere leverandører av generelle
konsulenttjenester til å delta i et kommende anbud.
Reitan Reital er et familieeid selskap og en av de største aktørene i den nordiske regionen innenfor
dagligvarebutikke.
Vi oppfordrer alle leverandører som deltar til å lese anbudsmateriale grundig.
Anbudsprosessen kommer til å foregå i Keelvar. Keelvar er en online-plattform med formål å kjøre
anbudskonkurranse og andre relaterte prosesser.

1



1.2 Hva ser vi etter?
REMA 1000 ønsker å etablere en rammeavtale for kjøp av konsulenttjenester. Målet med anbudsprosessen
er å inngå langsiktig samarbeid med utvalgte leverandører og konsolidere leverandørporteføljen. REMA vil
evaluere leverandørene på bakgrunn av:
1. Kommersielle betingelser
2. Kvalitet i leveransene til leverandør
3. Kategoridekning på tjenestetilbudet

REMA 1000 ønsker å etablere rammeavtaler for følgende tjenester, men ikke utelukkende:

Tjeneste Beskrivelse*
Operations Rådgiving innenfor operations, blant annet:
• Supply chain
• Sourcing & Procurement
• Transformasjon og forbedring av forretningsprosesser
• Generell lønnsomhetsforbedring
Strategi Strategirådgiving, blant annet:
• Corporate strategy
• Digital strategi
• Produktstrategi -og utvikling
Finansiell Finansiell rådgiving, blant annet:
• Økonomi/regnskapsnære tjenester
• M&A og transaksjoner
• Restrukturering
• Forbedring av regnskaps- og økonomifunksjoner
HR-rådgiving HR-rådgiving, blant annet:
• Rekruttering
• Organisasjonsutvikling
Risiko rådgiving Risiko rådgiving, blant annet:
• Risikovurdering & rådgiving på regulatoriske risikoer
• Granskning og compliance

* Ikke utelukkende


1.3 Omfanget på anbudet
Omfanget på anbudet er på ca. 57 (tusen) konsulenttimer per år de neste 3 årene. Vedlagt i tabell under er
estimert årlig volum fordelt utover konsulentroller (se prisark i Keelvar for forklaring per erfaringsnivå):


2

Konsulentroller Årlig estimert antall timer (tusen)*
Associate/Consultant 30
Senior Consultant 17
Manager/Project Manager 9
Associate Partner/Junior Partner & Partner 1
* Det estimerte volumet er basert på historisk data og budsjettert behov fro 2023. Disse volumene kan derfor ikke garanteres.

1.4 Invitasjon til informasjonsmøte på anbudsprosess
REMA 1000 arrangerer et informasjonsmøte for leverandører av konsulenttjenester. Formålet er å
introdusere anbudsprosessen for konsulenttjenester, inkludert en introduksjon av anbudsplattformen,
Keelvar.
Introduksjonsmøte vil bli holdt 21. desember. Kl 12:00 – 13:00 CET.
Vennligste bekreft deres deltakelse i anbudsprosessen og deltakelse på informasjonsmøte gjennom
meldingsfunksjonen i Keelvar, senest 22. desember.
Tilgang til Keelvar skal dere ha fått gjennom lenke vedlagt i egen e-post: «REMA 1000 – anbud for
konsulenttjenester». Vær oppmerksom på at den "systemgenererte e-posten" ovenfor kan havne i
søppelpostmappen din fra senderen: «no-reply@keelvar.com». Dersom du ikke har mottatt denne lenken, ta
kontakt med Martin Cappelen Smith.

For å delta i møtet, gå inn på vedlagte link:

https://teams.microsoft.com/l/meetup-
join/19%3ameeting_Njk3NTZmMTctMDY0Ni00YmJjLWE3YjktOTY4NTQyZWI1N2Zi%40thread.v2/0?co
ntext=%7b%22Tid%22%3a%22bbf77a8f-7fa8-45a0-81db-
7ad345a349c0%22%2c%22Oid%22%3a%22999ad771-0920-4877-82aa-238ac0baafb4%22%7d



2. Anbudsprosessen og tilhørende frister
Følgende tidslinje og frister har blitt satt for anbudet, det kan forekomme endringer i datoer:
Tidslinje Prosess Beskrivelse
20. Desember 2022 Anbudspublisering Anbudet vil bli holdt på en online e-sourcing plattform
som heter Keelvar. Her vil dere motta en invitasjon i
mailboksen fra følgende adresse: Keelvar Systems

3

no-reply@keelvar.com
3. januar 2023 Informasjonsmøte Online leverandørinformasjonsmøte: Informasjon om
REMA 1000 og anbudsprosessen.
Vennligst bekreft din deltakelse gjennom
meldingsfunksjonen i Keelvar senest 22. desember.
Invitasjonen til nettmøtet ligger under «1.3 Invitasjon til
informasjonsmøte på anbudsprosess».
10. januar 2023 Innsendelse av tilbud Tidsfrist for å sende inn i Keelvar, 10. januar 2023, Kl.
13:00 CET.
Uke 2 - 4 Evaluering av mottatte
tilbud
REMA vil evaluere mottatte tilbud.



2.1 Deltagelse i anbudsprosess
Hvis dere ønsker å delta i anbudet, ber vi dere vennligst gå til Keelvar og bekrefte deltakelse til
anbudsprosessen og informasjonsmøte 22. desember via meldingsfunksjonen i Keelvar. Dere vil få
tilgang til anbudsmaterialet i samme portal.
Vi håper at dette anbudet er interessant for dere, og vi ser frem til deres deltakelse i denne prosessen

2.2 Anbudspublisering og utsendelse
Dere vil finne alt av anbudsmateriale sammen med retningslinjer i Keelvar systemet. Anbudsmaterialet er
ikke offentlig publisert, ettersom det bare blir utsendt til forhåndsgodkjente leverandører. Som følge av dette,
skal ikke anbudsmateriale deles med andre parter/organisasjoner, hvis ikke de inngår som en del av
leverandørens tilbud – som en underleverandør.
For å bli ansett som kvalifisert for å bli vurdert, er det krav til at budet og alt av nødvendig dokumentasjon er
lastet opp i Keelvar. I tillegg må alle leverandører følge den oppsatte tidslinjen, samt godta REMA 1000 sine
standard vilkår og betingelser.

2.3 Innsending av spørsmål relatert til anbudsprosessen
Inviterte leverandører vil bli forespurt til å sende spørsmål relatert til innholdet i anbudet og de spesifikke
kravene via meldingssystemet på Keelvar.
All kommunikasjon i løpet av anbudsprosessen skal foregå gjennom Keelvar og blir håndtert av:
REMA Anskaffelser,
Martin Cappelen Smith
E-post: Martin.cappelen.smith@rema.no

4

(Denne e-posten skal kun benyttes dersom man ikke får tilgang eller har mottatt invitasjon til Keelvar. Andre
henvendelser vedrørende anbudet til denne e-posten vil ikke bli besvart.)
Vi ønsker ikke at dere henvender dere, eller kontakter, direkte til REMA 1000 / REMA 1000 ansatte eller
andre parter som har tilknytning til selskapet, dersom dere har ønske om ytterligere informasjon. Disse
partene har ikke tilgang til spørsmålene før etter tidsfristen. Vi ber om at all informasjon går igjennom
meldingssystemet til Keelvar. Dersom meldingene skulle inneholde informasjon sensitive til selskapet, vil
spørsmålene bli besvart kun til den aktuelle leverandøren.
Dersom dere skulle ha tekniske problemer med anbudsplattformen, Keelvar, vennligst ta kontakt med
Keelvar support på support@keelvar.com

2.4 Svar på skriftlige spørsmål
Alle skriftlige svar til innkommende spørsmål vil være anonymisert og besvares på fortløpende basis til alle
leverandører.

3. Innhold og struktur i anbudet

3.1 Krav til tilbud
Alle priser skal være i NOK ekskludert MVA.
Tilbud skal være gyldig i 16 uker etter frist til å gi tilbud.
Prisene oppgitt i dette anbudet skal inkludere alle honorarer og kostnader knyttet til kjøp av
konsulenttjenestene, eksklusiv eventuell overtidssats, transport- og losjikostnader (transport og losji betales
til kostpris uten påslag, og REMA 1000 kan bestemme hvilke hoteller som skal benyttes).

3.2 Dokumenter som må fylles ut og/eller legges ved i anbudet
For å kunne bli vurdert, er det påkrevd at leverandøren har fylt ut følgende dokumenter i anbudet.
Dokument Navn Formål Beskrivelse
0 Keelvar
introduksjonsguide
(PDF)
Informasjon til
leverandør
Introduksjon til Keelvar-plattformen
A Anbudsinformasjon
(PDF)
Informasjon til
leverandør
Detaljert informasjon på omfanget,
anbudsprosessen, definisjoner, krav for deltagelse
og evaluering.
B Rammeavtale for
kjøp av
konsulenttjenester
(PDF)
Informasjon til
leverandør
Rammeavtale for kjøp av konsulenttjenester
C REMA 1000 sine
etiske retningslinjer
(PDF)
Et hoveddokument og et tilhørende dokument med
forklaringer til REMA 1000 sin etiske retningslinjer
for leverandører
D Databehandleravtale
(PDF)
Databehandleravtale til REMA 1000

5

Keelvar RFI Utfylles av
leverandør
Leverandøren skal her svare på spørsmål relatert
til selskapet, kompetanse og tjenestetilbud, i tillegg
etterspørres det:
• Dokument som beskriver leverandøren og
dens hovedtjenester og
nøkkelkompetanser
• Eksempler på CV-er for alle roller som
leverandøren byr på, inkludert antall år
med relevant erfaring med hensyn til de
spesifikke kvalifikasjoner som er oppgitt i
anbudsdokumentet
• Dersom det er relevant, referanser fra
tidligere kunder med kontaktinformasjon
Keelvar Prisark Utfylles av
leverandør
Leverandøren skal her fylle ut priser på etterspurte
konsulentroller
Svar på prisarket gjøres ved å laste ned excel-
template som skal fylles ut og lastes opp

3.3 Guide til prisarket
Alle leverandører anbefales å gi et tilbud på alle tjenester i prisarket, dette er derimot ikke påkrevd.


3.4 Kommersielle betingelser
Rabatter på bakgrunn av endrede kommersielle betingelser vil bli lagt sammen. Det vil si at en rabatt på 3%
på betalingsbetingelser og 2% på kontraktslengde, vil til sammen gi en 5% rabatt på priser oppgitt i budarket.

Kolonnenavn Beskrivelse
Maksimum timepris eks. MVA
(onshore)
Maksimum timepriser er eks. mva., inkludert alle
ekstrakostnader unntatt, eventuell overtid, transport og losji.
Overtidssats (%) ved vanlig ukedag Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber over 8 timer hos kunde ved vanlig
ukedag.
Overtidssats (%) Lørdager, søn- og
helgedager
Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber lørdag, søndager og/eller helgedager
hos kunde.
Navn Beskrivelse
RABATT (%) Totalt forbruk hos
leverandør
Her har leverandøren mulighet til å legge inn rabatt basert på
hvor høyt forbruk REMA 1000 vil ha hos leverandøren.
Rabatten betales tilbake til REMA 1000 i slutten av året (en
kickback-modell).
RABATT (%) Betalingsbetingelser Standard betalingsbetingelser er 60 dager. Vennligst spesifiser
om du vil gi en rabatt eller en økning dersom andre
betalingsbetingelser gjelder.
RABATT (%) Kontraktslengde for
konsulenter ved avrop på rammeavtale
Standard kontraktslengde for konsulenter ved avrop på
rammeavtale er 0-6 måneder. Eventuelt kan leverandøren

6



3.5 Evaluering
Leverandøren skal oppfylle alle relevante krav i vedlagte dokumenter.

REMA 1000 forbeholder seg retten til å avvise tilbud som ikke oppfyller alle vurderingskriterier.
Det endelige utvalget av leverandører som vil få tilbud om kontrakt vil avhenge av hvilke tilbud som kommer.
REMA 1000 arbeider med en hypotese om at anbudsprosessen vil resultere i leverandørkonsolidering, og
dermed redusere antall leverandører per kategori.


4. Avtalebetingelser
Følgende kontraktuelle betingelser er gjeldende for dette anbudet:

• Betalingsbetingelser: 60 dager
• Prisene skal gjelde i hele avtaleperioden, med mindre det har vært en prisjustering i henhold til
Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Prisene skal årlig justeres 60% av Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Konsulentene skal føre timer til nærmeste kvarter
• Avtaleperioden for rammeavtalen er 3 år med opsjon på 1+1 forlengelse.
o Dersom avtalen ikke sies opp, vil avtalen fortsette å løpe med en oppsigelsesfrist på 3
måneders skriftlig varsel for begge parter.
• Kontraktslengde for konsulenter ved avrop på rammeavtale: 0 – 6 måneder
• Leverandør skal fakturere REMA etterskuddsvis for tjenester som leveres

Dersom tilbyder avdekker mangler i forespørselen eller konflikter mellom de ulike deler av denne, skal REMA
1000 øyeblikkelig varsles skriftlig om dette. Har dere andre spørsmål/kommentarer til forespørselen, skal
dette rettes skriftlig i spørsmålsfunksjonen til Keelvar.

spesifisere en prosentvis rabatt når konsulentkontraktens
lengde er mer enn 6 måneder.
RABATT (%) Kontraktslengde på
Rammeavtale (Standard 3 år)
Standard kontraktslengde er 3 år med mulighet for å forlenge
med ett år to ganger. Eventuelt kan leverandøren spesifisere en
prosentvis rabatt, som vil gi REMA 1000 incentiv til å inngå en
lengre kontrakt.
RABATT (%) dersom andre selskaper i
Reitangruppen benytter rammeavtalen
Rabatt som gis dersom andre selskaper i Reitangruppen velger
å benytte seg av rammeavtalen

Navn Beskrivelse
Total cost of ownership (TCO) De totale kostnadene ved leverandøren, inkludert forventet
påvirkning fra priser, gebyrer og kommersielle vilkår.
Kvalitet Kvalitet er en viktig parameter for å oppnå effekten man ønsker.
Kvalitet blir evaluert på graden av riktige konsulenter og
kompetanse for å matche oppgaveporteføljen hos REMA 1000.
Kategoridekning Leverandører vurderes på evnen til å gi en bred dekning av
rådgivingstjenester som er relevante for REMA 1000.

7

Forslaget til rammeavtale vil bli utarbeidet på bakgrunn av REMA 1000 sin standard rammeavtale. Denne
avtalen er basert på REMA 1000 sine krav og avtalte priser i denne anbudsrunden.
Kontrakter som inngås som følge av anbudsprosessen vil erstatte eksisterende kontrakter innenfor denne
kategorien. Annullering/erstatning av eksisterende kontrakter vil tre i kraft fra datoen ny kontrakt er signert.

5. Formelle krav til anbudsbesvarelsen
I det fremlagte tilbudet er det viktig at følgende krav er tilfredsstilt. Dersom dette ikke er tilfelle, er det
mulighet for at tilbudet kan bli avslått.
5.1 Formelle krav
Krav 1: Tilbudets innhold

Leverandørens tilbud må inneholde de følgende punktene:
1. Et komplett og utfylt prisark lastet opp i Keelvar før svarfristen.
2. Et komplett svar til alle RFI spørsmål før svarfristen.
a. Husk å laste opp alle påkrevde vedlegg

Krav 2: Tidsfrist

Tilbud kan ikke leveres senere enn 10. januar kl. 13:00 via Keelvar. Tilbud som blir levert etter denne fristen
risikerer å ikke bli akseptert og dermed heller ikke vurdert.

Krav 3: Tilbudets struktur

Strukturen til tilbudsforespørselen kan ikke bli endret. Alle relevante felter som dere ønsker å legge
inn tilbud på må fylles inn og oppfylle kravene til Keelvar. Vi oppfordrer leverandører til å legge inn tilbud på
så mange av områdene som mulig.

Krav 4: Tilbudets valuta

Leverandørens tilbud må være oppgitt i NOK.
Krav 5: Tilbudets gyldighet

Tilbudet skal være gyldig i 16 uker etter den satte fristen for levering.
Krav 6: Minimumskrav

Leverandøren må tilfredsstille alle REMA sine etiske krav (se vedlegg: REMA 1000 Etiske retningslinjer)


5.2 Andre krav til anbudet
- REMA 1000 vil teste tilbud gitt i dette anbudet på bakgrunn av mange ulike kriterier, og forbeholder
seg retten til å avvise alle tilbud. REMA 1000 har også retten til å evaluere alle vurderingskriterier i
dokumentasjonen og godkjenne tilbud som ikke har den laveste prisen.
- Enhver tvist som omhandler denne anbudsprosessen, vil løses under Norsk domstol

5.3 Ytterligere kostnader

8

REMA 1000 vil ikke godta kostnader knyttet til produktene utover det som fremkommer i dette anbudet.

5.4 Anonymitet, konfidensialitet, og taushetsplikt
REMA 1000 krever at alle deltagende leverandører holder all informasjon som kommer frem i
anbudsprosessen konfidensielt. REMA 1000 har samme prosedyre når det kommer til informasjonen fra
leverandørene.

5.5 Omfangsbegrensninger
Omfanget av dette anbudet gjelder bare REMA 1000 i Norge, som tilsier at omfanget utelater andre REMA
1000 institusjoner (f.eks. Reitan Convenience, REMA 1000 DK).

5.6 Kostnader relatert til anbudsprosessen
REMA 1000 vil ikke være ansvarlig for kostnader som påløpes hos leverandører som følger av denne
anbudsprosessen – dette referer til mulige kostnader tilknyttet utarbeidelsen av tilbudet eller deltagelse i
forhandlinger. Hvis det gjennomføres en test periode, vil leverandør(er) være ansvarlig for kostnader inntil
leverandør(ene) er godkjent.

5.7 Ansvarsfraskrivelse
REMA 1000 forbeholder seg retten, uten ansvar, til å kansellere anbudsrunden på ethvert tidspunkt.

5.8 Avslag på tilbud
Leverandører som ikke er kvalifisert eller oppfyller minstekravene kan bli avvist, og innholdet i et avvist tilbud
vil ikke bli vurdert nærmere.
Det er derfor svært viktig at tilbudet inneholder all nødvendig informasjon og leveres i formatet som
etterspørres.

5.9 Etiske retningslinjer
Det forventes at leverandører følger REMA 1000 sine etiske retningslinjer og bekrefter at disse
retningslinjene er fulgt ved å delta i anbudet.



1



1.2 Hva ser vi etter?
REMA 1000 ønsker å etablere en rammeavtale for kjøp av konsulenttjenester. Målet med anbudsprosessen
er å inngå langsiktig samarbeid med utvalgte leverandører og konsolidere leverandørporteføljen. REMA vil
evaluere leverandørene på bakgrunn av:
1. Kommersielle betingelser
2. Kvalitet i leveransene til leverandør
3. Kategoridekning på tjenestetilbudet

REMA 1000 ønsker å etablere rammeavtaler for følgende tjenester, men ikke utelukkende:

Tjeneste Beskrivelse*
Operations Rådgiving innenfor operations, blant annet:
• Supply chain
• Sourcing & Procurement
• Transformasjon og forbedring av forretningsprosesser
• Generell lønnsomhetsforbedring
Strategi Strategirådgiving, blant annet:
• Corporate strategy
• Digital strategi
• Produktstrategi -og utvikling
Finansiell Finansiell rådgiving, blant annet:
• Økonomi/regnskapsnære tjenester
• M&A og transaksjoner
• Restrukturering
• Forbedring av regnskaps- og økonomifunksjoner
HR-rådgiving HR-rådgiving, blant annet:
• Rekruttering
• Organisasjonsutvikling
Risiko rådgiving Risiko rådgiving, blant annet:
• Risikovurdering & rådgiving på regulatoriske risikoer
• Granskning og compliance

* Ikke utelukkende


1.3 Omfanget på anbudet
Omfanget på anbudet er på ca. 57 (tusen) konsulenttimer per år de neste 3 årene. Vedlagt i tabell under er
estimert årlig volum fordelt utover konsulentroller (se prisark i Keelvar for forklaring per erfaringsnivå):


2

Konsulentroller Årlig estimert antall timer (tusen)*
Associate/Consultant 30
Senior Consultant 17
Manager/Project Manager 9
Associate Partner/Junior Partner & Partner 1
* Det estimerte volumet er basert på historisk data og budsjettert behov fro 2023. Disse volumene kan derfor ikke garanteres.

1.4 Invitasjon til informasjonsmøte på anbudsprosess
REMA 1000 arrangerer et informasjonsmøte for leverandører av konsulenttjenester. Formålet er å
introdusere anbudsprosessen for konsulenttjenester, inkludert en introduksjon av anbudsplattformen,
Keelvar.
Introduksjonsmøte vil bli holdt 21. desember. Kl 12:00 – 13:00 CET.
Vennligste bekreft deres deltakelse i anbudsprosessen og deltakelse på informasjonsmøte gjennom
meldingsfunksjonen i Keelvar, senest 22. desember.
Tilgang til Keelvar skal dere ha fått gjennom lenke vedlagt i egen e-post: «REMA 1000 – anbud for
konsulenttjenester». Vær oppmerksom på at den "systemgenererte e-posten" ovenfor kan havne i
søppelpostmappen din fra senderen: «no-reply@keelvar.com». Dersom du ikke har mottatt denne lenken, ta
kontakt med Martin Cappelen Smith.

For å delta i møtet, gå inn på vedlagte link:

https://teams.microsoft.com/l/meetup-
join/19%3ameeting_Njk3NTZmMTctMDY0Ni00YmJjLWE3YjktOTY4NTQyZWI1N2Zi%40thread.v2/0?co
ntext=%7b%22Tid%22%3a%22bbf77a8f-7fa8-45a0-81db-
7ad345a349c0%22%2c%22Oid%22%3a%22999ad771-0920-4877-82aa-238ac0baafb4%22%7d



2. Anbudsprosessen og tilhørende frister
Følgende tidslinje og frister har blitt satt for anbudet, det kan forekomme endringer i datoer:
Tidslinje Prosess Beskrivelse
20. Desember 2022 Anbudspublisering Anbudet vil bli holdt på en online e-sourcing plattform
som heter Keelvar. Her vil dere motta en invitasjon i
mailboksen fra følgende adresse: Keelvar Systems

3

no-reply@keelvar.com
3. januar 2023 Informasjonsmøte Online leverandørinformasjonsmøte: Informasjon om
REMA 1000 og anbudsprosessen.
Vennligst bekreft din deltakelse gjennom
meldingsfunksjonen i Keelvar senest 22. desember.
Invitasjonen til nettmøtet ligger under «1.3 Invitasjon til
informasjonsmøte på anbudsprosess».
10. januar 2023 Innsendelse av tilbud Tidsfrist for å sende inn i Keelvar, 10. januar 2023, Kl.
13:00 CET.
Uke 2 - 4 Evaluering av mottatte
tilbud
REMA vil evaluere mottatte tilbud.



2.1 Deltagelse i anbudsprosess
Hvis dere ønsker å delta i anbudet, ber vi dere vennligst gå til Keelvar og bekrefte deltakelse til
anbudsprosessen og informasjonsmøte 22. desember via meldingsfunksjonen i Keelvar. Dere vil få
tilgang til anbudsmaterialet i samme portal.
Vi håper at dette anbudet er interessant for dere, og vi ser frem til deres deltakelse i denne prosessen

2.2 Anbudspublisering og utsendelse
Dere vil finne alt av anbudsmateriale sammen med retningslinjer i Keelvar systemet. Anbudsmaterialet er
ikke offentlig publisert, ettersom det bare blir utsendt til forhåndsgodkjente leverandører. Som følge av dette,
skal ikke anbudsmateriale deles med andre parter/organisasjoner, hvis ikke de inngår som en del av
leverandørens tilbud – som en underleverandør.
For å bli ansett som kvalifisert for å bli vurdert, er det krav til at budet og alt av nødvendig dokumentasjon er
lastet opp i Keelvar. I tillegg må alle leverandører følge den oppsatte tidslinjen, samt godta REMA 1000 sine
standard vilkår og betingelser.

2.3 Innsending av spørsmål relatert til anbudsprosessen
Inviterte leverandører vil bli forespurt til å sende spørsmål relatert til innholdet i anbudet og de spesifikke
kravene via meldingssystemet på Keelvar.
All kommunikasjon i løpet av anbudsprosessen skal foregå gjennom Keelvar og blir håndtert av:
REMA Anskaffelser,
Martin Cappelen Smith
E-post: Martin.cappelen.smith@rema.no

4

(Denne e-posten skal kun benyttes dersom man ikke får tilgang eller har mottatt invitasjon til Keelvar. Andre
henvendelser vedrørende anbudet til denne e-posten vil ikke bli besvart.)
Vi ønsker ikke at dere henvender dere, eller kontakter, direkte til REMA 1000 / REMA 1000 ansatte eller
andre parter som har tilknytning til selskapet, dersom dere har ønske om ytterligere informasjon. Disse
partene har ikke tilgang til spørsmålene før etter tidsfristen. Vi ber om at all informasjon går igjennom
meldingssystemet til Keelvar. Dersom meldingene skulle inneholde informasjon sensitive til selskapet, vil
spørsmålene bli besvart kun til den aktuelle leverandøren.
Dersom dere skulle ha tekniske problemer med anbudsplattformen, Keelvar, vennligst ta kontakt med
Keelvar support på support@keelvar.com

2.4 Svar på skriftlige spørsmål
Alle skriftlige svar til innkommende spørsmål vil være anonymisert og besvares på fortløpende basis til alle
leverandører.

3. Innhold og struktur i anbudet

3.1 Krav til tilbud
Alle priser skal være i NOK ekskludert MVA.
Tilbud skal være gyldig i 16 uker etter frist til å gi tilbud.
Prisene oppgitt i dette anbudet skal inkludere alle honorarer og kostnader knyttet til kjøp av
konsulenttjenestene, eksklusiv eventuell overtidssats, transport- og losjikostnader (transport og losji betales
til kostpris uten påslag, og REMA 1000 kan bestemme hvilke hoteller som skal benyttes).

3.2 Dokumenter som må fylles ut og/eller legges ved i anbudet
For å kunne bli vurdert, er det påkrevd at leverandøren har fylt ut følgende dokumenter i anbudet.
Dokument Navn Formål Beskrivelse
0 Keelvar
introduksjonsguide
(PDF)
Informasjon til
leverandør
Introduksjon til Keelvar-plattformen
A Anbudsinformasjon
(PDF)
Informasjon til
leverandør
Detaljert informasjon på omfanget,
anbudsprosessen, definisjoner, krav for deltagelse
og evaluering.
B Rammeavtale for
kjøp av
konsulenttjenester
(PDF)
Informasjon til
leverandør
Rammeavtale for kjøp av konsulenttjenester
C REMA 1000 sine
etiske retningslinjer
(PDF)
Et hoveddokument og et tilhørende dokument med
forklaringer til REMA 1000 sin etiske retningslinjer
for leverandører
D Databehandleravtale
(PDF)
Databehandleravtale til REMA 1000

5

Keelvar RFI Utfylles av
leverandør
Leverandøren skal her svare på spørsmål relatert
til selskapet, kompetanse og tjenestetilbud, i tillegg
etterspørres det:
• Dokument som beskriver leverandøren og
dens hovedtjenester og
nøkkelkompetanser
• Eksempler på CV-er for alle roller som
leverandøren byr på, inkludert antall år
med relevant erfaring med hensyn til de
spesifikke kvalifikasjoner som er oppgitt i
anbudsdokumentet
• Dersom det er relevant, referanser fra
tidligere kunder med kontaktinformasjon
Keelvar Prisark Utfylles av
leverandør
Leverandøren skal her fylle ut priser på etterspurte
konsulentroller
Svar på prisarket gjøres ved å laste ned excel-
template som skal fylles ut og lastes opp

3.3 Guide til prisarket
Alle leverandører anbefales å gi et tilbud på alle tjenester i prisarket, dette er derimot ikke påkrevd.


3.4 Kommersielle betingelser
Rabatter på bakgrunn av endrede kommersielle betingelser vil bli lagt sammen. Det vil si at en rabatt på 3%
på betalingsbetingelser og 2% på kontraktslengde, vil til sammen gi en 5% rabatt på priser oppgitt i budarket.

Kolonnenavn Beskrivelse
Maksimum timepris eks. MVA
(onshore)
Maksimum timepriser er eks. mva., inkludert alle
ekstrakostnader unntatt, eventuell overtid, transport og losji.
Overtidssats (%) ved vanlig ukedag Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber over 8 timer hos kunde ved vanlig
ukedag.
Overtidssats (%) Lørdager, søn- og
helgedager
Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber lørdag, søndager og/eller helgedager
hos kunde.
Navn Beskrivelse
RABATT (%) Totalt forbruk hos
leverandør
Her har leverandøren mulighet til å legge inn rabatt basert på
hvor høyt forbruk REMA 1000 vil ha hos leverandøren.
Rabatten betales tilbake til REMA 1000 i slutten av året (en
kickback-modell).
RABATT (%) Betalingsbetingelser Standard betalingsbetingelser er 60 dager. Vennligst spesifiser
om du vil gi en rabatt eller en økning dersom andre
betalingsbetingelser gjelder.
RABATT (%) Kontraktslengde for
konsulenter ved avrop på rammeavtale
Standard kontraktslengde for konsulenter ved avrop på
rammeavtale er 0-6 måneder. Eventuelt kan leverandøren

6



3.5 Evaluering
Leverandøren skal oppfylle alle relevante krav i vedlagte dokumenter.

REMA 1000 forbeholder seg retten til å avvise tilbud som ikke oppfyller alle vurderingskriterier.
Det endelige utvalget av leverandører som vil få tilbud om kontrakt vil avhenge av hvilke tilbud som kommer.
REMA 1000 arbeider med en hypotese om at anbudsprosessen vil resultere i leverandørkonsolidering, og
dermed redusere antall leverandører per kategori.


4. Avtalebetingelser
Følgende kontraktuelle betingelser er gjeldende for dette anbudet:

• Betalingsbetingelser: 60 dager
• Prisene skal gjelde i hele avtaleperioden, med mindre det har vært en prisjustering i henhold til
Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Prisene skal årlig justeres 60% av Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Konsulentene skal føre timer til nærmeste kvarter
• Avtaleperioden for rammeavtalen er 3 år med opsjon på 1+1 forlengelse.
o Dersom avtalen ikke sies opp, vil avtalen fortsette å løpe med en oppsigelsesfrist på 3
måneders skriftlig varsel for begge parter.
• Kontraktslengde for konsulenter ved avrop på rammeavtale: 0 – 6 måneder
• Leverandør skal fakturere REMA etterskuddsvis for tjenester som leveres

Dersom tilbyder avdekker mangler i forespørselen eller konflikter mellom de ulike deler av denne, skal REMA
1000 øyeblikkelig varsles skriftlig om dette. Har dere andre spørsmål/kommentarer til forespørselen, skal
dette rettes skriftlig i spørsmålsfunksjonen til Keelvar.

spesifisere en prosentvis rabatt når konsulentkontraktens
lengde er mer enn 6 måneder.
RABATT (%) Kontraktslengde på
Rammeavtale (Standard 3 år)
Standard kontraktslengde er 3 år med mulighet for å forlenge
med ett år to ganger. Eventuelt kan leverandøren spesifisere en
prosentvis rabatt, som vil gi REMA 1000 incentiv til å inngå en
lengre kontrakt.
RABATT (%) dersom andre selskaper i
Reitangruppen benytter rammeavtalen
Rabatt som gis dersom andre selskaper i Reitangruppen velger
å benytte seg av rammeavtalen

Navn Beskrivelse
Total cost of ownership (TCO) De totale kostnadene ved leverandøren, inkludert forventet
påvirkning fra priser, gebyrer og kommersielle vilkår.
Kvalitet Kvalitet er en viktig parameter for å oppnå effekten man ønsker.
Kvalitet blir evaluert på graden av riktige konsulenter og
kompetanse for å matche oppgaveporteføljen hos REMA 1000.
Kategoridekning Leverandører vurderes på evnen til å gi en bred dekning av
rådgivingstjenester som er relevante for REMA 1000.

7

Forslaget til rammeavtale vil bli utarbeidet på bakgrunn av REMA 1000 sin standard rammeavtale. Denne
avtalen er basert på REMA 1000 sine krav og avtalte priser i denne anbudsrunden.
Kontrakter som inngås som følge av anbudsprosessen vil erstatte eksisterende kontrakter innenfor denne
kategorien. Annullering/erstatning av eksisterende kontrakter vil tre i kraft fra datoen ny kontrakt er signert.

5. Formelle krav til anbudsbesvarelsen
I det fremlagte tilbudet er det viktig at følgende krav er tilfredsstilt. Dersom dette ikke er tilfelle, er det
mulighet for at tilbudet kan bli avslått.
5.1 Formelle krav
Krav 1: Tilbudets innhold

Leverandørens tilbud må inneholde de følgende punktene:
1. Et komplett og utfylt prisark lastet opp i Keelvar før svarfristen.
2. Et komplett svar til alle RFI spørsmål før svarfristen.
a. Husk å laste opp alle påkrevde vedlegg

Krav 2: Tidsfrist

Tilbud kan ikke leveres senere enn 10. januar kl. 13:00 via Keelvar. Tilbud som blir levert etter denne fristen
risikerer å ikke bli akseptert og dermed heller ikke vurdert.

Krav 3: Tilbudets struktur

Strukturen til tilbudsforespørselen kan ikke bli endret. Alle relevante felter som dere ønsker å legge
inn tilbud på må fylles inn og oppfylle kravene til Keelvar. Vi oppfordrer leverandører til å legge inn tilbud på
så mange av områdene som mulig.

Krav 4: Tilbudets valuta

Leverandørens tilbud må være oppgitt i NOK.
Krav 5: Tilbudets gyldighet

Tilbudet skal være gyldig i 16 uker etter den satte fristen for levering.
Krav 6: Minimumskrav

Leverandøren må tilfredsstille alle REMA sine etiske krav (se vedlegg: REMA 1000 Etiske retningslinjer)


5.2 Andre krav til anbudet
- REMA 1000 vil teste tilbud gitt i dette anbudet på bakgrunn av mange ulike kriterier, og forbeholder
seg retten til å avvise alle tilbud. REMA 1000 har også retten til å evaluere alle vurderingskriterier i
dokumentasjonen og godkjenne tilbud som ikke har den laveste prisen.
- Enhver tvist som omhandler denne anbudsprosessen, vil løses under Norsk domstol

5.3 Ytterligere kostnader

8

REMA 1000 vil ikke godta kostnader knyttet til produktene utover det som fremkommer i dette anbudet.

5.4 Anonymitet, konfidensialitet, og taushetsplikt
REMA 1000 krever at alle deltagende leverandører holder all informasjon som kommer frem i
anbudsprosessen konfidensielt. REMA 1000 har samme prosedyre når det kommer til informasjonen fra
leverandørene.

5.5 Omfangsbegrensninger
Omfanget av dette anbudet gjelder bare REMA 1000 i Norge, som tilsier at omfanget utelater andre REMA
1000 institusjoner (f.eks. Reitan Convenience, REMA 1000 DK).

5.6 Kostnader relatert til anbudsprosessen
REMA 1000 vil ikke være ansvarlig for kostnader som påløpes hos leverandører som følger av denne
anbudsprosessen – dette referer til mulige kostnader tilknyttet utarbeidelsen av tilbudet eller deltagelse i
forhandlinger. Hvis det gjennomføres en test periode, vil leverandør(er) være ansvarlig for kostnader inntil
leverandør(ene) er godkjent.

5.7 Ansvarsfraskrivelse
REMA 1000 forbeholder seg retten, uten ansvar, til å kansellere anbudsrunden på ethvert tidspunkt.

5.8 Avslag på tilbud
Leverandører som ikke er kvalifisert eller oppfyller minstekravene kan bli avvist, og innholdet i et avvist tilbud
vil ikke bli vurdert nærmere.
Det er derfor svært viktig at tilbudet inneholder all nødvendig informasjon og leveres i formatet som
etterspørres.

5.9 Etiske retningslinjer
Det forventes at leverandører følger REMA 1000 sine etiske retningslinjer og bekrefter at disse
retningslinjene er fulgt ved å delta i anbudet.



2

Konsulentroller Årlig estimert antall timer (tusen)*
Associate/Consultant 30
Senior Consultant 17
Manager/Project Manager 9
Associate Partner/Junior Partner & Partner 1
* Det estimerte volumet er basert på historisk data og budsjettert behov fro 2023. Disse volumene kan derfor ikke garanteres.

1.4 Invitasjon til informasjonsmøte på anbudsprosess
REMA 1000 arrangerer et informasjonsmøte for leverandører av konsulenttjenester. Formålet er å
introdusere anbudsprosessen for konsulenttjenester, inkludert en introduksjon av anbudsplattformen,
Keelvar.
Introduksjonsmøte vil bli holdt 21. desember. Kl 12:00 – 13:00 CET.
Vennligste bekreft deres deltakelse i anbudsprosessen og deltakelse på informasjonsmøte gjennom
meldingsfunksjonen i Keelvar, senest 22. desember.
Tilgang til Keelvar skal dere ha fått gjennom lenke vedlagt i egen e-post: «REMA 1000 – anbud for
konsulenttjenester». Vær oppmerksom på at den "systemgenererte e-posten" ovenfor kan havne i
søppelpostmappen din fra senderen: «no-reply@keelvar.com». Dersom du ikke har mottatt denne lenken, ta
kontakt med Martin Cappelen Smith.

For å delta i møtet, gå inn på vedlagte link:

https://teams.microsoft.com/l/meetup-
join/19%3ameeting_Njk3NTZmMTctMDY0Ni00YmJjLWE3YjktOTY4NTQyZWI1N2Zi%40thread.v2/0?co
ntext=%7b%22Tid%22%3a%22bbf77a8f-7fa8-45a0-81db-
7ad345a349c0%22%2c%22Oid%22%3a%22999ad771-0920-4877-82aa-238ac0baafb4%22%7d



2. Anbudsprosessen og tilhørende frister
Følgende tidslinje og frister har blitt satt for anbudet, det kan forekomme endringer i datoer:
Tidslinje Prosess Beskrivelse
20. Desember 2022 Anbudspublisering Anbudet vil bli holdt på en online e-sourcing plattform
som heter Keelvar. Her vil dere motta en invitasjon i
mailboksen fra følgende adresse: Keelvar Systems

3

no-reply@keelvar.com
3. januar 2023 Informasjonsmøte Online leverandørinformasjonsmøte: Informasjon om
REMA 1000 og anbudsprosessen.
Vennligst bekreft din deltakelse gjennom
meldingsfunksjonen i Keelvar senest 22. desember.
Invitasjonen til nettmøtet ligger under «1.3 Invitasjon til
informasjonsmøte på anbudsprosess».
10. januar 2023 Innsendelse av tilbud Tidsfrist for å sende inn i Keelvar, 10. januar 2023, Kl.
13:00 CET.
Uke 2 - 4 Evaluering av mottatte
tilbud
REMA vil evaluere mottatte tilbud.



2.1 Deltagelse i anbudsprosess
Hvis dere ønsker å delta i anbudet, ber vi dere vennligst gå til Keelvar og bekrefte deltakelse til
anbudsprosessen og informasjonsmøte 22. desember via meldingsfunksjonen i Keelvar. Dere vil få
tilgang til anbudsmaterialet i samme portal.
Vi håper at dette anbudet er interessant for dere, og vi ser frem til deres deltakelse i denne prosessen

2.2 Anbudspublisering og utsendelse
Dere vil finne alt av anbudsmateriale sammen med retningslinjer i Keelvar systemet. Anbudsmaterialet er
ikke offentlig publisert, ettersom det bare blir utsendt til forhåndsgodkjente leverandører. Som følge av dette,
skal ikke anbudsmateriale deles med andre parter/organisasjoner, hvis ikke de inngår som en del av
leverandørens tilbud – som en underleverandør.
For å bli ansett som kvalifisert for å bli vurdert, er det krav til at budet og alt av nødvendig dokumentasjon er
lastet opp i Keelvar. I tillegg må alle leverandører følge den oppsatte tidslinjen, samt godta REMA 1000 sine
standard vilkår og betingelser.

2.3 Innsending av spørsmål relatert til anbudsprosessen
Inviterte leverandører vil bli forespurt til å sende spørsmål relatert til innholdet i anbudet og de spesifikke
kravene via meldingssystemet på Keelvar.
All kommunikasjon i løpet av anbudsprosessen skal foregå gjennom Keelvar og blir håndtert av:
REMA Anskaffelser,
Martin Cappelen Smith
E-post: Martin.cappelen.smith@rema.no

4

(Denne e-posten skal kun benyttes dersom man ikke får tilgang eller har mottatt invitasjon til Keelvar. Andre
henvendelser vedrørende anbudet til denne e-posten vil ikke bli besvart.)
Vi ønsker ikke at dere henvender dere, eller kontakter, direkte til REMA 1000 / REMA 1000 ansatte eller
andre parter som har tilknytning til selskapet, dersom dere har ønske om ytterligere informasjon. Disse
partene har ikke tilgang til spørsmålene før etter tidsfristen. Vi ber om at all informasjon går igjennom
meldingssystemet til Keelvar. Dersom meldingene skulle inneholde informasjon sensitive til selskapet, vil
spørsmålene bli besvart kun til den aktuelle leverandøren.
Dersom dere skulle ha tekniske problemer med anbudsplattformen, Keelvar, vennligst ta kontakt med
Keelvar support på support@keelvar.com

2.4 Svar på skriftlige spørsmål
Alle skriftlige svar til innkommende spørsmål vil være anonymisert og besvares på fortløpende basis til alle
leverandører.

3. Innhold og struktur i anbudet

3.1 Krav til tilbud
Alle priser skal være i NOK ekskludert MVA.
Tilbud skal være gyldig i 16 uker etter frist til å gi tilbud.
Prisene oppgitt i dette anbudet skal inkludere alle honorarer og kostnader knyttet til kjøp av
konsulenttjenestene, eksklusiv eventuell overtidssats, transport- og losjikostnader (transport og losji betales
til kostpris uten påslag, og REMA 1000 kan bestemme hvilke hoteller som skal benyttes).

3.2 Dokumenter som må fylles ut og/eller legges ved i anbudet
For å kunne bli vurdert, er det påkrevd at leverandøren har fylt ut følgende dokumenter i anbudet.
Dokument Navn Formål Beskrivelse
0 Keelvar
introduksjonsguide
(PDF)
Informasjon til
leverandør
Introduksjon til Keelvar-plattformen
A Anbudsinformasjon
(PDF)
Informasjon til
leverandør
Detaljert informasjon på omfanget,
anbudsprosessen, definisjoner, krav for deltagelse
og evaluering.
B Rammeavtale for
kjøp av
konsulenttjenester
(PDF)
Informasjon til
leverandør
Rammeavtale for kjøp av konsulenttjenester
C REMA 1000 sine
etiske retningslinjer
(PDF)
Et hoveddokument og et tilhørende dokument med
forklaringer til REMA 1000 sin etiske retningslinjer
for leverandører
D Databehandleravtale
(PDF)
Databehandleravtale til REMA 1000

5

Keelvar RFI Utfylles av
leverandør
Leverandøren skal her svare på spørsmål relatert
til selskapet, kompetanse og tjenestetilbud, i tillegg
etterspørres det:
• Dokument som beskriver leverandøren og
dens hovedtjenester og
nøkkelkompetanser
• Eksempler på CV-er for alle roller som
leverandøren byr på, inkludert antall år
med relevant erfaring med hensyn til de
spesifikke kvalifikasjoner som er oppgitt i
anbudsdokumentet
• Dersom det er relevant, referanser fra
tidligere kunder med kontaktinformasjon
Keelvar Prisark Utfylles av
leverandør
Leverandøren skal her fylle ut priser på etterspurte
konsulentroller
Svar på prisarket gjøres ved å laste ned excel-
template som skal fylles ut og lastes opp

3.3 Guide til prisarket
Alle leverandører anbefales å gi et tilbud på alle tjenester i prisarket, dette er derimot ikke påkrevd.


3.4 Kommersielle betingelser
Rabatter på bakgrunn av endrede kommersielle betingelser vil bli lagt sammen. Det vil si at en rabatt på 3%
på betalingsbetingelser og 2% på kontraktslengde, vil til sammen gi en 5% rabatt på priser oppgitt i budarket.

Kolonnenavn Beskrivelse
Maksimum timepris eks. MVA
(onshore)
Maksimum timepriser er eks. mva., inkludert alle
ekstrakostnader unntatt, eventuell overtid, transport og losji.
Overtidssats (%) ved vanlig ukedag Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber over 8 timer hos kunde ved vanlig
ukedag.
Overtidssats (%) Lørdager, søn- og
helgedager
Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber lørdag, søndager og/eller helgedager
hos kunde.
Navn Beskrivelse
RABATT (%) Totalt forbruk hos
leverandør
Her har leverandøren mulighet til å legge inn rabatt basert på
hvor høyt forbruk REMA 1000 vil ha hos leverandøren.
Rabatten betales tilbake til REMA 1000 i slutten av året (en
kickback-modell).
RABATT (%) Betalingsbetingelser Standard betalingsbetingelser er 60 dager. Vennligst spesifiser
om du vil gi en rabatt eller en økning dersom andre
betalingsbetingelser gjelder.
RABATT (%) Kontraktslengde for
konsulenter ved avrop på rammeavtale
Standard kontraktslengde for konsulenter ved avrop på
rammeavtale er 0-6 måneder. Eventuelt kan leverandøren

6



3.5 Evaluering
Leverandøren skal oppfylle alle relevante krav i vedlagte dokumenter.

REMA 1000 forbeholder seg retten til å avvise tilbud som ikke oppfyller alle vurderingskriterier.
Det endelige utvalget av leverandører som vil få tilbud om kontrakt vil avhenge av hvilke tilbud som kommer.
REMA 1000 arbeider med en hypotese om at anbudsprosessen vil resultere i leverandørkonsolidering, og
dermed redusere antall leverandører per kategori.


4. Avtalebetingelser
Følgende kontraktuelle betingelser er gjeldende for dette anbudet:

• Betalingsbetingelser: 60 dager
• Prisene skal gjelde i hele avtaleperioden, med mindre det har vært en prisjustering i henhold til
Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Prisene skal årlig justeres 60% av Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Konsulentene skal føre timer til nærmeste kvarter
• Avtaleperioden for rammeavtalen er 3 år med opsjon på 1+1 forlengelse.
o Dersom avtalen ikke sies opp, vil avtalen fortsette å løpe med en oppsigelsesfrist på 3
måneders skriftlig varsel for begge parter.
• Kontraktslengde for konsulenter ved avrop på rammeavtale: 0 – 6 måneder
• Leverandør skal fakturere REMA etterskuddsvis for tjenester som leveres

Dersom tilbyder avdekker mangler i forespørselen eller konflikter mellom de ulike deler av denne, skal REMA
1000 øyeblikkelig varsles skriftlig om dette. Har dere andre spørsmål/kommentarer til forespørselen, skal
dette rettes skriftlig i spørsmålsfunksjonen til Keelvar.

spesifisere en prosentvis rabatt når konsulentkontraktens
lengde er mer enn 6 måneder.
RABATT (%) Kontraktslengde på
Rammeavtale (Standard 3 år)
Standard kontraktslengde er 3 år med mulighet for å forlenge
med ett år to ganger. Eventuelt kan leverandøren spesifisere en
prosentvis rabatt, som vil gi REMA 1000 incentiv til å inngå en
lengre kontrakt.
RABATT (%) dersom andre selskaper i
Reitangruppen benytter rammeavtalen
Rabatt som gis dersom andre selskaper i Reitangruppen velger
å benytte seg av rammeavtalen

Navn Beskrivelse
Total cost of ownership (TCO) De totale kostnadene ved leverandøren, inkludert forventet
påvirkning fra priser, gebyrer og kommersielle vilkår.
Kvalitet Kvalitet er en viktig parameter for å oppnå effekten man ønsker.
Kvalitet blir evaluert på graden av riktige konsulenter og
kompetanse for å matche oppgaveporteføljen hos REMA 1000.
Kategoridekning Leverandører vurderes på evnen til å gi en bred dekning av
rådgivingstjenester som er relevante for REMA 1000.

7

Forslaget til rammeavtale vil bli utarbeidet på bakgrunn av REMA 1000 sin standard rammeavtale. Denne
avtalen er basert på REMA 1000 sine krav og avtalte priser i denne anbudsrunden.
Kontrakter som inngås som følge av anbudsprosessen vil erstatte eksisterende kontrakter innenfor denne
kategorien. Annullering/erstatning av eksisterende kontrakter vil tre i kraft fra datoen ny kontrakt er signert.

5. Formelle krav til anbudsbesvarelsen
I det fremlagte tilbudet er det viktig at følgende krav er tilfredsstilt. Dersom dette ikke er tilfelle, er det
mulighet for at tilbudet kan bli avslått.
5.1 Formelle krav
Krav 1: Tilbudets innhold

Leverandørens tilbud må inneholde de følgende punktene:
1. Et komplett og utfylt prisark lastet opp i Keelvar før svarfristen.
2. Et komplett svar til alle RFI spørsmål før svarfristen.
a. Husk å laste opp alle påkrevde vedlegg

Krav 2: Tidsfrist

Tilbud kan ikke leveres senere enn 10. januar kl. 13:00 via Keelvar. Tilbud som blir levert etter denne fristen
risikerer å ikke bli akseptert og dermed heller ikke vurdert.

Krav 3: Tilbudets struktur

Strukturen til tilbudsforespørselen kan ikke bli endret. Alle relevante felter som dere ønsker å legge
inn tilbud på må fylles inn og oppfylle kravene til Keelvar. Vi oppfordrer leverandører til å legge inn tilbud på
så mange av områdene som mulig.

Krav 4: Tilbudets valuta

Leverandørens tilbud må være oppgitt i NOK.
Krav 5: Tilbudets gyldighet

Tilbudet skal være gyldig i 16 uker etter den satte fristen for levering.
Krav 6: Minimumskrav

Leverandøren må tilfredsstille alle REMA sine etiske krav (se vedlegg: REMA 1000 Etiske retningslinjer)


5.2 Andre krav til anbudet
- REMA 1000 vil teste tilbud gitt i dette anbudet på bakgrunn av mange ulike kriterier, og forbeholder
seg retten til å avvise alle tilbud. REMA 1000 har også retten til å evaluere alle vurderingskriterier i
dokumentasjonen og godkjenne tilbud som ikke har den laveste prisen.
- Enhver tvist som omhandler denne anbudsprosessen, vil løses under Norsk domstol

5.3 Ytterligere kostnader

8

REMA 1000 vil ikke godta kostnader knyttet til produktene utover det som fremkommer i dette anbudet.

5.4 Anonymitet, konfidensialitet, og taushetsplikt
REMA 1000 krever at alle deltagende leverandører holder all informasjon som kommer frem i
anbudsprosessen konfidensielt. REMA 1000 har samme prosedyre når det kommer til informasjonen fra
leverandørene.

5.5 Omfangsbegrensninger
Omfanget av dette anbudet gjelder bare REMA 1000 i Norge, som tilsier at omfanget utelater andre REMA
1000 institusjoner (f.eks. Reitan Convenience, REMA 1000 DK).

5.6 Kostnader relatert til anbudsprosessen
REMA 1000 vil ikke være ansvarlig for kostnader som påløpes hos leverandører som følger av denne
anbudsprosessen – dette referer til mulige kostnader tilknyttet utarbeidelsen av tilbudet eller deltagelse i
forhandlinger. Hvis det gjennomføres en test periode, vil leverandør(er) være ansvarlig for kostnader inntil
leverandør(ene) er godkjent.

5.7 Ansvarsfraskrivelse
REMA 1000 forbeholder seg retten, uten ansvar, til å kansellere anbudsrunden på ethvert tidspunkt.

5.8 Avslag på tilbud
Leverandører som ikke er kvalifisert eller oppfyller minstekravene kan bli avvist, og innholdet i et avvist tilbud
vil ikke bli vurdert nærmere.
Det er derfor svært viktig at tilbudet inneholder all nødvendig informasjon og leveres i formatet som
etterspørres.

5.9 Etiske retningslinjer
Det forventes at leverandører følger REMA 1000 sine etiske retningslinjer og bekrefter at disse
retningslinjene er fulgt ved å delta i anbudet.



3

no-reply@keelvar.com
3. januar 2023 Informasjonsmøte Online leverandørinformasjonsmøte: Informasjon om
REMA 1000 og anbudsprosessen.
Vennligst bekreft din deltakelse gjennom
meldingsfunksjonen i Keelvar senest 22. desember.
Invitasjonen til nettmøtet ligger under «1.3 Invitasjon til
informasjonsmøte på anbudsprosess».
10. januar 2023 Innsendelse av tilbud Tidsfrist for å sende inn i Keelvar, 10. januar 2023, Kl.
13:00 CET.
Uke 2 - 4 Evaluering av mottatte
tilbud
REMA vil evaluere mottatte tilbud.



2.1 Deltagelse i anbudsprosess
Hvis dere ønsker å delta i anbudet, ber vi dere vennligst gå til Keelvar og bekrefte deltakelse til
anbudsprosessen og informasjonsmøte 22. desember via meldingsfunksjonen i Keelvar. Dere vil få
tilgang til anbudsmaterialet i samme portal.
Vi håper at dette anbudet er interessant for dere, og vi ser frem til deres deltakelse i denne prosessen

2.2 Anbudspublisering og utsendelse
Dere vil finne alt av anbudsmateriale sammen med retningslinjer i Keelvar systemet. Anbudsmaterialet er
ikke offentlig publisert, ettersom det bare blir utsendt til forhåndsgodkjente leverandører. Som følge av dette,
skal ikke anbudsmateriale deles med andre parter/organisasjoner, hvis ikke de inngår som en del av
leverandørens tilbud – som en underleverandør.
For å bli ansett som kvalifisert for å bli vurdert, er det krav til at budet og alt av nødvendig dokumentasjon er
lastet opp i Keelvar. I tillegg må alle leverandører følge den oppsatte tidslinjen, samt godta REMA 1000 sine
standard vilkår og betingelser.

2.3 Innsending av spørsmål relatert til anbudsprosessen
Inviterte leverandører vil bli forespurt til å sende spørsmål relatert til innholdet i anbudet og de spesifikke
kravene via meldingssystemet på Keelvar.
All kommunikasjon i løpet av anbudsprosessen skal foregå gjennom Keelvar og blir håndtert av:
REMA Anskaffelser,
Martin Cappelen Smith
E-post: Martin.cappelen.smith@rema.no

4

(Denne e-posten skal kun benyttes dersom man ikke får tilgang eller har mottatt invitasjon til Keelvar. Andre
henvendelser vedrørende anbudet til denne e-posten vil ikke bli besvart.)
Vi ønsker ikke at dere henvender dere, eller kontakter, direkte til REMA 1000 / REMA 1000 ansatte eller
andre parter som har tilknytning til selskapet, dersom dere har ønske om ytterligere informasjon. Disse
partene har ikke tilgang til spørsmålene før etter tidsfristen. Vi ber om at all informasjon går igjennom
meldingssystemet til Keelvar. Dersom meldingene skulle inneholde informasjon sensitive til selskapet, vil
spørsmålene bli besvart kun til den aktuelle leverandøren.
Dersom dere skulle ha tekniske problemer med anbudsplattformen, Keelvar, vennligst ta kontakt med
Keelvar support på support@keelvar.com

2.4 Svar på skriftlige spørsmål
Alle skriftlige svar til innkommende spørsmål vil være anonymisert og besvares på fortløpende basis til alle
leverandører.

3. Innhold og struktur i anbudet

3.1 Krav til tilbud
Alle priser skal være i NOK ekskludert MVA.
Tilbud skal være gyldig i 16 uker etter frist til å gi tilbud.
Prisene oppgitt i dette anbudet skal inkludere alle honorarer og kostnader knyttet til kjøp av
konsulenttjenestene, eksklusiv eventuell overtidssats, transport- og losjikostnader (transport og losji betales
til kostpris uten påslag, og REMA 1000 kan bestemme hvilke hoteller som skal benyttes).

3.2 Dokumenter som må fylles ut og/eller legges ved i anbudet
For å kunne bli vurdert, er det påkrevd at leverandøren har fylt ut følgende dokumenter i anbudet.
Dokument Navn Formål Beskrivelse
0 Keelvar
introduksjonsguide
(PDF)
Informasjon til
leverandør
Introduksjon til Keelvar-plattformen
A Anbudsinformasjon
(PDF)
Informasjon til
leverandør
Detaljert informasjon på omfanget,
anbudsprosessen, definisjoner, krav for deltagelse
og evaluering.
B Rammeavtale for
kjøp av
konsulenttjenester
(PDF)
Informasjon til
leverandør
Rammeavtale for kjøp av konsulenttjenester
C REMA 1000 sine
etiske retningslinjer
(PDF)
Et hoveddokument og et tilhørende dokument med
forklaringer til REMA 1000 sin etiske retningslinjer
for leverandører
D Databehandleravtale
(PDF)
Databehandleravtale til REMA 1000

5

Keelvar RFI Utfylles av
leverandør
Leverandøren skal her svare på spørsmål relatert
til selskapet, kompetanse og tjenestetilbud, i tillegg
etterspørres det:
• Dokument som beskriver leverandøren og
dens hovedtjenester og
nøkkelkompetanser
• Eksempler på CV-er for alle roller som
leverandøren byr på, inkludert antall år
med relevant erfaring med hensyn til de
spesifikke kvalifikasjoner som er oppgitt i
anbudsdokumentet
• Dersom det er relevant, referanser fra
tidligere kunder med kontaktinformasjon
Keelvar Prisark Utfylles av
leverandør
Leverandøren skal her fylle ut priser på etterspurte
konsulentroller
Svar på prisarket gjøres ved å laste ned excel-
template som skal fylles ut og lastes opp

3.3 Guide til prisarket
Alle leverandører anbefales å gi et tilbud på alle tjenester i prisarket, dette er derimot ikke påkrevd.


3.4 Kommersielle betingelser
Rabatter på bakgrunn av endrede kommersielle betingelser vil bli lagt sammen. Det vil si at en rabatt på 3%
på betalingsbetingelser og 2% på kontraktslengde, vil til sammen gi en 5% rabatt på priser oppgitt i budarket.

Kolonnenavn Beskrivelse
Maksimum timepris eks. MVA
(onshore)
Maksimum timepriser er eks. mva., inkludert alle
ekstrakostnader unntatt, eventuell overtid, transport og losji.
Overtidssats (%) ved vanlig ukedag Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber over 8 timer hos kunde ved vanlig
ukedag.
Overtidssats (%) Lørdager, søn- og
helgedager
Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber lørdag, søndager og/eller helgedager
hos kunde.
Navn Beskrivelse
RABATT (%) Totalt forbruk hos
leverandør
Her har leverandøren mulighet til å legge inn rabatt basert på
hvor høyt forbruk REMA 1000 vil ha hos leverandøren.
Rabatten betales tilbake til REMA 1000 i slutten av året (en
kickback-modell).
RABATT (%) Betalingsbetingelser Standard betalingsbetingelser er 60 dager. Vennligst spesifiser
om du vil gi en rabatt eller en økning dersom andre
betalingsbetingelser gjelder.
RABATT (%) Kontraktslengde for
konsulenter ved avrop på rammeavtale
Standard kontraktslengde for konsulenter ved avrop på
rammeavtale er 0-6 måneder. Eventuelt kan leverandøren

6



3.5 Evaluering
Leverandøren skal oppfylle alle relevante krav i vedlagte dokumenter.

REMA 1000 forbeholder seg retten til å avvise tilbud som ikke oppfyller alle vurderingskriterier.
Det endelige utvalget av leverandører som vil få tilbud om kontrakt vil avhenge av hvilke tilbud som kommer.
REMA 1000 arbeider med en hypotese om at anbudsprosessen vil resultere i leverandørkonsolidering, og
dermed redusere antall leverandører per kategori.


4. Avtalebetingelser
Følgende kontraktuelle betingelser er gjeldende for dette anbudet:

• Betalingsbetingelser: 60 dager
• Prisene skal gjelde i hele avtaleperioden, med mindre det har vært en prisjustering i henhold til
Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Prisene skal årlig justeres 60% av Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Konsulentene skal føre timer til nærmeste kvarter
• Avtaleperioden for rammeavtalen er 3 år med opsjon på 1+1 forlengelse.
o Dersom avtalen ikke sies opp, vil avtalen fortsette å løpe med en oppsigelsesfrist på 3
måneders skriftlig varsel for begge parter.
• Kontraktslengde for konsulenter ved avrop på rammeavtale: 0 – 6 måneder
• Leverandør skal fakturere REMA etterskuddsvis for tjenester som leveres

Dersom tilbyder avdekker mangler i forespørselen eller konflikter mellom de ulike deler av denne, skal REMA
1000 øyeblikkelig varsles skriftlig om dette. Har dere andre spørsmål/kommentarer til forespørselen, skal
dette rettes skriftlig i spørsmålsfunksjonen til Keelvar.

spesifisere en prosentvis rabatt når konsulentkontraktens
lengde er mer enn 6 måneder.
RABATT (%) Kontraktslengde på
Rammeavtale (Standard 3 år)
Standard kontraktslengde er 3 år med mulighet for å forlenge
med ett år to ganger. Eventuelt kan leverandøren spesifisere en
prosentvis rabatt, som vil gi REMA 1000 incentiv til å inngå en
lengre kontrakt.
RABATT (%) dersom andre selskaper i
Reitangruppen benytter rammeavtalen
Rabatt som gis dersom andre selskaper i Reitangruppen velger
å benytte seg av rammeavtalen

Navn Beskrivelse
Total cost of ownership (TCO) De totale kostnadene ved leverandøren, inkludert forventet
påvirkning fra priser, gebyrer og kommersielle vilkår.
Kvalitet Kvalitet er en viktig parameter for å oppnå effekten man ønsker.
Kvalitet blir evaluert på graden av riktige konsulenter og
kompetanse for å matche oppgaveporteføljen hos REMA 1000.
Kategoridekning Leverandører vurderes på evnen til å gi en bred dekning av
rådgivingstjenester som er relevante for REMA 1000.

7

Forslaget til rammeavtale vil bli utarbeidet på bakgrunn av REMA 1000 sin standard rammeavtale. Denne
avtalen er basert på REMA 1000 sine krav og avtalte priser i denne anbudsrunden.
Kontrakter som inngås som følge av anbudsprosessen vil erstatte eksisterende kontrakter innenfor denne
kategorien. Annullering/erstatning av eksisterende kontrakter vil tre i kraft fra datoen ny kontrakt er signert.

5. Formelle krav til anbudsbesvarelsen
I det fremlagte tilbudet er det viktig at følgende krav er tilfredsstilt. Dersom dette ikke er tilfelle, er det
mulighet for at tilbudet kan bli avslått.
5.1 Formelle krav
Krav 1: Tilbudets innhold

Leverandørens tilbud må inneholde de følgende punktene:
1. Et komplett og utfylt prisark lastet opp i Keelvar før svarfristen.
2. Et komplett svar til alle RFI spørsmål før svarfristen.
a. Husk å laste opp alle påkrevde vedlegg

Krav 2: Tidsfrist

Tilbud kan ikke leveres senere enn 10. januar kl. 13:00 via Keelvar. Tilbud som blir levert etter denne fristen
risikerer å ikke bli akseptert og dermed heller ikke vurdert.

Krav 3: Tilbudets struktur

Strukturen til tilbudsforespørselen kan ikke bli endret. Alle relevante felter som dere ønsker å legge
inn tilbud på må fylles inn og oppfylle kravene til Keelvar. Vi oppfordrer leverandører til å legge inn tilbud på
så mange av områdene som mulig.

Krav 4: Tilbudets valuta

Leverandørens tilbud må være oppgitt i NOK.
Krav 5: Tilbudets gyldighet

Tilbudet skal være gyldig i 16 uker etter den satte fristen for levering.
Krav 6: Minimumskrav

Leverandøren må tilfredsstille alle REMA sine etiske krav (se vedlegg: REMA 1000 Etiske retningslinjer)


5.2 Andre krav til anbudet
- REMA 1000 vil teste tilbud gitt i dette anbudet på bakgrunn av mange ulike kriterier, og forbeholder
seg retten til å avvise alle tilbud. REMA 1000 har også retten til å evaluere alle vurderingskriterier i
dokumentasjonen og godkjenne tilbud som ikke har den laveste prisen.
- Enhver tvist som omhandler denne anbudsprosessen, vil løses under Norsk domstol

5.3 Ytterligere kostnader

8

REMA 1000 vil ikke godta kostnader knyttet til produktene utover det som fremkommer i dette anbudet.

5.4 Anonymitet, konfidensialitet, og taushetsplikt
REMA 1000 krever at alle deltagende leverandører holder all informasjon som kommer frem i
anbudsprosessen konfidensielt. REMA 1000 har samme prosedyre når det kommer til informasjonen fra
leverandørene.

5.5 Omfangsbegrensninger
Omfanget av dette anbudet gjelder bare REMA 1000 i Norge, som tilsier at omfanget utelater andre REMA
1000 institusjoner (f.eks. Reitan Convenience, REMA 1000 DK).

5.6 Kostnader relatert til anbudsprosessen
REMA 1000 vil ikke være ansvarlig for kostnader som påløpes hos leverandører som følger av denne
anbudsprosessen – dette referer til mulige kostnader tilknyttet utarbeidelsen av tilbudet eller deltagelse i
forhandlinger. Hvis det gjennomføres en test periode, vil leverandør(er) være ansvarlig for kostnader inntil
leverandør(ene) er godkjent.

5.7 Ansvarsfraskrivelse
REMA 1000 forbeholder seg retten, uten ansvar, til å kansellere anbudsrunden på ethvert tidspunkt.

5.8 Avslag på tilbud
Leverandører som ikke er kvalifisert eller oppfyller minstekravene kan bli avvist, og innholdet i et avvist tilbud
vil ikke bli vurdert nærmere.
Det er derfor svært viktig at tilbudet inneholder all nødvendig informasjon og leveres i formatet som
etterspørres.

5.9 Etiske retningslinjer
Det forventes at leverandører følger REMA 1000 sine etiske retningslinjer og bekrefter at disse
retningslinjene er fulgt ved å delta i anbudet.



4

(Denne e-posten skal kun benyttes dersom man ikke får tilgang eller har mottatt invitasjon til Keelvar. Andre
henvendelser vedrørende anbudet til denne e-posten vil ikke bli besvart.)
Vi ønsker ikke at dere henvender dere, eller kontakter, direkte til REMA 1000 / REMA 1000 ansatte eller
andre parter som har tilknytning til selskapet, dersom dere har ønske om ytterligere informasjon. Disse
partene har ikke tilgang til spørsmålene før etter tidsfristen. Vi ber om at all informasjon går igjennom
meldingssystemet til Keelvar. Dersom meldingene skulle inneholde informasjon sensitive til selskapet, vil
spørsmålene bli besvart kun til den aktuelle leverandøren.
Dersom dere skulle ha tekniske problemer med anbudsplattformen, Keelvar, vennligst ta kontakt med
Keelvar support på support@keelvar.com

2.4 Svar på skriftlige spørsmål
Alle skriftlige svar til innkommende spørsmål vil være anonymisert og besvares på fortløpende basis til alle
leverandører.

3. Innhold og struktur i anbudet

3.1 Krav til tilbud
Alle priser skal være i NOK ekskludert MVA.
Tilbud skal være gyldig i 16 uker etter frist til å gi tilbud.
Prisene oppgitt i dette anbudet skal inkludere alle honorarer og kostnader knyttet til kjøp av
konsulenttjenestene, eksklusiv eventuell overtidssats, transport- og losjikostnader (transport og losji betales
til kostpris uten påslag, og REMA 1000 kan bestemme hvilke hoteller som skal benyttes).

3.2 Dokumenter som må fylles ut og/eller legges ved i anbudet
For å kunne bli vurdert, er det påkrevd at leverandøren har fylt ut følgende dokumenter i anbudet.
Dokument Navn Formål Beskrivelse
0 Keelvar
introduksjonsguide
(PDF)
Informasjon til
leverandør
Introduksjon til Keelvar-plattformen
A Anbudsinformasjon
(PDF)
Informasjon til
leverandør
Detaljert informasjon på omfanget,
anbudsprosessen, definisjoner, krav for deltagelse
og evaluering.
B Rammeavtale for
kjøp av
konsulenttjenester
(PDF)
Informasjon til
leverandør
Rammeavtale for kjøp av konsulenttjenester
C REMA 1000 sine
etiske retningslinjer
(PDF)
Et hoveddokument og et tilhørende dokument med
forklaringer til REMA 1000 sin etiske retningslinjer
for leverandører
D Databehandleravtale
(PDF)
Databehandleravtale til REMA 1000

5

Keelvar RFI Utfylles av
leverandør
Leverandøren skal her svare på spørsmål relatert
til selskapet, kompetanse og tjenestetilbud, i tillegg
etterspørres det:
• Dokument som beskriver leverandøren og
dens hovedtjenester og
nøkkelkompetanser
• Eksempler på CV-er for alle roller som
leverandøren byr på, inkludert antall år
med relevant erfaring med hensyn til de
spesifikke kvalifikasjoner som er oppgitt i
anbudsdokumentet
• Dersom det er relevant, referanser fra
tidligere kunder med kontaktinformasjon
Keelvar Prisark Utfylles av
leverandør
Leverandøren skal her fylle ut priser på etterspurte
konsulentroller
Svar på prisarket gjøres ved å laste ned excel-
template som skal fylles ut og lastes opp

3.3 Guide til prisarket
Alle leverandører anbefales å gi et tilbud på alle tjenester i prisarket, dette er derimot ikke påkrevd.


3.4 Kommersielle betingelser
Rabatter på bakgrunn av endrede kommersielle betingelser vil bli lagt sammen. Det vil si at en rabatt på 3%
på betalingsbetingelser og 2% på kontraktslengde, vil til sammen gi en 5% rabatt på priser oppgitt i budarket.

Kolonnenavn Beskrivelse
Maksimum timepris eks. MVA
(onshore)
Maksimum timepriser er eks. mva., inkludert alle
ekstrakostnader unntatt, eventuell overtid, transport og losji.
Overtidssats (%) ved vanlig ukedag Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber over 8 timer hos kunde ved vanlig
ukedag.
Overtidssats (%) Lørdager, søn- og
helgedager
Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber lørdag, søndager og/eller helgedager
hos kunde.
Navn Beskrivelse
RABATT (%) Totalt forbruk hos
leverandør
Her har leverandøren mulighet til å legge inn rabatt basert på
hvor høyt forbruk REMA 1000 vil ha hos leverandøren.
Rabatten betales tilbake til REMA 1000 i slutten av året (en
kickback-modell).
RABATT (%) Betalingsbetingelser Standard betalingsbetingelser er 60 dager. Vennligst spesifiser
om du vil gi en rabatt eller en økning dersom andre
betalingsbetingelser gjelder.
RABATT (%) Kontraktslengde for
konsulenter ved avrop på rammeavtale
Standard kontraktslengde for konsulenter ved avrop på
rammeavtale er 0-6 måneder. Eventuelt kan leverandøren

6



3.5 Evaluering
Leverandøren skal oppfylle alle relevante krav i vedlagte dokumenter.

REMA 1000 forbeholder seg retten til å avvise tilbud som ikke oppfyller alle vurderingskriterier.
Det endelige utvalget av leverandører som vil få tilbud om kontrakt vil avhenge av hvilke tilbud som kommer.
REMA 1000 arbeider med en hypotese om at anbudsprosessen vil resultere i leverandørkonsolidering, og
dermed redusere antall leverandører per kategori.


4. Avtalebetingelser
Følgende kontraktuelle betingelser er gjeldende for dette anbudet:

• Betalingsbetingelser: 60 dager
• Prisene skal gjelde i hele avtaleperioden, med mindre det har vært en prisjustering i henhold til
Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Prisene skal årlig justeres 60% av Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Konsulentene skal føre timer til nærmeste kvarter
• Avtaleperioden for rammeavtalen er 3 år med opsjon på 1+1 forlengelse.
o Dersom avtalen ikke sies opp, vil avtalen fortsette å løpe med en oppsigelsesfrist på 3
måneders skriftlig varsel for begge parter.
• Kontraktslengde for konsulenter ved avrop på rammeavtale: 0 – 6 måneder
• Leverandør skal fakturere REMA etterskuddsvis for tjenester som leveres

Dersom tilbyder avdekker mangler i forespørselen eller konflikter mellom de ulike deler av denne, skal REMA
1000 øyeblikkelig varsles skriftlig om dette. Har dere andre spørsmål/kommentarer til forespørselen, skal
dette rettes skriftlig i spørsmålsfunksjonen til Keelvar.

spesifisere en prosentvis rabatt når konsulentkontraktens
lengde er mer enn 6 måneder.
RABATT (%) Kontraktslengde på
Rammeavtale (Standard 3 år)
Standard kontraktslengde er 3 år med mulighet for å forlenge
med ett år to ganger. Eventuelt kan leverandøren spesifisere en
prosentvis rabatt, som vil gi REMA 1000 incentiv til å inngå en
lengre kontrakt.
RABATT (%) dersom andre selskaper i
Reitangruppen benytter rammeavtalen
Rabatt som gis dersom andre selskaper i Reitangruppen velger
å benytte seg av rammeavtalen

Navn Beskrivelse
Total cost of ownership (TCO) De totale kostnadene ved leverandøren, inkludert forventet
påvirkning fra priser, gebyrer og kommersielle vilkår.
Kvalitet Kvalitet er en viktig parameter for å oppnå effekten man ønsker.
Kvalitet blir evaluert på graden av riktige konsulenter og
kompetanse for å matche oppgaveporteføljen hos REMA 1000.
Kategoridekning Leverandører vurderes på evnen til å gi en bred dekning av
rådgivingstjenester som er relevante for REMA 1000.

7

Forslaget til rammeavtale vil bli utarbeidet på bakgrunn av REMA 1000 sin standard rammeavtale. Denne
avtalen er basert på REMA 1000 sine krav og avtalte priser i denne anbudsrunden.
Kontrakter som inngås som følge av anbudsprosessen vil erstatte eksisterende kontrakter innenfor denne
kategorien. Annullering/erstatning av eksisterende kontrakter vil tre i kraft fra datoen ny kontrakt er signert.

5. Formelle krav til anbudsbesvarelsen
I det fremlagte tilbudet er det viktig at følgende krav er tilfredsstilt. Dersom dette ikke er tilfelle, er det
mulighet for at tilbudet kan bli avslått.
5.1 Formelle krav
Krav 1: Tilbudets innhold

Leverandørens tilbud må inneholde de følgende punktene:
1. Et komplett og utfylt prisark lastet opp i Keelvar før svarfristen.
2. Et komplett svar til alle RFI spørsmål før svarfristen.
a. Husk å laste opp alle påkrevde vedlegg

Krav 2: Tidsfrist

Tilbud kan ikke leveres senere enn 10. januar kl. 13:00 via Keelvar. Tilbud som blir levert etter denne fristen
risikerer å ikke bli akseptert og dermed heller ikke vurdert.

Krav 3: Tilbudets struktur

Strukturen til tilbudsforespørselen kan ikke bli endret. Alle relevante felter som dere ønsker å legge
inn tilbud på må fylles inn og oppfylle kravene til Keelvar. Vi oppfordrer leverandører til å legge inn tilbud på
så mange av områdene som mulig.

Krav 4: Tilbudets valuta

Leverandørens tilbud må være oppgitt i NOK.
Krav 5: Tilbudets gyldighet

Tilbudet skal være gyldig i 16 uker etter den satte fristen for levering.
Krav 6: Minimumskrav

Leverandøren må tilfredsstille alle REMA sine etiske krav (se vedlegg: REMA 1000 Etiske retningslinjer)


5.2 Andre krav til anbudet
- REMA 1000 vil teste tilbud gitt i dette anbudet på bakgrunn av mange ulike kriterier, og forbeholder
seg retten til å avvise alle tilbud. REMA 1000 har også retten til å evaluere alle vurderingskriterier i
dokumentasjonen og godkjenne tilbud som ikke har den laveste prisen.
- Enhver tvist som omhandler denne anbudsprosessen, vil løses under Norsk domstol

5.3 Ytterligere kostnader

8

REMA 1000 vil ikke godta kostnader knyttet til produktene utover det som fremkommer i dette anbudet.

5.4 Anonymitet, konfidensialitet, og taushetsplikt
REMA 1000 krever at alle deltagende leverandører holder all informasjon som kommer frem i
anbudsprosessen konfidensielt. REMA 1000 har samme prosedyre når det kommer til informasjonen fra
leverandørene.

5.5 Omfangsbegrensninger
Omfanget av dette anbudet gjelder bare REMA 1000 i Norge, som tilsier at omfanget utelater andre REMA
1000 institusjoner (f.eks. Reitan Convenience, REMA 1000 DK).

5.6 Kostnader relatert til anbudsprosessen
REMA 1000 vil ikke være ansvarlig for kostnader som påløpes hos leverandører som følger av denne
anbudsprosessen – dette referer til mulige kostnader tilknyttet utarbeidelsen av tilbudet eller deltagelse i
forhandlinger. Hvis det gjennomføres en test periode, vil leverandør(er) være ansvarlig for kostnader inntil
leverandør(ene) er godkjent.

5.7 Ansvarsfraskrivelse
REMA 1000 forbeholder seg retten, uten ansvar, til å kansellere anbudsrunden på ethvert tidspunkt.

5.8 Avslag på tilbud
Leverandører som ikke er kvalifisert eller oppfyller minstekravene kan bli avvist, og innholdet i et avvist tilbud
vil ikke bli vurdert nærmere.
Det er derfor svært viktig at tilbudet inneholder all nødvendig informasjon og leveres i formatet som
etterspørres.

5.9 Etiske retningslinjer
Det forventes at leverandører følger REMA 1000 sine etiske retningslinjer og bekrefter at disse
retningslinjene er fulgt ved å delta i anbudet.



5

Keelvar RFI Utfylles av
leverandør
Leverandøren skal her svare på spørsmål relatert
til selskapet, kompetanse og tjenestetilbud, i tillegg
etterspørres det:
• Dokument som beskriver leverandøren og
dens hovedtjenester og
nøkkelkompetanser
• Eksempler på CV-er for alle roller som
leverandøren byr på, inkludert antall år
med relevant erfaring med hensyn til de
spesifikke kvalifikasjoner som er oppgitt i
anbudsdokumentet
• Dersom det er relevant, referanser fra
tidligere kunder med kontaktinformasjon
Keelvar Prisark Utfylles av
leverandør
Leverandøren skal her fylle ut priser på etterspurte
konsulentroller
Svar på prisarket gjøres ved å laste ned excel-
template som skal fylles ut og lastes opp

3.3 Guide til prisarket
Alle leverandører anbefales å gi et tilbud på alle tjenester i prisarket, dette er derimot ikke påkrevd.


3.4 Kommersielle betingelser
Rabatter på bakgrunn av endrede kommersielle betingelser vil bli lagt sammen. Det vil si at en rabatt på 3%
på betalingsbetingelser og 2% på kontraktslengde, vil til sammen gi en 5% rabatt på priser oppgitt i budarket.

Kolonnenavn Beskrivelse
Maksimum timepris eks. MVA
(onshore)
Maksimum timepriser er eks. mva., inkludert alle
ekstrakostnader unntatt, eventuell overtid, transport og losji.
Overtidssats (%) ved vanlig ukedag Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber over 8 timer hos kunde ved vanlig
ukedag.
Overtidssats (%) Lørdager, søn- og
helgedager
Prosentvist påslag som leverandøren inkluderer på timesprisen
når konsulenten jobber lørdag, søndager og/eller helgedager
hos kunde.
Navn Beskrivelse
RABATT (%) Totalt forbruk hos
leverandør
Her har leverandøren mulighet til å legge inn rabatt basert på
hvor høyt forbruk REMA 1000 vil ha hos leverandøren.
Rabatten betales tilbake til REMA 1000 i slutten av året (en
kickback-modell).
RABATT (%) Betalingsbetingelser Standard betalingsbetingelser er 60 dager. Vennligst spesifiser
om du vil gi en rabatt eller en økning dersom andre
betalingsbetingelser gjelder.
RABATT (%) Kontraktslengde for
konsulenter ved avrop på rammeavtale
Standard kontraktslengde for konsulenter ved avrop på
rammeavtale er 0-6 måneder. Eventuelt kan leverandøren

6



3.5 Evaluering
Leverandøren skal oppfylle alle relevante krav i vedlagte dokumenter.

REMA 1000 forbeholder seg retten til å avvise tilbud som ikke oppfyller alle vurderingskriterier.
Det endelige utvalget av leverandører som vil få tilbud om kontrakt vil avhenge av hvilke tilbud som kommer.
REMA 1000 arbeider med en hypotese om at anbudsprosessen vil resultere i leverandørkonsolidering, og
dermed redusere antall leverandører per kategori.


4. Avtalebetingelser
Følgende kontraktuelle betingelser er gjeldende for dette anbudet:

• Betalingsbetingelser: 60 dager
• Prisene skal gjelde i hele avtaleperioden, med mindre det har vært en prisjustering i henhold til
Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Prisene skal årlig justeres 60% av Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Konsulentene skal føre timer til nærmeste kvarter
• Avtaleperioden for rammeavtalen er 3 år med opsjon på 1+1 forlengelse.
o Dersom avtalen ikke sies opp, vil avtalen fortsette å løpe med en oppsigelsesfrist på 3
måneders skriftlig varsel for begge parter.
• Kontraktslengde for konsulenter ved avrop på rammeavtale: 0 – 6 måneder
• Leverandør skal fakturere REMA etterskuddsvis for tjenester som leveres

Dersom tilbyder avdekker mangler i forespørselen eller konflikter mellom de ulike deler av denne, skal REMA
1000 øyeblikkelig varsles skriftlig om dette. Har dere andre spørsmål/kommentarer til forespørselen, skal
dette rettes skriftlig i spørsmålsfunksjonen til Keelvar.

spesifisere en prosentvis rabatt når konsulentkontraktens
lengde er mer enn 6 måneder.
RABATT (%) Kontraktslengde på
Rammeavtale (Standard 3 år)
Standard kontraktslengde er 3 år med mulighet for å forlenge
med ett år to ganger. Eventuelt kan leverandøren spesifisere en
prosentvis rabatt, som vil gi REMA 1000 incentiv til å inngå en
lengre kontrakt.
RABATT (%) dersom andre selskaper i
Reitangruppen benytter rammeavtalen
Rabatt som gis dersom andre selskaper i Reitangruppen velger
å benytte seg av rammeavtalen

Navn Beskrivelse
Total cost of ownership (TCO) De totale kostnadene ved leverandøren, inkludert forventet
påvirkning fra priser, gebyrer og kommersielle vilkår.
Kvalitet Kvalitet er en viktig parameter for å oppnå effekten man ønsker.
Kvalitet blir evaluert på graden av riktige konsulenter og
kompetanse for å matche oppgaveporteføljen hos REMA 1000.
Kategoridekning Leverandører vurderes på evnen til å gi en bred dekning av
rådgivingstjenester som er relevante for REMA 1000.

7

Forslaget til rammeavtale vil bli utarbeidet på bakgrunn av REMA 1000 sin standard rammeavtale. Denne
avtalen er basert på REMA 1000 sine krav og avtalte priser i denne anbudsrunden.
Kontrakter som inngås som følge av anbudsprosessen vil erstatte eksisterende kontrakter innenfor denne
kategorien. Annullering/erstatning av eksisterende kontrakter vil tre i kraft fra datoen ny kontrakt er signert.

5. Formelle krav til anbudsbesvarelsen
I det fremlagte tilbudet er det viktig at følgende krav er tilfredsstilt. Dersom dette ikke er tilfelle, er det
mulighet for at tilbudet kan bli avslått.
5.1 Formelle krav
Krav 1: Tilbudets innhold

Leverandørens tilbud må inneholde de følgende punktene:
1. Et komplett og utfylt prisark lastet opp i Keelvar før svarfristen.
2. Et komplett svar til alle RFI spørsmål før svarfristen.
a. Husk å laste opp alle påkrevde vedlegg

Krav 2: Tidsfrist

Tilbud kan ikke leveres senere enn 10. januar kl. 13:00 via Keelvar. Tilbud som blir levert etter denne fristen
risikerer å ikke bli akseptert og dermed heller ikke vurdert.

Krav 3: Tilbudets struktur

Strukturen til tilbudsforespørselen kan ikke bli endret. Alle relevante felter som dere ønsker å legge
inn tilbud på må fylles inn og oppfylle kravene til Keelvar. Vi oppfordrer leverandører til å legge inn tilbud på
så mange av områdene som mulig.

Krav 4: Tilbudets valuta

Leverandørens tilbud må være oppgitt i NOK.
Krav 5: Tilbudets gyldighet

Tilbudet skal være gyldig i 16 uker etter den satte fristen for levering.
Krav 6: Minimumskrav

Leverandøren må tilfredsstille alle REMA sine etiske krav (se vedlegg: REMA 1000 Etiske retningslinjer)


5.2 Andre krav til anbudet
- REMA 1000 vil teste tilbud gitt i dette anbudet på bakgrunn av mange ulike kriterier, og forbeholder
seg retten til å avvise alle tilbud. REMA 1000 har også retten til å evaluere alle vurderingskriterier i
dokumentasjonen og godkjenne tilbud som ikke har den laveste prisen.
- Enhver tvist som omhandler denne anbudsprosessen, vil løses under Norsk domstol

5.3 Ytterligere kostnader

8

REMA 1000 vil ikke godta kostnader knyttet til produktene utover det som fremkommer i dette anbudet.

5.4 Anonymitet, konfidensialitet, og taushetsplikt
REMA 1000 krever at alle deltagende leverandører holder all informasjon som kommer frem i
anbudsprosessen konfidensielt. REMA 1000 har samme prosedyre når det kommer til informasjonen fra
leverandørene.

5.5 Omfangsbegrensninger
Omfanget av dette anbudet gjelder bare REMA 1000 i Norge, som tilsier at omfanget utelater andre REMA
1000 institusjoner (f.eks. Reitan Convenience, REMA 1000 DK).

5.6 Kostnader relatert til anbudsprosessen
REMA 1000 vil ikke være ansvarlig for kostnader som påløpes hos leverandører som følger av denne
anbudsprosessen – dette referer til mulige kostnader tilknyttet utarbeidelsen av tilbudet eller deltagelse i
forhandlinger. Hvis det gjennomføres en test periode, vil leverandør(er) være ansvarlig for kostnader inntil
leverandør(ene) er godkjent.

5.7 Ansvarsfraskrivelse
REMA 1000 forbeholder seg retten, uten ansvar, til å kansellere anbudsrunden på ethvert tidspunkt.

5.8 Avslag på tilbud
Leverandører som ikke er kvalifisert eller oppfyller minstekravene kan bli avvist, og innholdet i et avvist tilbud
vil ikke bli vurdert nærmere.
Det er derfor svært viktig at tilbudet inneholder all nødvendig informasjon og leveres i formatet som
etterspørres.

5.9 Etiske retningslinjer
Det forventes at leverandører følger REMA 1000 sine etiske retningslinjer og bekrefter at disse
retningslinjene er fulgt ved å delta i anbudet.



6



3.5 Evaluering
Leverandøren skal oppfylle alle relevante krav i vedlagte dokumenter.

REMA 1000 forbeholder seg retten til å avvise tilbud som ikke oppfyller alle vurderingskriterier.
Det endelige utvalget av leverandører som vil få tilbud om kontrakt vil avhenge av hvilke tilbud som kommer.
REMA 1000 arbeider med en hypotese om at anbudsprosessen vil resultere i leverandørkonsolidering, og
dermed redusere antall leverandører per kategori.


4. Avtalebetingelser
Følgende kontraktuelle betingelser er gjeldende for dette anbudet:

• Betalingsbetingelser: 60 dager
• Prisene skal gjelde i hele avtaleperioden, med mindre det har vært en prisjustering i henhold til
Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Prisene skal årlig justeres 60% av Arbeidskraftkostnadindeks for Forretningsmessig tjenesteyting
• Konsulentene skal føre timer til nærmeste kvarter
• Avtaleperioden for rammeavtalen er 3 år med opsjon på 1+1 forlengelse.
o Dersom avtalen ikke sies opp, vil avtalen fortsette å løpe med en oppsigelsesfrist på 3
måneders skriftlig varsel for begge parter.
• Kontraktslengde for konsulenter ved avrop på rammeavtale: 0 – 6 måneder
• Leverandør skal fakturere REMA etterskuddsvis for tjenester som leveres

Dersom tilbyder avdekker mangler i forespørselen eller konflikter mellom de ulike deler av denne, skal REMA
1000 øyeblikkelig varsles skriftlig om dette. Har dere andre spørsmål/kommentarer til forespørselen, skal
dette rettes skriftlig i spørsmålsfunksjonen til Keelvar.

spesifisere en prosentvis rabatt når konsulentkontraktens
lengde er mer enn 6 måneder.
RABATT (%) Kontraktslengde på
Rammeavtale (Standard 3 år)
Standard kontraktslengde er 3 år med mulighet for å forlenge
med ett år to ganger. Eventuelt kan leverandøren spesifisere en
prosentvis rabatt, som vil gi REMA 1000 incentiv til å inngå en
lengre kontrakt.
RABATT (%) dersom andre selskaper i
Reitangruppen benytter rammeavtalen
Rabatt som gis dersom andre selskaper i Reitangruppen velger
å benytte seg av rammeavtalen

Navn Beskrivelse
Total cost of ownership (TCO) De totale kostnadene ved leverandøren, inkludert forventet
påvirkning fra priser, gebyrer og kommersielle vilkår.
Kvalitet Kvalitet er en viktig parameter for å oppnå effekten man ønsker.
Kvalitet blir evaluert på graden av riktige konsulenter og
kompetanse for å matche oppgaveporteføljen hos REMA 1000.
Kategoridekning Leverandører vurderes på evnen til å gi en bred dekning av
rådgivingstjenester som er relevante for REMA 1000.

7

Forslaget til rammeavtale vil bli utarbeidet på bakgrunn av REMA 1000 sin standard rammeavtale. Denne
avtalen er basert på REMA 1000 sine krav og avtalte priser i denne anbudsrunden.
Kontrakter som inngås som følge av anbudsprosessen vil erstatte eksisterende kontrakter innenfor denne
kategorien. Annullering/erstatning av eksisterende kontrakter vil tre i kraft fra datoen ny kontrakt er signert.

5. Formelle krav til anbudsbesvarelsen
I det fremlagte tilbudet er det viktig at følgende krav er tilfredsstilt. Dersom dette ikke er tilfelle, er det
mulighet for at tilbudet kan bli avslått.
5.1 Formelle krav
Krav 1: Tilbudets innhold

Leverandørens tilbud må inneholde de følgende punktene:
1. Et komplett og utfylt prisark lastet opp i Keelvar før svarfristen.
2. Et komplett svar til alle RFI spørsmål før svarfristen.
a. Husk å laste opp alle påkrevde vedlegg

Krav 2: Tidsfrist

Tilbud kan ikke leveres senere enn 10. januar kl. 13:00 via Keelvar. Tilbud som blir levert etter denne fristen
risikerer å ikke bli akseptert og dermed heller ikke vurdert.

Krav 3: Tilbudets struktur

Strukturen til tilbudsforespørselen kan ikke bli endret. Alle relevante felter som dere ønsker å legge
inn tilbud på må fylles inn og oppfylle kravene til Keelvar. Vi oppfordrer leverandører til å legge inn tilbud på
så mange av områdene som mulig.

Krav 4: Tilbudets valuta

Leverandørens tilbud må være oppgitt i NOK.
Krav 5: Tilbudets gyldighet

Tilbudet skal være gyldig i 16 uker etter den satte fristen for levering.
Krav 6: Minimumskrav

Leverandøren må tilfredsstille alle REMA sine etiske krav (se vedlegg: REMA 1000 Etiske retningslinjer)


5.2 Andre krav til anbudet
- REMA 1000 vil teste tilbud gitt i dette anbudet på bakgrunn av mange ulike kriterier, og forbeholder
seg retten til å avvise alle tilbud. REMA 1000 har også retten til å evaluere alle vurderingskriterier i
dokumentasjonen og godkjenne tilbud som ikke har den laveste prisen.
- Enhver tvist som omhandler denne anbudsprosessen, vil løses under Norsk domstol

5.3 Ytterligere kostnader

8

REMA 1000 vil ikke godta kostnader knyttet til produktene utover det som fremkommer i dette anbudet.

5.4 Anonymitet, konfidensialitet, og taushetsplikt
REMA 1000 krever at alle deltagende leverandører holder all informasjon som kommer frem i
anbudsprosessen konfidensielt. REMA 1000 har samme prosedyre når det kommer til informasjonen fra
leverandørene.

5.5 Omfangsbegrensninger
Omfanget av dette anbudet gjelder bare REMA 1000 i Norge, som tilsier at omfanget utelater andre REMA
1000 institusjoner (f.eks. Reitan Convenience, REMA 1000 DK).

5.6 Kostnader relatert til anbudsprosessen
REMA 1000 vil ikke være ansvarlig for kostnader som påløpes hos leverandører som følger av denne
anbudsprosessen – dette referer til mulige kostnader tilknyttet utarbeidelsen av tilbudet eller deltagelse i
forhandlinger. Hvis det gjennomføres en test periode, vil leverandør(er) være ansvarlig for kostnader inntil
leverandør(ene) er godkjent.

5.7 Ansvarsfraskrivelse
REMA 1000 forbeholder seg retten, uten ansvar, til å kansellere anbudsrunden på ethvert tidspunkt.

5.8 Avslag på tilbud
Leverandører som ikke er kvalifisert eller oppfyller minstekravene kan bli avvist, og innholdet i et avvist tilbud
vil ikke bli vurdert nærmere.
Det er derfor svært viktig at tilbudet inneholder all nødvendig informasjon og leveres i formatet som
etterspørres.

5.9 Etiske retningslinjer
Det forventes at leverandører følger REMA 1000 sine etiske retningslinjer og bekrefter at disse
retningslinjene er fulgt ved å delta i anbudet.



7

Forslaget til rammeavtale vil bli utarbeidet på bakgrunn av REMA 1000 sin standard rammeavtale. Denne
avtalen er basert på REMA 1000 sine krav og avtalte priser i denne anbudsrunden.
Kontrakter som inngås som følge av anbudsprosessen vil erstatte eksisterende kontrakter innenfor denne
kategorien. Annullering/erstatning av eksisterende kontrakter vil tre i kraft fra datoen ny kontrakt er signert.

5. Formelle krav til anbudsbesvarelsen
I det fremlagte tilbudet er det viktig at følgende krav er tilfredsstilt. Dersom dette ikke er tilfelle, er det
mulighet for at tilbudet kan bli avslått.
5.1 Formelle krav
Krav 1: Tilbudets innhold

Leverandørens tilbud må inneholde de følgende punktene:
1. Et komplett og utfylt prisark lastet opp i Keelvar før svarfristen.
2. Et komplett svar til alle RFI spørsmål før svarfristen.
a. Husk å laste opp alle påkrevde vedlegg

Krav 2: Tidsfrist

Tilbud kan ikke leveres senere enn 10. januar kl. 13:00 via Keelvar. Tilbud som blir levert etter denne fristen
risikerer å ikke bli akseptert og dermed heller ikke vurdert.

Krav 3: Tilbudets struktur

Strukturen til tilbudsforespørselen kan ikke bli endret. Alle relevante felter som dere ønsker å legge
inn tilbud på må fylles inn og oppfylle kravene til Keelvar. Vi oppfordrer leverandører til å legge inn tilbud på
så mange av områdene som mulig.

Krav 4: Tilbudets valuta

Leverandørens tilbud må være oppgitt i NOK.
Krav 5: Tilbudets gyldighet

Tilbudet skal være gyldig i 16 uker etter den satte fristen for levering.
Krav 6: Minimumskrav

Leverandøren må tilfredsstille alle REMA sine etiske krav (se vedlegg: REMA 1000 Etiske retningslinjer)


5.2 Andre krav til anbudet
- REMA 1000 vil teste tilbud gitt i dette anbudet på bakgrunn av mange ulike kriterier, og forbeholder
seg retten til å avvise alle tilbud. REMA 1000 har også retten til å evaluere alle vurderingskriterier i
dokumentasjonen og godkjenne tilbud som ikke har den laveste prisen.
- Enhver tvist som omhandler denne anbudsprosessen, vil løses under Norsk domstol

5.3 Ytterligere kostnader

8

REMA 1000 vil ikke godta kostnader knyttet til produktene utover det som fremkommer i dette anbudet.

5.4 Anonymitet, konfidensialitet, og taushetsplikt
REMA 1000 krever at alle deltagende leverandører holder all informasjon som kommer frem i
anbudsprosessen konfidensielt. REMA 1000 har samme prosedyre når det kommer til informasjonen fra
leverandørene.

5.5 Omfangsbegrensninger
Omfanget av dette anbudet gjelder bare REMA 1000 i Norge, som tilsier at omfanget utelater andre REMA
1000 institusjoner (f.eks. Reitan Convenience, REMA 1000 DK).

5.6 Kostnader relatert til anbudsprosessen
REMA 1000 vil ikke være ansvarlig for kostnader som påløpes hos leverandører som følger av denne
anbudsprosessen – dette referer til mulige kostnader tilknyttet utarbeidelsen av tilbudet eller deltagelse i
forhandlinger. Hvis det gjennomføres en test periode, vil leverandør(er) være ansvarlig for kostnader inntil
leverandør(ene) er godkjent.

5.7 Ansvarsfraskrivelse
REMA 1000 forbeholder seg retten, uten ansvar, til å kansellere anbudsrunden på ethvert tidspunkt.

5.8 Avslag på tilbud
Leverandører som ikke er kvalifisert eller oppfyller minstekravene kan bli avvist, og innholdet i et avvist tilbud
vil ikke bli vurdert nærmere.
Det er derfor svært viktig at tilbudet inneholder all nødvendig informasjon og leveres i formatet som
etterspørres.

5.9 Etiske retningslinjer
Det forventes at leverandører følger REMA 1000 sine etiske retningslinjer og bekrefter at disse
retningslinjene er fulgt ved å delta i anbudet.



"""
#cleanDocument(myBucket)
#print(identifyFooters(myBucket))
#print(cleanDocument(myBucket))
#print(settKryssCleanup(textMedKryss))

cleandebug = re.sub("¤HEADSTART¤([^¤^\n]+)\n*¤BUCKETINFO¤([^¤]*)¤HEADEND¤", "\g<1> ==> \g<2>", debugInfo)
print(cleandebug)