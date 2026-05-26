import { test, expect } from '@playwright/test';

test('PDF download', async ({ page }) => {
  test.setTimeout(60000);

  // Intercept the salvar-pdf request
  page.on('request', req => {
    if (req.url().includes('salvar-pdf')) {
      console.log(`[request] ${req.method()} ${req.url()}`);
      console.log('  headers:', JSON.stringify(req.headers()));
      const body = req.postData();
      console.log('  body size:', body?.length || 0);
      console.log('  body preview:', body?.substring(0, 200));
    }
  });
  page.on('requestfailed', req => {
    if (req.url().includes('salvar-pdf')) {
      console.log(`[FAILED] ${req.url()} reason: ${req.failure()?.errorText}`);
    }
  });
  page.on('console', msg => {
    if (msg.type() === 'error') console.log(`[error] ${msg.text()}`);
  });

  await page.goto('http://localhost:5173/editor?pipeline=e97a2945-b0b8-4e49-9007-e103afdade5d&brand=jennie');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);

  const pdfBtn = page.locator('button', { hasText: 'PDF' });
  await pdfBtn.click({ force: true });
  await page.waitForTimeout(15000);
});
