# Smoke Flows

## Purpose

These are the three public smoke flows that should remain stable as the project evolves.

## Flow 1 — Ingest and Query

1. Start the API.
2. Ingest a local file or web clipping.
3. Run a search query through `/search` or `query.py`.
4. Confirm results are returned from LanceDB.

## Flow 2 — Memory Review

1. Generate a daily review.
2. Run extraction on the produced review.
3. Confirm durable updates appear in core memory.

## Flow 3 — Voice Response

1. Start the API and voice daemon.
2. Speak a short query.
3. Confirm transcript reaches the brain.
4. Confirm a TTS response is returned and played.

## Automation

- `scripts/smoke_test_ingestion.py`
- `scripts/smoke_test_full.sh`
- `scripts/benchmark_voice.py`
