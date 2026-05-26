// src/lib/stores/auth.ts
// Estado do usuario logado + JWT

import { browser } from '$app/environment';
import { AuthDTO } from '$lib/dtos/AuthDTO';

const AUTH_KEY = 'kanban_auth';

function loadFromStorage(): AuthDTO | null {
  if (!browser) return null;
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    if (!raw) return null;
    const dto = new AuthDTO(JSON.parse(raw));
    return dto.isValid() ? dto : null;
  } catch {
    return null;
  }
}

let currentAuth = $state<AuthDTO | null>(loadFromStorage());

export function getAuth(): AuthDTO | null {
  return currentAuth;
}

export function setAuth(auth: AuthDTO): void {
  currentAuth = auth;
  if (browser) {
    localStorage.setItem(AUTH_KEY, JSON.stringify(auth.toPayload()));
  }
}

export function clearAuth(): void {
  currentAuth = null;
  if (browser) {
    localStorage.removeItem(AUTH_KEY);
  }
}

export function isLoggedIn(): boolean {
  return currentAuth !== null && currentAuth.isValid();
}

export function getToken(): string {
  return currentAuth?.token ?? '';
}
