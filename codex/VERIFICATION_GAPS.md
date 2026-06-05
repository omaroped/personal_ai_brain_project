# Verification Gaps

This document tracks logic and components that are implemented but unproven due to missing tests or environment issues.

## High Priority Gaps

| Component | Description | Why Unproven? |
|---|---|---|
| Ingestion Pipeline | Watcher → Extractor → Store loop. | Environment blocked; tests written but cannot run. |
| PDF Extraction | Arabic text extraction logic. | No tests verifying Arabic character reshaping/BIDI. |
| Vector Store | Hybrid search ranking. | Integration tests pending environment restoration. |

## Feature Gaps (Missing Tests)

| Component | Description | Notes |
|---|---|---|
| Privacy Router | Local-only routing helpers. | Basic tests exist, but edge cases are not covered. |
| Health Checks | Service readiness logic. | Mocked in tests, but real-world failure modes unproven. |
