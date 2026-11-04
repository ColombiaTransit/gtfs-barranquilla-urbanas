# Projectbesluit: meervoudige bronbevestiging voor vermoedelijke actuele exploitatie (2026-11-04)

## Besluit
Een route mag voor de **onderzoeks-GTFS** als vermoedelijk operationeel worden behandeld wanneer ten minste twee van de bronfamilies **SIU**, **officiële AMB-KMZ**, **ArcGIS** en **AMB-resolutie** dezelfde basisroute/variant ondersteunen, mits ten minste één bron een voldoende recente of operationele aanwijzing bevat (bijvoorbeeld SIU-vermelding of recente AMB-KMZ/resolutie). Oude ArcGIS-lijnen en historische resoluties alleen bewijzen geen huidige exploitatie.

Dit is een **projectaanname**, geen juridisch bewijs dat een vergunning in werking is getreden en geen bevestiging van actuele ritten. Leg per route vast welke bronfamilies matchen, op welke datum/versie, en of de match op basisroute of specifieke A/B-variant slaat. Tegenstrijdige routes, richting/variant of vervallen/vervangen vergunningen blijven handmatig te beoordelen.

## Consequenties
1. De blokkade 'juridische kennisgeving/ejecutoria/effectieve datum onbekend' is op zichzelf **geen technische GTFS-blokkade** meer voor een route met voldoende onafhankelijke bronbevestiging.
2. Frequenties uit de nieuwste toepasselijke AMB-resolutie mogen als **modelmatige dienstfrequenties** worden gebruikt, met bron, resolutienummer en expliciete onzekerheid over feitelijke uitvoering. Gebruik geen gecombineerde corridorfrequentie tweemaal op A/B-varianten of gezamenlijke exploitanten.
3. Een basisroutebevestiging geeft **geen** automatische A/B-richting, stopvolgorde of tripgrenzen. Ontbrekende SIU-stopvolgorde, onzekere KMZ-geometrie en tegenstrijdige variantgegevens blijven aparte QA-punten.
4. Een onbekend historisch eerste/laatste vertrek is niet hetzelfde als ontbrekende exploitatie; gebruik alleen de expliciet geaccepteerde dienstvenster-modelaanname waar passend, niet een verzonnen officieel rooster.
5. GTFS MobilityData-validatie controleert syntaxis en geografische consistentie, **niet** of een route werkelijk rijdt. Houd de onderzoeksfeed duidelijk als model gelabeld totdat publicatievoorwaarden zijn vastgesteld.

## Te implementeren in de bestaande Actions
- Voeg een evidence-matrix per route en variant toe (SIU/KMZ/ArcGIS/resolutie, bronversie, status, tegenstrijdigheden).
- Scheid 'research_operational_assumed' van 'legally_verified' en 'timetable_observed'.
- Laat de bestaande frequentie- en geometrie-Actions de evidence-matrix gebruiken om **alleen juridische datum-onzekerheid** voor meervoudig ondersteunde routes niet langer als technische blocker te behandelen.
- Behoud alle andere inhoudelijke blokkades en schrijf een auditrapport van vrijgegeven versus aangehouden routes; publiceer niet automatisch productie-GTFS.
