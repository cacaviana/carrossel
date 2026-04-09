import { test, expect } from '@playwright/test';

test('CORS test', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await page.waitForLoadState('networkidle');

  // Test fetch to different endpoints
  const results = await page.evaluate(async () => {
    const tests: Record<string, string> = {};

    // Test image-to-base64 (works)
    try {
      const r1 = await fetch('http://localhost:8000/api/image-to-base64', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: 'http://localhost:8000/api/brands/jennie/foto/file' }),
      });
      tests['image-to-base64'] = `${r1.status} OK`;
    } catch (e: any) {
      tests['image-to-base64'] = `FAILED: ${e.message}`;
    }

    // Test salvar-pdf (fails)
    try {
      const r2 = await fetch('http://localhost:8000/api/editor/salvar-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slides: [], logo: '', formato: 'carrossel' }),
      });
      tests['salvar-pdf'] = `${r2.status} OK`;
    } catch (e: any) {
      tests['salvar-pdf'] = `FAILED: ${e.message}`;
    }

    return tests;
  });

  console.log('Results:', JSON.stringify(results, null, 2));
});
