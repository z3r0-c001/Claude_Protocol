#!/usr/bin/env python3
"""
Generate protocol manifest with checksums for all components.

Usage:
    python3 generate-manifest.py [--output protocol-manifest.json]
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent  # .claude/scripts -> .claude -> root


def sha256_file(filepath: Path) -> str:
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return f"sha256:{sha256_hash.hexdigest()}"


def extract_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from markdown file."""
    try:
        content = filepath.read_text()
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                frontmatter = content[3:end].strip()
                result = {}
                for line in frontmatter.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        result[key] = value
                return result
    except Exception:
        pass
    return {}


def get_component_version(filepath: Path) -> str:
    """Get version from component (default 1.0.0 if not specified)."""
    frontmatter = extract_frontmatter(filepath)
    return frontmatter.get("version", "1.0.0")


def get_component_description(filepath: Path) -> str:
    """Get description from component frontmatter."""
    frontmatter = extract_frontmatter(filepath)
    return frontmatter.get("description", "")


def scan_directory(root: Path, pattern: str, category: str) -> dict:
    """Scan directory for components matching pattern."""
    components = {}
    claude_dir = root / ".claude"

    for filepath in claude_dir.glob(pattern):
        if filepath.is_file():
            # Get relative path from .claude
            rel_path = filepath.relative_to(claude_dir)

            # Create component key (e.g., "core/architect" for agents)
            if category == "agents":
                # Remove .md extension and agents/ prefix
                key = str(rel_path.parent / rel_path.stem).replace("agents/", "")
            elif category == "skills":
                # Use skill folder name
                key = rel_path.parent.name if rel_path.name in ["SKILL.md", "skill.md"] else rel_path.stem
                key = key.replace("skills/", "")
            elif category == "commands":
                key = rel_path.stem.replace("commands/", "")
            elif category == "hooks":
                key = rel_path.name.replace("hooks/", "")
            else:
                key = str(rel_path)

            components[key] = {
                "version": get_component_version(filepath),
                "checksum": sha256_file(filepath),
                "file": f".claude/{rel_path}",
                "description": get_component_description(filepath)
            }

    return components


def generate_manifest(root: Path) -> dict:
    """Generate complete protocol manifest."""
    manifest = {
        "protocol": {
            "version": "1.0.0",
            "release_date": datetime.now().strftime("%Y-%m-%d"),
            "min_claude_code_version": "1.0.0",
            "description": "Claude Protocol - Unified quality enforcement and autonomous operation"
        },
        "repository": {
            "url": "https://github.com/z3r0-c001/Claude_Protocol",
            "branch": "main",
            "raw_base": "https://raw.githubusercontent.com/z3r0-c001/Claude_Protocol/main"
        },
        "components": {
            "agents": {},
            "skills": {},
            "commands": {},
            "hooks": {},
            "config": {}
        },
        "deprecated": [],
        "patterns": {
            "recommended": {
                "agent_frontmatter": ["name", "description", "tools", "model", "supports_plan_mode"],
                "skill_frontmatter": ["name", "description", "allowed-tools"],
                "hook_naming": "kebab-case with extension (.sh or .py)",
                "command_naming": "kebab-case"
            }
        }
    }

    # Scan agents
    for pattern in ["agents/**/*.md"]:
        agents = scan_directory(root, pattern, "agents")
        manifest["components"]["agents"].update(agents)

    # Scan skills (SKILL.md files)
    for pattern in ["skills/**/SKILL.md", "skills/**/skill.md"]:
        skills = scan_directory(root, pattern, "skills")
        manifest["components"]["skills"].update(skills)

    # Scan commands
    for pattern in ["commands/*.md"]:
        commands = scan_directory(root, pattern, "commands")
        manifest["components"]["commands"].update(commands)

    # Scan hooks
    for pattern in ["hooks/*.sh", "hooks/*.py"]:
        hooks = scan_directory(root, pattern, "hooks")
        manifest["components"]["hooks"].update(hooks)

    # Add config files
    config_files = [
        ("settings", ".claude/settings.json"),
        ("skill-rules", ".claude/skills/skill-rules.json"),
    ]

    for key, rel_path in config_files:
        filepath = root / rel_path
        if filepath.exists():
            manifest["components"]["config"][key] = {
                "version": "1.0.0",
                "checksum": sha256_file(filepath),
                "file": rel_path,
                "description": f"Protocol {key} configuration"
            }

    return manifest


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate protocol manifest")
    parser.add_argument("--output", "-o", default="protocol-manifest.json",
                        help="Output file path")
    parser.add_argument("--pretty", "-p", action="store_true", default=True,
                        help="Pretty print JSON")
    args = parser.parse_args()

    root = get_project_root()
    manifest = generate_manifest(root)

    output_path = root / args.output
    with open(output_path, "w") as f:
        if args.pretty:
            json.dump(manifest, f, indent=2)
        else:
            json.dump(manifest, f)

    # Print summary
    print(f"Generated manifest: {output_path}")
    print(f"  Agents:   {len(manifest['components']['agents'])}")
    print(f"  Skills:   {len(manifest['components']['skills'])}")
    print(f"  Commands: {len(manifest['components']['commands'])}")
    print(f"  Hooks:    {len(manifest['components']['hooks'])}")
    print(f"  Config:   {len(manifest['components']['config'])}")


if __name__ == "__main__":
    main()
