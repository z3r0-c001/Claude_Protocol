#!/bin/bash
# Analyze codebase structure
echo "=== Codebase Analysis ==="

echo "Files by type:"
echo "  TypeScript: $(find . -name '*.ts' -not -path '*/node_modules/*' | wc -l)"
echo "  JavaScript: $(find . -name '*.js' -not -path '*/node_modules/*' | wc -l)"
echo "  Python: $(find . -name '*.py' -not -path '*/.venv/*' | wc -l)"
echo "  Go: $(find . -name '*.go' | wc -l)"

echo ""
echo "Package files:"
ls package.json pyproject.toml Cargo.toml go.mod 2>/dev/null || echo "  None found"

echo ""
echo "Config files:"
ls tsconfig.json .eslintrc* .prettierrc* 2>/dev/null || echo "  None found"

echo ""
echo "Test directories:"
ls -d test tests __tests__ spec 2>/dev/null || echo "  None found"
