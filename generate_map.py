import os

def generate_map():
    ignore = {'.git', '__pycache__', 'venv', '.pytest_cache', 'data', 'node_modules', '.venv_local', 'tree_output.txt'}
    lines = ["```"]
    for root, dirs, files in sorted(os.walk('.')):
        # Filter directories in place
        dirs[:] = [d for d in dirs if d not in ignore and not d.startswith('.')]
        
        # Calculate indentation
        level = root.replace('.', '', 1).count(os.sep)
        indent = '  ' * level
        
        # Add directory name
        base = os.path.basename(root)
        if not base: base = "."
        lines.append(f"{indent}{base}/")
        
        # Add files
        sub_indent = '  ' * (level + 1)
        for f in sorted(files):
            if f.startswith('.') or f in ignore: continue
            lines.append(f"{sub_indent}{f}")
            
    lines.append("```")
    return "\n".join(lines)

with open("PROJECT_MAP.txt", "w") as f:
    f.write(generate_map())
print("PROJECT_MAP.txt generated successfully.")
