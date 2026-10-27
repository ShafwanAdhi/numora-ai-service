/* Run via playwright-cli run-code --filename after opening /image-variants. */
async page => {
  const check = (condition, message) => { if (!condition) throw Error(message); };
  const generation = '**/api/image-variants/generate';
  const catalog = '**/api/image-variants';
  const results = {};
  let release = () => {};
  try {
    await page.selectOption('#activity', 'DRILL');
    await page.selectOption('#question', 'mcma-16-4-7');
    await page.selectOption('#mode', 'stock');
    await page.selectOption('#stock', 'mcma-16-4-7:stock-01');
    let started;
    const seen = new Promise(resolve => { started = resolve; });
    const gate = new Promise(resolve => { release = resolve; });
    let fulfilled;
    const finished = new Promise(resolve => { fulfilled = resolve; });
    await page.route(generation, async route => {
      const response = await route.fetch(); started();
      await gate; await route.fulfill({response}); fulfilled();
    });
    await page.click('#generate'); await seen;
    await page.selectOption('#stock', 'mcma-16-4-7:stock-02');
    release(); await finished; await page.waitForTimeout(200);
    check(await page.locator('#result').isHidden(), 'Old response overwrote changed selection');
    check((await page.locator('#status').innerText()).includes('Pilihan berubah'), 'Stale status applied');
    results.stale_response_rejected = true;
    await page.unroute(generation);
    await page.click('#generate'); await page.waitForFunction(() => !document.getElementById('result').hidden);
    check((await page.locator('#download').getAttribute('download')).includes('stock-2-v1'), 'Wrong stock download');
    results.stock_identity_download = true;

    let catalogStarted;
    const catalogSeen = new Promise(resolve => { catalogStarted = resolve; });
    const catalogGate = new Promise(resolve => { release = resolve; });
    await page.route(catalog, async route => { catalogStarted(); await catalogGate; await route.continue(); });
    await page.reload({waitUntil: 'domcontentloaded'}); await catalogSeen;
    check(await page.locator('#activity').isDisabled(), 'Activity enabled during catalog load');
    check(await page.locator('#seed').isDisabled(), 'Seed enabled during catalog load');
    release(); await page.waitForFunction(() => !document.getElementById('generate').disabled);
    results.loading_controls_disabled = true;
    await page.unroute(catalog);

    await page.route(catalog, route => route.fulfill({status: 500, json: {error: 'Uji katalog gagal'}}));
    await page.reload(); await page.waitForFunction(() => !document.getElementById('retry').hidden);
    check(await page.locator('#generate').isDisabled(), 'Generate enabled after catalog failure');
    await page.unroute(catalog); await page.click('#retry');
    await page.waitForFunction(() => !document.getElementById('generate').disabled);
    results.catalog_error_retry = true;

    await page.route(generation, route => route.fulfill({status: 400, json: {error: 'Uji generate gagal'}}));
    await page.click('#generate');
    await page.waitForFunction(() => document.getElementById('status').textContent.includes('Uji generate gagal'));
    check(await page.locator('#result').isHidden(), 'Old result visible on error');
    check(await page.locator('#generate').isEnabled(), 'Retry action unavailable');
    results.generate_error_state = true;
    await page.unroute(generation);

    await page.route(generation, async route => {
      const response = await route.fetch(); const data = await response.json();
      data.record.stem = '<img src=x onerror=window.injectionExecuted=true>';
      await route.fulfill({json: data});
    });
    await page.click('#generate'); await page.waitForFunction(() => !document.getElementById('result').hidden);
    check(await page.locator('#stem img').count() === 0, 'Source HTML was interpreted');
    check(await page.evaluate(() => window.injectionExecuted === undefined), 'Source script executed');
    results.source_text_safe = true;
    results.mobile_no_overflow = await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth);
    return results;
  } finally {
    release(); await page.unroute(generation); await page.unroute(catalog);
    await page.reload();
  }
}
