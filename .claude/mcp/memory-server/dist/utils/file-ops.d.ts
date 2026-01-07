/**
 * File operations for memory persistence with proper file locking
 */
import type { MemoryFile, MemoryCategory } from "../types/memory.js";
export declare function readMemoryFile(category: MemoryCategory): Promise<MemoryFile>;
export declare function writeMemoryFile(category: MemoryCategory, data: MemoryFile): Promise<void>;
export declare function readAllMemory(): Promise<Record<MemoryCategory, MemoryFile>>;
export declare function ensureMemoryDir(): void;
/**
 * Check if a memory file exists
 */
export declare function memoryFileExists(category: MemoryCategory): boolean;
/**
 * Get memory directory path
 */
export declare function getMemoryDir(): string;
//# sourceMappingURL=file-ops.d.ts.map