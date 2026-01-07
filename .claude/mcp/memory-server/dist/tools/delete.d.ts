/**
 * memory_delete tool - Delete entries from memory (requires confirmation)
 */
import type { MemoryCategory } from "../types/memory.js";
export interface DeleteInput {
    category: MemoryCategory;
    key: string;
    confirm: boolean;
}
export interface DeleteResult {
    success: boolean;
    message: string;
    requires_confirmation: boolean;
    deleted: boolean;
}
export declare function memoryDelete(input: DeleteInput): Promise<DeleteResult>;
export declare function formatDeleteResult(result: DeleteResult): string;
//# sourceMappingURL=delete.d.ts.map