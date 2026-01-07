/**
 * memory_delete tool - Delete entries from memory (requires confirmation)
 */
import { READ_ONLY_CATEGORIES } from "../types/memory.js";
import { readMemoryFile, writeMemoryFile } from "../utils/file-ops.js";
export async function memoryDelete(input) {
    const { category, key, confirm } = input;
    // Check for read-only categories
    if (READ_ONLY_CATEGORIES.includes(category)) {
        return {
            success: false,
            message: `Category "${category}" is read-only and cannot be modified.`,
            requires_confirmation: false,
            deleted: false
        };
    }
    try {
        // Read existing file
        const file = await readMemoryFile(category);
        // Find the entry
        const existingIndex = file.entries.findIndex((e) => e.key === key);
        if (existingIndex < 0) {
            return {
                success: false,
                message: `No entry found with key "${key}" in ${category}`,
                requires_confirmation: false,
                deleted: false
            };
        }
        const entry = file.entries[existingIndex];
        // Require confirmation for deletion
        if (!confirm) {
            return {
                success: true,
                message: formatDeletionConfirmation(category, key, entry.value),
                requires_confirmation: true,
                deleted: false
            };
        }
        // Delete the entry
        file.entries.splice(existingIndex, 1);
        await writeMemoryFile(category, file);
        return {
            success: true,
            message: `Deleted "${key}" from ${category}`,
            requires_confirmation: false,
            deleted: true
        };
    }
    catch (error) {
        return {
            success: false,
            message: `Error deleting from memory: ${error instanceof Error ? error.message : String(error)}`,
            requires_confirmation: false,
            deleted: false
        };
    }
}
function formatDeletionConfirmation(category, key, value) {
    return [
        "Are you sure you want to delete this entry?",
        "",
        `Category: ${category}`,
        `Key: ${key}`,
        `Value: ${value}`,
        "",
        "To confirm deletion, call memory_delete again with confirm: true"
    ].join("\n");
}
export function formatDeleteResult(result) {
    if (result.requires_confirmation) {
        return result.message;
    }
    if (!result.success) {
        return `Error: ${result.message}`;
    }
    return result.message;
}
//# sourceMappingURL=delete.js.map