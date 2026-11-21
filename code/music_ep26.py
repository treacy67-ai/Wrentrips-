"""Soundtrack for ep26 (camping trip, 10-minute tent vs pop-up tent). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep26")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(26)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def env(d): return np.arange(int(SR*d))/SR
def guitar(f,d=0.6,dec=5):                               # strummed-guitar-ish pluck
    t=env(d); return (np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*2*f*t)*np.exp(-t*8)+0.25*np.sin(2*np.pi*3*f*t)*np.exp(-t*15))*np.exp(-t*dec)*(1-np.exp(-t*600))
def bass(f,d=0.4):
    t=env(d); return (np.sin(2*np.pi*f*t)+0.25*np.sin(4*np.pi*f*t))*np.exp(-t*6)*(1-np.exp(-t*300))
def clank(f):                                            # metal tent pole
    t=env(0.35); return sum(np.sin(2*np.pi*f*r*t)*np.exp(-t*(9+4*k)) for k,r in enumerate((1,2.76,5.4)))*(1-np.exp(-t*2000))
def noise(d,lo=0.0):
    x=rng.normal(size=int(SR*d)); return x
def lowpass(x,a):
    y=np.zeros_like(x); acc=0.0
    for i in range(len(x)): acc+=a*(x[i]-acc); y[i]=acc
    return y
def whoosh(d=0.8):
    t=env(d); x=lowpass(noise(d),0.08); return x*np.sin(np.pi*t/d)**2
def slide(f0,f1,d=0.5):
    t=env(d); f=f0+(f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+0.3*np.sin(2*ph))*np.minimum(1,t*30)*np.exp(-t*1.5)
def pop():
    t=env(0.25); f=220*np.exp(-t*12)+70; ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*np.exp(-t*14)
def cricket(d=0.25):
    t=env(d); return np.sin(2*np.pi*4200*t)*(np.sin(2*np.pi*30*t)>0.2)*np.exp(-t*4)
def crackle(d):
    m=int(SR*d); x=np.zeros(m); idx=rng.integers(0,m,size=int(d*25)); x[idx]=rng.uniform(-1,1,size=len(idx))
    return lowpass(x,0.5)*3
# campfire folk strum, 100 bpm, D major, through the day scenes (0 - 12.6)
b=60/100
prog=[(73.42,[293.66,369.99,440.0]),(98.0,[293.66,392.0,493.88]),(110.0,[277.18,329.63,440.0]),(73.42,[293.66,369.99,440.0])]
t=0;bar=0
while t<12.4:
    root,ch=prog[bar%4]
    for k in range(4): add(t+k*b,bass(root if k%2==0 else root*1.5),0.45)
    for k in range(4):
        for j,f in enumerate(ch if k%2==0 else ch[::-1]): add(t+k*b+(0.5*b if k%2 else 0)+j*0.015,guitar(f,0.4,9),0.045)
        for j,f in enumerate(ch): add(t+k*b+j*0.015,guitar(f,0.4,9),0.05)
    bar+=1; t+=4*b
mel=[587.33,0,659.25,739.99,880,0,739.99,0, 659.25,0,587.33,0,493.88,0,0,0, 587.33,0,659.25,739.99,880,987.77,880,0, 739.99,0,659.25,0,587.33,0,0,0]
t=0;i=0
while t<12.3:
    f=mel[i%32]
    if f: add(t,guitar(f*1.0,0.5,6),0.1)
    i+=1; t+=b/2
# s0 (0.0): poles clanking as Leo fights them, slide when Leo complains
for k in range(9): add(0.3+k*0.22,clank(900+170*(k%4)),0.07)
add(2.3,slide(500,320,0.35),0.1)
# s1 (3.8): rising sweep as the tent goes up, ta-da, then wind and a sad slide
add(4.1,slide(200,600,1.0),0.1)
for j,f in enumerate((587.33,739.99,880,1174.66)): add(5.15+j*0.07,guitar(f,0.6,4),0.14)
add(5.7,whoosh(1.6),0.35); add(6.3,whoosh(1.0),0.3)
add(6.1,slide(900,300,0.9),0.1)
for j,f in enumerate((392.0,369.99,349.23,329.63)): add(7.0+j*0.18,slide(f,f*0.97,0.3 if j<3 else 0.7),0.1)
# s2 (8.2): whoosh of the throw, POP + sparkle as the dome springs open, cheeky resolve
add(8.7,whoosh(0.8),0.3)
add(9.5,pop(),0.6)
for j,f in enumerate((1174.66,1479.98,1760.0,2349.32)): add(9.55+j*0.05,guitar(f,0.5,7),0.09)
add(11.0,slide(600,900,0.3),0.08)
for j,f in enumerate((587.33,739.99,880,1174.66)): add(11.0+0.3+j*0.08,guitar(f,0.8,4),0.13)
# s3 (12.6): night - crickets, crackling fire, slow lullaby, a plate clatter at the rent line
add(12.6,crackle(4.0),0.08)
for k in range(8): add(12.8+k*0.45,cricket(),0.025)
lull=[(587.33,0.0),(739.99,0.6),(659.25,1.2),(587.33,1.8),(493.88,2.4),(587.33,3.0)]
for f,dt in lull: add(12.6+dt,guitar(f,1.2,2.5),0.11); add(12.6+dt,bass(73.42 if dt%1.2==0 else 110.0,0.8),0.25)
for k in range(7): add(15.5+k*0.085,clank(2400+150*k),0.03)
# end card (16.6)
for f in (73.42,146.83,293.66,369.99,440.0,587.33): add(16.6,guitar(f,3.0,1.3),0.18)
add(17.1,guitar(1174.66,2,2.5),0.08)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep26.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
