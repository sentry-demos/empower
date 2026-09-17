import * as Sentry from '@sentry/angular';

export function getTag(tag: string): string | undefined {
  return (Sentry.getCurrentScope() as any)._tags?.[tag];
}

export function getSeTag(): string | undefined {
  return sessionStorage.getItem('se') || undefined;
}

/**
 * Get the customer type tag value
 * @returns The customer type or undefined if not set
 */
export function getCustomerTypeTag(): string | undefined {
  return sessionStorage.getItem('customerType') || undefined;
}

/**
 * Get the last error event ID from sessionStorage
 * @returns The last error event ID or undefined if not set
 */
export function getLastErrorEventId(): string | undefined {
  return sessionStorage.getItem('lastErrorEventId') || undefined;
}

/**
 * Check if SE tag is set
 * @returns True if SE tag is set, false otherwise
 */
export function hasSeTag(): boolean {
  return !!getSeTag();
}

/**
 * Check if SE tag starts with a specific prefix
 * @param prefix The prefix to check
 * @returns True if SE tag starts with the prefix, false otherwise
 */
export function seTagStartsWith(prefix: string): boolean {
  const se = getSeTag();
  return se ? se.startsWith(prefix) : false;
}
