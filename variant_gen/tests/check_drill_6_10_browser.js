// playwright-cli run-code --filename; localhost:8768, temporary store.
async (page) => {
  const check = (ok, message) => { if (!ok) throw new Error(message); };
  const ready = () => page.locator('#workspace:not([disabled])').waitFor();
  await page.route('**/api/database/**', route => route.fulfill({json: {items: [], total: 0, limit: 50, offset: 0}}));
  await page.goto('http://127.0.0.1:8768'); await ready();
  check(await page.locator('#question option').count() === 390, '390 Drill originals');
  for (const indicator of ['6','7','8','9','10']) {
    await page.locator('#indicator').selectOption(indicator); await ready();
    check(await page.locator('#question option').count() === 30, `indicator ${indicator}`);
  }
  await page.locator('#source-level').selectOption('4');
  await page.locator('#workspace').waitFor({state: 'hidden'});
  check(await page.locator('#question option').count() === 0, 'level 4 empty');
  await page.locator('#source-level').selectOption(''); await ready();
  await page.locator('#indicator').selectOption('6'); await ready();
  await page.locator('#question').selectOption('pg-6-1-5'); await ready();
  check((await page.locator('#original').textContent()).includes('Belum tersedia'), 'missing source key');
  check(await page.locator('#generate').isDisabled(), 'HOLD cannot generate');
  for (const [indicator, qid] of [['6','pg-6-1-1'], ['8','mcma-8-1-6'], ['10','kategori-10-1-9']]) {
    await page.locator('#indicator').selectOption(indicator); await ready();
    await page.locator('#question').selectOption(qid); await ready();
    await page.locator('#seed').fill('11'); await page.locator('#seed').press('Tab'); await ready();
    await page.locator('#generate').click(); await ready();
    check((await page.locator('#variant').textContent()).includes('varian v1'), qid+' snapshot');
    const first = await page.locator('#variant').textContent();
    await page.locator('#generate').click(); await ready();
    check(await page.locator('#variant').textContent() === first, qid+' idempotent');
  }
  console.log('PASS: filters, empty level, HOLD missing key, PG/MCMA/KATEGORI local snapshots');
}
