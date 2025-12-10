/**
 * memory_read tool - Read entries from memory
 */
import type { MemoryCategory, MemoryEntry } from "../types/memory.js";
export interface ReadInput {
    category?: MemoryCategory;
    key?: string;
    limit?: number;
}
export interface ReadResult {
    success: boolean;
    data: Record<string, MemoryEntry[]> | MemoryEntry[] | MemoryEntry | null;
    message: string;
}
export declare function memoryRead(input: ReadInput): Promise<ReadResult>;
export declare function formatReadResult(result: ReadResult): string;
//# sourceMappingURL=read.d.ts.map