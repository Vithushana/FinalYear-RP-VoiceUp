/**
 * Get initials from a name
 * @param name - Full name (e.g., "Ranjan R" or "John Doe")
 * @returns Initials (e.g., "RR" or "JD")
 */
export const getInitials = (name: string): string => {
    if (!name) return "U";

    const words = name.trim().split(/\s+/);

    if (words.length === 1) {
        // Single word: take first 2 letters
        return words[0].slice(0, 2).toUpperCase();
    }

    // Multiple words: take first letter of each word (max 2)
    return words
        .slice(0, 2)
        .map(word => word[0])
        .join("")
        .toUpperCase();
};
