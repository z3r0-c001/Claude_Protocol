#!/bin/bash
# Context Detector Script
# Analyzes file content and patterns to suggest agent invocations
# Outputs structured JSON with agent suggestions and reasons

FILE_PATH="$1"
CONTENT="$2"  # Optional: file content if already available

if [ -z "$FILE_PATH" ]; then
  echo '{"hook":"context-detector","suggestions":[]}'
  exit 0
fi

# Get file info
BASENAME=$(basename "$FILE_PATH")
DIRNAME=$(dirname "$FILE_PATH")
EXT="${FILE_PATH##*.}"

# Arrays to collect suggestions
declare -a SUGGESTIONS=()

add_suggestion() {
  local agent="$1"
  local reason="$2"
  local priority="${3:-medium}"
  local announcement="$4"

  SUGGESTIONS+=("{\"agent\":\"$agent\",\"reason\":\"$reason\",\"priority\":\"$priority\",\"announcement\":\"$announcement\"}")
}

# Security-sensitive file detection
SECURITY_PATTERNS=(
  "auth"
  "password"
  "token"
  "secret"
  "credential"
  "login"
  "session"
  "jwt"
  "oauth"
  "api.?key"
  "encrypt"
  "decrypt"
  "hash"
  "salt"
  "permission"
  "role"
  "acl"
)

for pattern in "${SECURITY_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qiE "$pattern"; then
    add_suggestion "security-scanner" "File path contains security-related pattern: $pattern" "high" "Running security scan on $BASENAME..."
    break
  fi
done

# Also check content if provided
if [ -n "$CONTENT" ]; then
  for pattern in "${SECURITY_PATTERNS[@]}"; do
    if echo "$CONTENT" | grep -qiE "$pattern"; then
      add_suggestion "security-scanner" "File content contains security-related code" "high" "Running security scan on $BASENAME..."
      break
    fi
  done
fi

# Dependency file detection
DEPENDENCY_FILES=(
  "package.json"
  "package-lock.json"
  "yarn.lock"
  "pnpm-lock.yaml"
  "requirements.txt"
  "Pipfile"
  "pyproject.toml"
  "Cargo.toml"
  "go.mod"
  "Gemfile"
  "composer.json"
  "build.gradle"
  "pom.xml"
)

for depfile in "${DEPENDENCY_FILES[@]}"; do
  if [ "$BASENAME" = "$depfile" ]; then
    add_suggestion "dependency-auditor" "Dependency file detected: $BASENAME" "high" "Auditing dependencies in $BASENAME..."
    break
  fi
done

# Test file detection
if echo "$FILE_PATH" | grep -qiE "(test|spec|__tests__|\.test\.|\.spec\.)"; then
  add_suggestion "test-coverage-enforcer" "Test file detected" "medium" "Checking test coverage for $BASENAME..."
  add_suggestion "tester" "Test file may need review" "low" "Reviewing test quality in $BASENAME..."
fi

# Configuration file detection
CONFIG_PATTERNS=(
  "config"
  "settings"
  ".rc$"
  ".conf$"
  ".ini$"
  ".yaml$"
  ".yml$"
  ".toml$"
  ".env"
)

for pattern in "${CONFIG_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qiE "$pattern"; then
    add_suggestion "security-scanner" "Configuration file may contain sensitive settings" "medium" "Scanning configuration in $BASENAME..."
    break
  fi
done

# Architecture-related detection
ARCH_PATTERNS=(
  "controller"
  "service"
  "repository"
  "model"
  "schema"
  "migration"
  "middleware"
  "router"
  "handler"
  "factory"
  "adapter"
  "interface"
)

for pattern in "${ARCH_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qiE "$pattern"; then
    add_suggestion "architect" "File appears to be an architectural component: $pattern" "low" "Analyzing architecture implications..."
    break
  fi
done

# Database-related detection
DB_PATTERNS=(
  "database"
  "query"
  "migration"
  "schema"
  "model"
  "entity"
  "repository"
  "\.sql$"
)

for pattern in "${DB_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qiE "$pattern"; then
    add_suggestion "security-scanner" "Database-related file may need SQL injection review" "medium" "Scanning for database security issues..."
    break
  fi
done

# API endpoint detection
if echo "$FILE_PATH" | grep -qiE "(api|endpoint|route|controller|handler)"; then
  add_suggestion "security-scanner" "API endpoint may need input validation review" "medium" "Scanning API for security vulnerabilities..."
fi

# Performance-sensitive detection
PERF_PATTERNS=(
  "cache"
  "queue"
  "worker"
  "batch"
  "stream"
  "buffer"
  "async"
  "concurrent"
  "parallel"
  "pool"
)

for pattern in "${PERF_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qiE "$pattern"; then
    add_suggestion "performance-analyzer" "File may have performance implications: $pattern" "low" "Analyzing performance characteristics..."
    break
  fi
done

# Build JSON output
SUGGESTIONS_JSON=$(IFS=,; echo "[${SUGGESTIONS[*]}]")

echo "{\"hook\":\"context-detector\",\"file\":\"$FILE_PATH\",\"suggestions\":$SUGGESTIONS_JSON}"
exit 0
