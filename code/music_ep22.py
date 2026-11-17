"""Soundtrack for ep22 (hotel pool sunbeds). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep22")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(22)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def steel(f,d=0.6,dec=6):                            # steel-drum-ish
    t=np.arange(int(SR*d))/SR; s=np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*2.0*t)*np.exp(-t*9)+0.25*np.sin(2*np.pi*f*3.01*t)*np.exp(-t*14)
    return s*np.exp(-t*dec)*(1-np.exp(-t*500))
def bass(f,d=0.3):
    t=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.exp(-t*7)*(1-np.exp(-t*300))
def shaker(d=0.06,dec=70):
    m=int(SR*d); x=rng.normal(size=m); x=np.diff(x,prepend=0); return x*np.exp(-np.arange(m)/SR*dec)
def thud(f=110,d=0.18):                              # towel landing
    t=np.arange(int(SR*d))/SR; return np.sin(2*np.pi*f*np.exp(-t*9)*t)*np.exp(-t*22)+0.3*rng.normal(size=len(t))*np.exp(-t*60)
def beep(f=1760,d=0.07):
    t=np.arange(int(SR*d))/SR; return np.sign(np.sin(2*np.pi*f*t))*0.5*np.minimum(1,t*400)*np.minimum(1,(d-t)*400)
def slide(f0,f1,d=0.7):
    t=np.arange(int(SR*d))/SR; f=f0+(f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+0.4*np.sin(2*ph)+0.2*np.sin(3*ph))*np.minimum(1,t*30)*np.exp(-t*1.5)
def noise(d,lp=40):
    m=int(SR*d); x=rng.normal(size=m); return np.convolve(x,np.ones(lp)/lp,'same')
def thunder(d=1.4):
    x=noise(d,400); t=np.arange(len(x))/SR; return x*np.exp(-t*2.5)*np.minimum(1,t*40)*14
def rainbed(d):
    x=noise(d,6); t=np.arange(len(x))/SR; return x*np.minimum(1,t*3)*np.minimum(1,(d-t)*3)
def splash(d=0.7):
    x=noise(d,12); t=np.arange(len(x))/SR; return x*np.minimum(1,t*25)*np.exp(-t*5)*3
# calypso groove, 120 bpm, C major
b=60/120
prog=[(65.41,[523.25,659.25,783.99]),(87.31,[523.25,698.46,880.0]),(98.0,[493.88,587.33,783.99]),(65.41,[523.25,659.25,783.99])]
t=0;bar=0
while t<16.4:
    root,ch=prog[bar%4]
    for k,(off,mul) in enumerate(((0,1),(1.5,1),(2,1.5),(3,1),(3.5,1.5))): add(t+off*b,bass(root*mul,0.35),0.55)
    for off in (0.5,1.5,2.5,3.5):
        for f in ch: add(t+off*b,steel(f,0.25,14),0.045)
    for k in range(8): add(t+k*b/2,shaker(),0.05 if k%2 else 0.03)
    bar+=1; t+=4*b
mel=[783.99,0,659.25,783.99,0,880.0,783.99,0, 880.0,0,698.46,880.0,0,1046.5,880.0,0, 987.77,0,783.99,587.33,0,783.99,987.77,0, 1046.5,0,783.99,659.25,0,523.25,0,0]
t=0;i=0
while t<16.2:
    f=mel[i%32]
    if f: add(t,steel(f,0.55,6),0.2)
    i+=1; t+=b/2
# s0 (0.0): a towel lands on each sunbed, pitch falling as hope fades
for i in range(6): add(0.45+i*0.36,thud(150-i*12),0.5); add(0.45+i*0.36,steel(1318.5*2**(-i/6),0.25,12),0.14)
add(2.6,slide(520,300,0.5),0.16)
# s1 (3.8): alarm clock rings until 2.0, sad slide when he sees the towels
tt=3.8
while tt<3.8+2.0:
    for k in range(4): add(tt+k*0.09,beep(),0.07)
    tt+=0.5
add(3.8+1.1,slide(440,220,0.7),0.18); add(3.8+2.95,steel(1567.98,0.5,6),0.2)
# s2 (8.2): towel slap + fanfare, thunder at 2.2, rain from 2.3, umbrella pop at 2.5
add(8.2+0.6,thud(140),0.6)
for k,f in enumerate((523.25,659.25,783.99,1046.5)): add(8.2+0.7+k*0.1,steel(f,0.6,5),0.22)
add(8.2+2.2,thunder(),0.5); add(8.2+2.3,rainbed(2.0),0.5); add(8.2+2.55,steel(880,0.3,10),0.2); add(8.2+3.1,slide(392,262,0.5),0.14)
# s3 (12.6): flamingo paddles in, splash, sparkle
add(12.6+0.2,splash(0.9),0.3); add(12.6+0.9,splash(0.5),0.2)
for k,f in enumerate((783.99,987.77,1174.66,1567.98,2093.0)): add(12.6+1.5+k*0.09,steel(f,0.9,4),0.18)
add(12.6+2.85,steel(1567.98,0.5,6),0.2)
# end card (16.6)
for f in (65.41,130.81,261.63,329.63,392.0,523.25): add(16.6,steel(f,2.8,1.6),0.22)
add(17.1,steel(1567.98,2,2.5),0.14); add(17.6,splash(0.5),0.12)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep22.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
