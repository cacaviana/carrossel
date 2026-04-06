export function isValidHex(value: string): boolean {
  return /^#[0-9A-Fa-f]{6}$/.test(value);
}

export function isValidUrl(value: string): boolean {
  try {
    new URL(value);
    return true;
  } catch {
    return false;
  }
}

export function isMinLength(value: string, min: number): boolean {
  return value.trim().length >= min;
}

export function isNotEmpty(value: string): boolean {
  return value.trim().length > 0;
}
