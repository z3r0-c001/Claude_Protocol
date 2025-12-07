# MCP Memory Server Reference

Complete reference for the Claude Bootstrap Protocol MCP Memory Server.

## Overview

The MCP (Model Context Protocol) Memory Server provides persistent memory across Claude sessions. It stores:
- User preferences
- Project learnings
- Architectural decisions
- Corrections and patterns

## Architecture

```
.claude/mcp/memory-server/
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── src/
│   ├── index.ts           # MCP server entry point
│   ├── types/
│   │   └── memory.ts      # Type definitions
│   ├── utils/
│   │   ├── file-ops.ts    # JSON file operations
│   │   └── search.ts      # Fuzzy search (fuse.js)
│   └── tools/
│       ├── read.ts        # memory_read tool
│       ├── write.ts       # memory_write tool
│       ├── search.ts      # memory_search tool
│       ├── list.ts        # memory_list tool
│       ├── delete.ts      # memory_delete tool
│       └── prune.ts       # memory_prune tool
└── dist/                  # Compiled output (after build)
```

## Installation

```bash
cd .claude/mcp/memory-server
npm install
npm run build
```

## Configuration

The server is configured in `.mcp.json` at project root:

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": [".claude/mcp/memory-server/dist/index.js"],
      "env": {
        "MEMORY_PATH": ".claude/memory"
      }
    }
  }
}
```

## Memory Categories

| Category | Auto-Save | Description |
|----------|-----------|-------------|
| `user-preferences` | Yes | Coding style, verbosity, goals |
| `project-learnings` | Yes | Technical discoveries about codebase |
| `corrections` | Yes | Mistakes to avoid in future |
| `patterns` | Yes | Detected code patterns |
| `decisions` | Ask | Architecture and design decisions |
| `protocol-state` | Yes | Protocol configuration |

## MCP Tools

### memory_read

Read entries from memory.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | Category to read. Omit for all. |
| `key` | string | No | Specific key. Omit for all in category. |
| `limit` | number | No | Max entries. Default: 50 |

**Examples:**

```
# Read all memory
mcp__memory__memory_read

# Read all user preferences
mcp__memory__memory_read category="user-preferences"

# Read specific entry
mcp__memory__memory_read category="decisions" key="auth-approach"
```

**Response:**
```json
{
  "success": true,
  "entries": [
    {
      "category": "user-preferences",
      "key": "coding-style",
      "value": "Prefer functional programming patterns",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### memory_write

Write an entry to memory.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | Yes | Target category |
| `key` | string | Yes | Unique identifier |
| `value` | string | Yes | Content to remember |
| `reason` | string | No | Why this is being remembered |
| `context` | string | No | When/where this was learned |
| `metadata` | object | No | Additional structured data |
| `confirm` | boolean | No | Required for `decisions` category |

**Auto-Save Categories:**
- `user-preferences` - Silent save
- `project-learnings` - Silent save
- `corrections` - Silent save
- `patterns` - Silent save

**Confirmation Required:**
- `decisions` - Must set `confirm: true`

**Examples:**

```
# Auto-save a learning
mcp__memory__memory_write \
  category="project-learnings" \
  key="api-pattern" \
  value="This project uses REST with JSON:API spec" \
  reason="Discovered while implementing user endpoint"

# Save a decision (requires confirmation)
mcp__memory__memory_write \
  category="decisions" \
  key="database-choice" \
  value="PostgreSQL with Prisma ORM" \
  reason="Better type safety and migration support" \
  confirm=true
```

**Response:**
```json
{
  "success": true,
  "action": "created",
  "entry": {
    "category": "project-learnings",
    "key": "api-pattern",
    "value": "...",
    "created_at": "..."
  }
}
```

---

### memory_search

Search across all memory categories.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `categories` | array | No | Categories to search. Omit for all. |
| `fuzzy` | boolean | No | Enable fuzzy matching. Default: true |
| `limit` | number | No | Max results. Default: 20 |

**Examples:**

```
# Search all memory
mcp__memory__memory_search query="authentication"

# Search specific categories
mcp__memory__memory_search \
  query="database" \
  categories=["decisions", "patterns"]

# Exact match search
mcp__memory__memory_search query="PostgreSQL" fuzzy=false
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "category": "decisions",
      "key": "database-choice",
      "value": "PostgreSQL with Prisma ORM",
      "score": 0.95,
      "matches": ["PostgreSQL"]
    }
  ]
}
```

---

### memory_list

List all memory entries with summaries.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | Category to list. Omit for all. |
| `include_timestamps` | boolean | No | Include timestamps. Default: false |

**Examples:**

```
# List all entries
mcp__memory__memory_list

# List with timestamps
mcp__memory__memory_list include_timestamps=true

# List specific category
mcp__memory__memory_list category="patterns"
```

**Response:**
```json
{
  "success": true,
  "categories": {
    "user-preferences": {
      "count": 5,
      "keys": ["coding-style", "verbosity", "...]
    },
    "decisions": {
      "count": 3,
      "keys": ["database-choice", "auth-approach", "..."]
    }
  }
}
```

---

### memory_delete

Delete a specific entry.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | Yes | Category of entry |
| `key` | string | Yes | Key to delete |
| `confirm` | boolean | Yes | Must be true to delete |

**Example:**

```
mcp__memory__memory_delete \
  category="patterns" \
  key="old-pattern" \
  confirm=true
```

**Response:**
```json
{
  "success": true,
  "deleted": {
    "category": "patterns",
    "key": "old-pattern"
  }
}
```

---

### memory_prune

Remove old entries based on age or count.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `max_age_days` | number | No | Remove entries older than this. Default: 90 |
| `max_entries` | number | No | Keep only this many per category. Default: 100 |
| `dry_run` | boolean | No | Preview what would be deleted. Default: true |
| `confirm` | boolean | No | Required if dry_run is false |

**Examples:**

```
# Preview what would be pruned
mcp__memory__memory_prune dry_run=true

# Prune entries older than 30 days
mcp__memory__memory_prune max_age_days=30 dry_run=false confirm=true

# Keep only 50 entries per category
mcp__memory__memory_prune max_entries=50 dry_run=false confirm=true
```

**Response:**
```json
{
  "success": true,
  "dry_run": true,
  "would_delete": [
    {
      "category": "patterns",
      "key": "old-pattern",
      "age_days": 95
    }
  ],
  "total": 3
}
```

---

## Storage Format

Memory is stored as JSON files in `.claude/memory/`:

```
.claude/memory/
├── user-preferences.json
├── project-learnings.json
├── decisions.json
├── corrections.json
├── patterns.json
└── protocol-state.json
```

**Entry Format:**
```json
{
  "entries": {
    "key-name": {
      "value": "The content",
      "reason": "Why it was saved",
      "context": "When/where it was learned",
      "metadata": {},
      "created_at": "2024-01-15T10:30:00.000Z",
      "updated_at": "2024-01-15T10:30:00.000Z"
    }
  }
}
```

## Fuzzy Search

The memory server uses [Fuse.js](https://fusejs.io/) for fuzzy search:

**Features:**
- Typo tolerance
- Weighted scoring
- Partial matching

**Search Fields (by weight):**
1. Key (highest)
2. Value
3. Reason
4. Context (lowest)

## Error Handling

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `ENOENT` | Memory file doesn't exist | Auto-created on first write |
| `EACCES` | Permission denied | Check file permissions |
| `JSON parse error` | Corrupted file | Delete and restart |

**Recovery:**
```bash
# Reset memory (careful - loses all data)
rm -rf .claude/memory/*.json

# Rebuild MCP server
cd .claude/mcp/memory-server
rm -rf node_modules dist
npm install
npm run build
```

## Development

### Run in Development Mode

```bash
cd .claude/mcp/memory-server
npm run dev
```

### Build for Production

```bash
npm run build
```

### Debug

Set environment variable:
```bash
DEBUG=true node dist/index.js
```

## Integration with Claude

Claude automatically uses memory tools when:
1. Discovering user preferences
2. Learning about the codebase
3. Recording decisions (with confirmation)
4. Avoiding repeated mistakes

**Autonomous Behaviors:**
- Auto-save learnings without prompting
- Ask permission only for major decisions
- Search memory before asking questions
