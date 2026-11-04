# Scope juridische verificatie voor GTFS

De AMB-resoluties worden uitsluitend onderzocht op gegevens die relevant zijn voor het bouwen en valideren van de GTFS-feed.

## Wel relevant
- Routecode, naam, operator(en), A/B-varianten en gedeelde exploitatie.
- Traject, rijrichting, geometrie, haltevolgorde en eindpunten.
- Eerste/laatste vertrek, bedieningsdagen, piek- en dalperioden en intervallen.
- Rechtsgeldige wijziging, intrekking, voorwaarden en opvolgende besluiten, voor zover die route of dienstregeling beïnvloeden.
- Mapping naar `agency.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`, `frequencies.txt`, `calendar.txt`, `shapes.txt` en eventueel `attributions.txt`.

## Buiten scope
- Aantal voertuigen, minimale/maximale voertuigcapaciteit en verdeling van wagenpark tussen vervoerders.
- Andere vergunningdetails die geen effect hebben op route, dienstregeling of GTFS-identiteit.

Bij identieke gezamenlijk geëxploiteerde varianten: één samengestelde/virtuele GTFS-agency, één variant en één frequentie; betrokken vervoerders apart herkenbaar via attributies waar passend. Geen dubbele ritten of frequenties.

Bestaande historische notities mogen voertuiggegevens bevatten als letterlijke bronsamenvatting, maar die gegevens zijn **geen verificatieprioriteit, geen GTFS-vereiste en geen openstaande blocker**.

Juridische of feitelijke actuele dienst blijft onbevestigd zolang de relevante opvolgende besluiten en de uitvoeringsvoorwaarden niet zijn gecontroleerd.
