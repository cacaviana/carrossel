import { test, expect } from '@playwright/test';

test('PNG download works', async ({ page }) => {
  await page.goto('http://localhost:5173/editor?pipeline=e97a2945-b0b8-4e49-9007-e103afdade5d&brand=jennie');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);

  page.on('console', msg => console.log(`[${msg.type()}] ${msg.text()}`));
  page.on('pageerror', err => console.log(`[pageerror] ${err.message}`));

  // Check image src
  const src = await page.evaluate(() => {
    const imgs = document.querySelectorAll('img');
    return Array.from(imgs).map(i => i.src.substring(0, 100));
  });
  console.log('All img srcs:', src);

  // Test fetch directly from page context
  const testResult = await page.evaluate(async () => {
    const imgs = document.querySelectorAll('img');
    const firstSrc = imgs[0]?.src;
    if (!firstSrc) return 'no images found';
    if (firstSrc.startsWith('data:')) return 'already base64';
    try {
      const res = await fetch(firstSrc);
      const blob = await res.blob();
      return `fetch OK: status=${res.status}, size=${blob.size}, type=${blob.type}`;
    } catch (e: any) {
      return `fetch FAILED: ${e.message}`;
    }
  });
  console.log('Fetch test:', testResult);

  // Listen for download
  const downloadPromise = page.waitForEvent('download', { timeout: 15000 }).catch(() => null);

  const pngBtn = page.locator('button', { hasText: 'PNG' });
  await pngBtn.click();
  console.log('Clicked PNG');

  const download = await downloadPromise;
  console.log('Download result:', download ? download.suggestedFilename() : 'NULL');
  expect(download).not.toBeNull();
});
