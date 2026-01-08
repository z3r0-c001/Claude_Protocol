#!/usr/bin/env python3
"""
register-agent.py - Safely register an agent in agent-registry.json

Usage:
    python3 register-agent.py <agent-definition.json>
    python3 register-agent.py --name <name> --path <path> --description <desc> ...

This script MERGES new agents into the registry without overwriting existing entries.
"""

import json
import sys
import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def get_project_dir() -> Path:
    """Get project directory."""
    return Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))


def load_registry(registry_path: Path) -> dict:
    """Load existing registry or create empty one."""
    if registry_path.exists():
        try:
            return json.loads(registry_path.read_text())
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in registry: {e}", file=sys.stderr)
            sys.exit(1)
    return {
        "$schema": "./agent-registry.schema.json",
        "version": "1.0.0",
        "description": "Centralized registry of all agents",
        "agents": {},
        "command_mappings": {},
        "category_agent_mappings": {}
    }


def backup_registry(registry_path: Path) -> Path:
    """Create a backup of the registry."""
    if registry_path.exists():
        backup_path = registry_path.with_suffix(f'.json.bak')
        shutil.copy(registry_path, backup_path)
        return backup_path
    return None


def validate_agent_definition(agent_def: dict) -> list:
    """Validate agent definition, return list of errors."""
    errors = []
    required_fields = ['name', 'path', 'description', 'category_group', 'categories']

    for field in required_fields:
        if field not in agent_def:
            errors.append(f"Missing required field: {field}")

    if 'name' in agent_def:
        name = agent_def['name']
        if not name.replace('-', '').replace('_', '').isalnum():
            errors.append(f"Invalid agent name: {name} (use kebab-case)")

    if 'category_group' in agent_def:
        valid_groups = ['core', 'quality', 'domain', 'workflow']
        if agent_def['category_group'] not in valid_groups:
            errors.append(f"Invalid category_group: {agent_def['category_group']} (must be one of {valid_groups})")

    if 'categories' in agent_def:
        if not isinstance(agent_def['categories'], list):
            errors.append("categories must be a list")
        elif len(agent_def['categories']) == 0:
            errors.append("categories cannot be empty")

    return errors


def merge_agent(registry: dict, agent_def: dict, overwrite: bool = False) -> tuple:
    """
    Merge agent into registry.

    Returns (success: bool, message: str)
    """
    name = agent_def.get('name')

    if not name:
        return False, "Agent definition missing 'name'"

    agents = registry.setdefault('agents', {})

    if name in agents and not overwrite:
        return False, f"Agent '{name}' already exists. Use --overwrite to replace."

    # Add/update agent
    agents[name] = agent_def

    # Update category_agent_mappings
    cat_mappings = registry.setdefault('category_agent_mappings', {})
    for category in agent_def.get('categories', []):
        if category not in cat_mappings:
            cat_mappings[category] = []
        if name not in cat_mappings[category]:
            cat_mappings[category].append(name)

    action = "Updated" if name in agents else "Added"
    return True, f"{action} agent '{name}'"


def create_default_triggers(name: str, description: str, categories: list) -> dict:
    """Generate default triggers based on agent info."""
    # Extract keywords from name and description
    keywords = set()

    # From name
    for part in name.split('-'):
        if len(part) > 2:
            keywords.add(part.lower())

    # From description (simple word extraction)
    desc_words = description.lower().replace(',', ' ').replace('.', ' ').split()
    important_words = [w for w in desc_words if len(w) > 4 and w.isalpha()]
    keywords.update(important_words[:5])

    # Category-based file patterns
    file_patterns = []
    category_patterns = {
        'frontend': ['**/*.tsx', '**/*.jsx', '**/components/**'],
        'testing': ['**/*.test.*', '**/*.spec.*', '**/tests/**'],
        'security': ['**/auth/**', '**/security/**'],
        'data': ['**/migrations/**', '**/models/**', '**/*.sql'],
        'api': ['**/api/**', '**/routes/**', '**/controllers/**'],
        'documentation': ['**/docs/**', '**/*.md'],
    }

    for cat in categories:
        if cat in category_patterns:
            file_patterns.extend(category_patterns[cat])

    return {
        'exact_keywords': list(keywords)[:10],
        'phrase_patterns': [],
        'file_patterns': list(set(file_patterns)),
        'negation_patterns': []
    }


def main():
    parser = argparse.ArgumentParser(description='Register an agent in agent-registry.json')
    parser.add_argument('definition_file', nargs='?', help='JSON file with agent definition')
    parser.add_argument('--name', help='Agent name (kebab-case)')
    parser.add_argument('--path', help='Path to agent markdown file')
    parser.add_argument('--description', help='Agent description')
    parser.add_argument('--category-group', choices=['core', 'quality', 'domain', 'workflow'])
    parser.add_argument('--categories', nargs='+', help='Agent categories')
    parser.add_argument('--model-tier', choices=['standard', 'high'], default='standard')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing agent')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')

    args = parser.parse_args()

    project_dir = get_project_dir()
    registry_path = project_dir / '.claude' / 'agents' / 'agent-registry.json'

    # Build agent definition
    if args.definition_file:
        try:
            agent_def = json.loads(Path(args.definition_file).read_text())
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.name:
        agent_def = {
            'name': args.name,
            'path': args.path or f"{args.category_group or 'domain'}/{args.name}.md",
            'description': args.description or f"Custom {args.name} agent",
            'category_group': args.category_group or 'domain',
            'categories': args.categories or [],
            'model_tier': args.model_tier,
            'supports_plan_mode': True,
            'triggers': create_default_triggers(
                args.name,
                args.description or '',
                args.categories or []
            ),
            'orchestration': {
                'typical_position': 'middle',
                'often_follows': [],
                'often_precedes': [],
                'can_parallel_with': []
            }
        }
    else:
        parser.print_help()
        sys.exit(1)

    # Validate
    errors = validate_agent_definition(agent_def)
    if errors:
        print("Validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # Load existing registry
    registry = load_registry(registry_path)

    if args.dry_run:
        print("DRY RUN - Would register:")
        print(json.dumps(agent_def, indent=2))
        print(f"\nRegistry has {len(registry.get('agents', {}))} existing agents")
        sys.exit(0)

    # Backup
    backup = backup_registry(registry_path)
    if backup:
        print(f"Backed up registry to {backup.name}")

    # Merge
    success, message = merge_agent(registry, agent_def, args.overwrite)

    if not success:
        print(f"ERROR: {message}", file=sys.stderr)
        sys.exit(1)

    # Write updated registry
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2))

    print(f"SUCCESS: {message}")
    print(f"Registry now has {len(registry.get('agents', {}))} agents")

    # Show integration info
    print(f"\nAgent '{agent_def['name']}' will:")
    print(f"  - Auto-invoke on keywords: {agent_def.get('triggers', {}).get('exact_keywords', [])[:5]}")
    print(f"  - Satisfy enforcement rules for categories: {agent_def.get('categories', [])}")


if __name__ == '__main__':
    main()
