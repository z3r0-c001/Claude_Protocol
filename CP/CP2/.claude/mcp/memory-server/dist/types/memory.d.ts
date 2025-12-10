/**
 * Memory entry types for Claude Bootstrap Protocol
 */
export type MemoryCategory = "user-preferences" | "project-learnings" | "decisions" | "corrections" | "patterns" | "protocol-state";
export interface MemoryEntry {
    key: string;
    value: string;
    timestamp: string;
    reason?: string;
    context?: string;
    metadata?: Record<string, unknown>;
}
export interface CorrectionEntry extends MemoryEntry {
    wrong: string;
    correct: string;
}
export interface PatternEntry extends MemoryEntry {
    frequency: number;
    files?: string[];
}
export interface DecisionEntry extends MemoryEntry {
    alternatives_considered?: string[];
}
export interface MemoryFile {
    entries: MemoryEntry[];
    updated: string | null;
}
export interface ProtocolState {
    initialized: boolean;
    initialized_at: string | null;
    discovery_complete: boolean;
    generation_complete: boolean;
    bootstrap_complete: boolean;
    validation_complete: boolean;
    project: {
        name: string | null;
        description: string | null;
        type: string | null;
        languages: string[];
        frameworks: string[];
        build_command: string | null;
        test_command: string | null;
        lint_command: string | null;
    };
    components: {
        slash_commands: number;
        agents: number;
        skills: number;
        scripts: number;
    };
    user_preferences: {
        skill_level: string;
        verbosity: string;
        primary_goal: string;
        protected_paths: string[];
        validation_level: string;
    };
    generated_files: string[];
    validation_results: Array<{
        check: string;
        status: string;
        note?: string;
    }>;
    errors: string[];
}
export declare const AUTO_SAVE_CATEGORIES: MemoryCategory[];
export declare const PERMISSION_REQUIRED_CATEGORIES: MemoryCategory[];
export declare const READ_ONLY_CATEGORIES: MemoryCategory[];
//# sourceMappingURL=memory.d.ts.map