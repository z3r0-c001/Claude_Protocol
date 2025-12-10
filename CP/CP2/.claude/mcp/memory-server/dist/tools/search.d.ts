/**
 * memory_search tool - Search across memory categories
 */
import type { MemoryCategory } from "../types/memory.js";
import { type SearchResult } from "../utils/search.js";
export interface SearchInput {
    query: string;
    categories?: MemoryCategory[];
    fuzzy?: boolean;
    limit?: number;
}
export interface SearchResultOutput {
    success: boolean;
    results: SearchResult[];
    message: string;
}
export declare function memorySearch(input: SearchInput): Promise<SearchResultOutput>;
export declare function formatSearchResultOutput(result: SearchResultOutput): string;
//# sourceMappingURL=search.d.ts.map