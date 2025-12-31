#!/usr/bin/env python3
"""
PostToolUse Read hook: Detect large documents and suggest processing.

Checks line count of read content and provides suggestions:
- Already processed: shows summary path
- Large (>2000 lines): suggests /doc-ingest
- Medium (500-2000 lines): notes processing option
"""
import json
import sys
import os
import hashlib
from pathlib import Path

THRESHOLDS = {
    "small": 500,
    "medium": 2000,
}

# File extensions to consider as documentation
DOC_EXTENSIONS = {
    '.md', '.markdown', '.rst', '.txt', '.adoc', '.asciidoc',
    '.html', '.htm', '.pdf', '.docx', '.doc'
}


def get_project_dir() -> str:
    """Get the project directory from environment."""
    return os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())


def get_file_hash(file_path: str) -> str:
    """Generate a short hash for the file path."""
    return hashlib.sha256(file_path.encode()).hexdigest()[:12]


def is_documentation(file_path: str) -> bool:
    """Check if file is likely documentation based on path and extension."""
    path = Path(file_path)
    ext = path.suffix.lower()
    name = path.name.lower()

    # Check extension
    if ext in DOC_EXTENSIONS:
        return True

    # Check common doc paths
    doc_indicators = ['doc', 'docs', 'documentation', 'manual', 'guide', 'readme', 'reference', 'api']
    path_parts = [p.lower() for p in path.parts]

    for indicator in doc_indicators:
        if indicator in name or any(indicator in part for part in path_parts):
            return True

    return False


def get_docs_index() -> dict:
    """Load the docs index if it exists."""
    project_dir = get_project_dir()
    index_path = Path(project_dir) / ".claude" / "docs" / "index.json"

    if not index_path.exists():
        return {"docs": []}

    try:
        return json.loads(index_path.read_text())
    except (json.JSONDecodeError, IOError):
        return {"docs": []}


def find_processed_doc(file_path: str, index: dict) -> dict | None:
    """Check if document has already been processed."""
    # Normalize path for comparison
    norm_path = os.path.normpath(file_path)

    for doc in index.get("docs", []):
        if os.path.normpath(doc.get("source_path", "")) == norm_path:
            return doc

    return None


def output_json(data: dict) -> None:
    """Output JSON to stdout."""
    print(json.dumps(data))


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Extract tool info
    tool_input = input_data.get("tool_input", {})
    tool_result = input_data.get("tool_result", {})

    file_path = tool_input.get("file_path", "")

    # Get content - could be in different places depending on tool result format
    content = ""
    if isinstance(tool_result, dict):
        content = tool_result.get("content", tool_result.get("output", ""))
    elif isinstance(tool_result, str):
        content = tool_result

    # Skip if no file path or content
    if not file_path or not content:
        sys.exit(0)

    # Skip non-documentation files unless they're large
    lines = content.count('\n') + 1
    is_doc = is_documentation(file_path)

    # Only proceed if it's a doc file or if it's large
    if not is_doc and lines < THRESHOLDS["small"]:
        sys.exit(0)

    # Load docs index
    index = get_docs_index()

    # Check if already processed
    processed = find_processed_doc(file_path, index)

    context_parts = []

    if processed:
        doc_id = processed.get("id", "unknown")
        chunks = processed.get("chunks", 0)
        summary_path = f".claude/docs/processed/{doc_id}/summary.md"

        context_parts.append(
            f"DOC AVAILABLE: '{Path(file_path).name}' has been processed.\n"
            f"  Summary: {summary_path}\n"
            f"  Chunks: {chunks} sections available\n"
            f"  Use /doc-search <query> to find specific sections."
        )
    elif lines >= THRESHOLDS["medium"]:
        context_parts.append(
            f"LARGE DOCUMENT: '{Path(file_path).name}' has {lines} lines.\n"
            f"  This may exceed optimal context size.\n"
            f"  Recommendation: Run /doc-ingest \"{file_path}\"\n"
            f"  This will create a searchable summary and chunks for efficient reference."
        )
    elif lines >= THRESHOLDS["small"] and is_doc:
        context_parts.append(
            f"DOCUMENT NOTE: '{Path(file_path).name}' has {lines} lines.\n"
            f"  Consider /doc-ingest for better reference access if needed frequently."
        )

    # Output result if we have context to add
    if context_parts:
        output = {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "\n".join(context_parts)
            }
        }
        output_json(output)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Don't block on errors
        sys.exit(0)
