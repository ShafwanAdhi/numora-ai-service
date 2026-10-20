"""Approved local source repairs; existing engine, bounded numerical families."""
import re
from copy import deepcopy
from fractions import Fraction
from build_drill_1_5_level45_batch1 import Author
from author_drill_6_7_level45_batch4 import _nums

def revise(entry):
    e=deepcopy(entry); case=tuple(e[k] for k in ('indicator','level','source_number'))
    raw=deepcopy(e.get('source_projection_resolved') or e['source_projection'])
    s=deepcopy(raw); s['format']=e['format']
    s['stem']=re.sub(r'^(?:\([abc]\)\s*(?:BENAR|SALAH)\s*\n)+','',s['stem'])
    if case==(6,4,2):
        s['stem']+=' Setiap orang mengonsumsi 1 porsi per hari. Pasokan sponsor mulai diterima pada awal hari ke-3 sebelum konsumsi hari tersebut.'
        s['options'][2]='Hari ke-10'
        exp='Konsumsi awal 20 porsi/hari. Sisa akhir hari kedua 80 porsi. Konsumsi mulai hari ketiga 30 porsi/hari dengan pasokan 20 porsi/hari. Sisa bertahan 8 hari; habis akhir hari ke-10. C benar.'
    elif case==(6,4,4):
        s['options'][2]=r'$\frac{47}{3}$ hari (15 hari 16 jam)'
        exp='Pakan awal 600 jatah-harian. Lima hari pertama memakai 200, empat hari berikutnya memakai 200. Sisa 200 untuk 30 ayam bertahan 20/3 hari; total 47/3 hari. C benar.'
    elif case==(6,4,8):
        s['stem']+=' Semua kondisi bekerja 5 hari per minggu; produktivitas per jam-pekerja sama.'
        exp='Produktivitas 240/(6*8*5)=1 unit/jam-pekerja. Kondisi B 8*6*5=240 jam-pekerja sehingga X=240; Y=300/(10*5)=6. A,B,C benar; D salah.'
    elif case==(6,4,10):
        s['options'][2]=s['options'][2].replace(r'33,3\%',r'\frac{100}{3}\%')
        exp='Beban tersisa 240 hari-pekerja; waktu efektif 15 hari; kebutuhan 16 pekerja, tambahan 4. Kenaikan jam tepat 100/3 persen. Pernyataan 1 dan 3 benar.'
    elif case==(6,5,2):
        s['options'][1]='1,5 hari'; s['options'][2]='1,25 hari'
        exp='Sisa pekerjaan 15*(8-3)=75 relawan-hari; 12 relawan memerlukan 6,25 hari kerja. Tambahan 6,25-5=1,25 hari kerja. C benar.'
    elif case==(6,5,4):
        s['stem']=s['stem'].replace('pilihan komposisi pekerja yang paling tepat dan efisien','komposisi pekerja yang memenuhi target dengan jumlah pekerja paling sedikit')
        s['stem']+=' Penjahit tambahan dapat direkrut tanpa batas ketersediaan, dengan produktivitas sama seperti kelompok asalnya.'
        s['options'][3]='10 penjahit dari Kelompok Y saja'
        exp='Produktivitas X=120/(4*5)=6 dan Y=180/(6*4)=7,5 potong/orang/hari. Satu Y menghasilkan 30 potong dalam 4 hari. Minimum 300/30=10 pekerja Y; opsi lain tidak memenuhi target. D benar.'
    elif case==(6,5,8):
        s['stem']+=' Satu porsi adalah jatah konsumsi satu ternak selama satu hari; konsumsi setiap ternak sama dan tetap.'
        s['options'][3]=s['options'][3].replace('porsi-hari','porsi')
        exp='P=30*20=600 porsi. Q=600/40=15 hari; R=600/12=50 ekor. Jumlah ternak dan durasi berbanding terbalik. A,C,D benar.'
    elif case==(6,5,10):
        s['options'][1]='Tambahan minimum pekerja agar selesai tepat waktu adalah 3 orang.'
        exp='Empat dari 12 hari menyelesaikan 60 meter. Waktu efektif 12-4-2=6 hari; sisa 120 meter membutuhkan 8 pekerja. Tambahan minimum 2, bukan 3. Pernyataan 1 dan 3 benar.'
    elif case==(7,4,4):
        s['stem']=s['stem'].replace('memiliki penyelesaian $x=0$','memiliki satu-satunya penyelesaian $x=0$')
        s['options'][1]='Kesimpulan Andi benar, karena satu-satunya penyelesaian adalah $x=0$.'
        exp='Kedua ruas menyederhana menjadi 6x-6 sehingga setiap bilangan real memenuhi. x=0 adalah salah satu solusi, bukan satu-satunya. Kesimpulan Budi benar; A.'
    elif case==(7,5,8):
        s['stem']='Dua toko menjual kaus tim. Toko A memasang harga $3x+15.000$ rupiah per kaus. Toko B memasang harga $5x-25.000$ rupiah per kaus. Harga satu kaus pada kedua toko sama. Manakah evaluasi yang benar? (Jawaban benar lebih dari satu)'
        s['options'][0]='Nilai $x$ yang memenuhi adalah 20.000.'
        exp='3x+15000=5x-25000 memberi x=20000. Harga satu kaus Rp75000, dua kaus Rp150000. Harga kedua toko sama. A,B,D benar.'
    elif case==(7,5,9):
        s['stem']=s['stem'].replace('banyak siswa yang meminjam masing-masing 2 buku cerita','banyak siswa kelompok pertama yang masing-masing meminjam 2 buku cerita')
        s['stem']+=' Sebanyak 18 buku dipinjam kelompok lain dan jumlah ini tetap. Empat buku tambahan pada pernyataan ketiga dipinjam siswa baru pada kelompok pertama, masing-masing 2 buku per siswa.'
        exp='2n+18=50 memberi n=16. Total seluruh buku 50, bukan 32. Empat buku tambahan berarti dua siswa baru sehingga n=18. Pernyataan 1 dan 3 benar.'
    elif case==(9,4,1):
        s['options'][0]='Rp19.000,00'; s['options'][2]='Rp18.000,00'
        exp='Sistem 2n+3m=31000 dan 4n+m=37000 memberi n=8000 dan m=5000. Harga n+2m=18000. C benar.'
    elif case==(9,5,1):
        s['options'][0]='Salah, karena harga tiket sepeda air Rp12.500,00 dan komidi putar Rp20.000,00.'
        exp='Sistem 3s+2k=85000 dan 2s+4k=90000 memberi s=20000, k=12500. Sepeda air lebih mahal; alasan B tepat. A salah harga, C salah hasil, D mengasumsikan diskon tanpa data.'
    elif case==(9,5,5):
        s['stem']='Taman sekolah berbentuk persegi panjang. Siswa A menyatakan keliling taman 36 meter, sehingga $p+l=18$. Siswa B menyatakan selisih panjang dan lebar 4 meter, sehingga $p-l=4$. Pengelola menyatakan luas taman 80 meter persegi. Evaluasi yang tepat adalah ....'
        s['options']=['Salah, karena luas taman yang benar adalah 72 meter persegi.',
            'Salah, karena panjang taman 10 meter dan lebar 8 meter.',
            'Salah, karena panjang 11 meter, lebar 7 meter, dan luas 77 meter persegi.',
            'Benar, karena panjang taman 12 meter dan lebar 6 meter.']
        exp='p+l=18 dan p-l=4 memberi p=11, l=7. Luas 77 meter persegi, bukan 80. C benar.'
    elif case==(9,5,7):
        s['stem']+=' Harga satuan setiap jenis barang sama pada kedua toko. Semua jumlah kaus kaki dan sarung tangan pada paket dihitung per pasang.'
        exp='Sistem 2k+3s=70000 dan 4k+s=65000 memberi k=12500 dan s=15000 rupiah per pasang. Sarung tangan lebih mahal. B,D benar.'
    elif case==(10,4,2):
        s['stem']=s['stem'].replace('Selisih banyak buku antara Kelompok A dan Kelompok B','Banyak buku Kelompok A dikurangi banyak buku Kelompok B')
        s['options'][0]='$5a-10b+9$'; s['options'][2]='$5a-10b+15$'
        exp='Kelompok A=8a-4b+12, kelompok B=3a+6b-3. A dikurangi B=5a-10b+15. C benar.'
    elif case==(10,5,9):
        s['options'][2]=s['options'][2].replace(' (dalam ribuan)','')
        exp='2(x^2+3x-4)+3(x^2-2x+2)=5x^2-2. Koefisien x nol. Pada x=3 total 43 rupiah. Pernyataan 1 dan 3 benar.'
    else: raise ValueError(case)
    s['explanation']=exp
    e.pop('source_projection_resolved',None); e['source_projection']=s
    e['generator_raw_source_projection']=raw
    e['generator_source_review']=dict(date='2026-10-21',status='ENGINEERING_REVIEWED_NOT_CURRICULUM_APPROVED',
        authorization='USER_APPROVED_MINIMUM_LOCAL_REVISION',findings=e['issues'],
        source_validity=e['validity'],source_answer_status=e['answer_status'],
        actions=[dict(component=k,before=raw.get(k),after=s[k]) for k in ('stem','options','key','explanation') if raw.get(k)!=s[k]])
    return e

def author(e):
    a=Author(e); case=(a.i,a.l,a.n)
    if case==(6,4,2):
        a.stem=a.nums(a.stem,{'120':'120+60*k','20':'20+10*k'})
        a.options=[a.nums(t,{str(n):f'{n}+4*k'}) for t,n in zip(a.options,(5,6,10,8))]
        exp='Konsumsi awal [[20+10*k]] porsi/hari; sisa [[80+40*k]]. Mulai hari ketiga konsumsi [[30+10*k]] dengan pasokan [[20+10*k]], pengurangan bersih 10. Habis akhir hari ke-[[10+4*k]]. C benar.'
    elif case==(6,4,4):
        a.stem=a.nums(a.stem,{'15':'15+3*k'})
        for j,n in ((0,13),(1,14),(3,18)): a.options[j]=a.nums(a.options[j],{str(n):f'{n}+4*k'})
        a.options[2]=a.nums(a.options[2],{'47':'47+12*k','15':'15+4*k'})
        exp='Pakan awal [[600+120*k]] jatah-harian. Dua fase pertama memakai 400; sisa [[200+120*k]] untuk 30 ayam. Durasi total tepat [[47+12*k]]/3 hari = [[15+4*k]] hari 16 jam. C benar.'
    elif case==(6,4,8):
        a.stem=a.nums(a.stem,{'240':'240*(k+1)','300':'300*(k+1)'})
        a.options[0]=a.nums(a.options[0],{'240':'240*(k+1)'})
        a.answer_value(1,'240',' jam-pekerja per minggu')
        exp='Produktivitas [[k+1]] unit/jam-pekerja. Jam-pekerja mingguan A dan B sama, 240. X=[[240*(k+1)]], Y=6. A,B,C benar; D salah.'
    elif case==(6,4,10):
        a.stem=a.nums(a.stem,{'12':'12+3*k'})
        a.options[0]=a.nums(a.options[0],{'240':'240+60*k'})
        a.options[1]=a.nums(a.options[1],{'3':'3+k'})
        a.options[2]=a.nums(a.options[2],{'12':'12+3*k'})
        exp='Beban tersisa [[240+60*k]] hari-pekerja; waktu efektif 15 hari. Diperlukan [[16+4*k]] pekerja, tambahan [[4+k]], bukan [[3+k]]. Kenaikan jam tepat 100/3 persen. Pernyataan 1 dan 3 benar.'
    elif case==(6,5,2):
        a.stem=a.nums(a.stem,{'8':'8+4*k'})
        for j,n in enumerate(('1','1,5','1,25','2')): a.options[j]=a.nums(a.options[j],{n:f'{n.replace(",",".")}+k'})
        exp='Sisa [[75+60*k]] relawan-hari dikerjakan 12 orang selama [[6.25+5*k]] hari. Waktu rencana tersisa [[5+4*k]] hari. Tambahan [[1.25+k]] hari kerja. C benar.'
    elif case==(6,5,4):
        a.stem=a.nums(a.stem,{'300':'300+30*k'})
        a.options[3]=a.nums(a.options[3],{'10':'10+k'})
        exp='X menghasilkan 6 potong/orang/hari, Y 7,5. Target [[300+30*k]] dalam 4 hari memerlukan minimum [[10+k]] pekerja Y, karena tiap Y menghasilkan 30 potong. D benar; opsi lain tidak memenuhi target.'
    elif case==(6,5,8):
        a.stem=a.nums(a.stem,{'30':'30*(k+1)','40':'40*(k+1)'})
        a.options[2]=a.nums(a.options[2],{'50':'50*(k+1)'})
        a.options[3]=a.nums(a.options[3],{'600':'600*(k+1)'})
        exp='P=[[600*(k+1)]] porsi; Q=15 hari; R=[[50*(k+1)]] ekor. Konsumsi satu porsi/ekor/hari. Hubungan berbalik nilai. A,C,D benar.'
    elif case==(6,5,10):
        a.stem=a.nums(a.stem,{'180':'180*(k+1)','6':'6*(k+1)'})
        a.options[0]=a.nums(a.options[0],{'60':'60*(k+1)'})
        a.options[1]=a.nums(a.options[1],{'3':'3*(k+1)'})
        exp='Panjang selesai [[60*(k+1)]] meter. Sisa [[120*(k+1)]] meter dalam 6 hari membutuhkan [[8*(k+1)]] pekerja. Tambahan minimum [[2*(k+1)]], bukan [[3*(k+1)]]. Pernyataan 1 dan 3 benar.'
    elif case==(7,4,4):
        a.stem=a.stem.replace('3x-5','3x-'+a.var('5+k','5')).replace('6x-6','6x-'+a.var('6+2*k','6'))
        a.options[0]=a.options[0].replace('6x-6','6x-'+a.var('6+2*k','6'))
        exp='Kedua ruas menjadi 6x-[[6+2*k]]. Konstanta kedua ruas -[[6+2*k]]. Semua bilangan real memenuhi, sehingga Andi salah mengklaim solusi tunggal. Budi benar; A.'
    elif case==(7,5,8):
        a.allnums({n:f'{n.replace(".","")}*(k+1)' for n in ('15.000','25.000','20.000','75.000','150.000')})
        exp='Persamaan harga memberi x=[[20000*(k+1)]]. Harga satu kaus [[75000*(k+1)]] rupiah; dua kaus [[150000*(k+1)]]. Harga kedua toko sama. A,B,D benar.'
    elif case==(7,5,9):
        a.stem=a.stem.replace('=50','='+a.var('50+2*k','50'))
        a.options[0]=a.nums(a.options[0],{'16':'16+k'})
        a.options[1]=a.nums(a.options[1],{'32':'32+2*k'})
        a.options[2]=a.nums(a.options[2],{'18':'18+k'})
        exp='Total buku [[50+2*k]], kelompok lain 18 tetap. n=[[16+k]]; tambahan 4 buku untuk dua siswa baru memberi n=[[18+k]]. Pernyataan 1 dan 3 benar.'
    elif case in ((9,4,1),(9,5,1),(9,5,7)):
        values={(9,4,1):('31.000','37.000','19.000','20.000','18.000','22.000'),
                (9,5,1):('85.000','90.000','12.500','20.000','15.000'),
                (9,5,7):('70.000','65.000','12.500','15.000')}[case]
        a.allnums({n:f'{n.replace(".","")}*(k+1)' for n in values})
        exp={(9,4,1):'Harga nasi [[8000*(k+1)]], minuman [[5000*(k+1)]]. Total pesanan [[18000*(k+1)]] rupiah. C benar.',
             (9,5,1):'Harga sepeda air [[20000*(k+1)]], komidi putar [[12500*(k+1)]] rupiah. Sepeda air lebih mahal. B benar; A salah harga; C salah hasil; D tanpa data diskon.',
             (9,5,7):'Harga kaus kaki [[12500*(k+1)]], sarung tangan [[15000*(k+1)]] rupiah per pasang. Sarung tangan lebih mahal. B,D benar.'}[case]
    elif case==(9,5,5):
        a.stem=a.nums(a.stem,{'36':'36+4*k','18':'18+2*k','80':'80+18*k+k*k'})
        a.options[0]=a.nums(a.options[0],{'72':'72+18*k+k*k'})
        a.options[1]=a.nums(a.options[1],{'10':'10+k','8':'8+k'})
        a.options[2]=a.nums(a.options[2],{'11':'11+k','7':'7+k','77':'77+18*k+k*k'})
        a.options[3]=a.nums(a.options[3],{'12':'12+k','6':'6+k'})
        exp='Panjang [[11+k]], lebar [[7+k]], luas [[77+18*k+k*k]] meter persegi. Klaim [[80+18*k+k*k]] salah. C benar.'
    elif case==(10,4,2):
        a.stem=a.stem.replace('2a-b+3','2a-b+'+a.var('3+k','3'))
        a.options=[a.nums(t,{'9':'9+4*k','15':'15+4*k'}) for t in a.options]
        exp='A = 8a-4b+[[12+4*k]], B = 3a+6b-3. A-B = 5a-10b+[[15+4*k]]. C benar.'
    elif case==(10,5,9):
        a.stem=a.stem.replace('$2(', '$'+a.var('2*(k+1)','2')+'(').replace('$3(', '$'+a.var('3*(k+1)','3')+'(')
        a.options[0]=a.options[0].replace('5{x}',a.var('5*(k+1)','5')+'{x}').replace('-2','-'+a.var('2*(k+1)','2'))
        a.options[1]=a.nums(a.options[1],{'6':'6*(k+1)'})
        a.options[2]=a.nums(a.options[2],{'43':'43*(k+1)'})
        exp='Total [[5*(k+1)]]x^2-[[2*(k+1)]]. Koefisien x nol. Pada x=3 total [[43*(k+1)]] rupiah. Pernyataan 1 dan 3 benar.'
    else: raise ValueError(case)
    a.exp=a.explanation(exp)
    for name in ('x','n','m','p','l'):
        if any('{'+name+'}' in t for t in [a.stem,*a.options,a.exp]):
            a.variables[name]=dict(gen='derived',expr=repr('{'+name+'}')+' if k == 0 else '+repr(name))
    return a

def _math(text):
    return re.findall(r'\$([^$]+)\$',text)

def _poly(text):
    from author_drill_10_level45_batch4 import _poly as parse
    if 'n' in text:
        from sympy import Symbol
        return parse(text.replace('n','x')).subs(Symbol('x'),Symbol('n'))
    return parse(text)

def _prices(values):
    a,b,total,d,e,total2=values[:6]
    determinant=a*e-b*d
    assert determinant
    return (total*e-b*total2)/determinant,(a*total2-total*d)/determinant

def check_math(qid,c):
    from sympy import Symbol,solve
    from math import ceil
    case=tuple(map(int,qid.split('-')[1:])); stem=c['stem']
    texts=[o['text'] for o in c['options']]
    options=[_nums(t.split(' (hasil: ')[0]) for t in texts]; v=_nums(stem)
    if case==(6,4,2):
        stock,planned,elapsed,sponsor,added=v[:5]
        assert '1 porsi per hari' in stem and 'awal hari ke-3 sebelum konsumsi' in stem
        target=elapsed+(stock-stock/planned*elapsed)/(stock/planned+added-sponsor)
        truths=[n[0]==target for n in options]; expected=[stock/planned,target]
    elif case==(6,4,4):
        birds,planned,buyday,bought,sellday,sold=v
        first=buyday-1; second=sellday-first; final=birds+bought-sold
        stock=birds*planned; remaining=stock-birds*first-(birds+bought)*second
        target=first+second+remaining/final
        claims=[n[0] if j!=2 else n[0]/n[1] for j,n in enumerate(options)]
        assert options[2][2]+options[2][3]/24==claims[2]
        truths=[n==target for n in claims]; expected=[stock,remaining,target.numerator]
    elif case==(6,4,8):
        workers,hours,out,workers2,hours2,hours3,out3,days=v
        assert '5 hari per minggu' in stem
        productivity=out/(workers*hours*days)
        total2=workers2*hours2*days; production2=total2*productivity
        workers3=out3/(hours3*days*productivity)
        assert 'sama' in texts[1] and 'lebih banyak' in texts[3]
        truths=[options[0][0]==production2,workers*hours*days==total2,
                options[2][0]==workers3,production2>out]
        if 'hasil:' in texts[1]: assert _nums(texts[1].split('hasil: ')[1])[0]==total2
        expected=[productivity,production2,workers3]
    elif case==(6,4,10):
        planned,workers,elapsed,pause=v
        remaining=workers*(planned-elapsed); time=planned-elapsed-pause
        minimum=ceil(remaining/time)-workers
        rate=Fraction(100)*((planned-elapsed)/time-1)
        claims=options[2]
        truths=[options[0]==[pause,remaining],options[1][0]>=minimum,
                claims[0]==workers and claims[1]/claims[2]==rate]
        expected=[remaining,ceil(remaining/time),minimum]
    elif case==(6,5,2):
        total,planned,workers,elapsed,left,total2=v
        assert total==total2
        time=(planned-elapsed)*workers/(workers-left)
        extra=time-(planned-elapsed)
        truths=[ns[0]==extra for ns in options]; expected=[time,extra]
    elif case==(6,5,4):
        wx,px,dx,wy,py,dy,target,deadline=v
        assert 'Penjahit tambahan dapat direkrut' in stem and 'paling sedikit' in stem
        rx,ry=px/(wx*dx),py/(wy*dy)
        quantities=[(options[0][0],0),(0,options[1][0]),tuple(options[2]),(0,options[3][0])]
        minimum=ceil(target/(max(rx,ry)*deadline))
        truths=[(nx*rx+ny*ry)*deadline>=target and nx+ny==minimum for nx,ny in quantities]
        expected=[rx,ry,target,minimum]
    elif case==(6,5,8):
        label1,birds,days,label2,birds2,label3,days3=v
        assert (label1,label2,label3)==(1,2,3)
        assert 'jatah konsumsi satu ternak selama satu hari' in stem and 'porsi-hari' not in texts[3]
        stock=birds*days; time=stock/birds2; birds3=stock/days3
        truths=[options[0]==[2,time],False,options[2]==[3,birds3],options[3][0]==stock]
        assert 'senilai' in texts[1]
        expected=[stock,time,birds3]
    elif case==(6,5,10):
        length,planned,workers,elapsed,pause=v
        rate=length/(planned*workers); done=length*elapsed/planned; time=planned-elapsed-pause
        required=ceil((length-done)/(rate*time)); minimum=required-workers
        assert 'minimum' in texts[1]
        truths=[options[0]==[elapsed,done],options[1][0]==minimum,options[2][0]==time]
        expected=[done,length-done,required,minimum]
    elif case==(7,4,4):
        equation=_math(stem)[0].split('='); left,right=map(_poly,equation)
        assert left==right
        assert 'satu-satunya' in stem and 'satu-satunya' in texts[1]
        claim=_math(texts[0])[0].split('=')
        truths=[_poly(claim[0])==_poly(claim[1])==left,False,False,False]
        expected=[abs(left.subs(Symbol('x'),0))]
    elif case==(7,5,8):
        x=Symbol('x'); p1,p2=map(_poly,_math(stem))
        value=solve(p1-p2,x)[0]; price=p1.subs(x,value)
        truths=[options[0][0]==value,options[1]==[1,price],p2.subs(x,value)>price,
                options[3][0]*price==options[3][1]]
        expected=[value,price,2*price]
    elif case==(7,5,9):
        n=Symbol('n'); left,right=map(_poly,_math(stem)[0].split('='))
        students=solve(left-right,n)[0]; other=left.subs(n,0); per=left.coeff(n)
        assert '18 buku dipinjam kelompok lain' in stem and 'siswa baru' in stem
        extra,claimed=options[2]
        truths=[options[0][0]==students,options[1][0]==right,claimed==students+extra/per]
        assert other==18
        expected=[right,students,students+extra/per]
    elif case==(9,4,1):
        rice,drink=_prices(v); quantity1,quantity2=v[6:]
        cost=rice*quantity1+drink*quantity2
        truths=[ns[0]==cost for ns in options]; expected=[rice,drink,cost]
    elif case==(9,5,1):
        water,carousel=_prices(v)
        assert 'Salah' in texts[0] and 'Salah' in texts[1] and 'Benar' in texts[2]
        truths=[water>carousel and options[0]==[water,carousel],
                water>carousel and options[1]==[1,water,carousel],
                water<carousel and options[2][-2:]==[water,carousel],False]
        assert 'potongan' in texts[3]
        expected=[water,carousel]
    elif case==(9,5,5):
        equations=_math(stem); total=_poly(equations[0].split('=')[1]); difference=_poly(equations[1].split('=')[1])
        p,w=(total+difference)/2,(total-difference)/2; area=p*w; claim=v[-1]
        assert v[0]==2*total and v[2]==difference
        truths=[claim!=area and options[0][0]==area,
                claim!=area and options[1]==[p,w],
                claim!=area and options[2]==[p,w,area],claim==area and options[3]==[p,w]]
        expected=[p,w,area,claim]
    elif case==(9,5,7):
        socks,gloves=_prices(v)
        assert 'Harga satuan setiap jenis barang sama' in stem and 'dihitung per pasang' in stem
        truths=[options[0]==[1,socks],options[1]==[1,socks],gloves<socks,options[3]==[1,gloves]]
        expected=[socks,gloves]
    elif case==(10,4,2):
        a,b=map(_poly,_math(stem)); target=(a-b).expand()
        assert 'Kelompok A dikurangi' in stem
        truths=[_poly(_math(t)[0])==target for t in texts]
        expected=[abs(a.subs({Symbol('a'):0,Symbol('b'):0})),target.subs({Symbol('a'):0,Symbol('b'):0})]
    elif case==(10,5,9):
        x=Symbol('x'); target=sum(map(_poly,_math(stem))).expand()
        point=_poly(_math(texts[2])[0].split('=')[1]); result=target.subs(x,point)
        assert 'dalam ribuan' not in texts[2]
        truths=[_poly(_math(texts[0])[0])==target,options[1][0]==target.coeff(x),options[2][-1]==result]
        expected=[target.coeff(x,2),abs(target.subs(x,0)),result]
    else: raise AssertionError(case)
    assert list(map(bool,truths))==[bool(o['correct']) for o in c['options']],(qid,v,options,truths)
    explanation=_nums(c['explanation'].split('\n\n')[0])
    assert all(n in explanation for n in expected),(qid,expected,explanation)

def check_stock(record):
    """Classify the rendered equations by degree and number of variables."""
    from sympy import Poly
    equations=_math(record['stem']); assert len(equations)==4
    classifications=[]
    for equation in equations:
        left,right=map(_poly,equation.split('=')); polynomial=(left-right).expand()
        classifications.append(len(polynomial.free_symbols)==1 and Poly(polynomial).total_degree()==1)
    assert [o['text'] for o in record['options']]==[
        'Persamaan (i) dan (iii) merupakan Persamaan Linear Satu Variabel (PLSV).',
        'Persamaan (ii) merupakan PLSV karena hanya memiliki satu variabel.',
        'Persamaan (iv) bukan PLSV karena melibatkan dua variabel.',
        'Persamaan (iii) bukan PLSV karena bentuknya pecahan.']
    # Options always refer to i/iii, ii, iv, iii, respectively.
    truth=[classifications[0] and classifications[2],classifications[1],not classifications[3],not classifications[2]]
    assert [o['id'] for o,t in zip(record['options'],truth) if t]==record['key'].split(',')
    assert classifications==[True,False,True,False]
    assert 'penyebut konstan' in record['explanation']
