#!/usr/bin/env node
/**
 * Claude Memory Server - MCP Server for persistent memory operations
 *
 * Provides tools for reading, writing, searching, and managing memory
 * across Claude sessions.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  type Tool
} from "@modelcontextprotocol/sdk/types.js";

import { memoryRead, formatReadResult } from "./tools/read.js";
import { memoryWrite, formatWriteResult } from "./tools/write.js";
import { memorySearch, formatSearchResultOutput } from "./tools/search.js";
import { memoryList, formatListResult } from "./tools/list.js";
import { memoryDelete, formatDeleteResult } from "./tools/delete.js";
import { memoryPrune, formatPruneResult } from "./tools/prune.js";
import type { MemoryCategory } from "./types/memory.js";

// Tool definitions
const tools: Tool[] = [
  {
    name: "memory_read",
    description: "Read entries from memory. Returns all entries from specified category or all categories if none specified. Use this to check what's already known before asking the user.",
    inputSchema: {
      type: "object",
      properties: {
        category: {
          type: "string",
          enum: ["user-preferences", "project-learnings", "decisions", "corrections", "patterns", "protocol-state"],
          description: "Memory category to read. Omit to read all categories."
        },
        key: {
          type: "string",
          description: "Specific key to read. Omit to read all entries in category."
        },
        limit: {
          type: "number",
          description: "Maximum number of entries to return. Default: 50"
        }
      }
    }
  },
  {
    name: "memory_write",
    description: "Write an entry to memory. Auto-saves learnings, corrections, patterns, and preferences. Requires confirmation for major decisions. Use this to remember user preferences, learnings, and patterns for future sessions.",
    inputSchema: {
      type: "object",
      properties: {
        category: {
          type: "string",
          enum: ["user-preferences", "project-learnings", "decisions", "corrections", "patterns"],
          description: "Memory category. Use 'decisions' for major architectural choices (requires confirm: true)."
        },
        key: {
          type: "string",
          description: "Unique identifier for this entry"
        },
        value: {
          type: "string",
          description: "The content to remember"
        },
        reason: {
          type: "string",
          description: "Why this is being remembered (context)"
        },
        context: {
          type: "string",
          description: "Additional context about when/where this was learned"
        },
        metadata: {
          type: "object",
          description: "Additional structured metadata"
        },
        confirm: {
          type: "boolean",
          description: "Required for 'decisions' category. Set to true to confirm saving."
        }
      },
      required: ["category", "key", "value"]
    }
  },
  {
    name: "memory_search",
    description: "Search across all memory categories for matching entries. Supports fuzzy matching. Use this to find relevant past learnings, decisions, or preferences.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query (matches keys, values, and reasons)"
        },
        categories: {
          type: "array",
          items: {
            type: "string",
            enum: ["user-preferences", "project-learnings", "decisions", "corrections", "patterns"]
          },
          description: "Categories to search. Omit to search all."
        },
        fuzzy: {
          type: "boolean",
          description: "Enable fuzzy matching. Default: true"
        },
        limit: {
          type: "number",
          description: "Maximum results to return. Default: 20"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "memory_list",
    description: "List all memory entries with summaries. Useful for getting an overview without full content.",
    inputSchema: {
      type: "object",
      properties: {
        category: {
          type: "string",
          enum: ["user-preferences", "project-learnings", "decisions", "corrections", "patterns", "protocol-state"],
          description: "Category to list. Omit to list all."
        },
        include_timestamps: {
          type: "boolean",
          description: "Include timestamps in output. Default: false"
        }
      }
    }
  },
  {
    name: "memory_delete",
    description: "Delete a specific entry from memory. Requires confirmation to prevent accidental deletion.",
    inputSchema: {
      type: "object",
      properties: {
        category: {
          type: "string",
          enum: ["user-preferences", "project-learnings", "decisions", "corrections", "patterns"],
          description: "Category containing the entry"
        },
        key: {
          type: "string",
          description: "Key of the entry to delete"
        },
        confirm: {
          type: "boolean",
          description: "Set to true to confirm deletion"
        }
      },
      required: ["category", "key", "confirm"]
    }
  },
  {
    name: "memory_prune",
    description: "Remove old entries based on age or count thresholds. Use dry_run: true to preview, then confirm: true to execute.",
    inputSchema: {
      type: "object",
      properties: {
        max_age_days: {
          type: "number",
          description: "Remove entries older than this. Default: 90"
        },
        max_entries: {
          type: "number",
          description: "Keep only this many most recent per category. Default: 100"
        },
        dry_run: {
          type: "boolean",
          description: "Preview what would be deleted. Default: true"
        },
        confirm: {
          type: "boolean",
          description: "Set to true to confirm pruning (only needed if dry_run is false)"
        }
      }
    }
  }
];

// Create server instance
const server = new Server(
  {
    name: "claude-memory-server",
    version: "1.0.0"
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// Handler for listing tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Handler for calling tools
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "memory_read": {
        const result = await memoryRead({
          category: args?.category as MemoryCategory | undefined,
          key: args?.key as string | undefined,
          limit: args?.limit as number | undefined
        });
        return {
          content: [{ type: "text", text: formatReadResult(result) }]
        };
      }

      case "memory_write": {
        const result = await memoryWrite({
          category: args?.category as MemoryCategory,
          key: args?.key as string,
          value: args?.value as string,
          reason: args?.reason as string | undefined,
          context: args?.context as string | undefined,
          metadata: args?.metadata as Record<string, unknown> | undefined,
          confirm: args?.confirm as boolean | undefined
        });
        return {
          content: [{ type: "text", text: formatWriteResult(result) }]
        };
      }

      case "memory_search": {
        const result = await memorySearch({
          query: args?.query as string,
          categories: args?.categories as MemoryCategory[] | undefined,
          fuzzy: args?.fuzzy as boolean | undefined,
          limit: args?.limit as number | undefined
        });
        return {
          content: [{ type: "text", text: formatSearchResultOutput(result) }]
        };
      }

      case "memory_list": {
        const result = await memoryList({
          category: args?.category as MemoryCategory | undefined,
          include_timestamps: args?.include_timestamps as boolean | undefined
        });
        return {
          content: [{ type: "text", text: formatListResult(result) }]
        };
      }

      case "memory_delete": {
        const result = await memoryDelete({
          category: args?.category as MemoryCategory,
          key: args?.key as string,
          confirm: args?.confirm as boolean
        });
        return {
          content: [{ type: "text", text: formatDeleteResult(result) }]
        };
      }

      case "memory_prune": {
        const result = await memoryPrune({
          max_age_days: args?.max_age_days as number | undefined,
          max_entries: args?.max_entries as number | undefined,
          dry_run: args?.dry_run as boolean | undefined,
          confirm: args?.confirm as boolean | undefined
        });
        return {
          content: [{ type: "text", text: formatPruneResult(result) }]
        };
      }

      default:
        return {
          content: [{ type: "text", text: `Unknown tool: ${name}` }],
          isError: true
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error executing ${name}: ${error instanceof Error ? error.message : String(error)}`
        }
      ],
      isError: true
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Claude Memory Server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
