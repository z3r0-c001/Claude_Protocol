/**
 * Memory entry types for Claude Bootstrap Protocol
 * Includes Zod schemas for runtime validation
 */
import { z } from "zod";
// Zod schemas for validation
export const MemoryCategorySchema = z.enum([
    "user-preferences",
    "project-learnings",
    "decisions",
    "corrections",
    "patterns",
    "protocol-state"
]);
export const MemoryEntrySchema = z.object({
    key: z.string().min(1, "Key cannot be empty"),
    value: z.string(),
    timestamp: z.string().datetime({ message: "Invalid timestamp format" }),
    reason: z.string().optional(),
    context: z.string().optional(),
    metadata: z.record(z.unknown()).optional()
});
export const MemoryFileSchema = z.object({
    entries: z.array(MemoryEntrySchema),
    updated: z.string().datetime().nullable()
});
export const CorrectionEntrySchema = MemoryEntrySchema.extend({
    wrong: z.string(),
    correct: z.string()
});
export const PatternEntrySchema = MemoryEntrySchema.extend({
    frequency: z.number().int().min(0),
    files: z.array(z.string()).optional()
});
export const DecisionEntrySchema = MemoryEntrySchema.extend({
    alternatives_considered: z.array(z.string()).optional()
});
export const ProtocolStateSchema = z.object({
    initialized: z.boolean(),
    initialized_at: z.string().datetime().nullable(),
    discovery_complete: z.boolean(),
    generation_complete: z.boolean(),
    bootstrap_complete: z.boolean(),
    validation_complete: z.boolean(),
    project: z.object({
        name: z.string().nullable(),
        description: z.string().nullable(),
        type: z.string().nullable(),
        languages: z.array(z.string()),
        frameworks: z.array(z.string()),
        build_command: z.string().nullable(),
        test_command: z.string().nullable(),
        lint_command: z.string().nullable()
    }),
    components: z.object({
        slash_commands: z.number().int().min(0),
        agents: z.number().int().min(0),
        skills: z.number().int().min(0),
        scripts: z.number().int().min(0)
    }),
    user_preferences: z.object({
        skill_level: z.string(),
        verbosity: z.string(),
        primary_goal: z.string(),
        protected_paths: z.array(z.string()),
        validation_level: z.string()
    }),
    generated_files: z.array(z.string()),
    validation_results: z.array(z.object({
        check: z.string(),
        status: z.string(),
        note: z.string().optional()
    })),
    errors: z.array(z.string())
});
// Categories that auto-save without permission
export const AUTO_SAVE_CATEGORIES = [
    "user-preferences",
    "project-learnings",
    "corrections",
    "patterns"
];
// Categories that require explicit permission
export const PERMISSION_REQUIRED_CATEGORIES = [
    "decisions"
];
// Read-only categories (managed by protocol, not user)
export const READ_ONLY_CATEGORIES = [
    "protocol-state"
];
// All writable categories (for tool enum validation)
export const WRITABLE_CATEGORIES = [
    "user-preferences",
    "project-learnings",
    "decisions",
    "corrections",
    "patterns"
];
/**
 * Validate a memory file structure
 * Returns validated data or throws ZodError
 */
export function validateMemoryFile(data) {
    return MemoryFileSchema.parse(data);
}
/**
 * Safely validate a memory file, returning default on failure
 */
export function safeValidateMemoryFile(data) {
    const result = MemoryFileSchema.safeParse(data);
    if (result.success) {
        return result.data;
    }
    console.error("Memory file validation failed:", result.error.message);
    return { entries: [], updated: null };
}
/**
 * Validate a single memory entry
 */
export function validateMemoryEntry(data) {
    return MemoryEntrySchema.parse(data);
}
//# sourceMappingURL=memory.js.map