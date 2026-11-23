"""Soundtrack for ep28 (seaside taverna: translate app orders an octopus, Wren just points). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep28")); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(28)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def env(d): return np.arange(int(SR*d))/SR
def pluck(f,d=0.3,dec=9):                                # bright metallic pluck, bouzouki-ish
    t=env(d); return sum((0.55**k)*np.sin(2*np.pi*f*(k+1)*1.003**k*t)*np.exp(-t*dec*(1+0.6*k)) for k in range(6))*(1-np.exp(-t*1500))
def trem(f,d=0.5,rate=16):                               # tremolo-picked note
    t=env(d); s=np.zeros(len(t))
    for k in range(int(d*rate)):
        i=int(k/rate*SR); p=pluck(f,0.12,14); j=min(len(s),i+len(p)); s[i:j]+=p[:j-i]*(0.7+0.3*(k%2))
    return s*np.minimum(1,(d-t)/0.05+0.01)
def bass(f,d=0.4):
    t=env(d); return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.exp(-t*6)*(1-np.exp(-t*300))
def blip(f=1320,d=0.07):
    t=env(d); return np.sin(2*np.pi*f*t)*np.exp(-t*40)
def slide(f0,f1,d=0.5):
    t=env(d); f=f0+(f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+0.3*np.sin(2*ph))*np.minimum(1,t*30)*np.exp(-t*1.5)
def ding():
    t=env(1.0); return (np.sin(2*np.pi*2093*t)+0.6*np.sin(2*np.pi*3136*t))*np.exp(-t*4)
def squish(d=0.25):                                      # wet octopus wobble
    t=env(d); f=140+90*np.sin(2*np.pi*22*t)*np.exp(-t*4); ph=2*np.pi*np.cumsum(f)/SR
    return np.tanh(2*np.sin(ph))*np.sin(np.pi*t/d)
def whoosh(d=0.35):
    x=rng.normal(size=int(SR*d)); t=env(d); y=np.convolve(x,np.ones(25)/25,'same'); return y*np.sin(np.pi*t/d)*3
def step(): t=env(0.1); return np.sin(2*np.pi*90*t)*np.exp(-t*40)
# taverna dance in D (phrygian dominant flavour), 2/4 at 140 bpm, 0 - 16.6
b=60/140
scale=[293.66,311.13,369.99,392.0,440.0,466.16,523.25,587.33]
mel=[7,6,5,4, 5,4,2,1, 0,1,2,4, 2,1,0,0]
t=0;k=0
while t<16.4:
    root=146.83 if (k//8)%2==0 else 130.81*1.0 if (k//8)%4==1 else 146.83
    add(t,bass(root/2 if k%2==0 else root),0.35)
    add(t+b/2,pluck(root*2,0.2,12),0.06); add(t+b/2,pluck(root*3,0.2,12),0.04)
    add(t,pluck(scale[mel[k%16]],0.35,7),0.11)
    if k%4==3: add(t+b/2,pluck(scale[mel[(k+1)%16]],0.2,10),0.07)
    k+=1; t+=b
# s0 (0.0): app boot blips, confident little rise
for j in range(3): add(0.3+j*0.12,blip(990+220*j),0.12)
add(1.4,slide(400,700,0.3),0.06)
# s1 (3.8): typing blips as the translations appear, highlight ding, deflating slide
for j in range(6): add(3.8+0.4+j*0.23,blip(1500),0.1)
add(3.8+2.0,ding(),0.1)
add(3.8+2.2,slide(600,300,0.7),0.1)
# s2 (8.2): footsteps, cloche lift + tremolo reveal, octopus squishes
for j in range(4): add(8.2+j*0.18,step(),0.4)
add(8.2+1.2,whoosh(),0.2)
add(8.2+1.5,trem(587.33,0.8),0.12); add(8.2+1.5,trem(466.16,0.8),0.08)
for j in range(5): add(8.2+1.9+j*0.42,squish(),0.14)
# s3 (12.6): pointing whoosh, sparkle, quick "served" ding, happy run
add(12.6+0.5,whoosh(0.3),0.15)
for j,f in enumerate((1174.66,1396.91,1760.0)): add(12.6+0.6+j*0.07,pluck(f,0.4,6),0.09)
add(12.6+1.9,ding(),0.13)
for j,f in enumerate((587.33,659.25,739.99,880.0)): add(12.6+2.0+j*0.1,pluck(f,0.4,6),0.1)
add(12.6+2.6,squish(),0.12)
# end card (16.6): bright tremolo resolve in D major
for f in (73.42,146.83,293.66): add(16.6,pluck(f,3.0,1.0),0.2)
add(16.6,trem(587.33,1.6),0.08); add(16.6,trem(739.99,1.6),0.07); add(16.6,trem(880.0,1.6),0.06)
add(18.3,pluck(1174.66,1.4,2.5),0.07)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep28.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
