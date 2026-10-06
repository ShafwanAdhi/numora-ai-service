// playwright-cli run-code --filename; port8768, temporary store only.
async (page) => {
  const check = (ok, message) => { if (!ok) throw new Error(message); };
  const ready = () => page.locator('#workspace:not([disabled])').waitFor();
  await page.route('**/api/database/**', route => route.fulfill({json: {items: [], total: 0, limit: 50, offset: 0}}));
  await page.goto('http://127.0.0.1:8768'); await ready();
  check(await page.locator('#question option').count() === 790, '790 Drill originals');
  for (const indicator of ['3','4','5']) {
    await page.locator('#indicator').selectOption(indicator); await ready();
    check(await page.locator('#question option').count() === 30, '30 originals per indicator');
    for (const level of ['1','2','3']) {
      await page.locator('#source-level').selectOption(level); await ready();
      check(await page.locator('#question option').count() === 10, '10 originals per level');
    }
    await page.locator('#source-level').selectOption(''); await ready();
  }
  for (const [indicator,qid] of [['3','pg-3-1-1'],['4','mcma-4-1-7'],['5','kategori-5-1-9']]) {
    await page.locator('#indicator').selectOption(indicator); await ready();
    await page.locator('#question').selectOption(qid); await ready();
    await page.locator('#seed').fill('11'); await page.locator('#seed').press('Tab'); await ready();
    await page.locator('#generate').click(); await ready();
    check((await page.locator('#variant').textContent()).includes('varian v1'), qid+' snapshot');
    const first=await page.locator('#variant').textContent();
    await page.locator('#generate').click(); await ready();
    check(await page.locator('#variant').textContent()===first, qid+' idempotent');
  }
  await page.locator('#indicator').selectOption('3'); await ready();
  for (const qid of ['pg-3-1-3','pg-3-1-2']) {
    await page.locator('#question').selectOption(qid); await ready();
    check(await page.locator('#generate').isDisabled(), qid+' cannot generate');
  }
  await page.locator('#indicator').selectOption('4'); await ready();
  for (const qid of ['mcma-4-1-8','kategori-4-2-10']) {
    await page.locator('#question').selectOption(qid); await ready();
    check(await page.locator('#generate').isDisabled(), qid+' ambiguous source blocked');
  }
  await page.locator('#indicator').selectOption('5'); await ready();
  await page.locator('#question').selectOption('pg-5-2-4'); await ready();
  check(await page.locator('#generate').isDisabled(), 'deferred analysis blocked');
  console.log('PASS: indicators3–5/levels1–3, PG/MCMA/KATEGORI, idempotent, HOLD');
}
