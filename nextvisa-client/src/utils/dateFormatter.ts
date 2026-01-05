/**
 * Formats a date in the format "2026-1-8" to "January 1, 2026"
 * @param dateString - Date in the format YYYY-M-D or YYYY-MM-DD
 * @returns Formatted date as "Month Day, Year"
 */
export function formatDateOnly(dateString?: string): string {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  };
  return date.toLocaleDateString('en-US', options);
}

/**
 * Formats a date in the format "2026-1-8" to "January 1, 2026 12:00 PM"
 * @param dateString - Date in the format YYYY-M-D or YYYY-MM-DD
 * @returns Formatted date as "Month Day, Year"
 */
export function formatDate(dateString?: string): string {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
};