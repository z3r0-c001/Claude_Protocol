/**
 * memory_prune tool - Clean up old memory entries
 */

import type { MemoryCategory, MemoryEntry } from "../types/memory.js";
import { READ_ONLY_CATEGORIES } from "../types/memory.js";
import { readMemoryFile, writeMemoryFile } from "../utils/file-ops.js";

export interface PruneInput {
  max_age_days?: number;
  max_entries?: number;
  dry_run?: boolean;
  confirm?: boolean;
}

export interface PruneResult {
  success: boolean;
  message: string;
  dry_run: boolean;
  requires_confirmation: boolean;
  pruned: Record<string, number>;
}

const DEFAULT_MAX_AGE_DAYS = 90;
const DEFAULT_MAX_ENTRIES = 100;

const PRUNABLE_CATEGORIES: MemoryCategory[] = [
  "user-preferences",
  "project-learnings",
  "decisions",
  "corrections",
  "patterns"
];

export async function memoryPrune(input: PruneInput): Promise<PruneResult> {
  const {
    max_age_days = DEFAULT_MAX_AGE_DAYS,
    max_entries = DEFAULT_MAX_ENTRIES,
    dry_run = true,
    confirm = false
  } = input;

  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - max_age_days);
  const cutoffTimestamp = cutoffDate.toISOString();

  const pruned: Record<string, number> = {};
  const toRemove: Record<string, string[]> = {};

  try {
    // First pass: identify what would be pruned
    for (const category of PRUNABLE_CATEGORIES) {
      const file = await readMemoryFile(category);
      const entriesToRemove: string[] = [];

      // Sort by timestamp (newest first)
      const sorted = [...file.entries].sort((a, b) => {
        const timeA = a.timestamp ? new Date(a.timestamp).getTime() : 0;
        const timeB = b.timestamp ? new Date(b.timestamp).getTime() : 0;
        return timeB - timeA;
      });

      for (let i = 0; i < sorted.length; i++) {
        const entry = sorted[i];
        const isOld = entry.timestamp && entry.timestamp < cutoffTimestamp;
        const isOverLimit = i >= max_entries;

        if (isOld || isOverLimit) {
          entriesToRemove.push(entry.key);
        }
      }

      if (entriesToRemove.length > 0) {
        toRemove[category] = entriesToRemove;
        pruned[category] = entriesToRemove.length;
      }
    }

    // Calculate total
    const totalToPrune = Object.values(pruned).reduce((a, b) => a + b, 0);

    if (totalToPrune === 0) {
      return {
        success: true,
        message: "No entries need pruning.",
        dry_run,
        requires_confirmation: false,
        pruned: {}
      };
    }

    // Dry run: just report what would be removed
    if (dry_run) {
      return {
        success: true,
        message: formatPrunePreview(pruned, toRemove, max_age_days, max_entries),
        dry_run: true,
        requires_confirmation: false,
        pruned
      };
    }

    // Require confirmation for actual pruning
    if (!confirm) {
      return {
        success: true,
        message: formatPruneConfirmation(pruned, max_age_days, max_entries),
        dry_run: false,
        requires_confirmation: true,
        pruned
      };
    }

    // Actually prune
    for (const category of PRUNABLE_CATEGORIES) {
      if (!toRemove[category]) continue;

      const file = await readMemoryFile(category);
      const keysToRemove = new Set(toRemove[category]);

      file.entries = file.entries.filter((entry) => !keysToRemove.has(entry.key));
      await writeMemoryFile(category, file);
    }

    return {
      success: true,
      message: `Pruned ${totalToPrune} entries across ${Object.keys(pruned).length} categories.`,
      dry_run: false,
      requires_confirmation: false,
      pruned
    };
  } catch (error) {
    return {
      success: false,
      message: `Error pruning memory: ${error instanceof Error ? error.message : String(error)}`,
      dry_run,
      requires_confirmation: false,
      pruned: {}
    };
  }
}

function formatPrunePreview(
  pruned: Record<string, number>,
  toRemove: Record<string, string[]>,
  maxAgeDays: number,
  maxEntries: number
): string {
  const total = Object.values(pruned).reduce((a, b) => a + b, 0);
  const lines = [
    `DRY RUN: Would prune ${total} entries`,
    `(entries older than ${maxAgeDays} days or beyond ${maxEntries} per category)`,
    ""
  ];

  for (const [category, keys] of Object.entries(toRemove)) {
    lines.push(`## ${category} (${keys.length} to remove)`);
    for (const key of keys.slice(0, 5)) {
      lines.push(`  - ${key}`);
    }
    if (keys.length > 5) {
      lines.push(`  ... and ${keys.length - 5} more`);
    }
    lines.push("");
  }

  lines.push("To prune, call memory_prune with dry_run: false, confirm: true");

  return lines.join("\n");
}

function formatPruneConfirmation(
  pruned: Record<string, number>,
  maxAgeDays: number,
  maxEntries: number
): string {
  const total = Object.values(pruned).reduce((a, b) => a + b, 0);
  const lines = [
    `About to permanently delete ${total} entries:`,
    ""
  ];

  for (const [category, count] of Object.entries(pruned)) {
    lines.push(`  - ${category}: ${count} entries`);
  }

  lines.push("");
  lines.push(`Criteria: older than ${maxAgeDays} days OR beyond ${maxEntries} per category`);
  lines.push("");
  lines.push("To confirm, call memory_prune with confirm: true");

  return lines.join("\n");
}

export function formatPruneResult(result: PruneResult): string {
  if (result.requires_confirmation || result.dry_run) {
    return result.message;
  }

  if (!result.success) {
    return `Error: ${result.message}`;
  }

  return result.message;
}
