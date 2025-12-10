/**
 * memory_prune tool - Clean up old memory entries
 */
export interface PruneInput {
    max_age_days?: number;
    max_entries?: number;
    dry_run?: boolean;
    confirm?: boolean;
}
export interface PruneResult {
    success: boolean;
    message: string;
    dry_run: boolean;
    requires_confirmation: boolean;
    pruned: Record<string, number>;
}
export declare function memoryPrune(input: PruneInput): Promise<PruneResult>;
export declare function formatPruneResult(result: PruneResult): string;
//# sourceMappingURL=prune.d.ts.map