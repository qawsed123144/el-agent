# Earthquake Anomaly Agent

This project is an Elasticsearch-powered seismic analysis agent built with Elastic Agent Builder.

It ingests earthquake data from the USGS FDSN API, stores it in a time-series index, and applies ES|QL-based anomaly detection logic before optionally integrating structured runbook guidance.

---

## Repository Structure
elastic-earthquake-agent/
│
├── ingest/
│ └── ingest_usgs.py
│
├── instruction/
│ └── instruction.md
│
├── runbooks/
│ └── runbooks.json
│
├── .gitignore
└── README.md

## Data Scope Notice

This project currently uses predefined date ranges for ingestion.

It is not continuously streaming live data.

The ingestion script uses the following fixed ranges:
DATE_RANGES = [
("2024-01-01", "2024-06-30"),
("2024-07-01", "2024-12-31"),
("2025-01-01", "2025-06-30"),
("2025-07-01", "2025-12-31"),
("2026-01-01", "2026-02-28"),
]


These ranges are intentionally limited for demonstration and reproducibility.

---

## Environment Configuration

You must configure Elasticsearch connection settings before running ingestion.

Required variables:

- ES_URL
- ES_API_KEY
- ES_INDEX

---

## Option 1 — Using .env (Recommended)

Create a `.env` file in the project root:
ES_URL="https://your-elastic-endpoint:443
"
ES_API_KEY="your_api_key_here"
ES_INDEX="events_geo"

Then load it before running:
```
source .env
python ingest/ingest_usgs.py
```


---

## Option 2 — Using export (Quick Start)

You may export variables directly:

---

## Ingestion Flow

1. Fetch earthquake data from USGS FDSN API (GeoJSON)
2. Normalize fields
3. Index into Elasticsearch 
4. Enable ES|QL-based anomaly evaluation

---
## Loading Runbooks into Elasticsearch

This project uses a dedicated index named `runbooks` as a structured operational knowledge base.

Runbooks are stored in:runbooks/runbooks.ndjson

This file is in NDJSON format (newline-delimited JSON) and is designed for Elasticsearch Bulk API.

Each runbook entry consists of:

- An action line
- A document line

### Option A — Kibana Dev Tools (Console)

1. Open Kibana → Dev Tools → Console
2. Paste the content of `runbooks/runbooks.ndjson`
3. Run:

```http
POST _bulk
... (paste NDJSON here)
```


## Agent Logic

The agent:

- Classifies queries (DESCRIPTIVE, HISTORICAL, ANOMALY, DRILL_DOWN)
- Always retrieves numerical evidence via ES|QL
- Applies anomaly thresholds deterministically
- Only calls runbook Search when anomaly is confirmed
- Never fabricates numerical data

See `instruction/instruction.md` for full behavior specification.

---