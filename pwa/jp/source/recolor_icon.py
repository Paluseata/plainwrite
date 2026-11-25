"""Plainwrite-J icon: the Plainwrite icon with a sakura-pink body on a white page (sakura over rice). The screen stays as it is."""
import sys
from PIL import Image
BG=(18,20,23);BODY=(43,48,55);KEY=(59,64,72);FKEY=(79,88,99)
T_BODY=(242,183,199);T_PRESS=(222,146,170);PRESS_SRC=(52,58,66);T_KEY=(226,150,172);T_FKEY=(251,214,223)
LCD=(179,188,163);T_BG=(255,255,255)
def onseg(c,a,b):
    d=[b[i]-a[i] for i in range(3)];t=sum((c[i]-a[i])*d[i] for i in range(3))/sum(x*x for x in d)
    if not .04<t<=1:return None
    return t if t<.97 and sum((a[i]+d[i]*t-c[i])**2 for i in range(3))<30 else None
def lum(c):return .3*c[0]+.59*c[1]+.11*c[2]
def lerp(a,b,t):return tuple(round(a[i]+(b[i]-a[i])*t) for i in range(3))
def remap(c,knots):   # piecewise-linear along the source greys' brightness
    L=lum(c)
    for (s0,t0),(s1,t1) in zip(knots,knots[1:]):
        a,b=lum(s0),lum(s1)
        if a<=L<=b or (L<a and s0 is knots[0][0]) or (L>b and s1 is knots[-1][0]):
            return lerp(t0,t1,min(1,max(0,(L-a)/(b-a))))
    return c
def run(src,dst):
    im=Image.open(src).convert('RGBA');W,H=im.size;px=im.load()
    # the middle row of keys (the file keys) is the lighter one: find its rows
    frows=[y for y in range(H) if any(px[x,y][:3]==FKEY for x in range(W))]
    f0,f1=(min(frows),max(frows)) if frows else (H,H)
    pad=max(2,H//128)
    near=lambda c:sum((c[i]-PRESS_SRC[i])**2 for i in range(3))<=12
    pp=[(x,y) for y in range(f0-pad,min(H,f1+pad+1)) for x in range(W) if near(px[x,y][:3])]
    m=max(2,H//100)
    # the biggest run of that colour along the row is the pressed key (stray edge pixels elsewhere don't count)
    from collections import Counter
    cols=Counter(p[0] for p in pp);runs=[];cur=[]
    for x in sorted(cols):
        if cur and x-cur[-1]>1:runs.append(cur);cur=[]
        cur.append(x)
    if cur:runs.append(cur)
    best=max(runs,key=lambda r:sum(cols[x] for x in r)) if runs else None
    if best:
        ys=[p[1] for p in pp if best[0]<=p[0]<=best[-1]]
        pb=(best[0]-m,min(ys)-m,best[-1]+m,max(ys)+m)
    else:pb=None
    for y in range(H):
        for x in range(W):
            r,g,b,a=px[x,y]
            if (r,g,b)==BG:px[x,y]=T_BG+(a,);continue
            t=onseg((r,g,b),BODY,LCD) if g>=b-1 else None                       # the screen's soft edge against the body
            if t is not None:px[x,y]=lerp(T_BODY,LCD,t)+(a,);continue
            if g>b+5 and g>=r:continue                        # the green screen and its text
            fk=f0-pad<=y<=f1+pad
            if pb and pb[0]<=x<=pb[2] and pb[1]<=y<=pb[3]:   # the pressed file key (Plainwrite 1.03 icon): deeper pink
                L0,L1=lum(BODY),lum(PRESS_SRC);t=min(1,max(0,(lum((r,g,b))-L0)/(L1-L0)))
                px[x,y]=lerp(T_BODY,T_PRESS,t)+(a,);continue
            knots=[(BG,T_BG),(BODY,T_BODY),(FKEY,T_FKEY)] if fk else [(BG,T_BG),(BODY,T_BODY),(KEY,T_KEY)]
            px[x,y]=remap((r,g,b),knots)+(a,)
    im.save(dst)
for s,d in zip(sys.argv[1::2],sys.argv[2::2]):run(s,d)
