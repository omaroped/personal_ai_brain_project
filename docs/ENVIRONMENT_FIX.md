# Environment Fixes

## Dependency Issues
- **Issue:** `rebuild_venv.sh` failed because `silero-vad==5.1.1` is not available on PyPI.
- **Available Versions:** 5.0.1b2, 5.0.1b3, 5.1, 5.1.2, 6.0.0, 6.1.0, 6.2.0, 6.2.1.
- **Recommended Fix:** Update `requirements.txt` to use `silero-vad==5.1.2` or `silero-vad>=5.1`.

- **Issue:** `rebuild_venv.sh` failed because `letta-client==0.2.12` is not available on PyPI.
- **Available Versions:** Many 0.1.x versions (up to 0.1.324) and 1.x versions.
- **Recommended Fix:** Update `requirements.txt` to a valid version of `letta-client`, e.g., `0.1.212` (if that was the intent) or the latest stable 0.1.x version.

- **Issue:** `rebuild_venv.sh` failed because of a dependency conflict between `pyarrow==17.0.0` and `pylance 0.11.1` (from `lancedb`). `pylance` requires `pyarrow<15.0.1`.
- **Recommended Fix:** Update `requirements.txt` to use a compatible version of `pyarrow`, e.g., `pyarrow==14.0.1`.

## Python Version
- Python 3.11 is present and `venv` module is working.
