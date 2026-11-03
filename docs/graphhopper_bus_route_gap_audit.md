# GraphHopper bus-routing voor Barranquilla

## API en adres

De GitHub Actions-workflow gebruikt de ColombiaTransit-organisatievariabele `GRAPHHOPPER_URL` voor de **eigen** GraphHopper-server achter Cloudflare. Het adres wordt niet in documentatie of scripts hardcoded. Het verplichte routingprofiel is `bus`.

Gebruik voor algemene GraphHopper-API-uitleg uitsluitend de publieke documentatie:

- [GraphHopper open-source Routing Web API](https://github.com/graphhopper/graphhopper/blob/master/docs/web/api-doc.md)
- [GraphHopper documentatie](https://docs.graphhopper.com/)

De workflow gebruikt `GET /info` om het busprofiel te verifiëren en `POST /route` met `profile: bus`, `points_encoded: false`, `calc_points: true` en coördinaten in `[lon,lat]`-volgorde. Dezelfde `requests.Session` wordt voor beide API-aanroepen hergebruikt.

## Cloudflare

De client stuurt voor zowel `/info` als `/route` browserachtige headers mee: een Chrome `User-Agent`, `Accept`, `Accept-Language`, `Cache-Control`, `Pragma`, `Sec-Fetch-Mode` en `Sec-Fetch-Dest`. Zo wordt een onnodig afwijkende Python-request vermeden.

**Beperking:** browserheaders zijn niet voldoende om een Cloudflare JavaScript-challenge, cookiechallenge of WAF-beleid gegarandeerd te doorlopen. Als de requests toch HTTP 403/503 krijgen, moet Cloudflare de GitHub Actions-client op de GraphHopper-API-paden toestaan of een geschikte authenticatie-/service-regel krijgen. De code logt geen echte URL, token of volledige foutrespons.

Een GitHub-organisatievariabele is **geen geheim**. Wie de URL zelf wil afschermen, gebruikt een Organization Secret; de huidige workflow gebruikt bewust de opgegeven variabele.

## Onderzoeksworkflow

[GitHub Action: Check AMB stop gap directions with private GraphHopper bus profile](../.github/workflows/check-amb-graphhopper-bus-directions.yml)

Brondata: 73 haltegaten en 125 SIU-/OSM-kandidaatkoppelingen uit de bestaande datasets; hiervoor worden geen nieuwe OSM-/Overpass-queries uitgevoerd.

Voor ieder traject wordt A→B en B→A met het busprofiel gecontroleerd. Om te voorkomen dat de kortste route een officiële AMB-KMZ-lus overslaat, wordt ook een busroute via tussenpunten van de KMZ berekend. Vervolgens kan GraphHopper een route via een kandidaat-halte proberen. Instapzijde (`curbsides`) staat standaard uit: het eerste experiment kreeg HTTP 400, vermoedelijk omdat de vereiste busprofielopties ontbreken.

Uitvoer in `sources/amb/graphhopper_bus_direction_review/`. De berekende wegen bewijzen geen daadwerkelijke haltebediening of officiële variantkeuze; stop_sequences en GTFS-tijden blijven ongewijzigd.
