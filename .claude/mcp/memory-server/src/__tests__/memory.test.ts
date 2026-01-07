/**
 * Tests for memory server functionality
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { rmSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

// Set test memory path before imports
const TEST_MEMORY_PATH = join(process.cwd(), '.test-memory');
process.env.MEMORY_PATH = TEST_MEMORY_PATH;

import { readMemoryFile, writeMemoryFile, readAllMemory } from '../utils/file-ops.js';
import { searchMemory } from '../utils/search.js';
import type { MemoryFile, MemoryCategory } from '../types/memory.js';

describe('Memory File Operations', () => {
  beforeEach(() => {
    // Clean up test directory
    if (existsSync(TEST_MEMORY_PATH)) {
      rmSync(TEST_MEMORY_PATH, { recursive: true });
    }
    mkdirSync(TEST_MEMORY_PATH, { recursive: true });
  });

  afterEach(() => {
    // Clean up after tests
    if (existsSync(TEST_MEMORY_PATH)) {
      rmSync(TEST_MEMORY_PATH, { recursive: true });
    }
  });

  describe('readMemoryFile', () => {
    it('returns empty file for non-existent category', async () => {
      const result = await readMemoryFile('user-preferences');
      expect(result).toEqual({ entries: [], updated: null });
    });

    it('reads existing memory file', async () => {
      const testData: MemoryFile = {
        entries: [
          {
            key: 'test-key',
            value: 'test-value',
            timestamp: new Date().toISOString()
          }
        ],
        updated: new Date().toISOString()
      };

      await writeMemoryFile('user-preferences', testData);
      const result = await readMemoryFile('user-preferences');

      expect(result.entries).toHaveLength(1);
      expect(result.entries[0].key).toBe('test-key');
    });
  });

  describe('writeMemoryFile', () => {
    it('creates memory file with entries', async () => {
      const testData: MemoryFile = {
        entries: [
          {
            key: 'pref-1',
            value: 'value-1',
            timestamp: new Date().toISOString(),
            reason: 'test reason'
          }
        ],
        updated: null
      };

      await writeMemoryFile('project-learnings', testData);
      const result = await readMemoryFile('project-learnings');

      expect(result.entries).toHaveLength(1);
      expect(result.updated).not.toBeNull();
    });

    it('overwrites existing entries', async () => {
      const initial: MemoryFile = {
        entries: [{ key: 'a', value: '1', timestamp: new Date().toISOString() }],
        updated: null
      };

      const updated: MemoryFile = {
        entries: [
          { key: 'a', value: '2', timestamp: new Date().toISOString() },
          { key: 'b', value: '3', timestamp: new Date().toISOString() }
        ],
        updated: null
      };

      await writeMemoryFile('corrections', initial);
      await writeMemoryFile('corrections', updated);

      const result = await readMemoryFile('corrections');
      expect(result.entries).toHaveLength(2);
      expect(result.entries[0].value).toBe('2');
    });
  });

  describe('readAllMemory', () => {
    it('reads all categories', async () => {
      const result = await readAllMemory();

      expect(result).toHaveProperty('user-preferences');
      expect(result).toHaveProperty('project-learnings');
      expect(result).toHaveProperty('decisions');
      expect(result).toHaveProperty('corrections');
      expect(result).toHaveProperty('patterns');
      expect(result).toHaveProperty('protocol-state');
    });
  });
});

describe('Memory Search', () => {
  const testMemory: Record<MemoryCategory, MemoryFile> = {
    'user-preferences': {
      entries: [
        { key: 'verbosity', value: 'concise', timestamp: new Date().toISOString() },
        { key: 'skill-level', value: 'expert', timestamp: new Date().toISOString() }
      ],
      updated: new Date().toISOString()
    },
    'project-learnings': {
      entries: [
        { key: 'typescript-config', value: 'Use strict mode', timestamp: new Date().toISOString(), reason: 'Better type safety' },
        { key: 'testing-approach', value: 'Jest with coverage', timestamp: new Date().toISOString() }
      ],
      updated: new Date().toISOString()
    },
    'decisions': { entries: [], updated: null },
    'corrections': { entries: [], updated: null },
    'patterns': { entries: [], updated: null },
    'protocol-state': { entries: [], updated: null }
  };

  describe('searchMemory', () => {
    it('finds exact matches', () => {
      const results = searchMemory('typescript', testMemory, { fuzzy: false });
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].entry.key).toBe('typescript-config');
    });

    it('finds fuzzy matches', () => {
      const results = searchMemory('typscript', testMemory, { fuzzy: true, threshold: 0.6 });
      expect(results.length).toBeGreaterThan(0);
    });

    it('respects category filter', () => {
      const results = searchMemory('expert', testMemory, { 
        categories: ['user-preferences'],
        fuzzy: false 
      });
      expect(results.length).toBe(1);
      expect(results[0].category).toBe('user-preferences');
    });

    it('respects limit', () => {
      const results = searchMemory('e', testMemory, { limit: 2, fuzzy: false });
      expect(results.length).toBeLessThanOrEqual(2);
    });

    it('returns empty for no matches', () => {
      const results = searchMemory('xyznonexistent', testMemory, { fuzzy: false });
      expect(results).toHaveLength(0);
    });
  });
});
