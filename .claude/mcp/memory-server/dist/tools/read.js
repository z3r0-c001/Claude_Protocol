/**
 * memory_read tool - Read entries from memory
 */
import { readMemoryFile, readAllMemory } from "../utils/file-ops.js";
export async function memoryRead(input) {
    const { category, key, limit = 50 } = input;
    try {
        // Read specific key from specific category
        if (category && key) {
            const file = await readMemoryFile(category);
            const entry = file.entries.find((e) => e.key === key);
            if (entry) {
                return {
                    success: true,
                    data: entry,
                    message: `Found entry "${key}" in ${category}`
                };
            }
            else {
                return {
                    success: true,
                    data: null,
                    message: `No entry found with key "${key}" in ${category}`
                };
            }
        }
        // Read all entries from specific category
        if (category) {
            const file = await readMemoryFile(category);
            const entries = file.entries.slice(0, limit);
            return {
                success: true,
                data: entries,
                message: `Found ${entries.length} entries in ${category}${file.entries.length > limit ? ` (showing first ${limit})` : ""}`
            };
        }
        // Read all categories
        const allMemory = await readAllMemory();
        const result = {};
        let totalCount = 0;
        for (const [cat, file] of Object.entries(allMemory)) {
            const entries = file.entries.slice(0, Math.floor(limit / 6));
            result[cat] = entries;
            totalCount += entries.length;
        }
        return {
            success: true,
            data: result,
            message: `Loaded ${totalCount} entries across all categories`
        };
    }
    catch (error) {
        return {
            success: false,
            data: null,
            message: `Error reading memory: ${error instanceof Error ? error.message : String(error)}`
        };
    }
}
export function formatReadResult(result) {
    if (!result.success) {
        return `Error: ${result.message}`;
    }
    if (result.data === null) {
        return result.message;
    }
    // Single entry
    if ("key" in result.data && "value" in result.data) {
        const entry = result.data;
        const lines = [
            `Key: ${entry.key}`,
            `Value: ${entry.value}`
        ];
        if (entry.reason)
            lines.push(`Reason: ${entry.reason}`);
        if (entry.timestamp)
            lines.push(`Recorded: ${entry.timestamp}`);
        return lines.join("\n");
    }
    // Array of entries
    if (Array.isArray(result.data)) {
        if (result.data.length === 0) {
            return "No entries found.";
        }
        const lines = result.data.map((entry) => {
            let line = `- ${entry.key}: ${entry.value}`;
            if (entry.reason)
                line += ` (${entry.reason})`;
            return line;
        });
        return `${result.message}\n\n${lines.join("\n")}`;
    }
    // Record of categories
    const lines = [result.message, ""];
    for (const [category, entries] of Object.entries(result.data)) {
        if (entries.length === 0)
            continue;
        lines.push(`## ${category}`);
        for (const entry of entries) {
            lines.push(`  - ${entry.key}: ${entry.value}`);
        }
        lines.push("");
    }
    return lines.join("\n");
}
//# sourceMappingURL=read.js.map