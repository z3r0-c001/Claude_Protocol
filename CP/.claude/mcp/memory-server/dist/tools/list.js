/**
 * memory_list tool - List memory entries with summaries
 */
import { readMemoryFile, readAllMemory } from "../utils/file-ops.js";
function truncate(str, maxLength = 50) {
    if (str.length <= maxLength)
        return str;
    return str.slice(0, maxLength - 3) + "...";
}
export async function memoryList(input) {
    const { category, include_timestamps = false } = input;
    try {
        if (category) {
            const file = await readMemoryFile(category);
            const entries = file.entries.map((entry) => ({
                key: entry.key,
                preview: truncate(entry.value),
                ...(include_timestamps && entry.timestamp ? { timestamp: entry.timestamp } : {})
            }));
            return {
                success: true,
                data: entries,
                message: `${category}: ${entries.length} entries`
            };
        }
        // List all categories
        const allMemory = await readAllMemory();
        const result = {};
        let totalCount = 0;
        for (const [cat, file] of Object.entries(allMemory)) {
            const entries = file.entries.map((entry) => ({
                key: entry.key,
                preview: truncate(entry.value),
                ...(include_timestamps && entry.timestamp ? { timestamp: entry.timestamp } : {})
            }));
            result[cat] = entries;
            totalCount += entries.length;
        }
        return {
            success: true,
            data: result,
            message: `Total: ${totalCount} entries across ${Object.keys(result).length} categories`
        };
    }
    catch (error) {
        return {
            success: false,
            data: [],
            message: `Error listing memory: ${error instanceof Error ? error.message : String(error)}`
        };
    }
}
export function formatListResult(result) {
    if (!result.success) {
        return `Error: ${result.message}`;
    }
    const lines = [result.message, ""];
    if (Array.isArray(result.data)) {
        // Single category
        for (const entry of result.data) {
            let line = `- ${entry.key}: ${entry.preview}`;
            if (entry.timestamp)
                line += ` (${entry.timestamp})`;
            lines.push(line);
        }
    }
    else {
        // All categories
        for (const [category, entries] of Object.entries(result.data)) {
            if (entries.length === 0)
                continue;
            lines.push(`## ${category} (${entries.length})`);
            for (const entry of entries) {
                let line = `  - ${entry.key}: ${entry.preview}`;
                if (entry.timestamp)
                    line += ` (${entry.timestamp})`;
                lines.push(line);
            }
            lines.push("");
        }
    }
    return lines.join("\n");
}
//# sourceMappingURL=list.js.map