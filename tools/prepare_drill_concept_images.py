"""Build twelve reviewed conceptual assets explicitly; no runtime/model/random calls."""
import io
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'variant_gen'))
from image_variants.templates import sha256

SOURCE=ROOT/'docs/sources/incoming/2026-10-27-indikator-16-19-final-images'
OUTPUT=ROOT/'variant_gen/image_templates'
IDS=('pg-16-4-2','mcma-16-4-6','mcma-16-4-7','pg-16-5-1')
INK='#263d48'; BLUE='#d6e9f2'; GREEN='#e0eee5'


def label(identity,text,box,size=18):
    return {'id':identity,'text':text,'box':box,'font_size':size,'min_font_size':14}


class Drawing:
    def __init__(self):
        self.image=Image.new('RGB',(1920,1280),'white');self.draw=ImageDraw.Draw(self.image)
        self.faces=[]
    def line(self,points,color=INK,width=2,dashed=False):
        if dashed:
            a,b=points;length=math.dist(a,b)
            for start in range(0,math.ceil(length),12):
                ts=[start/length,min(start+7,length)/length]
                self.line([(a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])) for t in ts],color,1)
        else:self.draw.line([(round(x*2),round(y*2)) for x,y in points],fill=color,width=width*2)
    def polygon(self,vertices,kind,color=BLUE):
        self.draw.polygon([(round(x*2),round(y*2)) for x,y in vertices],fill=color)
        self.line([*vertices,vertices[0]])
        self.faces.append({'kind':kind,'vertices':vertices})
    def rect(self,x,y,w,h):self.polygon([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],'rectangle')
    def circle(self,cx,cy,r):
        self.draw.ellipse(((cx-r)*2,(cy-r)*2,(cx+r)*2,(cy+r)*2),fill=GREEN,outline=INK,width=4)
        self.faces.append({'kind':'circle','center':[cx,cy],'radius':r})
    def sector(self,cx,cy,r,sweep):
        self.draw.pieslice(((cx-r)*2,(cy-r)*2,(cx+r)*2,(cy+r)*2),start=0,end=sweep,
                           fill=BLUE,outline=INK,width=4)
        self.faces.append({'kind':'sector','center':[cx,cy],'radius':r,'sweep_degrees':sweep})
    def png(self):
        stream=io.BytesIO();self.image.resize((960,640),Image.Resampling.LANCZOS).save(
            stream,format='PNG',compress_level=9,optimize=False)
        return stream.getvalue()


def panel(drawing,kind,position,caption='',identity='A'):
    x,y=position;start=len(drawing.faces)
    def rect(a,b,w,h):drawing.rect(x+a,y+b,w,h)
    def poly(vertices):drawing.polygon([(x+a,y+b) for a,b in vertices],'triangle')
    if kind=='cube':
        for a,b in [(1,0),(0,1),(1,1),(2,1),(3,1),(1,2)]:rect(110+a*38,60+b*38,38,38)
    elif kind=='prism':
        for index in range(3):rect(130+index*50,80,50,75)
        for vertices in [[(180,80),(230,80),(205,80-25*math.sqrt(3))],
                         [(180,155),(230,155),(205,155+25*math.sqrt(3))]]:poly(vertices)
    elif kind in ('pyramid','missing-pyramid'):
        rect(187,90,60,60)
        triangles=[[(187,90),(247,90),(217,38)],[(247,90),(247,150),(299,120)],
                   [(247,150),(187,150),(217,202)],[(187,150),(187,90),(135,120)]]
        for index,triangle in enumerate(triangles):
            if kind=='missing-pyramid' and index==1:continue
            poly(triangle)
    elif kind in ('cylinder','short-cylinder'):
        width=140.8 if kind=='cylinder' else 64
        rect(218-width/2,95,width,51.2)
        for cy in (72.6,168.6):drawing.circle(x+218,y+cy,22.4)
    elif kind in ('cone','short-cone'):
        drawing.sector(x+160,y+105,70,180 if kind=='cone' else 90)
        drawing.circle(x+300,y+130,35)
    else:raise ValueError(kind)
    faces=drawing.faces[start:]
    evidence={'id':identity,'kind':kind,'faces':faces,
              'rectangle_count':sum(f['kind']=='rectangle' for f in faces),
              'triangle_count':sum(f['kind']=='triangle' for f in faces),
              'circle_count':sum(f['kind']=='circle' for f in faces)}
    if 'cone' in kind:evidence['arc_relation']='shorter' if kind=='short-cone' else 'equal'
    if kind=='short-cylinder':evidence['wrap_relation']='shorter'
    labels=[label('panel_'+identity,identity,[x+5,y,x+50,y+35],24)]
    if caption:labels.append(label('caption_'+identity,caption,[x+15,y+205,x+425,y+245],16))
    return evidence,labels


def build_scenario(qid,name):
    drawing=Drawing();labels=[];geometry={}
    if qid=='pg-16-4-2' and name=='original':
        original=Image.open(SOURCE/'media/image3.png').convert('RGB').resize((754,418),Image.Resampling.LANCZOS)
        drawing.image.paste(original.resize((1508,836),Image.Resampling.NEAREST),(206,200))
        geometry={'kind':'preserved-source','source_file':'media/image3.png',
                  'panels':[{'id':p} for p in 'ABCD']}
        title='Empat jaring-jaring bangun ruang'
        alt='Panel A: persegi dengan empat segitiga. B: tiga persegi panjang dan dua segitiga. C: persegi dengan lima segitiga. D: lingkaran dan juring.'
    elif qid=='mcma-16-4-6':
        center=[(240,190),(150,346),(330,346)]
        faces=[center,[(240,190),(150,346),(60,190)],
               [(150,346),(330,346),(240,502)],[(330,346),(240,190),(420,190)]]
        for index,vertices in enumerate(faces):drawing.polygon(vertices,'triangle',GREEN if index==0 else BLUE)
        for index in range(3):drawing.line([center[index],center[(index+1)%3]],dashed=True)
        vertices=[(700,180),(580,390),(700,450),(820,390)]
        drawing.draw.polygon([(x*2,y*2) for x,y in [vertices[0],vertices[1],vertices[2]]],fill=BLUE)
        drawing.draw.polygon([(x*2,y*2) for x,y in [vertices[0],vertices[2],vertices[3]]],fill=GREEN)
        edges=[(0,1),(1,2),(2,3),(0,3),(0,2),(1,3)]
        for a,b in edges:drawing.line([vertices[a],vertices[b]],dashed=(a,b)==(1,3))
        for x,y in vertices:drawing.draw.ellipse((x*2-6,y*2-6,x*2+6,y*2+6),fill=INK)
        labels=[label('net','Jaring-jaring',[45,85,435,130],22),
                label('solid','Bangun terlipat',[525,85,915,130],22)]
        geometry={'kind':'tetrahedron','net_faces':faces,'solid_vertices':vertices,'solid_edges':edges}
        title='Jaring-jaring dan bangun terlipat'
        alt='Di kiri terdapat empat bidang segitiga yang tersambung sebagai jaring-jaring. Di kanan bangun terlipat dengan empat titik yang ditandai; garis putus-putus menunjukkan rusuk di belakang.'
    elif qid=='mcma-16-4-7' or (qid=='pg-16-5-1' and name=='stock-02'):
        drawing.rect(230,260,500,140)
        circle_centers=[(480,480)]
        if not (qid=='mcma-16-4-7' and name=='stock-01'):circle_centers.insert(0,(480,180))
        for cx,cy in circle_centers:drawing.circle(cx,cy,80)
        drawing.line([(480,480),(560,480)])
        drawing.line([(750,260),(750,400)])
        for y in (260,400):drawing.line([(740,y),(760,y)])
        labels=[label('radius','r',[565,445,650,485],22),
                label('height','h',[765,305,850,345],22),
                label('length','p',[400,305,560,345],22)]
        geometry={'kind':'cylinder-net','panels':[{'id':'net','circle_count':len(circle_centers),
                  'rectangle_count':1,'faces':drawing.faces,'label_symbols':{'r':'radius','h':'height','p':'wrap_length'}}]}
        title='Jaring-jaring tabung'
        alt=('Jaring-jaring dengan '+('satu lingkaran' if len(circle_centers)==1 else 'dua lingkaran kongruen')+
             ' dan satu persegi panjang. r menandai radius lingkaran, p panjang persegi panjang, h lebarnya.')
    else:
        if qid=='pg-16-4-2':
            kinds=['cube','prism','missing-pyramid','cone'] if name=='stock-01' else ['cylinder','pyramid','prism','short-cone']
            captions=['','','','busur = keliling alas'] if name=='stock-01' else ['p = keliling alas','','','busur < keliling alas']
        elif name=='original':
            kinds=['cylinder','prism','short-cylinder','cone']
            captions=['r = 7 cm; panjang selimut = 44 cm','','r = 7 cm; panjang selimut = 20 cm','r = 7 cm; busur juring = 44 cm']
        else:
            kinds=['prism','cylinder','short-cone','pyramid']
            captions=['tepi pasangan sama','p = keliling alas','busur < keliling alas','tepi pasangan sama']
        panels=[]
        for index,(kind,caption) in enumerate(zip(kinds,captions)):
            position=(30+(index%2)*465,80+(index//2)*250)
            evidence,more=panel(drawing,kind,position,caption,'ABCD'[index]);panels.append(evidence);labels+=more
        geometry={'kind':'four-panels','panels':panels}
        title='Empat rancangan jaring-jaring'
        alt='Empat panel A sampai D: '+ '; '.join('ABCD'[i]+': '+kind.replace('-',' ')+
             (', '+captions[i] if captions[i] else '') for i,kind in enumerate(kinds))+'. Gambar skematis.'
        alt=alt.replace('missing pyramid','persegi dan tiga segitiga').replace('short cone','lingkaran dan juring').replace('short cylinder','tabung').replace('cylinder','tabung').replace('pyramid','limas segi empat').replace('prism','prisma segitiga').replace('cube','kubus').replace('cone','kerucut')
    labels=[label('title',title,[20,15,940,65],25),*labels,
            label('schematic','Gambar skematis, tidak berskala.',[20,590,940,630],16)]
    return drawing.png(),labels,geometry,alt


def main():
    inventory_bytes=(SOURCE/'image-inventory.json').read_bytes();inventory=json.loads(inventory_bytes)
    font_sha=sha256((OUTPUT/'fonts/DejaVuSans.ttf').read_bytes())
    for qid in IDS:
        if (OUTPUT/qid).exists():raise ValueError('Refusing to overwrite existing conceptual assets: '+qid)
    reviewed={}
    for qid in IDS:
        pin=inventory['family_pins'][qid]
        source=next(a for a in inventory['assets'] if a['question_id']==qid)
        folder=OUTPUT/qid/'v1';folder.mkdir(parents=True)
        for name in ['original','stock-01','stock-02']:
            variant=None if name=='original' else qid+':'+name
            stock=next((s for s in pin['stocks'] if s['variant_id']==variant),None)
            png,labels,geometry,alt=build_scenario(qid,name)
            spec={'schema_version':1,'question_id':qid,'template_version':1,'scenario':name,
                  'renderer':'labels-v1','canvas':[960,640],'labels':labels,'alt_text':alt,
                  'geometry':geometry,'base_sha256':sha256(png),'font_sha256':font_sha,
                  'source_inventory_sha256':sha256(inventory_bytes),'source_sha256':source['sha256'],
                  'compatibility':{'original_version':pin['original_version'],'original_hash':pin['original_hash'],
                      'original_full_sha256':pin['original_full_sha256'],'stock_variant_id':variant,
                      'stock_version':stock['stock_version'] if stock else None,
                      'stock_content_sha256':stock['content_sha256'] if stock else None}}
            data=(json.dumps(spec,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
            (folder/(name+'.json')).write_bytes(data);(folder/(name+'.png')).write_bytes(png)
            reviewed[qid+':'+name]=sha256(data)
    registry=ROOT/'variant_gen/drill_concept_images/registry.py'
    if registry.exists():raise ValueError('Review registry already exists')
    registry.write_text('"""Reviewed conceptual v1 template bytes. Never refresh automatically at runtime."""\nREVIEWED_SCENARIOS = '+repr(reviewed)+'\n',encoding='utf-8')
    print('Prepared 12 conceptual scenarios; no question/config/stock files changed.')


if __name__=='__main__':main()
