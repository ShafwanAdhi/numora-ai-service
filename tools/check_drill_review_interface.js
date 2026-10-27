/* Fixture rows are inserted by test_drill_review_interface.py before CLI execution. */
async page => {
  const cases = []; // REVIEW_CASES
  if (!cases.length) throw Error('Run via tools/test_drill_review_interface.py');
  const checked = [];
  await page.waitForFunction(() => !document.getElementById('generate').disabled);
  await page.selectOption('#activity', 'DRILL');
  for (const item of cases) {
    const request = item.request;
    await page.selectOption('#question', request.question_id);
    await page.selectOption('#mode', request.mode);
    if (request.mode === 'generator') await page.fill('#seed', String(request.seed));
    if (request.mode === 'stock') await page.selectOption('#stock', request.stock_variant_id);
    await page.click('#generate');
    await page.waitForFunction(() => !document.getElementById('result').hidden &&
      !document.getElementById('generate').disabled);
    const actual = await page.evaluate(async () => {
      const get = id => document.getElementById(id);
      const raw = await (await fetch(get('download').href)).arrayBuffer();
      const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', raw)))
        .map(value => value.toString(16).padStart(2, '0')).join('');
      return {sha256: hash, stem: get('stem').textContent, answer: get('answer').textContent,
        metadata: JSON.parse(get('metadata').textContent), imageWidth: get('image').naturalWidth,
        seedDisabled: get('seed').disabled, stockDisabled: get('stock').disabled,
        overflow: document.documentElement.scrollWidth > innerWidth};
    });
    if (actual.sha256 !== item.sha256 || actual.stem !== item.stem ||
        !actual.answer.startsWith('Kunci: ' + item.key + '\n') ||
        actual.metadata.question_id !== request.question_id || actual.metadata.mode !== request.mode ||
        actual.metadata.original_hash !== item.original_hash || actual.imageWidth !== 960 ||
        actual.overflow || actual.seedDisabled !== (request.mode !== 'generator') ||
        actual.stockDisabled !== (request.mode !== 'stock')) {
      throw Error('Interface mismatch: ' + item.case_id);
    }
    if (request.mode === 'stock' && actual.metadata.source.stock_variant_id !== request.stock_variant_id)
      throw Error('Stock identity mismatch: ' + item.case_id);
    checked.push({case_id: item.case_id, sha256: actual.sha256, status: 'PASS'});
  }
  return {question_id: cases[0].request.question_id, status: 'PASS', cases: checked};
}
