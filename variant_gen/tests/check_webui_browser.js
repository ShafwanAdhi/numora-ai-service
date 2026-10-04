// Run against a local webui.py via playwright-cli run-code --filename <this file>.
// Database responses are fixtures; never sends generator writes or uses DB credentials.
async (page) => {
  const check = (condition, message) => { if (!condition) throw new Error(message); };
  await page.route('**/api/database/**', route => route.fulfill({status: 503,
    contentType: 'application/json', body: JSON.stringify({error: 'Isi DATABASE_URL di .env repo Numora-ai-service, lalu restart interface.'})}));
  await page.setViewportSize({width: 1280, height: 900});
  await page.goto('http://127.0.0.1:8766');
  await page.locator('#workspace:not([disabled])').waitFor();
  await page.screenshot({path: 'output/playwright/service-ai-consistent.png'});
  await page.getByRole('tab', {name: 'DB Utama'}).click();
  await page.getByText('Isi DATABASE_URL', {exact: false}).waitFor();
  check(await page.locator('#panel-ai').isHidden(), 'AI panel must hide');
  await page.getByRole('tab', {name: 'Service AI'}).click();
  await page.getByText('Atur config', {exact: true}).click();
  const draft = (await page.locator('#config-editor').inputValue()) + '\n ';
  await page.getByLabel('Config JSON', {exact: true}).fill(draft);
  check(await page.getByRole('button', {name: 'Generate', exact: true}).isDisabled(), 'dirty draft disables Generate');

  const packages = [{id: 'empty', name: 'Paket kosong', packageVersion: 1, status: 'DRAFT', isDemo: true, itemCount: 0},
    {id: 'pinned', name: 'Paket pinned', packageVersion: 1, status: 'PUBLISHED', isDemo: false, itemCount: 1}];
  const original = {versionId: 'v1', versionNumber: 1, variantCode: 'O', kind: 'ORIGINAL', questionType: 'PG',
    contentStatus: 'DRAFT', validationState: 'DRAFT', familyId: 'family',
    stem: {text: '<img src=x onerror="window.pwned=1"> pinned-v1'},
    optionsOrStatements: [{id: 'A', content: {text: 'pilihan'}}], answerKey: {optionId: 'A'},
    explanation: {text: 'pembahasan'}, parentOriginalQuestionVersionId: null};
  const variant = {...original, versionId: 'variant-v1', kind: 'VARIANT', variantCode: 'V1', stem: {text: 'variant'}};
  const latest = {...original, versionId: 'v2', versionNumber: 2, stem: {text: 'new-v2'}};
  let fail = false;
  await page.unroute('**/api/database/**');
  await page.route('**/api/database/**', async route => {
    if (fail) return route.fulfill({status: 503, contentType: 'application/json', body: JSON.stringify({error: 'Database fixture unavailable'})});
    const url = new URL(route.request().url());
    const base = {limit: Number(url.searchParams.get('limit')), offset: Number(url.searchParams.get('offset'))};
    let result;
    if (url.pathname.endsWith('/packages')) result = {...base, total: packages.length, items: packages};
    if (url.pathname.endsWith('/package')) {
      const pkg = packages.find(item => item.id === url.searchParams.get('id'));
      result = {...base, package: pkg, total: pkg.itemCount,
        items: pkg.itemCount ? [{...original, itemId: 'item', displayOrder: 1, questionVersionId: 'v1'}] : []};
    }
    if (url.pathname.endsWith('/family')) result = {...base, total: 3, items: [original, latest, variant]};
    await route.fulfill({contentType: 'application/json', body: JSON.stringify(result)});
  });
  await page.getByRole('tab', {name: 'DB Utama'}).click();
  await page.locator('#db-package').selectOption('empty');
  await page.getByText('Paket ini belum berisi soal', {exact: false}).waitFor();
  await page.locator('#db-package').selectOption('pinned');
  await page.locator('#db-member:not([disabled])').waitFor();
  const itemBounds = await page.locator('#db-item').boundingBox();
  const memberBounds = await page.locator('#db-member').boundingBox();
  check(Math.abs(itemBounds.y - memberBounds.y) < 2, 'DB question and version selectors share a row');
  const pinnedBounds = await page.locator('#db-pinned').boundingBox();
  const familyBounds = await page.locator('#db-family').boundingBox();
  check(Math.abs(pinnedBounds.y - familyBounds.y) < 2, 'DB comparison content aligns like AI comparison');
  await page.screenshot({path: 'output/playwright/db-utama-consistent.png'});
  check((await page.locator('#db-pinned').textContent()).includes('pinned-v1'), 'pinned v1 retained');
  check(!(await page.locator('#db-pinned').textContent()).includes('new-v2'), 'must not replace pinned version');
  check(await page.locator('#db-pinned img').count() === 0, 'HTML must remain text');
  check(!await page.evaluate(() => window.pwned), 'unsafe markup must not execute');
  await page.locator('#db-member').selectOption('variant-v1');
  check((await page.locator('#db-family').textContent()).includes('VARIANT'), 'variant renders');
  check((await page.locator('#db-family').textContent()).includes('Belum tersimpan'), 'missing lineage honest');
  packages.push({...packages[0], id: 'uploaded', name: 'Upload baru'});
  await page.getByRole('button', {name: 'Muat ulang', exact: true}).click();
  await page.locator('#db-package option[value="uploaded"]').waitFor({state: 'attached'});
  await page.locator('#db-controls:not([disabled])').waitFor();
  fail = true;
  await page.getByRole('button', {name: 'Muat ulang', exact: true}).click();
  await page.getByText('Database fixture unavailable', {exact: true}).waitFor();
  check(!(await page.locator('#db-pinned').textContent()).includes('pinned-v1'), 'failure clears stale content');
  await page.getByRole('tab', {name: 'Service AI'}).click();
  check(await page.locator('#config-editor').inputValue() === draft, 'draft preserved');
  await page.getByRole('tab', {name: 'Service AI'}).focus();
  await page.keyboard.press('End');
  check(await page.getByRole('tab', {name: 'DB Utama'}).getAttribute('aria-selected') === 'true', 'End selects DB');
  await page.keyboard.press('ArrowLeft');
  check(await page.getByRole('tab', {name: 'Service AI'}).getAttribute('aria-selected') === 'true', 'ArrowLeft selects AI');
  await page.setViewportSize({width: 390, height: 844});
  check(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), 'mobile no horizontal overflow');
  await page.getByRole('tab', {name: 'DB Utama'}).click();
  check(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), 'DB mobile no horizontal overflow');
  console.log('Browser: tabs, keyboard, draft, empty package, pinned version, family, refresh, safe HTML, errors, mobile OK');
}
