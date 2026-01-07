/**
 * Memory entry types for Claude Bootstrap Protocol
 * Includes Zod schemas for runtime validation
 */
import { z } from "zod";
export declare const MemoryCategorySchema: z.ZodEnum<["user-preferences", "project-learnings", "decisions", "corrections", "patterns", "protocol-state"]>;
export declare const MemoryEntrySchema: z.ZodObject<{
    key: z.ZodString;
    value: z.ZodString;
    timestamp: z.ZodString;
    reason: z.ZodOptional<z.ZodString>;
    context: z.ZodOptional<z.ZodString>;
    metadata: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
}, "strip", z.ZodTypeAny, {
    key: string;
    value: string;
    timestamp: string;
    reason?: string | undefined;
    context?: string | undefined;
    metadata?: Record<string, unknown> | undefined;
}, {
    key: string;
    value: string;
    timestamp: string;
    reason?: string | undefined;
    context?: string | undefined;
    metadata?: Record<string, unknown> | undefined;
}>;
export declare const MemoryFileSchema: z.ZodObject<{
    entries: z.ZodArray<z.ZodObject<{
        key: z.ZodString;
        value: z.ZodString;
        timestamp: z.ZodString;
        reason: z.ZodOptional<z.ZodString>;
        context: z.ZodOptional<z.ZodString>;
        metadata: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    }, "strip", z.ZodTypeAny, {
        key: string;
        value: string;
        timestamp: string;
        reason?: string | undefined;
        context?: string | undefined;
        metadata?: Record<string, unknown> | undefined;
    }, {
        key: string;
        value: string;
        timestamp: string;
        reason?: string | undefined;
        context?: string | undefined;
        metadata?: Record<string, unknown> | undefined;
    }>, "many">;
    updated: z.ZodNullable<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    entries: {
        key: string;
        value: string;
        timestamp: string;
        reason?: string | undefined;
        context?: string | undefined;
        metadata?: Record<string, unknown> | undefined;
    }[];
    updated: string | null;
}, {
    entries: {
        key: string;
        value: string;
        timestamp: string;
        reason?: string | undefined;
        context?: string | undefined;
        metadata?: Record<string, unknown> | undefined;
    }[];
    updated: string | null;
}>;
export declare const CorrectionEntrySchema: z.ZodObject<{
    key: z.ZodString;
    value: z.ZodString;
    timestamp: z.ZodString;
    reason: z.ZodOptional<z.ZodString>;
    context: z.ZodOptional<z.ZodString>;
    metadata: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
} & {
    wrong: z.ZodString;
    correct: z.ZodString;
}, "strip", z.ZodTypeAny, {
    key: string;
    value: string;
    timestamp: string;
    wrong: string;
    correct: string;
    reason?: string | undefined;
    context?: string | undefined;
    metadata?: Record<string, unknown> | undefined;
}, {
    key: string;
    value: string;
    timestamp: string;
    wrong: string;
    correct: string;
    reason?: string | undefined;
    context?: string | undefined;
    metadata?: Record<string, unknown> | undefined;
}>;
export declare const PatternEntrySchema: z.ZodObject<{
    key: z.ZodString;
    value: z.ZodString;
    timestamp: z.ZodString;
    reason: z.ZodOptional<z.ZodString>;
    context: z.ZodOptional<z.ZodString>;
    metadata: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
} & {
    frequency: z.ZodNumber;
    files: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    key: string;
    value: string;
    timestamp: string;
    frequency: number;
    reason?: string | undefined;
    context?: string | undefined;
    metadata?: Record<string, unknown> | undefined;
    files?: string[] | undefined;
}, {
    key: string;
    value: string;
    timestamp: string;
    frequency: number;
    reason?: string | undefined;
    context?: string | undefined;
    metadata?: Record<string, unknown> | undefined;
    files?: string[] | undefined;
}>;
export declare const DecisionEntrySchema: z.ZodObject<{
    key: z.ZodString;
    value: z.ZodString;
    timestamp: z.ZodString;
    reason: z.ZodOptional<z.ZodString>;
    context: z.ZodOptional<z.ZodString>;
    metadata: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
} & {
    alternatives_considered: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    key: string;
    value: string;
    timestamp: string;
    reason?: string | undefined;
    context?: string | undefined;
    metadata?: Record<string, unknown> | undefined;
    alternatives_considered?: string[] | undefined;
}, {
    key: string;
    value: string;
    timestamp: string;
    reason?: string | undefined;
    context?: string | undefined;
    metadata?: Record<string, unknown> | undefined;
    alternatives_considered?: string[] | undefined;
}>;
export declare const ProtocolStateSchema: z.ZodObject<{
    initialized: z.ZodBoolean;
    initialized_at: z.ZodNullable<z.ZodString>;
    discovery_complete: z.ZodBoolean;
    generation_complete: z.ZodBoolean;
    bootstrap_complete: z.ZodBoolean;
    validation_complete: z.ZodBoolean;
    project: z.ZodObject<{
        name: z.ZodNullable<z.ZodString>;
        description: z.ZodNullable<z.ZodString>;
        type: z.ZodNullable<z.ZodString>;
        languages: z.ZodArray<z.ZodString, "many">;
        frameworks: z.ZodArray<z.ZodString, "many">;
        build_command: z.ZodNullable<z.ZodString>;
        test_command: z.ZodNullable<z.ZodString>;
        lint_command: z.ZodNullable<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        type: string | null;
        name: string | null;
        description: string | null;
        languages: string[];
        frameworks: string[];
        build_command: string | null;
        test_command: string | null;
        lint_command: string | null;
    }, {
        type: string | null;
        name: string | null;
        description: string | null;
        languages: string[];
        frameworks: string[];
        build_command: string | null;
        test_command: string | null;
        lint_command: string | null;
    }>;
    components: z.ZodObject<{
        slash_commands: z.ZodNumber;
        agents: z.ZodNumber;
        skills: z.ZodNumber;
        scripts: z.ZodNumber;
    }, "strip", z.ZodTypeAny, {
        slash_commands: number;
        agents: number;
        skills: number;
        scripts: number;
    }, {
        slash_commands: number;
        agents: number;
        skills: number;
        scripts: number;
    }>;
    user_preferences: z.ZodObject<{
        skill_level: z.ZodString;
        verbosity: z.ZodString;
        primary_goal: z.ZodString;
        protected_paths: z.ZodArray<z.ZodString, "many">;
        validation_level: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        skill_level: string;
        verbosity: string;
        primary_goal: string;
        protected_paths: string[];
        validation_level: string;
    }, {
        skill_level: string;
        verbosity: string;
        primary_goal: string;
        protected_paths: string[];
        validation_level: string;
    }>;
    generated_files: z.ZodArray<z.ZodString, "many">;
    validation_results: z.ZodArray<z.ZodObject<{
        check: z.ZodString;
        status: z.ZodString;
        note: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        status: string;
        check: string;
        note?: string | undefined;
    }, {
        status: string;
        check: string;
        note?: string | undefined;
    }>, "many">;
    errors: z.ZodArray<z.ZodString, "many">;
}, "strip", z.ZodTypeAny, {
    initialized: boolean;
    initialized_at: string | null;
    discovery_complete: boolean;
    generation_complete: boolean;
    bootstrap_complete: boolean;
    validation_complete: boolean;
    project: {
        type: string | null;
        name: string | null;
        description: string | null;
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
    validation_results: {
        status: string;
        check: string;
        note?: string | undefined;
    }[];
    errors: string[];
}, {
    initialized: boolean;
    initialized_at: string | null;
    discovery_complete: boolean;
    generation_complete: boolean;
    bootstrap_complete: boolean;
    validation_complete: boolean;
    project: {
        type: string | null;
        name: string | null;
        description: string | null;
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
    validation_results: {
        status: string;
        check: string;
        note?: string | undefined;
    }[];
    errors: string[];
}>;
export type MemoryCategory = z.infer<typeof MemoryCategorySchema>;
export type MemoryEntry = z.infer<typeof MemoryEntrySchema>;
export type MemoryFile = z.infer<typeof MemoryFileSchema>;
export type CorrectionEntry = z.infer<typeof CorrectionEntrySchema>;
export type PatternEntry = z.infer<typeof PatternEntrySchema>;
export type DecisionEntry = z.infer<typeof DecisionEntrySchema>;
export type ProtocolState = z.infer<typeof ProtocolStateSchema>;
export declare const AUTO_SAVE_CATEGORIES: MemoryCategory[];
export declare const PERMISSION_REQUIRED_CATEGORIES: MemoryCategory[];
export declare const READ_ONLY_CATEGORIES: MemoryCategory[];
export declare const WRITABLE_CATEGORIES: MemoryCategory[];
/**
 * Validate a memory file structure
 * Returns validated data or throws ZodError
 */
export declare function validateMemoryFile(data: unknown): MemoryFile;
/**
 * Safely validate a memory file, returning default on failure
 */
export declare function safeValidateMemoryFile(data: unknown): MemoryFile;
/**
 * Validate a single memory entry
 */
export declare function validateMemoryEntry(data: unknown): MemoryEntry;
//# sourceMappingURL=memory.d.ts.map