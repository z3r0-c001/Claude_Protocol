/**
 * Fuzzy search utilities for memory
 */

import Fuse from "fuse.js";
import type { MemoryEntry, MemoryCategory, MemoryFile } from "../types/memory.js";

export interface SearchResult {
  category: MemoryCategory;
  entry: MemoryEntry;
  score: number;
}

export interface SearchOptions {
  categories?: MemoryCategory[];
  fuzzy?: boolean;
  limit?: number;
  threshold?: number;
}

const DEFAULT_OPTIONS: SearchOptions = {
  fuzzy: true,
  limit: 20,
  threshold: 0.4
};

export function searchMemory(
  query: string,
  memoryData: Record<MemoryCategory, MemoryFile>,
  options: SearchOptions = {}
): SearchResult[] {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const results: SearchResult[] = [];

  const categoriesToSearch = opts.categories || [
    "user-preferences",
    "project-learnings",
    "decisions",
    "corrections",
    "patterns"
  ] as MemoryCategory[];

  for (const category of categoriesToSearch) {
    const file = memoryData[category];
    if (!file || !file.entries || file.entries.length === 0) {
      continue;
    }

    if (opts.fuzzy) {
      // Fuzzy search using Fuse.js
      const fuse = new Fuse(file.entries, {
        keys: ["key", "value", "reason", "context"],
        threshold: opts.threshold,
        includeScore: true,
        ignoreLocation: true
      });

      const fuseResults = fuse.search(query);

      for (const result of fuseResults) {
        results.push({
          category,
          entry: result.item,
          score: 1 - (result.score || 0) // Convert to similarity score
        });
      }
    } else {
      // Exact/partial match
      const lowerQuery = query.toLowerCase();

      for (const entry of file.entries) {
        const matches =
          entry.key.toLowerCase().includes(lowerQuery) ||
          entry.value.toLowerCase().includes(lowerQuery) ||
          (entry.reason?.toLowerCase().includes(lowerQuery) ?? false);

        if (matches) {
          results.push({
            category,
            entry,
            score: 1.0
          });
        }
      }
    }
  }

  // Sort by score (highest first) and apply limit
  return results
    .sort((a, b) => b.score - a.score)
    .slice(0, opts.limit);
}

export function formatSearchResults(results: SearchResult[]): string {
  if (results.length === 0) {
    return "No matching entries found.";
  }

  const lines: string[] = [`Found ${results.length} matching entries:\n`];

  for (const result of results) {
    lines.push(`[${result.category}] ${result.entry.key}`);
    lines.push(`  Value: ${result.entry.value}`);
    if (result.entry.reason) {
      lines.push(`  Reason: ${result.entry.reason}`);
    }
    lines.push(`  Score: ${(result.score * 100).toFixed(0)}%`);
    lines.push("");
  }

  return lines.join("\n");
}
