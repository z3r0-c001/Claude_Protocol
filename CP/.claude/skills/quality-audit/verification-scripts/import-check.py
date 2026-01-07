#!/usr/bin/env python3
"""
Check if Python imports are valid.
Usage: ./import-check.py <file.py>
"""

import sys
import ast
import subprocess
import importlib.util

def extract_imports(file_path):
    """Extract all imports from a Python file."""
    with open(file_path) as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError as e:
            print(f"SYNTAX_ERROR: {e}")
            return []
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    'module': alias.name,
                    'root': alias.name.split('.')[0],
                    'type': 'import'
                })
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append({
                    'module': node.module,
                    'root': node.module.split('.')[0],
                    'type': 'from',
                    'names': [a.name for a in node.names]
                })
    
    return imports

def check_import(module_name):
    """Check if a module can be imported."""
    # Standard library modules
    stdlib = {
        'os', 'sys', 'json', 'ast', 'typing', 're', 'collections',
        'functools', 'itertools', 'pathlib', 'subprocess', 'datetime',
        'time', 'math', 'random', 'copy', 'io', 'tempfile', 'shutil',
        'glob', 'fnmatch', 'argparse', 'logging', 'unittest', 'dataclasses',
        'enum', 'abc', 'contextlib', 'warnings', 'traceback', 'inspect',
        'importlib', 'pkgutil', 'builtins', 'string', 'textwrap',
        'urllib', 'http', 'email', 'html', 'xml', 'csv', 'sqlite3',
        'hashlib', 'hmac', 'secrets', 'base64', 'binascii', 'struct',
        'codecs', 'unicodedata', 'locale', 'gettext', 'threading',
        'multiprocessing', 'concurrent', 'asyncio', 'socket', 'ssl',
        'select', 'selectors', 'signal', 'mmap', 'ctypes', 'gc',
        'weakref', 'array', 'queue', 'heapq', 'bisect', 'pprint',
        'pickle', 'shelve', 'dbm', 'gzip', 'bz2', 'lzma', 'zipfile',
        'tarfile', 'zlib', 'configparser', 'netrc', 'plistlib',
        'stat', 'filecmp', 'pty', 'tty', 'termios', 'fcntl', 'pwd',
        'grp', 'posix', 'platform', 'errno', 'curses'
    }
    
    root = module_name.split('.')[0]
    
    if root in stdlib:
        return {'status': 'STDLIB', 'module': module_name}
    
    # Check if importable
    spec = importlib.util.find_spec(root)
    if spec is not None:
        return {'status': 'FOUND', 'module': module_name}
    
    return {'status': 'NOT_FOUND', 'module': module_name}

def main():
    if len(sys.argv) < 2:
        print("Usage: import-check.py <file.py>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    imports = extract_imports(file_path)
    
    results = {
        'found': [],
        'stdlib': [],
        'not_found': []
    }
    
    checked = set()
    for imp in imports:
        root = imp['root']
        if root in checked:
            continue
        checked.add(root)
        
        result = check_import(root)
        if result['status'] == 'FOUND':
            results['found'].append(root)
        elif result['status'] == 'STDLIB':
            results['stdlib'].append(root)
        else:
            results['not_found'].append(root)
    
    print(f"Standard Library: {', '.join(results['stdlib']) or 'none'}")
    print(f"Found (installed): {', '.join(results['found']) or 'none'}")
    print(f"NOT FOUND: {', '.join(results['not_found']) or 'none'}")
    
    if results['not_found']:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
