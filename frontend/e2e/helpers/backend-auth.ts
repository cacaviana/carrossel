import { expect, type Page, type APIRequestContext, request } from '@playwright/test';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

/**
 * Helper de auth que faz login REAL contra o backend (JWT verdadeiro).
 * Usado pelas specs novas pos-C1/C2 (JWT obrigatorio).
 *
 * Pre-condicao: backend UP em localhost:8000 com MongoDB configurado
 * e usuario 'e2e-test@itvalley.com' com senha 'Admin@123' criado.
 */

const BACKEND_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:5173';

export const TEST_USER_A = {
  email: 'e2e-test@itvalley.com',
  password: 'Admin@123',
  tenant_id: 'itvalley-dev',
};

// Cache de tokens compartilhado entre workers via filesystem
const CACHE_DIR = join(tmpdir(), 'carrossel-e2e-auth-cache');
if (!existsSync(CACHE_DIR)) mkdirSync(CACHE_DIR, { recursive: true });

function cacheFile(email: string): string {
  const safe = email.replace(/[^a-z0-9]/gi, '_');
  return join(CACHE_DIR, `${safe}.json`);
}

function readCache(email: string): { token: string; authPayload: any } | null {
  try {
    const path = cacheFile(email);
    if (!existsSync(path)) return null;
    const raw = JSON.parse(readFileSync(path, 'utf-8'));
    if (raw.expiresAt < Date.now()) return null;
    return { token: raw.token, authPayload: raw.authPayload };
  } catch {
    return null;
  }
}

function writeCache(email: string, token: string, authPayload: any) {
  try {
    writeFileSync(cacheFile(email), JSON.stringify({
      token,
      authPayload,
      expiresAt: Date.now() + 20 * 60 * 1000,
    }));
  } catch {}
}

/**
 * Faz login real no backend e retorna { token, authPayload }.
 * Cacheia token por 20 minutos via filesystem (compartilhado entre workers).
 * NAO mexe na Page — util pra chamadas API puras.
 */
export async function loginBackend(email: string = TEST_USER_A.email, password: string = TEST_USER_A.password) {
  const cached = readCache(email);
  if (cached) return cached;

  const apiContext = await request.newContext({ baseURL: BACKEND_URL });
  let lastErr = '';
  // Retry em caso de 429 (rate limit) com backoff + jitter
  for (let i = 0; i < 5; i++) {
    const res = await apiContext.post('/api/auth/login', {
      data: { email, password },
    });
    if (res.ok()) {
      const data = await res.json();
      await apiContext.dispose();
      const authPayload = {
        token: data.access_token,
        user_id: data.user_id,
        tenant_id: data.tenant_id,
        email: data.email,
        name: data.name,
        role: data.role,
        avatar_url: data.avatar_url ?? '',
      };
      writeCache(email, data.access_token, authPayload);
      return { token: data.access_token, authPayload };
    }
    lastErr = `${res.status()}: ${await res.text()}`;
    if (res.status() === 429) {
      // Recheck cache — talvez outro worker ja conseguiu
      const recheck = readCache(email);
      if (recheck) {
        await apiContext.dispose();
        return recheck;
      }
      // Backoff com jitter
      const wait = 10000 + Math.random() * 10000;
      await new Promise(r => setTimeout(r, wait));
      continue;
    }
    break;
  }
  await apiContext.dispose();
  throw new Error(`Login falhou: ${lastErr}`);
}

/**
 * Login real + injeta JWT no localStorage do frontend.
 * Frontend le kanban_auth do localStorage no onMount (auth.svelte.ts).
 */
export async function loginReal(page: Page, email?: string, password?: string) {
  const { authPayload } = await loginBackend(email, password);

  // Vai pra home pra ter document disponivel, dai injeta no localStorage
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await page.evaluate((auth) => {
    localStorage.setItem('kanban_auth', JSON.stringify(auth));
  }, authPayload);

  return authPayload;
}

/**
 * Limpa localStorage antes de cada teste.
 */
export async function logout(page: Page) {
  await page.goto('/', { waitUntil: 'commit' });
  await page.evaluate(() => localStorage.removeItem('kanban_auth'));
}

/**
 * Cria JWT direto via API (sem UI) pra qualquer tenant.
 * Permite testar isolamento multi-tenant com tokens de tenants diferentes.
 * Usa endpoint legado de login com DEFAULT_TENANT_ID=itvalley-dev.
 */
export async function makeAPIContext(token: string): Promise<APIRequestContext> {
  return await request.newContext({
    baseURL: BACKEND_URL,
    extraHTTPHeaders: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
}

/**
 * Checa se backend esta UP.
 */
export async function backendHealthy(): Promise<boolean> {
  try {
    const ctx = await request.newContext({ baseURL: BACKEND_URL });
    const res = await ctx.get('/health', { timeout: 3000 });
    await ctx.dispose();
    return res.ok();
  } catch {
    return false;
  }
}
