#!/bin/bash
# Post-Write Validation Script
# Runs after files are written to validate syntax and lint
# Outputs structured JSON for Claude to act on

FILE_PATH="$1"
OUTPUT_MODE="${2:-json}"  # json or human

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  if [ "$OUTPUT_MODE" = "json" ]; then
    echo '{"hook":"post-write-validate","status":"skip","issues":[],"message":"File not found or empty path"}'
  fi
  exit 0
fi

# Collect issues
ISSUES=()
AGENT_SUGGESTIONS=()

# Get file extension
EXT="${FILE_PATH##*.}"
BASENAME=$(basename "$FILE_PATH")

add_issue() {
  local type="$1"
  local message="$2"
  local severity="$3"
  local suggestion="$4"
  local line="${5:-0}"

  ISSUES+=("{\"type\":\"$type\",\"file\":\"$FILE_PATH\",\"line\":$line,\"message\":\"$message\",\"severity\":\"$severity\",\"suggestion\":\"$suggestion\"}")
}

add_agent_suggestion() {
  local agent="$1"
  local reason="$2"
  AGENT_SUGGESTIONS+=("{\"agent\":\"$agent\",\"reason\":\"$reason\"}")
}

case "$EXT" in
  py)
    # Python: syntax check
    ERROR_OUTPUT=$(python3 -m py_compile "$FILE_PATH" 2>&1) || {
      LINE=$(echo "$ERROR_OUTPUT" | grep -oE "line [0-9]+" | head -1 | grep -oE "[0-9]+")
      add_issue "syntax_error" "Python syntax error" "auto_fix" "Fix the syntax error in the Python code" "${LINE:-0}"
    }

    # Python: lint (if ruff available)
    if command -v ruff &> /dev/null; then
      LINT_OUTPUT=$(ruff check "$FILE_PATH" --output-format=json 2>/dev/null) || true
      if [ -n "$LINT_OUTPUT" ] && [ "$LINT_OUTPUT" != "[]" ]; then
        add_issue "lint_warning" "Ruff lint warnings found" "suggest" "Run 'ruff check --fix' or review lint warnings" "0"
      fi
    fi
    ;;

  js|jsx)
    # JavaScript: syntax check
    if ! node --check "$FILE_PATH" 2>/dev/null; then
      add_issue "syntax_error" "JavaScript syntax error" "auto_fix" "Fix the syntax error in the JavaScript code" "0"
    fi

    # JavaScript: lint (if eslint available)
    if command -v npx &> /dev/null && [ -f "node_modules/.bin/eslint" ]; then
      if ! npx eslint "$FILE_PATH" --quiet 2>/dev/null; then
        add_issue "lint_warning" "ESLint warnings found" "suggest" "Run 'npx eslint --fix' or review lint warnings" "0"
      fi
    fi
    ;;

  ts|tsx)
    # TypeScript: use tsc if available
    if command -v npx &> /dev/null && [ -f "node_modules/.bin/tsc" ]; then
      if ! npx tsc --noEmit "$FILE_PATH" 2>/dev/null; then
        add_issue "type_error" "TypeScript type error" "suggest" "Fix the type errors in the TypeScript code" "0"
      fi
    fi
    ;;

  go)
    # Go: vet
    if command -v go &> /dev/null; then
      if ! go vet "$FILE_PATH" 2>/dev/null; then
        add_issue "vet_warning" "Go vet warnings" "suggest" "Review go vet warnings" "0"
      fi
    fi
    ;;

  rs)
    # Rust: check (if in cargo project)
    if [ -f "Cargo.toml" ] && command -v cargo &> /dev/null; then
      if ! cargo check --message-format=short 2>/dev/null | head -5; then
        add_issue "cargo_warning" "Cargo check warnings" "suggest" "Review cargo check output" "0"
      fi
    fi
    ;;

  json)
    # JSON: validate
    if ! python3 -m json.tool "$FILE_PATH" > /dev/null 2>&1; then
      add_issue "json_error" "Invalid JSON syntax" "auto_fix" "Fix the JSON syntax error" "0"
    fi
    ;;

  yaml|yml)
    # YAML: validate
    if ! python3 -c "import yaml; yaml.safe_load(open('$FILE_PATH'))" 2>/dev/null; then
      add_issue "yaml_error" "Invalid YAML syntax" "auto_fix" "Fix the YAML syntax error" "0"
    fi
    ;;

  sh|bash)
    # Shell: syntax check
    ERROR_OUTPUT=$(bash -n "$FILE_PATH" 2>&1) || {
      LINE=$(echo "$ERROR_OUTPUT" | grep -oE "line [0-9]+" | head -1 | grep -oE "[0-9]+")
      add_issue "shell_syntax_error" "Shell script syntax error" "auto_fix" "Fix the shell script syntax error" "${LINE:-0}"
    }
    ;;
esac

# Quick laziness check on the file
if grep -qE "(// \.\.\.|# \.\.\.|/\* \.\.\. \*/)" "$FILE_PATH" 2>/dev/null; then
  add_issue "laziness" "Placeholder comments found (// ... or # ...)" "suggest" "Replace placeholder comments with actual implementation" "0"
fi

if grep -qE "(// TODO|# TODO|// FIXME|# FIXME)" "$FILE_PATH" 2>/dev/null; then
  add_issue "todo" "TODO/FIXME markers found" "suggest" "Implement the TODO items or remove the markers" "0"
fi

if grep -qE "(^\s*pass$|NotImplementedError|// implement|# implement)" "$FILE_PATH" 2>/dev/null; then
  add_issue "stub" "Stub implementation detected" "suggest" "Replace stub with actual implementation" "0"
fi

# Context-based agent suggestions
if echo "$BASENAME" | grep -qiE "(auth|password|token|secret|credential|login|session)"; then
  add_agent_suggestion "security-scanner" "File name suggests security-sensitive code"
fi

if echo "$FILE_PATH" | grep -qiE "(test|spec)"; then
  add_agent_suggestion "test-coverage-enforcer" "Test file detected - verify coverage"
fi

# Determine overall status
STATUS="pass"
if [ ${#ISSUES[@]} -gt 0 ]; then
  # Check if any are errors vs warnings
  for issue in "${ISSUES[@]}"; do
    if echo "$issue" | grep -qE '"severity":"auto_fix"'; then
      STATUS="error"
      break
    fi
  done
  if [ "$STATUS" = "pass" ]; then
    STATUS="warning"
  fi
fi

# Output based on mode
if [ "$OUTPUT_MODE" = "json" ]; then
  # Build JSON output
  ISSUES_JSON=$(IFS=,; echo "[${ISSUES[*]}]")
  AGENTS_JSON=$(IFS=,; echo "[${AGENT_SUGGESTIONS[*]}]")

  echo "{\"hook\":\"post-write-validate\",\"status\":\"$STATUS\",\"file\":\"$FILE_PATH\",\"issues\":$ISSUES_JSON,\"agent_suggestions\":$AGENTS_JSON}"
else
  # Human-readable output
  echo "Post-write validation for: $FILE_PATH"
  echo "Status: $STATUS"
  if [ ${#ISSUES[@]} -gt 0 ]; then
    echo "Issues found: ${#ISSUES[@]}"
    for issue in "${ISSUES[@]}"; do
      echo "  - $issue"
    done
  fi
fi

# Exit with error count for backward compatibility
exit ${#ISSUES[@]}
