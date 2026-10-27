"""Exact projected geometry, followed by deterministic native drawing layers."""
from fractions import Fraction

from expr import is_num
from .models import ImageVariantError, PyramidGeometry


def pyramid_water_vertices(apex: tuple, rim: tuple, ratio: Fraction) -> tuple:
    if not is_num(ratio) or not 0 < ratio < 1:
        raise ImageVariantError('Water ratio must be exact and between zero and one')
    if len(apex) != 2 or len(rim) != 4:
        raise ImageVariantError('Pyramid requires an apex and four rim vertices')
    if any(len(point) != 2 or any(not is_num(x) for x in point) for point in (apex, *rim)):
        raise ImageVariantError('Pyramid coordinates must be exact pairs')
    r=Fraction(ratio)
    return tuple(tuple(Fraction(p)+r*(v-p) for p,v in zip(apex,vertex)) for vertex in rim)


def build_pyramid_geometry(spec, ratio) -> PyramidGeometry:
    water=pyramid_water_vertices(spec.apex,spec.rim,ratio)
    center=tuple(sum(p[i] for p in water)/4 for i in (0,1))
    return PyramidGeometry(Fraction(ratio),water,center)


def draw_pyramid(image, spec, geometry, scale):
    """Draw an empty vessel first; no original 2/3 water survives in the base."""
    from PIL import Image, ImageDraw
    def point(p):
        return tuple(round(Fraction(n)*scale) for n in p)
    def line(draw,points,fill,width=1):
        draw.line([point(p) for p in points],fill=fill,width=width*scale)
    def dashed(draw,a,b,fill=(75,85,95),width=1):
        for n in range(0,40,2):
            points=[tuple(Fraction(x)+Fraction(k,40)*(y-x) for x,y in zip(a,b)) for k in (n,n+1)]
            line(draw,points,fill,width)
    p=spec.apex;v=spec.rim;w=geometry.water
    layer=Image.new('RGBA',image.size,(0,0,0,0));d=ImageDraw.Draw(layer)
    d.polygon([point(q) for q in (p,v[3],v[2])],fill=(110,130,145,35))
    image=Image.alpha_composite(image.convert('RGBA'),layer)
    d=ImageDraw.Draw(image)
    dashed(d,v[1],p,fill=(95,105,110,255))
    # Water faces meet at the same projected apex; surface uses all four W_i.
    for vertices,color in (((p,w[1],w[2]),(65,170,215,100)),
                           ((p,w[0],w[1]),(60,160,215,100)),
                           ((p,w[0],w[3]),(35,160,210,125)),
                           ((p,w[3],w[2]),(25,135,190,145)),
                           (w,(85,195,230,115))):
        layer=Image.new('RGBA',image.size,(0,0,0,0))
        ImageDraw.Draw(layer).polygon([point(q) for q in vertices],fill=color)
        image=Image.alpha_composite(image,layer)
    d=ImageDraw.Draw(image)
    line(d,(*w,w[0]),(35,130,175,255))
    line(d,(*v,v[0]),(20,30,35,255),2)
    for i in (0,2,3):line(d,(v[i],p),(20,30,35,255),2)
    center=tuple(sum(q[i] for q in v)/4 for i in (0,1))
    dashed(d,center,p,fill=(60,75,85,255))
    # Total-height ticks and dynamic water-height bracket use the same axis.
    x=134
    line(d,((x,center[1]),(x,p[1])),(35,45,50,255))
    for y in (center[1],p[1]):line(d,((x-6,y),(x+6,y)),(35,45,50,255))
    x=480;y=geometry.surface_center[1]
    dashed(d,geometry.surface_center,(x,y),fill=(70,105,125,255))
    line(d,((x,y),(x,p[1])),(55,85,100,255))
    for h in (y,p[1]):line(d,((x-5,h),(x+5,h)),(55,85,100,255))
    line(d,((x,(y+p[1])/2),(491,201)),(70,100,115,255))
    return image.convert('RGB')
