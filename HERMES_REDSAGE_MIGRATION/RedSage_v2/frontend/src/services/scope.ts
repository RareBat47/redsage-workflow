/**
 * Client-side mirror of backend/services/scope_validator.py matching rules.
 * Keep the two in sync. The backend remains the authority (it enforces the
 * 422s); this only drives target-picker UX so we never send a target the
 * server would reject.
 */

const normalize = (value: string): string => value.trim().toLowerCase().replace(/\.+$/, '');

export function targetMatchesScopeEntry(target: string, entry: string): boolean {
  const normalizedTarget = normalize(target);
  const normalizedEntry = normalize(entry);
  if (!normalizedTarget || !normalizedEntry || normalizedTarget.startsWith('*.')) return false;
  if (normalizedEntry.startsWith('*.')) {
    const suffix = normalizedEntry.slice(2);
    return normalizedTarget === suffix || normalizedTarget.endsWith(`.${suffix}`);
  }
  // IP/CIDR membership is enforced server-side; exact matching is enough for
  // picker stickiness.
  return normalizedTarget === normalizedEntry;
}

export function targetMatchesWhitelist(target: string, whitelist: string[]): boolean {
  return whitelist.some((entry) => targetMatchesScopeEntry(target, entry));
}

/** First entry usable as a concrete command target ('' when only wildcards exist). */
export function defaultScopeTarget(whitelist: string[]): string {
  return whitelist.find((entry) => entry.trim() && !entry.trim().startsWith('*.')) ?? '';
}
