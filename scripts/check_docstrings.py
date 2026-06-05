# MODULE: Enforce function docstrings in project Python files.
import ast
import os
import sys
from pathlib import Path

def check_docstrings_in_file(file_path, project_root):
    """
    Checks if all functions and classes in a file have docstrings.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return 0

    missing = []
    for node in tree.body:
        # Check top-level classes and functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                missing.append(f"{node.name} (line {node.lineno})")
        
        # Check methods within classes
        if isinstance(node, ast.ClassDef):
            for subnode in node.body:
                if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not ast.get_docstring(subnode):
                        missing.append(f"{node.name}.{subnode.name} (line {subnode.lineno})")
    
    if missing:
        rel_path = file_path.relative_to(project_root)
        print(f"Missing docstrings in {rel_path}:")
        for m in missing:
            print(f"  - {m}")
        return len(missing)
    return 0

def check_all_docstrings():
    """
    Iterates over all Python files in src/ and checks for missing docstrings.
    """
    project_root = Path(__file__).parent.parent.absolute()
    src_dir = project_root / "src"
    
    if not src_dir.exists():
        print(f"Error: {src_dir} does not exist.")
        return 1

    total_missing = 0
    for root, dirs, files in os.walk(src_dir):
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                total_missing += check_docstrings_in_file(file_path, project_root)

    if total_missing > 0:
        print(f"\nTotal items missing docstrings: {total_missing}")
        # We don't necessarily want to fail the check if we are just "enforcing" but not blocking
        # but usually "enforce" means exit non-zero.
        return 1
    else:
        print("All functions and classes have docstrings.")
        return 0

if __name__ == "__main__":
    sys.exit(check_all_docstrings())
