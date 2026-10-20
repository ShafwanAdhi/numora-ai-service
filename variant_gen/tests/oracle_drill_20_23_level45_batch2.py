"""Recompute27 families from rendered text; never read config formulas or values."""
import re
from fractions import Fraction as F

from drill_11_15_math import nums
from oracle_drill_20_23_level45_batch1 import stats


def check_math(q,c):
    case=tuple(map(int,q.split('-')[1:]));s=c['stem'];options=c['options']
    v=nums(s);p=[nums(o['text']) for o in options]
    def annex(j,value):return not p[j] or p[j]==[value]
    def table():
        data=[F(n) for n in re.findall(r'^\| [^|]+ \| (\d+) \|$',s,re.M)]
        assert data and all(x>0 and x.denominator==1 for x in data),q
        return data
    def pair(scores=False):
        assert len(v)==10 and min(v)>=0,(q,v)
        if scores:assert max(v)<=100,(q,v)
        return stats(v[:5]),stats(v[5:])
    def fraction_pair():
        # Occurrences of the die face are fixed labels, not observed frequencies.
        assert len(v)==6 and v[1]==v[4] and 1<=v[1]<=6,(q,v)
        ta,_,ea,tb,_,eb=v
        assert 0<ea<=ta and 0<eb<=tb and all(x.denominator==1 for x in [ta,ea,tb,eb]),q
        return ea/ta,eb/tb

    if case==(20,4,2):
        data=table();assert len(data)==5
        answer=max(data)
        truth=[data[0]==answer,data[3]==answer and annex(1,data[3]),data[4]==min(data),data[2]>data[3]]
    elif case==(20,4,3):
        data=table();assert len(data)==4 and v[0]==sum(data),(q,v)
        answer=sum(data)
        # Nominal categories: bar chart compares frequencies; lines imply a sequence.
        truth=[False,annex(1,answer),False,False]
    elif case==(20,5,7):
        assert len(v)==7 and v[1:3]==[1,2] and v[4]==1 and v[6]==2,(q,v)
        middle,low,high=v[0],v[3],v[5]
        assert middle+low+high==100 and min(middle,low,high)>0
        answer=middle
        assert p[0][:2]==[1,2],p
        annotated=len(p[0])==2 or p[0][2:]==[middle]
        truth=[middle==max(middle,low,high) and annotated,False,True,False,True]
    elif case==(20,5,10):
        data=table();assert len(data)==3 and v[0]==sum(data),(q,v)
        answer=data[0]
        truth=[data[0]==max(data) and annex(0,data[0]),False,True,True]
    elif case==(21,4,4):
        assert len(v)==6 and min(v)>=0 and max(v)<=100
        data=v[:5];old,med,_,_=stats(data);new,_,_,_=stats(v);answer=old
        truth=[new==old,new>old and v[-1]>old and annex(1,old),new<old,new==med]
    elif case==(21,4,8):
        (ma,da,moa,ra),(mb,db,mob,rb)=pair(True);answer=da
        truth=[da==db and annex(0,da),bool(moa) and bool(mob) and max(mob)>max(moa),ra<rb,ma==mb,False]
    elif case==(21,5,1):
        assert len(v)==6 and min(v)>=0 and max(v)<=100
        _,med,modes,_=stats(v);assert not modes
        answer=med;truth=[False,annex(1,med),False,False]
    elif case==(21,5,2):
        assert len(v)==5 and min(v)>0
        mean,med,modes,_=stats(v)
        assert not modes and v[-1]-max(v[:-1])>2*(max(v[:-1])-min(v[:-1])) and mean>med
        answer=med;truth=[False,annex(1,med),False,False]
    elif case==(21,5,3):
        (ma,_,_,ra),(mb,_,_,rb)=pair();answer=ma
        truth=[ma==mb and v[:5]==v[5:],False,ma==mb and ra!=rb and annex(2,ma),ma<mb]
    elif case==(21,5,5):
        (ma,da,_,ra),(mb,db,_,rb)=pair();assert min(v)>0
        answer=ra;truth=[ra<rb and annex(0,ra),False,ra==rb,False]
    elif case==(21,5,8):
        assert len(v)==7 and min(v)>0
        data=v[:5];old,med,modes,spread=stats(data);new_data=list(data)
        assert v[5] in data;new_data[new_data.index(v[5])]=v[6]
        new,new_med,new_modes,new_spread=stats(new_data);answer=new
        truth=[new<old and annex(0,new),new_med==med,new_modes==modes,new_spread<spread,new_med>med]
    elif case==(21,5,10):
        (ma,da,_,ra),(mb,db,mob,rb)=pair();assert 0<min(v) and max(v)<=24
        answer=ma;truth=[ma==mb,da>db,ra>rb,p[3]==mob]
    elif case in ((22,4,5),(22,5,3)):
        (ma,da,_,ra),(mb,db,_,rb)=pair_with_claim(v,case)
        answer=da
        if case==(22,4,5):
            truth=[False,False,ma==mb and da==db and ra<rb and annex(2,da),False]
        else:
            truth=[False,False,ma==mb and da==db and ra>rb and annex(2,da),False]
    elif case==(22,4,10):
        (ma,da,_,ra),(mb,db,_,rb)=pair(True);answer=ma
        truth=[ma==mb and annex(0,ma),da==db,rb<ra,ra<rb]
    elif case==(22,5,1):
        (ma,da,_,ra),(mb,db,_,rb)=pair(True);answer=da
        truth=[ra<rb and annex(0,da),False,ra==rb,False]
    elif case==(22,5,2):
        (ma,da,_,ra),(mb,db,_,rb)=pair();assert min(v)>0;answer=ma
        truth=[ma==mb and rb>ra and annex(0,ma),ma>mb,db>da,ra==rb]
    elif case==(22,5,4):
        (ma,da,_,ra),(mb,db,_,rb)=pair(True);answer=da
        assert p[0]==[max(v[5:])],(q,p)
        truth=[False,False,da==db and ma==mb and ra!=rb and annex(2,da),da>db]
    elif case==(22,5,5):
        (_,da,_,ra),(_,db,_,rb)=pair();assert min(v)>0;answer=ra
        truth=[ra<rb and p[0]==[ra],rb<ra and p[1]==[rb],ra==rb,False]
    elif case==(22,5,6):
        (ma,da,_,ra),(mb,db,mob,rb)=pair(True);answer=ma
        truth=[ma==mb,da==db,ra>rb,p[3]==mob,ra>rb]
    elif case==(22,5,7):
        (ma,da,_,ra),(mb,db,mob,rb)=pair(True);answer=ma
        truth=[ma>mb,da>db,ra>rb,p[3]==mob,p[4]==[rb]]
    elif case==(22,5,8):
        (ma,da,_,ra),(mb,db,mob,rb)=pair();answer=ma
        truth=[ma==mb and annex(0,ma),da==db,ra>rb,p[3]==mob,ra==rb]
    elif case==(22,5,9):
        (ma,da,_,ra),(mb,db,_,rb)=pair(True);answer=ma
        truth=[ma==mb and annex(0,ma),da==db,ra>rb,p[3]==[rb]]
    elif case==(23,4,8):
        fa,fb=fraction_pair();answer=fa
        assert p[0][0]==p[1][0]==6 and p[3]==[6,F(1,6)],p
        truth=[abs(p[0][1]-fa)<=F(1,2000),abs(p[1][1]-fb)<=F(1,2000),
               abs(fa-F(1,6))<abs(fb-F(1,6)),True,p[4]==[6,F(1,6)]]
        assert p[4]==[6,fa],p
    elif case==(23,5,2):
        assert len(v)==3;total,event,claim=v;assert 0<event<=total and event.denominator==total.denominator==1
        answer=event/total;assert claim==answer
        truth=[False,False,p[2]==[answer],False,p[4]==[answer]]
        assert p[3]==[F(1,2)] and p[4]==[event],p
    elif case==(23,5,5):
        fa,fb=fraction_pair();answer=fb
        assert p[0]==[F(1,6)] and (p[1]==[F(1,6)] or p[1]==[F(1,6),fb]),p
        truth=[abs(fa-F(1,6))<abs(fb-F(1,6)),abs(fb-F(1,6))<abs(fa-F(1,6)),fa==fb,False,False]
        assert p[4]==[3,F(1,3)],p
    elif case==(23,5,9):
        assert len(v)==4 and v[1:3]==[1,2],(q,v)
        total,_,_,event=v;assert 0<event<=total and total.denominator==event.denominator==1
        answer=event/total
        truth=[p[0]==[1,2,F(1,3)],p[1]==[1,2,answer],answer==F(1,3),answer<F(1,3)]
    else:raise AssertionError(case)
    assert [o['correct'] for o in options]==truth,(q,v,p,truth)
    assert nums(c['explanation'])[0]==answer,(q,c['explanation'],answer)


def pair_with_claim(v,case):
    assert len(v)==(11 if case==(22,5,3) else 10) and min(v)>=0 and max(v)<=100,v
    if len(v)==11:assert v[-1]==max(v[:5]),v
    return stats(v[:5]),stats(v[5:10])
