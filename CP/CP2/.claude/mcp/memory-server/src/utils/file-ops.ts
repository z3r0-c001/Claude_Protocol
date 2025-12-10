/**
 * File operations for memory persistence with basic locking
 */

import { readFile, writeFile, mkdir } from "fs/promises";
import { existsSync } from "fs";
import { dirname } from "path";
import type { MemoryFile, MemoryCategory } from "../types/memory.js";

// Simple in-memory lock to prevent concurrent writes
const locks = new Map<string, Promise<void>>();

async function acquireLock(key: string): Promise<() => void> {
  while (locks.has(key)) {
    await locks.get(key);
  }

  let release: () => void;
  const lockPromise = new Promise<void>((resolve) => {
    release = resolve;
  });

  locks.set(key, lockPromise);

  return () => {
    locks.delete(key);
    release!();
  };
}

function getMemoryPath(): string {
  return process.env.MEMORY_PATH || ".claude/memory";
}

function getCategoryPath(category: MemoryCategory): string {
  return `${getMemoryPath()}/${category}.json`;
}

export async function readMemoryFile(category: MemoryCategory): Promise<MemoryFile> {
  const path = getCategoryPath(category);
  const release = await acquireLock(category);

  try {
    if (!existsSync(path)) {
      return { entries: [], updated: null };
    }

    const content = await readFile(path, "utf-8");
    const parsed = JSON.parse(content);

    // Handle both old format (entries array) and new format
    if (Array.isArray(parsed)) {
      return { entries: parsed, updated: null };
    }

    return parsed as MemoryFile;
  } catch (error) {
    // Return empty file on parse error
    return { entries: [], updated: null };
  } finally {
    release();
  }
}

export async function writeMemoryFile(
  category: MemoryCategory,
  data: MemoryFile
): Promise<void> {
  const path = getCategoryPath(category);
  const release = await acquireLock(category);

  try {
    // Ensure directory exists
    const dir = dirname(path);
    if (!existsSync(dir)) {
      await mkdir(dir, { recursive: true });
    }

    // Update timestamp
    data.updated = new Date().toISOString();

    // Write with pretty formatting
    await writeFile(path, JSON.stringify(data, null, 2), "utf-8");
  } finally {
    release();
  }
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
    // Sync version for initialization
    require("fs").mkdirSync(path, { recursive: true });
  }
}
