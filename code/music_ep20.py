"""Soundtrack for ep20 (baggage claim). Original, synthesised with numpy. 19.8 s, 44.1 kHz."""
import numpy as np, wave, os
SR=44100; T=19.8; n=int(SR*T); out=np.zeros(n)
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","build","ep20")); os.makedirs(OUT,exist_ok=True)
def add(t0,sig,g=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if 0<=i<n: out[i:j]+=sig[:j-i]*g
def marimba(f,d=0.5,dec=9):
    t=np.arange(int(SR*d))/SR; s=np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*f*4*t)*np.exp(-t*30)+0.15*np.sin(2*np.pi*f*2*t)
    return s*np.exp(-t*dec)*(1-np.exp(-t*600))
def bass(f,d=0.3):
    t=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.exp(-t*7)*(1-np.exp(-t*300))
rng=np.random.default_rng(20)
def shaker(d=0.06):
    m=int(SR*d); return rng.normal(size=m)*np.exp(-np.arange(m)/SR*70)
def squeak(f0=900,f1=1500,d=0.14):
    t=np.arange(int(SR*d))/SR; f=f0+(f1-f0)*np.sin(np.pi*t/d); ph=2*np.pi*np.cumsum(f)/SR
    return np.sign(np.sin(ph))*0.5*np.sin(np.pi*t/d)**2
def slide(f0,f1,d=0.7):
    t=np.arange(int(SR*d))/SR; f=f0+(f1-f0)*(t/d); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)+0.4*np.sin(2*ph)+0.2*np.sin(3*ph))*np.minimum(1,t*30)*np.exp(-t*1.5)
# bouncy carousel groove, 132 bpm, F major
b=60/132
prog=[(87.31,[349.23,440.0,523.25]),(110.0,[440.0,523.25,659.25]),(116.54,[466.16,587.33,698.46]),(130.81,[523.25,659.25,783.99])]
t=0;i=0
while t<16.4:
    root,ch=prog[(i//4)%4]
    add(t,bass(root if i%2==0 else root*1.5),0.55)
    add(t+b/2,shaker(),0.10); add(t,shaker(0.03),0.05)
    add(t+b/2,marimba(ch[i%3],0.3,14),0.16); add(t+b/2,marimba(ch[(i+1)%3],0.3,14),0.12)
    i+=1; t+=b
mel=[698.46,0,783.99,880.0,0,783.99,698.46,523.25, 587.33,0,698.46,0,880.0,783.99,0,0]
t=0;i=0
while t<16.2:
    f=mel[i%16]
    if f: add(t,marimba(f,0.45,8),0.24)
    i+=1; t+=b/2
# s0 (0.0): counter ticking up
for k in range(12): add(0.2+k*0.23,marimba(1000+k*45,0.1,30),0.12)
# s1 (3.8): bag thump, pop, duck squeaks, wrong-answer blip
add(3.8+0.8,bass(80,0.4),0.9)
for k in range(8): add(3.8+1.2+k*0.13,squeak(850+k*60,1400+k*70),0.16)
add(3.8+3.2,marimba(311.13,0.4,6),0.3); add(3.8+3.2,marimba(293.66,0.4,6),0.3)
# s2 (8.2): fanfare sparkle when Wren's bag arrives
for k,f in enumerate((698.46,880.0,1046.5,1396.9,1760.0)): add(8.2+1.45+k*0.1,marimba(f,0.9,4),0.22)
# s3 (12.6): cosy lands (ding) then dignity slides down
add(12.6+1.0,marimba(1396.9,0.9,4),0.3); add(12.6+1.2,slide(392,196,0.8),0.22)
# end card (16.6)
for f in (174.61,349.23,440.0,523.25,698.46): add(16.6,marimba(f,2.8,1.6),0.22)
add(17.1,marimba(1396.9,2,2.5),0.14); add(17.6,squeak(1000,1600,0.16),0.1)
out*=np.minimum(1,(T-np.arange(n)/SR)/0.8); out=out/np.abs(out).max()*0.8
w=wave.open(os.path.join(OUT,'music_ep20.wav'),'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
