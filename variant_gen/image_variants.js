/* Local-only image preview. All question/source text is inserted as textContent. */
'use strict';
const $ = id => document.getElementById(id);
let catalog = [], blobUrl = null, requestId = 0;
const modeNames = {original: 'Original', generator: 'Generator', stock: 'Stok'};

function status(text, error = false) {
  $('status').textContent = text;
  $('status').className = error ? 'error' : '';
}
function clearResult() {
  if (blobUrl) URL.revokeObjectURL(blobUrl);
  blobUrl = null;
  $('image').removeAttribute('src');
  $('download').removeAttribute('href');
  $('result').hidden = true;
  $('empty').hidden = false;
}
function option(value, text) {
  const node = document.createElement('option');
  node.value = value; node.textContent = text;
  return node;
}
function selected() { return catalog.find(row => row.id === $('question').value); }
function modeControls() {
  const mode = $('mode').value;
  const hasQuestion = Boolean(selected());
  $('seed-control').hidden = mode !== 'generator';
  $('seed').disabled = !hasQuestion || mode !== 'generator';
  $('stock-control').hidden = mode !== 'stock';
  $('stock').disabled = !hasQuestion || mode !== 'stock';
  $('stock').required = mode === 'stock';
  $('generate').textContent = mode === 'generator' ? 'Buat varian' : 'Tampilkan gambar';
  $('generate').disabled = !hasQuestion || (mode === 'stock' && !$('stock').options.length);
}
function questionControls() {
  const row = selected();
  $('mode').replaceChildren(...(row?.modes || []).map(mode => option(mode, modeNames[mode])));
  $('mode').disabled = !row;
  $('stock').replaceChildren(...(row?.stocks || []).map(stock =>
    option(stock.variant_id, `Stok ${stock.stock_index} · versi ${stock.stock_version}`)));
  modeControls();
}
function activityControls() {
  const rows = catalog.filter(row => row.activity === $('activity').value);
  $('question').replaceChildren(...rows.map(row => option(row.id,
    row.id + ' | ' + row.stem.replace(/\s+/g, ' ').slice(0, 85))));
  $('question').disabled = !rows.length;
  questionControls();
  if (!rows.length) status('Belum ada soal bergambar untuk aktivitas ini.');
}
function changed(update) {
  ++requestId;
  clearResult();
  if (update) update();
  modeControls();
  status(selected() ? 'Pilihan berubah. Tampilkan gambar untuk melihat hasil.' :
    'Belum ada soal bergambar untuk aktivitas ini.');
}
async function api(url, options) {
  const response = await fetch(url, options);
  let data;
  try { data = await response.json(); }
  catch { throw Error('Respons server tidak valid. Coba lagi.'); }
  if (!response.ok) throw Error(data.error || 'Permintaan gagal.');
  return data;
}
async function load() {
  const current = ++requestId;
  clearResult();
  $('retry').hidden = true;
  $('activity').disabled = true;
  $('seed').disabled = true;
  $('stock').disabled = true;
  $('generate').disabled = true;
  $('question').disabled = true;
  $('mode').disabled = true;
  status('Memuat pilihan soal...');
  try {
    const rows = await api('/api/image-variants');
    if (current !== requestId) return;
    catalog = rows;
    $('activity').disabled = false;
    activityControls();
    if (selected()) status('Siap menampilkan gambar.');
  } catch (error) {
    if (current !== requestId) return;
    catalog = [];
    $('retry').hidden = false;
    status(error.message || 'Tidak dapat menghubungi workbench.', true);
  }
}

$('activity').addEventListener('change', () => changed(activityControls));
$('question').addEventListener('change', () => changed(questionControls));
$('mode').addEventListener('change', () => changed());
$('stock').addEventListener('change', () => changed());
$('seed').addEventListener('input', () => changed());
$('retry').addEventListener('click', load);
$('form').addEventListener('submit', async event => {
  event.preventDefault();
  const current = ++requestId;
  const payload = {question_id: $('question').value, mode: $('mode').value};
  if (payload.mode === 'generator') payload.seed = Number($('seed').value);
  if (payload.mode === 'stock') payload.stock_variant_id = $('stock').value;
  clearResult();
  $('generate').disabled = true;
  status('Menyiapkan soal dan gambar...');
  let pendingUrl = null;
  try {
    const data = await api('/api/image-variants/generate', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
    });
    if (current !== requestId) return;
    const {record, image} = data;
    const bytes = Uint8Array.from(atob(image.base64), char => char.charCodeAt(0));
    pendingUrl = URL.createObjectURL(new Blob([bytes], {type: 'image/png'}));
    const probe = new Image(); probe.src = pendingUrl;
    try { await probe.decode(); }
    catch { throw Error('Gambar tidak dapat dimuat. Coba lagi.'); }
    if (current !== requestId) return;
    blobUrl = pendingUrl; pendingUrl = null;
    $('image').src = blobUrl;
    $('image').alt = image.alt_text;
    $('download').href = blobUrl;
    const suffix = data.mode === 'stock' ? `stock-${record.stock_index}-v${record.variant_ver}` :
      data.mode === 'original' ? 'original' : `s${record.seed}`;
    $('download').download = `${record.question_id}-${suffix}-${image.sha256.slice(0, 12)}.png`;
    $('dimensions').textContent = `${image.width} x ${image.height} px · PNG · ${modeNames[data.mode]}`;
    $('stem').textContent = record.stem;
    $('options').replaceChildren(...record.options.map(value => {
      const li = document.createElement('li'); li.textContent = value.text; return li;
    }));
    $('answer').textContent = 'Kunci: ' + record.key + '\n\n' + (record.explanation || 'Pembahasan belum tersedia.');
    $('values-details').hidden = data.mode !== 'generator';
    $('values').textContent = JSON.stringify(record.values_used, null, 2);
    $('metadata').textContent = JSON.stringify({question_id: record.question_id,
      mode: data.mode, source: data.source, seed: record.seed,
      config_version: record.config_ver, config_hash: record.config_hash,
      original_hash: record.original_hash, png_sha256: image.sha256,
      provenance: image.provenance}, null, 2);
    $('result').hidden = false; $('empty').hidden = true;
    status(data.mode === 'generator' ? 'Varian siap. Gambar dan soal memakai hasil generator yang sama.' :
      data.mode === 'stock' ? 'Stok siap. Gambar mengikuti isi stok yang dipilih.' : 'Original siap ditinjau.');
  } catch (error) {
    if (current === requestId) status(error.message || 'Tidak dapat menghubungi workbench.', true);
  } finally {
    if (pendingUrl) URL.revokeObjectURL(pendingUrl);
    if (current === requestId) modeControls();
  }
});
window.addEventListener('pagehide', () => { if (blobUrl) URL.revokeObjectURL(blobUrl); });
load();
