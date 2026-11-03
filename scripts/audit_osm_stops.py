#!/usr/bin/env python3
"""Audit a user-supplied Overpass bus-stop export against AMB route polylines.

Outputs STOP CANDIDATES only, not GTFS stops.txt/stop_times.txt.
OSM objects without network are NOT automatically traditional TPC stops.
ODbL data must retain attribution to OpenStreetMap contributors.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[1]


def write_csv(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def classify(tags):
    """Only explicit OSM tags identify a particular transport network."""
    network = str(tags.get("network") or "").casefold()
    operator = str(tags.get("operator") or "").casefold()
    if "transmetro" in network or "transmetro" in operator or network == "alimentador":
        return "transmetro_explicit"
    if "baranoa" in network or "cootransguajaro" in operator:
        return "regional_baranoa_explicit"
    return "unclassified_candidate"


def boarding_candidate(tags, kind):
    """Vehicle stop_positions are not necessarily passenger platforms."""
    if kind != "unclassified_candidate":
        return False
    return tags.get("public_transport") == "platform" or tags.get("highway") in (
        "bus_stop", "crossing;bus_stop"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm", default=str(ROOT / "sources/osm/overpass_barranquilla_bus_stops_2026-11-03.json"))
    parser.add_argument("--shapes", default="build/amb-arcgis-shapes/arcgis_routes_original.geojson")
    parser.add_argument("--out", default="build/amb-osm-stops")
    args = parser.parse_args()
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)

    osm = json.loads(Path(args.osm).read_text(encoding="utf-8-sig"))
    source_geojson = json.loads(Path(args.shapes).read_text(encoding="utf-8-sig"))
    if not isinstance(osm.get("elements"), list) or not source_geojson.get("features"):
        raise SystemExit("Missing Overpass elements or ArcGIS route features")

    # UTM 18N, metre-scale coordinates appropriate for Barranquilla.
    to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True).transform
    gis_features = [
        f for f in source_geojson["features"]
        if f.get("geometry", {}).get("type") in ("LineString", "MultiLineString")
    ]
    if not gis_features:
        raise SystemExit("No line geometry in ArcGIS GeoJSON")
    geometries = [transform(to_utm, shape(f["geometry"])) for f in gis_features]
    tree = STRtree(geometries)

    # Nearby tagged Transmetro points make untagged OSM candidates especially
    # worth reviewing; proximity does not automatically mean same network.
    explicit_tm = []
    for entry in osm["elements"]:
        if classify(entry.get("tags") or {}) != "transmetro_explicit":
            continue
        pos = entry if entry.get("type") == "node" else entry.get("center") or {}
        if pos.get("lat") is not None and pos.get("lon") is not None:
            explicit_tm.append(transform(to_utm, Point(float(pos["lon"]), float(pos["lat"]))))
    tm_tree = STRtree(explicit_tm) if explicit_tm else None

    rows = []
    for entry in osm["elements"]:
        tags = entry.get("tags") or {}
        if entry.get("type") == "node":
            lat, lon = entry.get("lat"), entry.get("lon")
        else:
            center = entry.get("center") or {}
            lat, lon = center.get("lat"), center.get("lon")
        if lat is None or lon is None:
            raise SystemExit(f"Missing location for {entry.get('type')} {entry.get('id')}")
        category = classify(tags)
        point = transform(to_utm, Point(float(lon), float(lat)))
        nearest_index = int(tree.nearest(point))
        nearest_distance = round(point.distance(geometries[nearest_index]), 1)
        near_tm = round(point.distance(explicit_tm[int(tm_tree.nearest(point))]), 1) if tm_tree else None
        nearby_indices = tree.query(point.buffer(50))
        within50 = [
            gis_features[int(idx)]["properties"].get("Name", "")
            for idx in nearby_indices if geometries[int(idx)].distance(point) <= 50
        ]
        row = {
            "osm_type": entry["type"],
            "osm_id": entry["id"],
            "lat": lat, "lon": lon,
            "name": tags.get("name", ""),
            "osm_network": tags.get("network", ""),
            "osm_operator": tags.get("operator", ""),
            "public_transport": tags.get("public_transport", ""),
            "highway": tags.get("highway", ""),
            "ref": tags.get("ref", ""),
            "shelter": tags.get("shelter", ""),
            "bus": tags.get("bus", ""),
            "classification": category,
            "boarding_candidate": str(boarding_candidate(tags, category)).lower(),
            "nearest_arcgis_route_code": gis_features[nearest_index]["properties"].get("Name", ""),
            "nearest_arcgis_distance_m": nearest_distance,
            "nearest_tagged_transmetro_distance_m": near_tm,
            "near_tagged_transmetro_50m": str(near_tm is not None and near_tm <= 50).lower(),
            "n_arcgis_route_features_within_50m": len(within50),
            "arcgis_route_names_within_50m": ";".join(sorted(set(within50))),
            "tpc_confirmed": "no",
            "route_stop_sequence_confirmed": "no",
            "source": "OpenStreetMap / Overpass API",
            "source_date_utc": osm.get("osm3s", {}).get("timestamp_osm_base", ""),
        }
        rows.append(row)

    if not rows:
        raise SystemExit("No OSM stops provided")
    columns = list(rows[0])
    unclassified = [r for r in rows if r["classification"] == "unclassified_candidate"]
    platforms = [r for r in unclassified if r["boarding_candidate"] == "true"]
    priority = [r for r in platforms if r["nearest_arcgis_distance_m"] <= 50]
    write_csv(output / "all_osm_stops_audit.csv", rows, columns)
    write_csv(output / "unclassified_osm_stops.csv", unclassified, columns)
    write_csv(output / "possible_boarding_platforms.csv", platforms, columns)
    write_csv(output / "priority_platforms_near_amb_routes_50m.csv", priority, columns)
    geodata = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature",
             "properties": {
                 "osm_type": r["osm_type"], "osm_id": r["osm_id"], "name": r["name"],
                 "nearest_arcgis_route_code": r["nearest_arcgis_route_code"],
                 "nearest_arcgis_distance_m": r["nearest_arcgis_distance_m"],
                 "tpc_confirmed": "no"
             },
             "geometry": {"type": "Point", "coordinates": [float(r["lon"]), float(r["lat"])]}}
            for r in platforms
        ],
    }
    (output / "possible_boarding_platforms.geojson").write_text(
        json.dumps(geodata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    categories = Counter(r["classification"] for r in rows)
    summary = {
        "source": "User-supplied Overpass API export",
        "osm_timestamp_utc": osm.get("osm3s", {}).get("timestamp_osm_base", ""),
        "license": "ODbL — OpenStreetMap contributors",
        "total_osm_elements": len(rows),
        "nodes": sum(r["osm_type"] == "node" for r in rows),
        "ways_with_overpass_center": sum(r["osm_type"] == "way" for r in rows),
        "transmetro_explicit": categories["transmetro_explicit"],
        "regional_baranoa_explicit": categories["regional_baranoa_explicit"],
        "unclassified_network": len(unclassified),
        "unclassified_stop_positions": sum(r["public_transport"] == "stop_position" for r in unclassified),
        "unclassified_possible_boarding_locations": len(platforms),
        "unclassified_possible_boarding_locations_named": sum(bool(r["name"]) for r in platforms),
        "unclassified_possible_boarding_locations_within_50m": len(priority),
        "unclassified_boarding_near_tagged_transmetro_50m":
            sum(r["near_tagged_transmetro_50m"] == "true" for r in platforms),
        "unclassified_possible_boarding_locations_within_100m":
            sum(r["nearest_arcgis_distance_m"] <= 100 for r in platforms),
        "arcgis_reference_features": len(gis_features),
        "confirmed_tpc_stops_from_this_export": 0,
        "caution": "Proximity to a 2019/2023 GIS route polyline is not proof of TPC boarding or stop order.",
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# OSM bushaltes — Barranquilla, 3 november 2026", "",
        "Bron: Overpass-export uit gebruikersbestand, ODbL OpenStreetMap contributors.",
        "Routelijnen: historische openbare AMB ArcGIS-gegevens (2019/2023).", "",
        "| Categorie | Aantal |", "|---|---:|",
        f"| OSM-objecten totaal | {len(rows)} |",
        f"| Expliciet Transmetro / Alimentador | {categories['transmetro_explicit']} |",
        f"| Regionale Baranoa–Barranquilla | {categories['regional_baranoa_explicit']} |",
        f"| Niet geclassificeerd | {len(unclassified)} |",
        f"| Daarvan stop_position | {summary['unclassified_stop_positions']} |",
        f"| Daarvan mogelijke instapplaats of platform | {len(platforms)} |",
        f"| Daarvan binnen 50 m van een GIS-route | {len(priority)} |",
        f"| Mogelijke instapplaats binnen 50 m van expliciet Transmetro-punt | {summary['unclassified_boarding_near_tagged_transmetro_50m']} |",
        f"| Daarvan binnen 100 m | {summary['unclassified_possible_boarding_locations_within_100m']} |",
        f"| Bevestigde TPC-haltes | 0 |", "",
        "Geen onbevestigde stop wordt in GTFS stops.txt opgenomen.",
        "OSM-way locaties zijn Overpass centers; dit zijn geen volledige perronpolygonen.",
        "Afstanden zijn in meter berekend met EPSG:32618.",
        "Stopvolgorde, instapfunctie en TPC-bediening zijn niet bewezen.",
        "De originele export en de geselecteerde punten behouden ODbL-herkomst.",
        "Gebruik SIU/SIBUS en verifieer vervolgens de routevolgorde.",
    ]
    (output / "summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
