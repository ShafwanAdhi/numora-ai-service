"""Real formula-linked families for indicator 4/5 level 4/5 questions."""
from copy import deepcopy
import re
from build_drill_1_5_level45_batch1 import Author
from expr import placeholders

EQUAL_COMPOSITION={'pg-4-4-4','mcma-4-4-8','pg-4-5-4','mcma-4-5-8','kategori-4-5-9'}
def _qid(e):
 s=e['source_projection']; return f"{s['format'].lower()}-{e['indicator']}-{e['level']}-{e['source_number']}"

def prepare(entry,academic):
 if not academic.get('issues') or academic.get('validity')=='VALID':
  if academic.get('recommendation')=='NO_BLOCKING_ACADEMIC_FINDING': return entry,[]
 out=deepcopy(entry); q=out['source_projection']; qid=_qid(out); reasons=[x['proposed_correction'] for x in academic['issues']]
 if qid in EQUAL_COMPOSITION: q['stem']+='\nSyarat pembagian: setiap kelompok atau wadah harus memiliki komposisi yang sama untuk masing-masing jenis, semua item utuh, dan seluruh item terbagi habis.'
 if qid=='pg-4-4-5':
  q.update(stem='Balok kecil berukuran $12 cm×15 cm×20 cm$ disusun searah tanpa celah dan tanpa memotong balok untuk membentuk sebuah kubus. Panjang rusuk kubus terkecil yang dapat dibentuk adalah ....',options=['$30 cm$','$40 cm$','$60 cm$','$120 cm$'],key=['C'],key_caption='C. $60 cm$',explanation='Pembahasan:\nRusuk kubus harus habis dibagi 12, 15, dan 20. $KPK(12,15,20)=60$, jadi rusuknya $60 cm$. Jumlah balok adalah $(60÷12)(60÷15)(60÷20)=60$ balok; angka 60 balok berbeda besaran dari panjang rusuk 60 cm.')
 elif qid=='mcma-4-4-7': q['explanation']=q['explanation'].replace('detik ke-48','menit ke-48')
 elif qid=='mcma-4-4-8': q['additional_notes']='Sembilan wadah bukan maksimum; 27 membagi kedua jumlah.'
 elif qid=='pg-4-5-4': q['key_caption']='C. Laporan Regu B'
 elif qid=='pg-4-5-5':
  q['stem']=q['stem'].replace('jika kriteria yang diinginkan adalah memperpanjang rentang waktu jatuh tempo bersamaan?','jika kedua usulan wajib dibandingkan dengan jadwal awal 42 hari dan kriterianya adalah memperpanjang rentang waktu jatuh tempo bersamaan?')
  q['options']=['Kebijakan I memenuhi kriteria karena $KPK(7,14)=14$ hari','Kebijakan II memenuhi kriteria karena $KPK(12,18)=36$ hari','Kedua kebijakan memenuhi kriteria karena intervalnya positif','Tidak ada kebijakan yang memenuhi kriteria karena $14<42$ dan $36<42$ hari']; q['key']=['D']; q['key_caption']='D. Tidak ada kebijakan yang memenuhi kriteria'; q['explanation']='Pembahasan:\nJadwal awal: $KPK(14,21)=42$ hari. Kebijakan I: $KPK(7,14)=14$ hari. Kebijakan II: $KPK(12,18)=36$ hari. Karena 14 dan 36 kurang dari 42, tidak ada usulan yang memperpanjang rentang dibandingkan dengan jadwal awal.'
 elif qid=='mcma-4-5-7': q['additional_notes']='Jumlah kejadian memakai floor(300÷72)=4, tanpa pembulatan.'
 elif qid in {'pg-5-4-3','pg-5-5-3'}: q['stem']+='\nSetiap wadah mula-mula kosong, tidak bocor, tidak memiliki aliran lain, dan debit rata-rata dihitung selama pengisian.'
 elif qid=='kategori-5-4-10': q['additional_notes']='14 jam adalah distraktor; 108÷9=12 jam.'
 elif qid=='pg-5-5-4': q['key']=['B']; q['key_caption']='B. Evaluasi Y'
 if reasons:
  q['key_caption']=(q.get('key_caption') or ', '.join(q['key']))+' (draft koreksi)'
  q['explanation']=q['explanation'].replace('Pembahasan:','Pembahasan draft koreksi:',1)
  q['additional_notes']=('PROPOSED — draft karantina untuk review akademik. '+q.get('additional_notes','')).strip()
 return out,reasons

def author(entry):
 a=Author(entry); i,l,n=a.i,a.l,a.n; z='k+1'
 a.variables['k']['range']=[0,24]
 if i==4 and n==2:
  e2=('2+k%10' if l==4 else '3+k%10'); e3='2+k//10'
  # Replace complete products so the two independent shared exponents are never conflated.
  m=a.var(e2+'+1','3'); n2=a.var(e2,'2' if l==4 else '3'); m3=a.var(e3+'+1','3'); n3=a.var(e3,'2')
  if l==4:
   a.stem=a.stem.replace('{2}^{3}×{3}^{3}',f'{{2}}^{{{m}}}×{{3}}^{{{m3}}}').replace('{2}^{2}×{3}^{2}',f'{{2}}^{{{n2}}}×{{3}}^{{{n3}}}')
   a.options=[x.replace('{2}^{3}×{3}^{3}',f'{{2}}^{{{m}}}×{{3}}^{{{m3}}}').replace('{2}^{2}×{3}^{2}',f'{{2}}^{{{n2}}}×{{3}}^{{{n3}}}').replace('{2}^{2}×3',f'{{2}}^{{{n2}}}×3') for x in a.options]
  else:
   hi2=a.var(e2+'+1','4'); hi3=a.var(e3+'+1','3')
   a.stem=a.stem.replace('{2}^{4}×{3}^{2}',f'{{2}}^{{{hi2}}}×{{3}}^{{{n3}}}').replace('{2}^{3}×{3}^{3}',f'{{2}}^{{{n2}}}×{{3}}^{{{hi3}}}').replace('{2}^{3}×{3}^{2}',f'{{2}}^{{{n2}}}×{{3}}^{{{n3}}}')
   a.options=[x.replace('{2}^{4}×{3}^{3}',f'{{2}}^{{{hi2}}}×{{3}}^{{{hi3}}}').replace('{2}^{3}×{3}^{2}',f'{{2}}^{{{n2}}}×{{3}}^{{{n3}}}') for x in a.options]
  a.exp=a.explanation('Faktor sekutu 2 dan 3 memakai pangkat terkecil [['+e2+']] dan [['+e3+']]. FPB = 2^[['+e2+']] × 3^[['+e3+']] = [[2**('+e2+')*3**('+e3+')]].')
 elif i==4 and n in (3,4,8,9,10):
  raw=a.stem+' '.join(a.options); keep={'9'} if n==9 else set(); mp={x:f'{x}*({z})' for x in set(re.findall(r'(?<![\w.,])\d+(?![\d.,])',raw)) if x not in keep and int(x)>=9}
  base={(4,3):24,(4,4):24,(4,8):27,(4,10):30,(5,3):36,(5,4):27,(5,8):48,(5,9):30}[(l,n)]
  a.allnums(mp); a.exp=a.explanation('Hitung FPB dari dua jumlah yang ditampilkan: FPB = [['+str(base)+'*('+z+')]]. Periksa keterbagian, isi tiap kelompok, dan syarat maksimum pada setiap opsi.')
 elif i==4 and n==5 and l==4:
  a.allnums({x:f'{x}*({z})' for x in ('12','15','20','30','40','60','120')}); a.exp=a.explanation('KPK tiga ukuran = [[60*('+z+')]] cm. Jumlah balok = (60/12)(60/15)(60/20)=60.')
 elif i==4 and n==5:
  a.allnums({x:f'{x}*({z})' for x in ('7','12','14','18','21','36','42')}); a.exp=a.explanation('KPK awal = [[42*('+z+')]], usulan I = [[14*('+z+')]], usulan II = [[36*('+z+')]]. Keduanya lebih pendek; opsi D benar.')
 elif i==4 and n==7:
  p,q,d,period=(16,24,120,48) if l==4 else (24,36,300,72)
  if l==4:
   per='24*(k+2)'; dur='120 if k==0 else 72*(k+2)-1'
   a.allnums({'16':'8*(k+2)','24':'12*(k+2)','48':per,'120':dur})
   hour=a.var("'08' if 8+floor(24*(k+2)/60)==8 else '09' if 8+floor(24*(k+2)/60)==9 else 8+floor(24*(k+2)/60)",'08')
   minute=a.var("'00' if (24*(k+2))%60==0 else (24*(k+2))%60",'48')
   a.options=[x.replace('08.48',hour+'.'+minute) for x in a.options]
   a.options=[x.replace('2 jam (',a.var("''",'2 jam (')).replace(' menit)',' menit'+a.var("''",')')) for x in a.options]
  else:
   per=f'{period}*({z})'; dur=f'{d}*({z})'; a.allnums({str(p):f'{p}*({z})',str(q):f'{q}*({z})',str(period):per,str(d):dur,'12':f'12*({z})'})
   a.stem=a.stem.replace('$5$ menit','$'+a.var('5*(k+1)','5')+'$ menit')
   a.options=[x.replace('FPB(24,36)','FPB('+a.var('24*(k+1)','24')+','+a.var('36*(k+1)','36')+')') for x in a.options]
  a.exp=a.explanation('KPK periode = [['+per+']]. Frekuensi setelah awal = floor([['+dur+']]/[['+per+']]) = [['+str(d//period)+']].')
 elif i==5 and n==2:
  b,o,new,r=(600,5,10,300) if l==4 else (400,6,12,200)
  double=f'{2*b:,}'.replace(',','.')
  a.allnums({str(b):f'{b}+20*k',double:f'2*({b}+20*k)',str(o):f'{o}+k',str(new):f'2*({o}+k)',str(r):f'({b}+20*k)/2'})
  a.exp=a.explanation('Ukuran nyata = [['+f'({o}+k)*({b}+20*k)'+']]. Gambar baru dua kali lebih besar, sehingga penyebut skala baru = [['+f'({b}+20*k)/2'+']].')
 elif i==5 and n==3:
  v1,t1,v2,t2,q1,q2,d=(360,18,600,24,20,25,5) if l==4 else (400,16,720,24,25,30,5)
  targets=(f'{d}+k-2',f'{d}+k',f'{d}+k+2',f'{d}+k+5')
  for j,literal in enumerate(('3','5','7','10')): a.options[j]=a.nums(a.options[j],{literal:targets[j]})
  a.allnums({str(v1):f'{q1}*({t1}+k)',str(t1):f'{t1}+k',str(v2):f'({q2}+k)*({t2}+k)',str(t2):f'{t2}+k',str(q2):f'{q2}+k',str(d):f'{d}+k'})
  a.exp=a.explanation('Debit pertama = [['+str(q1)+']], debit kedua = [['+f'{q2}+k'+']], selisih = [['+f'{d}+k'+']] liter/menit.')
 elif i==5 and n==4:
  c1,p1,c2,p2,u1,u2,d=(12,42000,20,66000,3500,3300,200) if l==4 else (15,60000,25,92500,4000,3700,300)
  fmt=lambda x:f'{x:,}'.replace(',','.')
  a.allnums({str(c1):f'{c1}+k',fmt(p1):f'{u1}*({c1}+k)',str(c2):f'{c2}+k',fmt(p2):f'({u2}-10*k)*({c2}+k)',fmt(u1):str(u1),fmt(u2):f'{u2}-10*k',str(d):f'{d}+10*k'})
  a.exp=a.explanation('Harga per unit pertama = [['+str(u1)+']], kedua = [['+f'{u2}-10*k'+']], selisih = [['+f'{d}+10*k'+']].')
 elif i==5 and n==5:
  if l==4:
   a.allnums({x:f'{x}*({z})' for x in ('2','16','5','40','7','56','72','10','3','9')})
   target='9'
  else:
   a.stem=a.stem.replace('$8$ | $64$','$'+a.var('8*('+z+')','8')+'$ | $'+a.var('64*('+z+')','64')+'$')
   a.stem=a.stem.replace('dari $64$ ke','dari $'+a.var('64*('+z+')','64')+'$ ke')
   a.stem=a.stem.replace('($8+', '($'+a.var('8*('+z+')','8')+'+')
   a.stem=a.stem.replace(r'\frac{64}{8}',r'\frac{'+a.var('64*('+z+')','64')+'}{'+a.var('8*('+z+')','8')+'}')
   a.allnums({x:f'{x}*({z})' for x in ('3','24','6','48','88','10','2','11','12')}); target='11'
  a.exp=a.explanation('Setiap pasangan tabel menghasilkan laju 8 per jam. Waktu target = [['+target+'*('+z+')]] jam. Substitusi laju tersebut memverifikasi opsi yang benar.')
 elif i==5 and n==10:
  rate=9; raw=a.stem+' '.join(a.options); mp={x:f'{x}*({z})' for x in set(re.findall(r'(?<![\w.,])\d+(?![\d.,])',raw)) if int(x)>rate and int(x)%rate==0}; mp[str(rate)]=f'{rate}*({z})'; a.allnums(mp)
  a.exp=a.explanation('Semua pasangan tabel menghasilkan laju yang sama, [['+f'{rate}*({z})'+']] per jam. Substitusi laju tersebut memverifikasi opsi yang benar.')
 elif i==5 and n==7:
  sc,x,y=(250,14,8) if l==4 else (300,12,8); rl=x*sc//100; rw=y*sc//100; area=rl*rw
  a.allnums({str(sc):f'{sc}*({z})',str(rl):f'{rl}*({z})',str(rw):f'{rw}*({z})',str(area):f'{area}*({z})**2'})
  a.exp=a.explanation('Panjang = [['+f'{rl}*({z})'+']] m, lebar = [['+f'{rw}*({z})'+']] m, luas = [['+f'{area}*({z})**2'+']] m^2.')
 elif i==5 and n==8:
  d1,t1,d2,t2,v=(120,2,135,2.25,60) if l==4 else (140,2,175,2.5,70)
  a.allnums({str(d1):f'({v}+k)*{t1}',str(d2):f'({v}+k)*{t2}',str(v-10):f'{v}+k-10',str(v):f'{v}+k'})
  a.exp=a.explanation('Kecepatan pertama = [['+f'{v}+k'+']] dan kecepatan kedua = [['+f'{v}+k'+']] km/jam; keduanya sama.')
 else: raise AssertionError(a.qid)
 # Qualitative keyed options must also carry the newly computed conclusion so
 # the strict same-answer guard sees a substantively different answer.
 conclusions={
  'pg-4-5-2':(0,'2**(3+k%10)*3**(2+k//10)',' sebagai nilai FPB'),
  'pg-4-5-4':(2,'27*(k+1)',' kelompok'),
  'pg-5-4-4':(1,'200+10*k',' rupiah per pulpen'),
  'pg-5-4-5':(2,'9*(k+1)',' jam'),
  'pg-5-5-2':(2,'(400+20*k)/2',' sebagai penyebut skala'),
  'pg-5-5-3':(1,'5+k',' liter/menit'),
  'pg-5-5-4':(1,'300+10*k',' rupiah per buku'),
  'pg-5-5-5':(1,'11*(k+1)',' jam'),
 }
 if a.qid in conclusions:
  idx,expr,unit=conclusions[a.qid]
  a.options[idx]+=a.var("', dengan hasil '",'')+a.var(expr,'')+a.var(repr(unit),'')
 # Function commas are argument separators, not Indonesian decimal marks.
 if i==4:
  def parameterize_call(match):
   parts=[]
   for token in match[2].split(','):
    parts.append(a.var(str(int(token))+'*(k+1)',token) if token.strip().isdigit() else token)
   return match[1]+'('+','.join(parts)+')'
  a.stem=re.sub(r'\b(FPB|KPK)\(([^)]*)\)',parameterize_call,a.stem)
  a.options=[re.sub(r'\b(FPB|KPK)\(([^)]*)\)',parameterize_call,text) for text in a.options]
 for name in placeholders(a.stem+''.join(a.options)+a.exp)-a.variables.keys():
  a.variables[name]=dict(gen='derived',expr=f"'{{{name}}}' if k == 0 else {name!r}",fmt='id')
 return a
