import os
import requests
from datetime import datetime, timezone
from elasticsearch import Elasticsearch, helpers

ES_URL = os.getenv("ES_URL")
ES_API_KEY = os.getenv("ES_API_KEY")
INDEX = os.getenv("ES_INDEX")

import time

DATE_RANGES = [
    ("2024-01-01", "2024-06-30"),
    ("2024-07-01", "2024-12-31"),
    ("2025-01-01", "2025-06-30"),
    ("2025-07-01", "2025-12-31"),
    ("2026-01-01", "2026-02-28"),
]

def to_iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()

def main():
    es = Elasticsearch(ES_URL, api_key=ES_API_KEY)

    for start_date, end_date in DATE_RANGES:
        print(f"--- Processing {start_date} to {end_date} ---")
        
        url = (
            "https://earthquake.usgs.gov/fdsnws/event/1/query"
            "?format=geojson"
            f"&starttime={start_date}"
            f"&endtime={end_date}"
            "&minmagnitude=2"
            "&limit=20000"
        )

        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        actions_array = []
        for feature in data.get("features", []):
            props = feature.get("properties")
            geo = feature.get("geometry")
            coords = geo.get("coordinates")
            lon, lat = coords[0], coords[1]
            depth_km = coords[2] if len(coords) >= 3 else None
            event_id = feature.get("id")
            event_time = props.get("time")
            if event_time is None:
                continue

            doc = {
                "@timestamp": to_iso(event_time),
                "event_type": "earthquake",
                "magnitude": props.get("mag"),
                "depth_km": depth_km,
                "location": {"lat": lat, "lon": lon},
                "place": props.get("place"),
                "source": "usgs",
                "event_id": event_id,
                "url": props.get("url"),
            }

            actions_array.append({
                "_op_type": "index",
                "_index": INDEX,
                "_id": event_id,
                "_source": doc
            })

        if not actions_array:
            print("No data to ingest for this period.")
            continue

        ok, errors = helpers.bulk(
            es.options(request_timeout=60),
            actions_array,
            refresh="wait_for",
        )

        print(f"Ingested Count: {ok}")
        if errors:
            print("Some errors occurred:")
            print(errors[:3])
            
        time.sleep(1)


if __name__ == "__main__":
    main()
