/**
 * File operations for memory persistence with proper file locking
 */

import { readFile, writeFile, mkdir } from "fs/promises";
import { existsSync, mkdirSync } from "fs";
import { dirname } from "path";
import lockfile from "proper-lockfile";
import type { MemoryFile, MemoryCategory } from "../types/memory.js";
import { safeValidateMemoryFile } from "../types/memory.js";

// Lock options for proper-lockfile
const LOCK_OPTIONS = {
  retries: {
    retries: 5,
    factor: 2,
    minTimeout: 100,
    maxTimeout: 1000,
    randomize: true
  },
  stale: 10000 // Consider lock stale after 10 seconds
};

function getMemoryPath(): string {
  return process.env.MEMORY_PATH || ".claude/memory";
}

function getCategoryPath(category: MemoryCategory): string {
  return `${getMemoryPath()}/${category}.json`;
}

/**
 * Execute a function with file lock protection
 */
async function withFileLock<T>(
  filePath: string,
  fn: () => Promise<T>
): Promise<T> {
  // Ensure directory and file exist for locking
  const dir = dirname(filePath);
  if (!existsSync(dir)) {
    await mkdir(dir, { recursive: true });
  }
  
  // Create empty file if it doesn't exist (required for locking)
  if (!existsSync(filePath)) {
    await writeFile(filePath, JSON.stringify({ entries: [], updated: null }, null, 2));
  }

  let release: (() => Promise<void>) | null = null;
  
  try {
    release = await lockfile.lock(filePath, LOCK_OPTIONS);
    return await fn();
  } finally {
    if (release) {
      await release();
    }
  }
}

export async function readMemoryFile(category: MemoryCategory): Promise<MemoryFile> {
  const path = getCategoryPath(category);
  
  // If file doesn't exist, return empty (no lock needed)
  if (!existsSync(path)) {
    return { entries: [], updated: null };
  }

  return withFileLock(path, async () => {
    try {
      const content = await readFile(path, "utf-8");
      const parsed = JSON.parse(content);

      // Handle legacy format (entries array without wrapper)
      if (Array.isArray(parsed)) {
        return { entries: parsed, updated: null };
      }

      // Validate with Zod schema
      return safeValidateMemoryFile(parsed);
    } catch (error) {
      // Log error but return empty to prevent blocking
      console.error(`Error reading memory file ${path}:`, error);
      return { entries: [], updated: null };
    }
  });
}

export async function writeMemoryFile(
  category: MemoryCategory,
  data: MemoryFile
): Promise<void> {
  const path = getCategoryPath(category);

  await withFileLock(path, async () => {
    // Ensure directory exists
    const dir = dirname(path);
    if (!existsSync(dir)) {
      await mkdir(dir, { recursive: true });
    }

    // Update timestamp
    data.updated = new Date().toISOString();

    // Write with pretty formatting
    await writeFile(path, JSON.stringify(data, null, 2), "utf-8");
  });
}

export async function readAllMemory(): Promise<Record<MemoryCategory, MemoryFile>> {
  const categories: MemoryCategory[] = [
    "user-preferences",
    "project-learnings",
    "decisions",
    "corrections",
    "patterns",
    "protocol-state"
  ];

  const result: Partial<Record<MemoryCategory, MemoryFile>> = {};

  // Read all categories in parallel (each has its own lock)
  await Promise.all(
    categories.map(async (category) => {
      result[category] = await readMemoryFile(category);
    })
  );

  return result as Record<MemoryCategory, MemoryFile>;
}

export function ensureMemoryDir(): void {
  const path = getMemoryPath();
  if (!existsSync(path)) {
    mkdirSync(path, { recursive: true });
  }
}

/**
 * Check if a memory file exists
 */
export function memoryFileExists(category: MemoryCategory): boolean {
  return existsSync(getCategoryPath(category));
}

/**
 * Get memory directory path
 */
export function getMemoryDir(): string {
  return getMemoryPath();
}
