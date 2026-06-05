# MODULE: Enumerate project-owned Python modules.
import os
from pathlib import Path

def list_modules():
    """
    Scans the src/ directory and prints the relative path of all project-owned Python modules.
    """
    project_root = Path(__file__).parent.parent.absolute()
    src_dir = project_root / "src"
    
    if not src_dir.exists():
        print(f"Error: {src_dir} does not exist.")
        return

    modules = []
    for root, dirs, files in os.walk(src_dir):
        # Skip __pycache__
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
            
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                relative_path = file_path.relative_to(project_root)
                modules.append(str(relative_path))
    
    modules.sort()
    for module in modules:
        print(module)

if __name__ == "__main__":
    list_modules()
