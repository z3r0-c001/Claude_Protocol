---
description: Run project tests. Usage: /test [pattern] [--coverage] [--watch]
---

# Test Command

Run project tests with optional filtering and coverage.

## Usage

- `/test` - Run all tests
- `/test auth` - Run tests matching "auth"
- `/test --coverage` - Run with coverage report
- `/test --watch` - Run in watch mode

## Process

1. **Detect Test Framework**
   - Check for jest.config, vitest.config, pytest.ini, etc.
   - Determine the test command from package.json or equivalent

2. **Build Test Command**
   - Base: detected test command
   - Add pattern filter if specified
   - Add --coverage flag if requested
   - Add --watch flag if requested

3. **Run Tests**
   - Execute the test command
   - Capture output

4. **Report Results**
   - Test summary (pass/fail counts)
   - Failed test details
   - Coverage summary (if requested)

## Common Test Frameworks

| File | Framework | Command |
|------|-----------|---------|
| jest.config.* | Jest | npm test |
| vitest.config.* | Vitest | npm test |
| pytest.ini | pytest | pytest |
| go.mod | Go | go test ./... |
| Cargo.toml | Rust | cargo test |

---

Detect the test framework and run the appropriate test command.
