// playwright-cli run-code --filename; localhost:8767, temporary configs/store.
async (page) => {
  const check = (ok, message) => { if (!ok) throw new Error(message); };
  const ready = () => page.locator('#workspace:not([disabled])').waitFor();
  await page.route('**/api/database/**', route => route.fulfill({json: {items: [], total: 0, limit: 50, offset: 0}}));
  await page.goto('http://127.0.0.1:8767'); await ready();
  check(await page.locator('#question option').count() === 390, '390 Drill originals');
  for (const indicator of ['20','21','22','23']) {
    await page.locator('#indicator').selectOption(indicator); await ready();
    check(await page.locator('#question option').count() === 30, `indicator ${indicator}`);
  }
  await page.locator('#source-level').selectOption('4');
  await page.locator('#workspace').waitFor({state:'hidden'});
  check(await page.locator('#question option').count() === 0, 'source level 4 remains empty');
  await page.locator('#source-level').selectOption(''); await ready();
  await page.locator('#indicator').selectOption('20'); await ready();
  await page.locator('#question').selectOption('kategori-20-1-9'); await ready();
  check((await page.locator('#original').textContent()).includes('2: Kualitatif'), 'category label preserved');
  check(await page.locator('#save').isDisabled(), 'deferred editor disabled');
  await page.locator('#question').selectOption('pg-20-3-3'); await ready();
  check(await page.locator('#generate').isDisabled(), 'HOLD generation disabled');
  check((await page.locator('#original').textContent()).includes('belum disahkan'), 'HOLD source key labeled');
  await page.locator('#question').selectOption('pg-20-1-2'); await ready();
  check((await page.locator('#original .stem').textContent()).includes('Andi | 4'), 'table row label retained');
  await page.locator('#seed').fill('9'); await page.locator('#seed').press('Tab'); await ready();
  await page.locator('#generate').click(); await ready();
  check((await page.locator('#variant').textContent()).includes('varian v1'), 'local snapshot');
  const first = await page.locator('#variant').textContent();
  await page.locator('#generate').click(); await ready();
  check(await page.locator('#variant').textContent() === first, 'seed reused');
  await page.locator('#reason').fill('browser local review');
  await page.locator('#regen').click(); await ready();
  check((await page.locator('#variant').textContent()).includes('varian v2'), 'regen appends version');
  await page.locator('#version').selectOption('1'); await ready();
  check(await page.locator('#variant').textContent() === first, 'history preserves v1');
  await page.locator('#config-section summary').click();
  const draft = await page.locator('#config-editor').inputValue();
  await page.locator('#config-editor').fill(draft+'\n ');
  check(await page.locator('#generate').isDisabled(), 'dirty draft blocks generation');
  await page.evaluate(() => { window.confirm = () => false; });
  await page.locator('#indicator').selectOption('21');
  check(await page.locator('#indicator').inputValue() === '20', 'cancel restores filter');
  await page.locator('#config-editor').fill(draft);
  await page.locator('#lint').click(); await ready();
  check((await page.locator('#lint-output').textContent()).includes('[ok] reproduces'), 'draft lint');
  await page.locator('#save').click(); await ready();
  check((await page.locator('#config-note').textContent()).includes('v3'), 'saved config version 2');
  await page.locator('#tab-ai').focus(); await page.keyboard.press('ArrowRight');
  check(await page.locator('#tab-db').getAttribute('aria-selected') === 'true', 'keyboard database tab');
  await page.keyboard.press('ArrowLeft');
  check(await page.locator('#tab-ai').getAttribute('aria-selected') === 'true', 'keyboard AI tab');
  check(await page.evaluate(() => document.querySelectorAll('#original script').length === 0), 'source rendered as text');
  await page.setViewportSize({width:390,height:844});
  check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), '390px no overflow');
  await page.screenshot({path:'output/playwright/drill-20-23-mobile.png',fullPage:true});
  return {originals:120, indicators:4, seedHistory:true, categoryLabels:true, database:'mocked', mobile:390};
}
