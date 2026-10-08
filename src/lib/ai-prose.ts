/** Render cached AI prose as plain text without exposing source links. */
export function aiProse(value: string): string {
  return value
    .replace(/^\s*\[[^\]]+\]:\s*(?:https?:\/\/|www\.)[^\n]*$/gm, "")
    .replace(/!?\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\)/g, "$1")
    .replace(/\[([^\]]+)\]\[[^\]]*\]/g, "$1")
    .replace(/<a\b[^>]*>([\s\S]*?)<\/a>/gi, "$1")
    .replace(/<(?:https?:\/\/|www\.)[^>]+>/gi, "")
    .replace(/(?:https?:\/\/|www\.)[^\s<>]+/gi, "")
    .replace(/\[(?:sectors|source|news|ihsg)-[^\]]+\]/gi, "")
    .replace(/[ \t]+/g, " ")
    .trim();
}
