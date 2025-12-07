/**
 * memory_write tool - Write entries to memory
 * Auto-saves for learnings, asks permission for decisions
 */

import type { MemoryCategory, MemoryEntry } from "../types/memory.js";
import {
  AUTO_SAVE_CATEGORIES,
  PERMISSION_REQUIRED_CATEGORIES,
  READ_ONLY_CATEGORIES
} from "../types/memory.js";
import { readMemoryFile, writeMemoryFile } from "../utils/file-ops.js";

export interface WriteInput {
  category: MemoryCategory;
  key: string;
  value: string;
  reason?: string;
  context?: string;
  metadata?: Record<string, unknown>;
  confirm?: boolean; // Required for permission categories
}

export interface WriteResult {
  success: boolean;
  message: string;
  requires_permission: boolean;
  saved: boolean;
}

export async function memoryWrite(input: WriteInput): Promise<WriteResult> {
  const { category, key, value, reason, context, metadata, confirm } = input;

  // Check for read-only categories
  if (READ_ONLY_CATEGORIES.includes(category)) {
    return {
      success: false,
      message: `Category "${category}" is read-only and cannot be modified directly.`,
      requires_permission: false,
      saved: false
    };
  }

  // Check if category requires permission
  if (PERMISSION_REQUIRED_CATEGORIES.includes(category) && !confirm) {
    return {
      success: true,
      message: formatPermissionRequest(category, key, value, reason),
      requires_permission: true,
      saved: false
    };
  }

  try {
    // Read existing file
    const file = await readMemoryFile(category);

    // Create new entry
    const newEntry: MemoryEntry = {
      key,
      value,
      timestamp: new Date().toISOString(),
      reason,
      context,
      metadata
    };

    // Check if key already exists
    const existingIndex = file.entries.findIndex((e) => e.key === key);

    if (existingIndex >= 0) {
      // Update existing entry
      file.entries[existingIndex] = newEntry;
    } else {
      // Add new entry
      file.entries.push(newEntry);
    }

    // Write back
    await writeMemoryFile(category, file);

    const action = existingIndex >= 0 ? "Updated" : "Saved";
    const permissionNote = AUTO_SAVE_CATEGORIES.includes(category)
      ? " (auto-saved)"
      : " (confirmed)";

    return {
      success: true,
      message: `${action} "${key}" in ${category}${permissionNote}`,
      requires_permission: false,
      saved: true
    };
  } catch (error) {
    return {
      success: false,
      message: `Error writing to memory: ${error instanceof Error ? error.message : String(error)}`,
      requires_permission: false,
      saved: false
    };
  }
}

function formatPermissionRequest(
  category: MemoryCategory,
  key: string,
  value: string,
  reason?: string
): string {
  const lines = [
    "This is a major decision that requires confirmation.",
    "",
    `Category: ${category}`,
    `Key: ${key}`,
    `Value: ${value}`
  ];

  if (reason) {
    lines.push(`Reason: ${reason}`);
  }

  lines.push("");
  lines.push("To save this decision, call memory_write again with confirm: true");

  return lines.join("\n");
}

export function formatWriteResult(result: WriteResult): string {
  if (result.requires_permission) {
    return result.message;
  }

  if (!result.success) {
    return `Error: ${result.message}`;
  }

  return result.message;
}
