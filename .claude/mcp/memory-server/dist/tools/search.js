/**
 * memory_search tool - Search across memory categories
 */
import { readAllMemory } from "../utils/file-ops.js";
import { searchMemory, formatSearchResults } from "../utils/search.js";
export async function memorySearch(input) {
    const { query, categories, fuzzy = true, limit = 20 } = input;
    if (!query || query.trim().length === 0) {
        return {
            success: false,
            results: [],
            message: "Search query cannot be empty"
        };
    }
    try {
        const allMemory = await readAllMemory();
        const results = searchMemory(query, allMemory, {
            categories,
            fuzzy,
            limit
        });
        return {
            success: true,
            results,
            message: results.length > 0
                ? `Found ${results.length} matching entries`
                : `No entries matching "${query}"`
        };
    }
    catch (error) {
        return {
            success: false,
            results: [],
            message: `Error searching memory: ${error instanceof Error ? error.message : String(error)}`
        };
    }
}
export function formatSearchResultOutput(result) {
    if (!result.success) {
        return `Error: ${result.message}`;
    }
    return formatSearchResults(result.results);
}
//# sourceMappingURL=search.js.map