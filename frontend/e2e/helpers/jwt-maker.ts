import { createHmac } from 'crypto';

/**
 * Cria um JWT HS256 manualmente (sem biblioteca) pra usar nos testes multi-tenant.
 * Usa o mesmo JWT_SECRET_KEY do backend (.env).
 *
 * Util quando precisamos testar isolamento entre tenants — o endpoint /auth/login
 * sempre retorna token do DEFAULT_TENANT_ID, entao montamos tokens manuais pra
 * tenant A e tenant B separadamente.
 */

const JWT_SECRET = process.env.JWT_SECRET_KEY
  ?? '3ucjO_Wprluu_W2I6Rrk9mtUOpy19PJATzU4z9Ib8lKYlhGdoy_WWUo_po_17G24';

function base64url(input: Buffer | string): string {
  return Buffer.from(input)
    .toString('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
}

export function makeJWT(payload: Record<string, any>, secret: string = JWT_SECRET): string {
  const header = { alg: 'HS256', typ: 'JWT' };
  const now = Math.floor(Date.now() / 1000);
  const fullPayload = { exp: now + 24 * 3600, ...payload };

  const encodedHeader = base64url(JSON.stringify(header));
  const encodedPayload = base64url(JSON.stringify(fullPayload));
  const message = `${encodedHeader}.${encodedPayload}`;

  const signature = createHmac('sha256', secret).update(message).digest();
  return `${message}.${base64url(signature)}`;
}

export function makeTokenForTenant(tenantId: string, role: string = 'admin', email?: string): string {
  return makeJWT({
    user_id: `user-${tenantId}-${role}`,
    tenant_id: tenantId,
    role,
    email: email ?? `${role}@${tenantId}.test`,
    name: `Test ${tenantId} ${role}`,
  });
}
