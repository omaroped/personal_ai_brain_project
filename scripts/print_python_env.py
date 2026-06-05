import sys
import os
import site

def print_env():
    print(f"Python Interpreter: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print("\nSite Packages:")
    for path in site.getsitepackages():
        print(f"  - {path}")
    if site.getusersitepackages():
        print(f"  - {site.getusersitepackages()} (user)")
    
    print("\nEnvironment Variables (Selected):")
    important_vars = ['PYTHONPATH', 'VIRTUAL_ENV', 'PATH', 'PYTHONHOME']
    for var in important_vars:
        print(f"  {var}: {os.environ.get(var, 'Not Set')}")

    print("\nAll Environment Variables:")
    for key, value in sorted(os.environ.items()):
        print(f"  {key}: {value}")

if __name__ == "__main__":
    print_env()
