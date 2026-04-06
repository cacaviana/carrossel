import { browser } from '$app/environment';
export const API_BASE = browser
  ? (import.meta.env.VITE_API_URL || 'http://localhost:8000')
  : 'http://localhost:8000';
