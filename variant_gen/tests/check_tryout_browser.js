// Run via playwright-cli run-code --filename; server on8766 with TEMP configs.
async (page) => {
  const check = (ok, message) => { if (!ok) throw new Error(message); };
  let databaseRequests = 0;
  page.on('request', request => { if (request.url().includes('/api/database/')) databaseRequests++; });
  const ready = () => page.locator('#workspace:not([disabled])').waitFor();
  await page.goto('http://127.0.0.1:8766'); await ready();
  await page.locator('#activity').selectOption('TRYOUT'); await ready();
  check(await page.locator('#question option').count() === 30, '30 Tryout originals');
  check(await page.locator('#level-filter').isHidden(), 'Tryout hides Drill levels');
  for (const [chapter, count] of [['1',8],['2',8],['3',7],['4',7]]) {
    await page.locator('#indicator').selectOption(chapter); await ready();
    check(await page.locator('#question option').count() === count, `chapter ${chapter}`);
  }
  await page.locator('#indicator').selectOption(''); await ready();
  await page.locator('#package').selectOption('tryout-1'); await ready();
  await page.locator('#question').selectOption('tryout-1-b1-q07'); await ready();
  check(await page.locator('#generate').isDisabled(), 'deferred generation disabled');
  check(await page.locator('#config-editor').isDisabled(), 'deferred config disabled');
  await page.locator('#question').selectOption('tryout-1-b1-q01'); await ready();
  await page.locator('#seed').fill('7'); await page.locator('#seed').press('Tab'); await ready();
  await page.locator('#generate-package').click(); await ready();
  check(await page.locator('#package-items details').count() === 30, '30 response preview entries');
  check((await page.locator('#package-items').textContent()).includes('27 varian + 3 original'), '27+3 inventory');
  const pinned = await page.locator('#package-items').textContent();
  check(await page.locator('#regen').count() === 0, 'no regen');
  check(await page.locator('#version').count() === 0, 'no history selector');
  check(await page.locator('#export-package').count() === 0, 'no download');
  await page.locator('#generate').click(); await ready();
  const first = await page.locator('#variant').textContent();
  for (let i = 0; i < 12; i++) {
    await page.locator('#generate').click(); await ready();
    check(await page.locator('#variant').textContent() === first, 'repeatable response');
  }
  await page.locator('#generate-package').click(); await ready();
  check(await page.locator('#package-items').textContent() === pinned, 'repeatable package content');
  await page.reload(); await ready();
  check(!(await page.locator('#variant').textContent()).includes('varian v1'), 'reload has no cached variant');
  check(await page.locator('#package-preview').isHidden(), 'reload has no cached package');
  await page.locator('#activity').selectOption('TRYOUT'); await ready();
  await page.locator('#package').selectOption('tryout-1'); await ready();
  await page.locator('#question').selectOption('tryout-1-b1-q01'); await ready();
  await page.locator('#config-section summary').click();
  const draft = await page.locator('#config-editor').inputValue();
  await page.locator('#config-editor').fill(draft + '\n ');
  check(await page.locator('#generate-package').isDisabled(), 'dirty draft blocks package');
  await page.evaluate(() => { window.confirm = () => false; });
  await page.locator('#activity').selectOption('DRILL');
  check(await page.locator('#activity').inputValue() === 'TRYOUT', 'cancel retains activity');
  await page.locator('#config-editor').fill(draft);
  await page.locator('#lint').click(); await ready();
  check((await page.locator('#lint-output').textContent()).includes('[ok] reproduces'), 'config lint');
  await page.setViewportSize({width:390,height:844});
  check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'mobile no horizontal overflow');
  check(databaseRequests === 0, 'no database request');
  return {originals:30, variants:27, deferred:3, databaseRequests};
}
