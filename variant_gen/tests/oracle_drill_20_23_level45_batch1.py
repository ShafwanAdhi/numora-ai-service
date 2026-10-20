"""Independent exact arithmetic from rendered stimulus/options; never reads config values."""
import re
from collections import Counter
from fractions import Fraction as F
from statistics import median

from drill_11_15_math import nums


def stats(values):
    counts=Counter(values);highest=max(counts.values())
    modes=sorted(v for v,n in counts.items() if n==highest) if highest>1 else []
    return sum(values)/len(values),F(median(values)),modes,max(values)-min(values)


def check_math(q,c):
    case=tuple(map(int,q.split('-')[1:]));s=c['stem'];options=c['options']
    p=[nums(o['text']) for o in options];v=nums(s)
    def annex(index,value):return not p[index] or p[index]==[value]
    def rates():
        total=int(re.search(r'dilempar(?: sebanyak)? (\d+) kali',s,re.I)[1])
        pairs=[(int(a),int(b)) for a,b in re.findall(r'angka ([1-6]) muncul (\d+) kali',s,re.I)]
        assert [a for a,b in pairs]==list(range(1,7)),q
        counts=[F(b) for a,b in pairs];assert sum(counts)==total and min(counts)>=0,q
        return total,counts,[n/total for n in counts]
    def total_event():
        total=F(re.search(r'dilempar(?: sebanyak)? (\d+) kali',s,re.I)[1])
        event=F(re.search(r'muncul(?: sebanyak)? (\d+) kali',s,re.I)[1])
        assert 0<=event<=total,q
        return total,event

    if case==(20,4,7):
        assert len(v)==8 and all(0<=x<=100 for x in v),v
        mean,med,modes,spread=stats(v);answer=mean
        truth=[p[0]==modes,p[1]==[med],p[2]==[mean],p[3]==[spread],all(x>p[4][0] for x in v)]
    elif case==(20,4,9):
        data=[F(n) for n in re.findall(r'^\| (?:Senin|Selasa|Rabu|Kamis) \| (\d+) \|$',s,re.M)]
        assert len(data)==4 and min(data)>0,data
        mon,tue,wed,thu=data;answer=max(data)
        truth=[thu==max(data),p[1]==[tue-mon],wed==max(data),p[3]==[mon+wed]]
    elif case==(20,5,5):
        data=[F(n) for n in re.findall(r'^\| [^|]+ \| (\d+) \|$',s,re.M)]
        assert len(data)==3 and sum(data)==100 and min(data)>0,data
        low,middle,high=data;answer=middle
        assert p[0]==[high] and p[2]==[2,4,middle],p
        truth=[high>50,high==max(data),middle==max(data) and high<50,False]
    elif case==(21,4,1):
        data,claim=v[:8],v[8];assert len(v)==9 and min(data)>=0 and max(data)<=100
        _,med,_,_=stats(data);answer=med
        truth=[False,p[1]==[med] and claim!=med,p[2]==[med] and claim!=med,False]
    elif case==(21,4,2):
        assert len(v)==5;mean,med,_,_=stats(v);answer=mean
        truth=[mean>med and p[0]==[mean,med],mean>med and p[1]==[mean,med],mean<=med and p[2]==[mean,med],mean<=med and p[3]==[mean,med]]
    elif case==(21,4,3):
        assert len(v)==7;mean,med,modes,spread=stats(v);answer=modes[0]
        truth=[p[0]==[modes[0],spread],p[1]==[modes[0],spread],p[2]==[med,spread],p[3]==[mean,modes[0]]]
    elif case in ((21,4,5),(22,4,1),(22,4,6)):
        assert len(v)==10 and min(v)>=0 and max(v)<=100,v
        ma,da,_,ra=stats(v[:5]);mb,db,_,rb=stats(v[5:]);answer=ma
        same=ma==mb and da==db
        if case==(21,4,5):truth=[same and ra==rb,ra==rb,same and ra!=rb and annex(2,ma),ma!=mb]
        elif case==(22,4,1):truth=[ma>mb,da>db,same and ra!=rb and annex(2,ma),ra==rb]
        else:truth=[ma==mb and annex(0,ma),da==db,ra>rb,mb>ma,ra<rb]
    elif case==(21,4,6):
        assert len(v)==5;mean,med,modes,spread=stats(v);answer=mean
        truth=[p[0]==[mean],p[1]==[med],p[2]==modes,p[3]==[spread],mean<med]
    elif case==(21,4,7):
        assert len(v)==7 and min(v)>=0 and max(v)<=100
        mean,med,modes,spread=stats(v);answer=med
        reduced=list(v);reduced.remove(p[4][0]);new_med=F(median(reduced))
        truth=[p[0]==[med],p[1]==modes,p[2]==[spread],p[3]==[mean],p[4][1]==new_med]
    elif case==(21,5,4):
        assert len(v)==7 and min(v)>=0 and max(v)<=100,v
        data=v[:5];old,med,_,spread=stats(data);new_data=list(data)
        assert v[5]==min(data);new_data[new_data.index(v[5])]=v[6]
        new,new_med,_,new_spread=stats(new_data);answer=new
        truth=[new>old and med==new_med and new_spread<spread and annex(0,new),
               new<old and new_med>med and spread==new_spread,
               new==old and new_med<med and new_spread>spread,
               new>old and new_med>med and new_spread==spread]
    elif case==(21,5,9):
        assert len(v)==5;mean,med,modes,spread=stats(v);answer=mean
        truth=[p[0]==[mean],p[1]==[med],p[2]==modes,p[3]==[spread]]
    elif case==(22,4,2):
        assert len(v)==10;ma,_,_,ra=stats(v[:5]);mb,_,_,rb=stats(v[5:]);answer=ma
        truth=[ra>rb,rb>ra and annex(1,ma),ra==rb,ma>mb]
    elif case==(22,4,4):
        assert len(v)==10 and min(v)>=0 and max(v)<=100
        _,da,moa,ra=stats(v[:5]);_,db,mob,rb=stats(v[5:]);answer=da
        truth=[da>db and bool(mob) and max(moa)>max(mob),da==db and rb>ra and annex(1,da),ra>rb,p[3]==mob]
    elif case==(22,4,8):
        assert len(v)==10;ma,da,_,ra=stats(v[:5]);mb,db,_,rb=stats(v[5:]);answer=mb
        truth=[mb>ma,da==db,rb>ra,p[3]==[ma],False]
    elif case==(22,5,10):
        assert len(v)==10;ma,da,_,ra=stats(v[:5]);mb,db,modes,rb=stats(v[5:]);answer=ma
        truth=[ma>mb,da==db,ra>rb,p[3]==modes]
    elif case==(23,4,1):
        total,event=total_event();answer=event/total
        assert all(len(x)==1 and 0<=x[0]<=1 for x in p)
        truth=[x==[answer] for x in p]
    elif case==(23,4,2):
        total,event=total_event();answer=(total-event)/total
        assert all(len(x)==1 and 0<=x[0]<=1 for x in p)
        truth=[x==[answer] for x in p]
    elif case==(23,4,3):
        assert len(v)==2;total,event=v;assert 0<=event<=total
        answer=event/total;assert 0<=p[4][0]<=p[4][1]==100
        truth=[False,p[1]==[answer],p[2]==[answer],False,False]
    elif case==(23,4,4):
        assert len(v)==2;total,odd=v;assert 0<=odd<=total
        answer=(total-odd)/total
        assert all(len(x)==1 and 0<=x[0]<=1 for x in p)
        truth=[x==[answer] for x in p]
    elif case in ((23,4,6),(23,4,9),(23,5,6)):
        total,counts,frequencies=rates();answer=frequencies[0]
        if case==(23,4,6):
            truth=[p[0]==[1,frequencies[0]],p[1]==[4,frequencies[3]],p[2]==[6,frequencies[5]],p[3]==[2,frequencies[1]],p[4]==[sum(frequencies)]]
        elif case==(23,4,9):
            assert p[3]==[2,3],p
            truth=[p[0]==[1,frequencies[0]],p[1]==[4,frequencies[3]],p[2]==[5,frequencies[4]],counts[1]>counts[2]]
        else:
            assert p[3]==[3,5],p
            truth=[p[0]==[1,frequencies[0]],p[1][0]==4 and abs(p[1][1]-frequencies[3])<=F(1,2000),
                   p[2][0]==6 and abs(p[2][1]-frequencies[5])<=F(1,2000),counts[2]>counts[4],p[4]==[sum(frequencies)]]
    elif case==(23,4,10):
        total,event=total_event();answer=event/total
        truth=[p[0]==[answer],p[1]==[(total-event)/total],p[2]==[F(1,2)],p[3]==[abs(2*event-total)]]
    elif case==(23,5,1):
        total,event=total_event();answer=event/total;claim=v[-1]
        truth=[p[0]==[event,total,claim] and claim==answer,abs(p[1][0]-answer)<=F(1,2000) and claim!=answer,False,claim==answer,False]
    elif case==(23,5,10):
        total,event=total_event();answer=event/total
        truth=[p[0]==[answer],p[1]==[(total-event)/total],p[2]==[F(1,2)],p[3]==[abs(answer-F(1,2))]]
    else:raise AssertionError(case)
    assert [o['correct'] for o in options]==truth,(q,v,p,truth)
    assert nums(c['explanation'])[0]==answer,(q,c['explanation'],answer)
