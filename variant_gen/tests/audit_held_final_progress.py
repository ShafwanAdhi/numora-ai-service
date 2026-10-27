"""Refresh progress from the actual loader, configs and verified conceptual stock."""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from bank import load_workspace_bank
from config_store import ConfigStore,validate_config
from conceptual_stock import load_stock

OUT=ROOT.parent/'docs/audits/2026-10-22-held-final-revisions'


def main():
    bank=load_workspace_bank(ROOT/'data/q0_bank.csv');configs=ConfigStore(ROOT/'configs')
    stocks=load_stock(ROOT/'data/conceptual_stock.json',bank)
    counts={i:Counter(originals=0,generator=0,stock=0,held=0,unavailable=0) for i in range(1,24)}
    activities={};pending=[];levels={}
    for q in bank.ids():
        o=bank.get(q);activity=o['classification']['activity']
        mode=('held' if o.get('metadata',{}).get('generation_status')=='HOLD_SOURCE' else
              'stock' if stocks.get(q) else 'generator' if configs.versions(q) else 'unavailable')
        if mode=='generator':assert validate_config(configs.load(q)[0],o)==[],q
        activities.setdefault(activity,Counter(originals=0,generator=0,stock=0,held=0,unavailable=0))
        activities[activity].update({'originals':1,mode:1})
        if activity=='DRILL':
            i=o['classification']['indicator'];level=o['classification']['source_level']
            counts[i].update({'originals':1,mode:1})
            levels.setdefault((i,level),Counter(originals=0,generator=0,stock=0,held=0,unavailable=0))
            levels[i,level].update({'originals':1,mode:1})
        if mode in ('held','unavailable'):pending.append(q)
    assert len(bank.ids())==1180 and not pending
    assert all(c['originals']==50 for c in counts.values())
    assert len(levels)==115 and all(c['originals']==10 for c in levels.values())
    groups=[]
    for name,lo,hi in [('1-5',1,5),('6-10',6,10),('11-15',11,15),('16-19',16,19),('20-23',20,23)]:
        total=Counter()
        for i in range(lo,hi+1):total.update(counts[i])
        groups.append(dict(group=name,**{k:total[k] for k in ('originals','generator','stock','held','unavailable')}))
    payload=dict(date='2026-10-22',scope='Local runtime; no main database writes',activities=activities,
                 conceptual_variants=sum(map(len,stocks.values())),groups=groups,
                 indicators=[dict(indicator=i,**counts[i]) for i in counts],
                 levels=[dict(indicator=i,level=l,**c) for (i,l),c in sorted(levels.items())],pending=pending)
    (OUT/'progress.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    with (OUT/'indicators.csv').open('w',newline='',encoding='utf8') as stream:
        writer=csv.DictWriter(stream,fieldnames=payload['indicators'][0]);writer.writeheader();writer.writerows(payload['indicators'])
    summary=['# Progres original dan generator indikator 1–23','',
             'Snapshot lokal 22 Oktober 2026 setelah audit revisi final dan penyelesaian 16 generator HOLD.',
             '', '**1.150 original Drill: 1.067 generator, 83 original konseptual dengan stok, 0 HOLD, 0 unavailable.**',
             'Setiap indikator lengkap 5 level × 10 soal; seluruh 1.150 original terlayani secara lokal.', '',
             '| Kelompok | Original | Generator | Konseptual | HOLD |', '|---|---:|---:|---:|---:|']
    summary += [f"| {c['group']} | {c['originals']} | {c['generator']} | {c['stock']} | {c['held']} |" for c in groups]
    summary += ['', '| Indikator | Original | Generator | Konseptual | HOLD |','|---|---:|---:|---:|---:|']
    summary += [f"| {i} | {c['originals']} | {c['generator']} | {c['stock']} | {c['held']} |" for i,c in counts.items()]
    summary += ['', 'Tryout: **30 original, 27 generator, 3 konseptual, 0 HOLD**.',
                'Total: **1.180 original, 1.094 generator, 86 original konseptual / 248 stok varian editorial**.', '',
                '16 generator baru: indikator 1 (+1), 5 (+1), 6 (+1), 21 (+4), 22 (+3), 23 (+6).',
                'Tiga konflik kunci/opsi diperbaiki lokal dengan persetujuan pengguna. Asumsi independensi, pengambilan seragam dan pembulatan diperjelas; sumber DOCX tetap utuh.',
                '15 generator mempunyai 30 kasus berbeda dari original; pg-23-5-3 mempunyai 8 kasus (3–10 lemparan). Domain sengaja dibatasi, dapat diatur melalui konfigurasi setelah audit ulang.',
                'Pemeriksaan mencakup reproduksi original, seluruh domain, seed deterministik dan endpoint stateless.', '',
                'Cakupan ini inventaris runtime lokal dan audit 16 revisi, bukan audit akademik ulang seluruh 1.180 soal. ACTIVE menyatakan siap generator lokal; tidak menyatakan persetujuan publikasi kurikulum atau kalibrasi IRT.',
                'Database, repository Numora, stok konseptual dan penyimpanan varian runtime tidak diubah. Tidak commit/push.', '',
                '[Audit 16 soal dan koreksi](audits/2026-10-22-held-final-revisions/README.md) · [Inventaris JSON](audits/2026-10-22-held-final-revisions/progress.json)']
    (ROOT.parent/'docs/PROGRESS.md').write_text('\n'.join(summary)+'\n',encoding='utf8')
    print(json.dumps(dict(activities=activities,conceptual_variants=payload['conceptual_variants']),indent=2))


if __name__=='__main__':main()
