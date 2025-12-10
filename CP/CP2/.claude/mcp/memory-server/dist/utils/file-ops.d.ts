/**
 * File operations for memory persistence with basic locking
 */
import type { MemoryFile, MemoryCategory } from "../types/memory.js";
export declare function readMemoryFile(category: MemoryCategory): Promise<MemoryFile>;
export declare function writeMemoryFile(category: MemoryCategory, data: MemoryFile): Promise<void>;
export declare function readAllMemory(): Promise<Record<MemoryCategory, MemoryFile>>;
export declare function ensureMemoryDir(): void;
//# sourceMappingURL=file-ops.d.ts.map