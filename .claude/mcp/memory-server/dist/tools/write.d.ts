/**
 * memory_write tool - Write entries to memory
 * Auto-saves for learnings, asks permission for decisions
 */
import type { MemoryCategory } from "../types/memory.js";
export interface WriteInput {
    category: MemoryCategory;
    key: string;
    value: string;
    reason?: string;
    context?: string;
    metadata?: Record<string, unknown>;
    confirm?: boolean;
}
export interface WriteResult {
    success: boolean;
    message: string;
    requires_permission: boolean;
    saved: boolean;
}
export declare function memoryWrite(input: WriteInput): Promise<WriteResult>;
export declare function formatWriteResult(result: WriteResult): string;
//# sourceMappingURL=write.d.ts.map