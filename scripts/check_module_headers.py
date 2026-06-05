# MODULE: Enforce # MODULE: headers in project Python files.
import os
import sys
from pathlib import Path

def check_headers():
    """
    Checks that all .py files in src/ start with a '# MODULE:' header.
    """
    project_root = Path(__file__).parent.parent.absolute()
    src_dir = project_root / "src"
    
    if not src_dir.exists():
        print(f"Error: {src_dir} does not exist.")
        return 1

    missing_headers = []
    for root, dirs, files in os.walk(src_dir):
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline()
                        if not first_line.startswith("# MODULE:"):
                            missing_headers.append(str(file_path.relative_to(project_root)))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    if missing_headers:
        print("Missing '# MODULE:' header in the following files:")
        for file in sorted(missing_headers):
            print(f"  {file}")
        return 1
    else:
        print("All modules have '# MODULE:' headers.")
        return 0

if __name__ == "__main__":
    sys.exit(check_headers())
