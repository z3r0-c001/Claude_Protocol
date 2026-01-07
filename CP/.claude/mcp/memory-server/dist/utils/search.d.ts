/**
 * Fuzzy search utilities for memory
 */
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
export declare function searchMemory(query: string, memoryData: Record<MemoryCategory, MemoryFile>, options?: SearchOptions): SearchResult[];
export declare function formatSearchResults(results: SearchResult[]): string;
//# sourceMappingURL=search.d.ts.map