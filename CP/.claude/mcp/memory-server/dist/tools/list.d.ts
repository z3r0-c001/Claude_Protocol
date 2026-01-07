/**
 * memory_list tool - List memory entries with summaries
 */
import type { MemoryCategory } from "../types/memory.js";
export interface ListInput {
    category?: MemoryCategory;
    include_timestamps?: boolean;
}
export interface ListEntry {
    key: string;
    preview: string;
    timestamp?: string;
}
export interface ListResult {
    success: boolean;
    data: Record<string, ListEntry[]> | ListEntry[];
    message: string;
}
export declare function memoryList(input: ListInput): Promise<ListResult>;
export declare function formatListResult(result: ListResult): string;
//# sourceMappingURL=list.d.ts.map