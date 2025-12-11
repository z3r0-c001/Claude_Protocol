/**
 * memory_list tool - List memory entries with summaries
 */

import type { MemoryCategory } from "../types/memory.js";
import { readMemoryFile, readAllMemory } from "../utils/file-ops.js";

export interface ListInput {
  category?: MemoryCategory;
  include_timestamps?: boolean;
}

export interface ListEntry {
  key: string;
  preview: string;
  timestamp?: string;
}

export interface ListResult {
  success: boolean;
  data: Record<string, ListEntry[]> | ListEntry[];
  message: string;
}

function truncate(str: string, maxLength: number = 50): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + "...";
}

export async function memoryList(input: ListInput): Promise<ListResult> {
  const { category, include_timestamps = false } = input;

  try {
    if (category) {
      const file = await readMemoryFile(category);
      const entries: ListEntry[] = file.entries.map((entry) => ({
        key: entry.key,
        preview: truncate(entry.value),
        ...(include_timestamps && entry.timestamp ? { timestamp: entry.timestamp } : {})
      }));

      return {
        success: true,
        data: entries,
        message: `${category}: ${entries.length} entries`
      };
    }

    // List all categories
    const allMemory = await readAllMemory();
    const result: Record<string, ListEntry[]> = {};
    let totalCount = 0;

    for (const [cat, file] of Object.entries(allMemory)) {
      const entries: ListEntry[] = file.entries.map((entry) => ({
        key: entry.key,
        preview: truncate(entry.value),
        ...(include_timestamps && entry.timestamp ? { timestamp: entry.timestamp } : {})
      }));
      result[cat] = entries;
      totalCount += entries.length;
    }

    return {
      success: true,
      data: result,
      message: `Total: ${totalCount} entries across ${Object.keys(result).length} categories`
    };
  } catch (error) {
    return {
      success: false,
      data: [],
      message: `Error listing memory: ${error instanceof Error ? error.message : String(error)}`
    };
  }
}

export function formatListResult(result: ListResult): string {
  if (!result.success) {
    return `Error: ${result.message}`;
  }

  const lines: string[] = [result.message, ""];

  if (Array.isArray(result.data)) {
    // Single category
    for (const entry of result.data) {
      let line = `- ${entry.key}: ${entry.preview}`;
      if (entry.timestamp) line += ` (${entry.timestamp})`;
      lines.push(line);
    }
  } else {
    // All categories
    for (const [category, entries] of Object.entries(result.data)) {
      if (entries.length === 0) continue;

      lines.push(`## ${category} (${entries.length})`);
      for (const entry of entries) {
        let line = `  - ${entry.key}: ${entry.preview}`;
        if (entry.timestamp) line += ` (${entry.timestamp})`;
        lines.push(line);
      }
      lines.push("");
    }
  }

  return lines.join("\n");
}
