#!/usr/bin/env python3
"""
PreToolUse Hallucination Check for Claude Code
===============================================
Extracts import statements from code and verifies the packages exist.
Blocks writes that reference non-existent packages.

For Python: checks PyPI
For JS/TS: checks npm registry
For local imports (./foo, ../bar): always allows

Install:
  1. Copy to .claude/hooks/pretool-hallucination-check.py
  2. chmod +x .claude/hooks/pretool-hallucination-check.py
  3. Add to settings.json PreToolUse hooks
"""

import json
import sys
import re
import urllib.request
import urllib.error
from typing import Optional
from pathlib import Path

# Cache to avoid repeated lookups in same session
_package_cache: dict[str, bool] = {}

# =============================================================================
# IMPORT EXTRACTION
# =============================================================================

def extract_python_imports(content: str) -> set[str]:
    """Extract top-level package names from Python imports."""
    packages = set()
    
    # import foo, import foo.bar, import foo as f
    for match in re.finditer(r'^import\s+([\w.]+)', content, re.MULTILINE):
        pkg = match.group(1).split('.')[0]
        packages.add(pkg)
    
    # from foo import bar, from foo.bar import baz
    for match in re.finditer(r'^from\s+([\w.]+)\s+import', content, re.MULTILINE):
        pkg = match.group(1).split('.')[0]
        packages.add(pkg)
    
    return packages


def extract_js_imports(content: str) -> set[str]:
    """Extract package names from JS/TS imports."""
    packages = set()
    
    # import x from 'package'
    # import { x } from 'package'
    # import 'package'
    for match in re.finditer(r'''import\s+.*?from\s+['"]([^'"]+)['"]''', content):
        pkg = match.group(1)
        if not pkg.startswith('.') and not pkg.startswith('/'):
            # Handle scoped packages: @org/pkg -> @org/pkg
            # Handle subpaths: lodash/merge -> lodash
            if pkg.startswith('@'):
                parts = pkg.split('/')
                if len(parts) >= 2:
                    packages.add(f"{parts[0]}/{parts[1]}")
            else:
                packages.add(pkg.split('/')[0])
    
    # require('package')
    for match in re.finditer(r'''require\s*\(\s*['"]([^'"]+)['"]\s*\)''', content):
        pkg = match.group(1)
        if not pkg.startswith('.') and not pkg.startswith('/'):
            if pkg.startswith('@'):
                parts = pkg.split('/')
                if len(parts) >= 2:
                    packages.add(f"{parts[0]}/{parts[1]}")
            else:
                packages.add(pkg.split('/')[0])
    
    return packages


# =============================================================================
# PACKAGE VERIFICATION
# =============================================================================

# Standard library modules (don't check these)
PYTHON_STDLIB = {
    'abc', 'aifc', 'argparse', 'array', 'ast', 'asyncio', 'atexit', 'base64',
    'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2', 'calendar',
    'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop',
    'collections', 'colorsys', 'compileall', 'concurrent', 'configparser',
    'contextlib', 'contextvars', 'copy', 'copyreg', 'cProfile', 'crypt',
    'csv', 'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal',
    'difflib', 'dis', 'distutils', 'doctest', 'email', 'encodings', 'enum',
    'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch',
    'fractions', 'ftplib', 'functools', 'gc', 'getopt', 'getpass', 'gettext',
    'glob', 'graphlib', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac', 'html',
    'http', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io',
    'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3', 'linecache',
    'locale', 'logging', 'lzma', 'mailbox', 'mailcap', 'marshal', 'math',
    'mimetypes', 'mmap', 'modulefinder', 'multiprocessing', 'netrc', 'nis',
    'nntplib', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev',
    'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform',
    'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats',
    'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri',
    'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy',
    'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil',
    'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver',
    'spwd', 'sqlite3', 'ssl', 'stat', 'statistics', 'string', 'stringprep',
    'struct', 'subprocess', 'sunau', 'symtable', 'sys', 'sysconfig', 'syslog',
    'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'test',
    'textwrap', 'threading', 'time', 'timeit', 'tkinter', 'token', 'tokenize',
    'tomllib', 'trace', 'traceback', 'tracemalloc', 'tty', 'turtle',
    'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib',
    'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser',
    'winreg', 'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp',
    'zipfile', 'zipimport', 'zlib', 'zoneinfo',
    # typing extras
    'typing_extensions',
}

# Node built-ins
NODE_BUILTINS = {
    'assert', 'buffer', 'child_process', 'cluster', 'console', 'constants',
    'crypto', 'dgram', 'dns', 'domain', 'events', 'fs', 'http', 'https',
    'module', 'net', 'os', 'path', 'perf_hooks', 'process', 'punycode',
    'querystring', 'readline', 'repl', 'stream', 'string_decoder', 'sys',
    'timers', 'tls', 'tty', 'url', 'util', 'v8', 'vm', 'wasi', 'worker_threads',
    'zlib', 'node:assert', 'node:buffer', 'node:child_process', 'node:cluster',
    'node:console', 'node:constants', 'node:crypto', 'node:dgram', 'node:dns',
    'node:domain', 'node:events', 'node:fs', 'node:http', 'node:https',
    'node:module', 'node:net', 'node:os', 'node:path', 'node:perf_hooks',
    'node:process', 'node:punycode', 'node:querystring', 'node:readline',
    'node:repl', 'node:stream', 'node:string_decoder', 'node:sys',
    'node:timers', 'node:tls', 'node:tty', 'node:url', 'node:util', 'node:v8',
    'node:vm', 'node:wasi', 'node:worker_threads', 'node:zlib',
}


def check_pypi(package: str) -> bool:
    """Check if a Python package exists on PyPI."""
    if package in _package_cache:
        return _package_cache[package]
    
    if package in PYTHON_STDLIB:
        _package_cache[package] = True
        return True
    
    try:
        url = f"https://pypi.org/pypi/{package}/json"
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'claude-code-hook/1.0')
        with urllib.request.urlopen(req, timeout=5) as response:
            exists = response.status == 200
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        exists = False
    
    _package_cache[package] = exists
    return exists


def check_npm(package: str) -> bool:
    """Check if an npm package exists."""
    if package in _package_cache:
        return _package_cache[package]
    
    if package in NODE_BUILTINS:
        _package_cache[package] = True
        return True
    
    try:
        # Handle scoped packages
        encoded = package.replace('/', '%2F')
        url = f"https://registry.npmjs.org/{encoded}"
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'claude-code-hook/1.0')
        with urllib.request.urlopen(req, timeout=5) as response:
            exists = response.status == 200
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        exists = False
    
    _package_cache[package] = exists
    return exists


# =============================================================================
# MAIN LOGIC
# =============================================================================

def detect_language(file_path: str, content: str) -> Optional[str]:
    """Detect the programming language from file extension or content."""
    ext = Path(file_path).suffix.lower() if file_path else ""
    
    if ext in ('.py', '.pyw', '.pyi'):
        return 'python'
    elif ext in ('.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'):
        return 'javascript'
    
    # Heuristic: check for language-specific patterns
    if re.search(r'^(import|from)\s+\w+', content, re.MULTILINE):
        if re.search(r'^from\s+\w+\s+import', content, re.MULTILINE):
            return 'python'
    if re.search(r'''import\s+.*from\s+['"]''', content):
        return 'javascript'
    
    return None


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Failed to parse hook input: {e}", file=sys.stderr)
        sys.exit(1)
    
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)
    
    content = tool_input.get("content", tool_input.get("new_string", ""))
    file_path = tool_input.get("file_path", "")
    
    if not content:
        sys.exit(0)
    
    language = detect_language(file_path, content)
    if not language:
        sys.exit(0)
    
    # Extract and verify packages
    hallucinations = []
    
    if language == 'python':
        packages = extract_python_imports(content)
        for pkg in packages:
            if not check_pypi(pkg):
                hallucinations.append(f"Python package '{pkg}' not found on PyPI")
    
    elif language == 'javascript':
        packages = extract_js_imports(content)
        for pkg in packages:
            if not check_npm(pkg):
                hallucinations.append(f"npm package '{pkg}' not found on registry")
    
    if hallucinations:
        msg = "HALLUCINATION CHECK FAILED - These packages don't exist:\n\n"
        for h in hallucinations:
            msg += f"  • {h}\n"
        msg += "\nVerify package names and use only real, existing packages."
        print(msg, file=sys.stderr)
        sys.exit(2)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
