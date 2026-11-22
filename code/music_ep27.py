"""Soundtrack for ep27 (art gallery: crowd of phones vs the $12 gift-shop poster). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep27")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(27)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def env(d): return np.arange(int(SR*d))/SR
def harpsi(f,d=0.5,dec=6):                               # bright plucked harpsichord-ish tone
    t=env(d); return sum((0.6**k)*np.sin(2*np.pi*f*(k+1)*t)*np.exp(-t*dec*(1+0.5*k)) for k in range(5))*(1-np.exp(-t*900))
def bass(f,d=0.5):
    t=env(d); return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.exp(-t*5)*(1-np.exp(-t*300))
def shutter():                                           # camera click: two short noise ticks
    t=env(0.09); x=rng.normal(size=len(t))*np.exp(-t*160); x[int(0.045*SR):]+=rng.normal(size=len(t)-int(0.045*SR))*np.exp(-t[:len(t)-int(0.045*SR)]*200)
    return x*0.6
def boing(d=0.3):
    t=env(d); f=180+260*np.exp(-t*9)*np.abs(np.sin(t*40)); ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*np.exp(-t*6)
def slide(f0,f1,d=0.5):
    t=env(d); f=f0+(f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+0.3*np.sin(2*ph))*np.minimum(1,t*30)*np.exp(-t*1.5)
def ding():                                              # cash-register bell
    t=env(1.0); return (np.sin(2*np.pi*2093*t)+0.6*np.sin(2*np.pi*3136*t))*np.exp(-t*4)
def rustle(d):
    x=rng.normal(size=int(SR*d)); y=np.convolve(x,np.ones(40)/40,'same'); t=env(d); return (x-y)*np.sin(np.pi*t/d)
def quack():                                             # nasal buzzy duck call with a pitch drop
    t=env(0.28); f=520*np.exp(-t*2.5); ph=2*np.pi*np.cumsum(f)/SR
    saw=sum(np.sin(k*ph)/k for k in range(1,14)); return saw*np.sin(np.pi*t/0.28)**0.5*(1+0.5*np.sin(2*np.pi*28*t))*0.5
# polite gallery minuet, 3/4 at 132 bpm, G major (0 - 12.6)
b=60/132
prog=[(98.0,[392.0,493.88,587.33]),(146.83,[369.99,440.0,587.33]),(130.81,[329.63,392.0,523.25]),(146.83,[369.99,440.0,587.33])]
mel=[783.99,659.25,587.33, 659.25,739.99,783.99, 659.25,523.25,587.33, 739.99,659.25,587.33]
t=0;bar=0
while t<12.4:
    root,ch=prog[bar%4]
    add(t,bass(root),0.4)
    for k in (1,2):
        for j,f in enumerate(ch): add(t+k*b+j*0.01,harpsi(f,0.35,9),0.04)
    for k in range(3): add(t+k*b,harpsi(mel[(bar%4)*3+k],0.45,6),0.1)
    bar+=1; t+=3*b
# s0 (0.0): steady shutter clicks from the crowd, sad slide at Leo's line
for k in range(10): add(0.2+k*0.37+0.05*rng.random(),shutter(),0.25)
add(1.6,slide(520,330,0.4),0.1)
# s1 (3.8): boings for every jump, frantic shutters, a deflating slide at the camera roll
for k in range(7): add(3.8+0.2+k*0.63,boing(),0.12)
for k in range(22): add(3.8+0.3+k*0.1,shutter(),0.2)
add(3.8+2.5,slide(700,260,0.8),0.1)
# s2 (8.2): footsteps in, paper unroll, reveal fanfare + quack, register ding at "$12"
for k in range(4): add(8.2+k*0.2,bass(196,0.12),0.15)
add(9.2,rustle(0.6),0.25)
for j,f in enumerate((392.0,493.88,587.33,783.99)): add(9.8+j*0.08,harpsi(f,0.9,3),0.16)
add(10.1,quack(),0.35)
add(9.6,ding(),0.12)
add(11.2,slide(500,800,0.3),0.08)
# s3 (12.6): crowd turns - shutter storm, then a cheeky resolve
for k in range(40): add(12.9+k*0.06+0.03*rng.random(),shutter(),0.16)
for j,f in enumerate((587.33,739.99,880.0)): add(14.0+j*0.12,harpsi(f,0.7,4),0.12)
add(15.2,quack(),0.25)
for j,f in enumerate((783.99,659.25,587.33,493.88,587.33,392.0)): add(14.8+j*0.25,harpsi(f,0.5,5),0.1)
# end card (16.6)
for f in (98.0,196.0,392.0,493.88,587.33,783.99): add(16.6,harpsi(f,3.0,1.2),0.16)
add(17.1,harpsi(1567.98,2,2.5),0.06)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep27.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
