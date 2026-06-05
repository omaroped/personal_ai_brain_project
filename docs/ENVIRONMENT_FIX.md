# Environment Fix: Python Virtual Environment

## Issue
The checked-in `venv/` directory was created in an environment that may have different shared library paths or Python minor versions (e.g., Python 3.11 on a different host), leading to "shared library not found" errors when running `venv/bin/python`.

## Recommended Fix: Rebuild the Virtual Environment

Because virtual environments contain absolute paths and are tied to the host's system libraries, the most reliable way to fix a broken venv is to delete and recreate it.

### Step-by-Step Rebuild
1. **Remove the existing venv:**
   ```bash
   rm -rf /home/omar/personal_ai_brain_project/venv
   ```

2. **Recreate the venv using the system Python 3.11:**
   ```bash
   python3.11 -m venv /home/omar/personal_ai_brain_project/venv
   ```

3. **Activate the new venv:**
   ```bash
   source /home/omar/personal_ai_brain_project/venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r /home/omar/personal_ai_brain_project/requirements.txt
   ```

## Automated Rebuild Script
A script has been provided at `scripts/rebuild_venv.sh` to automate this process.

## Verification
After rebuilding, verify the environment with:
```bash
source venv/bin/activate
python --version  # Should be 3.11.x
pytest --version  # Should run without library errors
```
